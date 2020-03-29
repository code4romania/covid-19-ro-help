import os
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from django import template

register = template.Library()

@register.inclusion_tag('meta.html', takes_context=True)
def meta_tags(context):
    request = context['request']
    image_path = os.path.join(settings.STATIC_URL, context.get('image', "images/logo-meta.png"))
    image_url = "{scheme}://{host}{image_path}".format(scheme=request.scheme, host=request.get_host(), image_path=image_path)
    return {
        "url": request.build_absolute_uri,
        "type": "website",
        "title": _(context.get('title', "RO Help")),
        "image": mark_safe(image_url),
        "description": _(context.get('description', "A coherent and safe collection of aid.")),
    }
