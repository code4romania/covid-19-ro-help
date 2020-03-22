from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_email(template, context, subject, to):
    html = get_template(template)
    html_content = html.render(context)
    msg = EmailMultiAlternatives(subject, html_content, settings.NO_REPLY_EMAIL, [to])
    msg.attach_alternative(html_content, "text/html")
    return msg.send()
