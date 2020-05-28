import os
import urllib.parse

from django import template
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.inclusion_tag("meta.html", takes_context=True)
def meta_tags(context):
    request = context["request"]
    image_path = urllib.parse.urljoin(settings.STATIC_URL, context.get("image", "images/logo-meta.png"))
    return {
        "url": request.build_absolute_uri,
        "type": "website",
        "title": _(context.get("title", "Luptă împotriva pandemiei de Covid-19.")),
        "image": request.build_absolute_uri(image_path),
        "description": _(
            context.get(
                "description",
                "Intră pe rohelp.ro și donează exact acolo unde este nevoie! Transparent, ușor, eficient!",
            )
        ),
    }
