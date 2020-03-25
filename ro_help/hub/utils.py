from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_email(template, context, subject, to):
    html = get_template(template)
    html_content = html.render(context)

    msg = EmailMultiAlternatives(subject, html_content, settings.NO_REPLY_EMAIL, [to])
    msg.attach_alternative(html_content, "text/html")

    return msg.send()
