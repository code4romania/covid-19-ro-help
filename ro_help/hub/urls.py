from django.urls import path
from django.views.generic import TemplateView

from hub.views import NGOListView, NGODetailView


urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    path("ngos", NGOListView.as_view(), name="ngos"),
    path("ngos/<int:pk>", NGODetailView.as_view(), name="ngo-detail"),
]

