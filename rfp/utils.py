from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .constants import RFP_EMAIL_SUBJECTS
from .models import AuthUser


def send_rfp_invitation_emails(rfp, vendor_ids):
    vendors = AuthUser.objects.filter(id__in=vendor_ids).order_by("id")

    for vendor in vendors:
        if not vendor.email:
            continue

        html_message = render_to_string(
            "rfp/emails/rfp_invitation.html",
            {
                "vendor_name": f"{vendor.first_name} {vendor.last_name}".strip() or vendor.username,
                "item_name": rfp.item_name,
                "item_description": rfp.item_description,
                "quantity": rfp.quantity,
                "minimum_price": int(rfp.minimum_price) if rfp.minimum_price is not None else "",
                "maximum_price": int(rfp.maximum_price) if rfp.maximum_price is not None else "",
                "last_date": rfp.last_date.date().isoformat() if rfp.last_date else "",
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=RFP_EMAIL_SUBJECTS["invitation"],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor.email],
            html_message=html_message,
            fail_silently=False,
        )


def send_quote_submission_email(rfp, vendor, quote):
    admin = rfp.created_by
    if not admin or not admin.email:
        return

    html_message = render_to_string(
        "rfp/emails/quote_submitted.html",
        {
            "admin_name": f"{admin.first_name} {admin.last_name}".strip() or admin.username,
            "vendor_name": f"{vendor.first_name} {vendor.last_name}".strip() or vendor.username,
            "vendor_email": vendor.email,
            "item_name": rfp.item_name,
            "rfp_no": rfp.rfp_no,
            "item_price": int(quote.item_price) if quote.item_price is not None else "",
            "total_cost": str(quote.total_cost) if quote.total_cost is not None else "",
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=RFP_EMAIL_SUBJECTS["quote_submitted"],
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin.email],
        html_message=html_message,
        fail_silently=False,
    )
