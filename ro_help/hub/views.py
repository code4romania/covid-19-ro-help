from django.views.generic import ListView

from hub.models import NGO


class NGOListView(ListView):
    # TODO: add requests_count to filters
    allow_filters = ['county', 'city']

    template_name = 'ngo/list.html'

    def get_queryset(self):
        ngos = NGO.objects.all()

        filters = {
            name: self.request.GET[name]
            for name in self.allow_filters
            if name in self.request.GET
        }

        return ngos.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["counties"] = NGO.objects.order_by("county").values_list("county", flat=True).distinct("county")

        cities = NGO.objects.order_by("city")
        if self.request.GET.get("county"):
            cities = cities.filter(county=self.request.GET.get("county"))

        context["cities"] = cities.values_list("city", flat=True).distinct("city")

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")

        return context
