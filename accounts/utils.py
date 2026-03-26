from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .constants import EMAIL_SUBJECTS


def send_registration_email(user, role):
    if role == "admin":
        subject = EMAIL_SUBJECTS["admin_signup"]
    else:
        subject = EMAIL_SUBJECTS["vendor_signup"]

    html_message = render_to_string(
        "accounts/emails/registration_success.html",
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": role,
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
