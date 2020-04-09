import json

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

class InfoContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(f"static/data/sidebar_{translation.get_language()}.json") as info:
            context["info"] = json.loads(info.read())

        return context


class StaticPageView(InfoContextMixin, TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        return context