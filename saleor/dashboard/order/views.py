from __future__ import unicode_literals

from django.contrib import messages
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from payments import PaymentError
from prices import Price

from ...order.models import (Order, OrderedItem, DeliveryGroup, Payment,
                             OrderNote)
from ...userprofile.forms import AddressForm
from ..views import (StaffMemberOnlyMixin, FilterByStatusMixin,
                     staff_member_required)
from .forms import (OrderNoteForm, ManagePaymentForm, MoveItemsForm,
                    ChangeQuantityForm, ShipGroupForm)


class OrderListView(StaffMemberOnlyMixin, FilterByStatusMixin, ListView):
    template_name = 'dashboard/order/list.html'
    paginate_by = 20
    model = Order
    status_choices = Order.STATUS_CHOICES
    status_order = ['new', 'payment-pending', 'fully-paid', 'shipped',
                    'cancelled']


@staff_member_required
def order_details(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related(
        'notes', 'payments', 'history', 'groups'), pk=pk)
    notes = order.notes.all()
    payment = order.payments.last()
    groups = list(order)
    for group in groups:
        group.can_ship = (payment and payment.status == 'confirmed' and
                          group.status == 'new')

    note = OrderNote(order=order, user=request.user)
    note_form = OrderNoteForm(request.POST or None, instance=note)
    if note_form.is_valid():
        note_form.save()
        order.create_history_entry(comment=_('Added note'), user=request.user)
        messages.success(request, _('Note added'))
        return redirect('dashboard:order-details', pk=pk)

    ctx = {'order': order, 'payment': payment, 'notes': notes, 'groups': groups,
           'note_form': note_form}

    captured = preauthorized = refunded = Price(
        0, currency=order.get_total().currency)
    if payment:
        ctx['can_capture'] = (payment.status == 'preauth' and
                              order.status != 'cancelled')
        ctx['can_release'] = payment.status == 'preauth'
        ctx['can_refund'] = payment.status == 'confirmed'
        preauthorized = Price(payment.total, currency=payment.currency)
        if payment.status == 'confirmed':
            captured = Price(payment.captured_amount,
                             currency=payment.currency)
        if payment.status == 'refunded':
            refunded = Price(payment.total - payment.captured_amount,
                             currency=payment.currency)
    else:
        ctx['can_capture'] = ctx['can_release'] = ctx['can_refund'] = False
    ctx['captured'] = captured
    ctx['preauthorized'] = preauthorized
    ctx['refunded'] = refunded
    return TemplateResponse(request, 'dashboard/order/detail.html', ctx)


@staff_member_required
def manage_payment(request, pk, action):
    payment = get_object_or_404(Payment, pk=pk)
    form = ManagePaymentForm(request.POST or None, payment=payment)
    if form.is_valid():
        try:
            form.handle_action(action, request.user)
        except (PaymentError, ValueError) as e:
            messages.error(request, _('Payment gateway error: ') + e.message)
        else:
            amount = form.cleaned_data['amount']
            currency = payment.currency
            if action == 'capture':
                comment = _('Captured %(amount)s %(currency)s' % {
                    'amount': amount, 'currency': currency})
            elif action == 'refund':
                comment = _('Refunded %(amount)s %(currency)s' % {
                    'amount': amount, 'currency': currency})
            elif action == 'release':
                comment = _('Released payment')
            payment.order.create_history_entry(comment=comment,
                                               user=request.user)
            messages.success(request, comment)
        return redirect('dashboard:order-details', pk=payment.order.pk)
    else:
        amount = 0
        if action == 'release':
            template = 'dashboard/includes/modal_release.html'
        else:
            if action == 'refund':
                amount = payment.captured_amount
            elif action == 'capture':
                amount = payment.order.get_total().gross
            template = 'dashboard/includes/modal_capture_refund.html'
        initial = {'amount': amount, 'action': action}
        form = ManagePaymentForm(payment=payment, initial=initial)
        ctx = {'form': form, 'action': action, 'currency': payment.currency,
               'captured': payment.captured_amount, 'payment': payment}
        return TemplateResponse(request, template, ctx)


@staff_member_required
def edit_order_line(request, pk):
    item = OrderedItem.objects.get(pk=pk)
    quantity_form = ChangeQuantityForm(request.POST or None, instance=item)
    move_items_form = MoveItemsForm(request.POST or None, instance=item)

    action = request.GET.get('action', None)
    if action == 'quantity_form' and quantity_form.is_valid():
        quantity_form.save(user=request.user)
        messages.success(request, _('Quantity updated'))
        return redirect('dashboard:order-details',
                        pk=item.delivery_group.order.pk)
    elif action == 'move_items_form' and move_items_form.is_valid():
        move_items_form.save(user=request.user)
        messages.success(request, _('Moved items'))
        return redirect('dashboard:order-details',
                        pk=item.delivery_group.order.pk)
    else:
        ctx = {'object': item, 'quantity_form': quantity_form,
               'move_items_form': move_items_form}
        ctx.update(csrf(request))
        template = 'dashboard/includes/modal_order_line_edit.html'
        return TemplateResponse(request, template, ctx)


@staff_member_required
def ship_delivery_group(request, pk):
    group = get_object_or_404(DeliveryGroup.objects.select_subclasses(), pk=pk)
    form = ShipGroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save(request.user)
        messages.success(request, _('Shipped delivery group #%s' % group.pk))
        return redirect('dashboard:order-details', pk=group.order.pk)
    else:
        ctx = {'group': group}
        ctx.update(csrf(request))
        template = 'dashboard/includes/modal_ship_delivery_group.html'
        return TemplateResponse(request, template, ctx)


@staff_member_required
def address_view(request, order_pk, group_pk=None):
    address_type = 'shipping' if group_pk else 'billing'
    order = Order.objects.get(pk=order_pk)
    if address_type == 'shipping':
        address = order.get_groups().get(pk=group_pk).address
    else:
        address = order.billing_address
    form = AddressForm(request.POST or None, instance=address)
    if form.is_valid():
        form.save()
        if address_type == 'shipping':
            msg = _('Updated shipping address for group #%s' % group_pk)
        else:
            msg = _('Updated billing address')
        order.create_history_entry(comment=msg, user=request.user)
        messages.success(request, msg)
        return redirect('dashboard:order-details', pk=order.pk)
    ctx = {'order': order, 'address_type': address_type, 'form': form}
    return TemplateResponse(request, 'dashboard/order/address-edit.html', ctx)
