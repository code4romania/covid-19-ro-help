from django import template

from hub.utils import build_full_url

TWITTER_ENDPOINT = "https://twitter.com/intent/tweet?text=%s"
FACEBOOK_ENDPOINT = "https://www.facebook.com/sharer/sharer.php?u=%s"
LINKEDIN_ENDPOINT = "https://www.linkedin.com/sharing/share-offsite/?url=%s"

register = template.Library()


@register.inclusion_tag("partials/social_sharing.html", takes_context=True)
def social_buttons(context, obj):
    request = context["request"]
    full_path_url = build_full_url(request, obj)

    context["facebook_url"] = FACEBOOK_ENDPOINT % full_path_url
    context["twitter_url"] = TWITTER_ENDPOINT % full_path_url
    context["linkedin_url"] = LINKEDIN_ENDPOINT % full_path_url
    return context
