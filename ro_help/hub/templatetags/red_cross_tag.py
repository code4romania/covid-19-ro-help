from django import template
from django.conf import settings
from hub.models import (
    NGO,
    NGONeed,
    KIND,
)
from django.core.cache import cache

register = template.Library()


@register.simple_tag
def fetch_red_cross_data():
    """
    Fetches and caches the red cross ong data.
    :return: the RC object and the money need if it exists.
    """
    cached_data = cache.get("red_cross")
    if cached_data:
        return cached_data
    red_cross_obj = NGO.objects.filter(name=settings.RED_CROSS_NAME).first()
    if not red_cross_obj:
        return None

    rc_tag_obj = {"obj": red_cross_obj}
    rc_tag_obj["money_need"] = NGONeed.objects.filter(ngo=red_cross_obj, kind=KIND.MONEY).first()
    cache.set("red_cross", rc_tag_obj)
    return rc_tag_obj
