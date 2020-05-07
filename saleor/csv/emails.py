from typing import TYPE_CHECKING

from templated_email import send_templated_mail

from ..celeryconf import app
from ..core.emails import get_email_context
from ..core.utils import build_absolute_uri
from . import events

if TYPE_CHECKING:
    from .models import ExportFile


EXPORT_TEMPLATES = {"export_products": "csv/export_products_csv"}


@app.task
def send_email_with_link_to_download_csv(export_file: "ExportFile", template_name: str):
    recipient_email = export_file.created_by.email
    send_kwargs, ctx = get_email_context()
    ctx["csv_link"] = build_absolute_uri(export_file.content_file.url)
    send_templated_mail(
        template_name=EXPORT_TEMPLATES[template_name],
        recipient_list=[recipient_email],
        context=ctx,
        **send_kwargs,
    )
    events.export_file_sent_event(export_file=export_file, user=export_file.created_by)
