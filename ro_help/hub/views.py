from django.views.generic import ListView, DetailView

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

        filters['needs__kind'] = self.request.GET.get('kind', 'money')
        filters['needs__resolved_on'] = None

        return ngos.order_by('name').filter(**filters).distinct("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")
        context["current_kind"] = self.request.GET.get("kind", "money")

        ngos = NGO.objects.filter(needs__kind=context['current_kind'])

        context["counties"] = ngos.order_by("county").values_list("county", flat=True).distinct("county")

        cities = ngos.order_by("city")
        if self.request.GET.get("county"):
            cities = cities.filter(county=self.request.GET.get("county"))

        context["cities"] = cities.values_list("city", flat=True).distinct("city")

        return context


class NGODetailView(DetailView):
    template_name = 'ngo/detail.html'
    context_object_name = 'ngo'
    model = NGO

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_kind"] = self.request.GET.get("kind", "money")
        return context
