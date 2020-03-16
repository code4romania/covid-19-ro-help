from django.urls import path, include
from django.views.generic import TemplateView

from hub.views import NGOListView, NGODetailView, NGOHelperCreateView


urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("ngos", NGOListView.as_view(), name="ngos"),
    path("ngos/<int:pk>", NGODetailView.as_view(), name="ngo-detail"),
    path("ngos/<int:ngo>/<int:need>/", NGOHelperCreateView.as_view(), name="ngo-helper-create"),
    path("i18n/", include("django.conf.urls.i18n")),
]
