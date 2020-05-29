from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.timezone import now

from ..core import JobStatus
from ..core.models import Job, ModelWithMetadata
from ..core.utils.json_serializer import CustomJsonEncoder
from ..order.models import Order
from . import InvoiceEvents


class InvoiceQueryset(models.QuerySet):
    def ready(self):
        return self.filter(job__status=JobStatus.SUCCESS)


class Invoice(ModelWithMetadata):
    order = models.ForeignKey(
        Order, related_name="invoices", null=True, on_delete=models.SET_NULL
    )
    number = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)
    url = models.URLField(null=True, max_length=2048)
    objects = InvoiceQueryset.as_manager()

    def update_invoice(self, number=None, url=None):
        if number is not None:
            self.number = number
        if url is not None:
            self.url = url
        self.save()


class InvoiceJob(Job):
    status = models.CharField(
        max_length=32, default=JobStatus.PENDING, choices=JobStatus.CHOICES
    )
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name="job"
    )


class InvoiceEvent(models.Model):
    """Model used to store events that happened during the invoice lifecycle."""

    date = models.DateTimeField(default=now, editable=False)
    type = models.CharField(max_length=255, choices=InvoiceEvents.CHOICES)
    invoice = models.ForeignKey(
        Invoice, related_name="events", blank=True, null=True, on_delete=models.SET_NULL
    )
    order = models.ForeignKey(
        Order,
        related_name="invoice_events",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    parameters = JSONField(blank=True, default=dict, encoder=CustomJsonEncoder)

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.user!r})"
