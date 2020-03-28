from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_email(template, context, subject, to):
    html = get_template(template)
    html_content = html.render(context)

    msg = EmailMultiAlternatives(subject, html_content, settings.NO_REPLY_EMAIL, [to])
    msg.attach_alternative(html_content, "text/html")

    return msg.send()


def build_full_url(request, obj):
    """
    :param request: django Request object
    :param obj: any obj that implements get_absolute_url() and for which
    we can generate a unique URL
    :return: returns the full URL towards the obj detail page (if any)
    """
    return request.build_absolute_uri(obj.get_absolute_url())
