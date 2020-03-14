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