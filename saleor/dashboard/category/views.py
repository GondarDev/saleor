from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from ...product.models import Category
from ..views import StaffMemberOnlyMixin, staff_member_required
from .forms import CategoryForm


@staff_member_required
def category_list(request, root=None):
    ctx = {}
    categories = Category.objects.all()
    if root:
        current_node = get_object_or_404(Category, pk=root)
        categories = current_node.get_descendants()
        ctx['current_node'] = current_node
        ctx['category_breadcrumbs'] = current_node.get_ancestors(include_self=True)
    min_level = categories[0].get_level() if categories else 0
    max_level = min_level + 1
    categories = categories.filter(level__gte=min_level, level__lte=max_level)
    ctx['categories'] = categories
    ctx['min_level'] = min_level
    return TemplateResponse(request, 'dashboard/category/list.html', ctx)


@staff_member_required
def category_details(request, pk=None, parent_pk=None):
    ctx = {}
    if pk:
        category = get_object_or_404(Category.objects.all(), pk=pk)
        title = category.name
    else:
        category = Category()
        title = _('Add new category')
    initial = {}
    if parent_pk:
        initial['parent'] = parent_pk
        ctx['parent_pk'] = parent_pk
    form = CategoryForm(request.POST or None, instance=category, initial=initial)
    if form.is_valid():
        form.save()
        if pk:
            msg = _('Updated category %s') % category
        else:
            msg = _('Added category %s') % category
        messages.success(request, msg)
        return redirect('dashboard:categories')
    else:
        if form.errors:
            messages.error(request, _('Failed to save category'))
    ctx.update({'category': category, 'form': form, 'title': title})
    return TemplateResponse(request, 'dashboard/category/detail.html', ctx)


class CategoryDeleteView(StaffMemberOnlyMixin, DeleteView):
    model = Category
    template_name = 'dashboard/category/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:categories')

    def get_context_data(self, **kwargs):
        ctx = super(CategoryDeleteView, self).get_context_data(**kwargs)
        ctx['descendants'] = list(self.get_object().get_descendants())
        ctx['products_count'] = len(self.get_object().products.all())
        return ctx

    def post(self, request, *args, **kwargs):
        result = self.delete(request, *args, **kwargs)
        messages.success(request, _('Deleted category %s') % self.object)
        return result
