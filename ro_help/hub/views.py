from django.views.generic import ListView

from hub.models import NGO


class NGOListView(ListView):
    # TODO: add requests_count to filters
    allow_filters = ['county', 'city']

    template_name = 'ngo/list.html'

    def get_queryset(self):
        ngos = NGO.objects.all()

        filters = {
            name: self.kwargs[name]
            for name in self.allow_filters
            if name in self.kwargs
        }

        return ngos.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ngos = context["object_list"]

        context["counties"] = ngos.order_by("county").values_list("county", flat=True).distinct("county")
        context["cities"] = ngos.order_by("city").values_list("city", flat=True).distinct("city")

        return context
