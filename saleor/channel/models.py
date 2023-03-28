from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from ..permission.enums import ChannelPermissions
from . import AllocationStrategy, MarkAsPaidStrategy


class Channel(models.Model):
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)
    currency_code = models.CharField(max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)
    default_country = CountryField()
    allocation_strategy = models.CharField(
        max_length=255,
        choices=AllocationStrategy.CHOICES,
        default=AllocationStrategy.PRIORITIZE_SORTING_ORDER,
    )
    order_mark_as_paid_strategy = models.CharField(
        max_length=255,
        choices=MarkAsPaidStrategy.CHOICES,
        default=MarkAsPaidStrategy.PAYMENT_FLOW,
    )

    automatically_confirm_all_new_orders = models.BooleanField(default=True, null=True)
    automatically_fulfill_non_shippable_gift_card = models.BooleanField(
        default=True,
        null=True,
    )
    order_mark_as_paid_strategy = models.CharField(
        max_length=255,
        choices=MarkAsPaidStrategy.CHOICES,
        default=MarkAsPaidStrategy.PAYMENT_FLOW,
    )

    class Meta:
        ordering = ("slug",)
        app_label = "channel"
        permissions = (
            (
                ChannelPermissions.MANAGE_CHANNELS.codename,
                "Manage channels.",
            ),
        )

    def __str__(self):
        return self.slug
