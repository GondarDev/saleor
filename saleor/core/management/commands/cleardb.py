"""Clear random data.

This command removes random data generated by `populatedb` command, such as example
orders, products or customer accounts. It doesn't remove shop's configuration, such as
an admin account, site settings or menus.
"""

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from saleor.account.models import User
from saleor.checkout.models import Checkout
from saleor.discount.models import Sale, Voucher
from saleor.order.models import Order
from saleor.payment.models import Payment, Transaction
from saleor.product.models import Product
from saleor.shipping.models import ShippingMethod


class Command(BaseCommand):
    help = "Removes data from the database preserving shop configuration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-staff",
            action="store_true",
            help="Delete staff user accounts (doesn't delete superuser accounts).",
        )

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError("Cannot clear the database in DEBUG=True mode.")

        Checkout.objects.all().delete()
        self.stdout.write("Removed checkouts")

        Transaction.objects.all().delete()
        self.stdout.write("Removed transactions")

        Payment.objects.all().delete()
        self.stdout.write("Removed payments")

        Order.objects.all().delete()
        self.stdout.write("Removed orders")

        Product.objects.all().delete()
        self.stdout.write("Removed products")

        Sale.objects.all().delete()
        self.stdout.write("Removed sales")

        ShippingMethod.objects.all().delete()
        self.stdout.write("Removed shipping methods")

        Voucher.objects.all().delete()
        self.stdout.write("Removed vouchers")

        # Delete all users except for staff members.
        staff = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        User.objects.exclude(pk__in=staff).delete()
        self.stdout.write("Removed customers")

        should_delete_staff = options.get("delete_staff")
        if should_delete_staff:
            staff = staff.exclude(is_superuser=True)
            staff.delete()
            self.stdout.write("Removed staff users")

        # Remove addresses of staff members. Used to clear saved addresses of staff
        # accounts used on demo for testing checkout.
        for user in staff:
            user.addresses.all().delete()
        self.stdout.write("Removed staff addresses")
