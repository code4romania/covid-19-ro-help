from django.urls import path, include
from django.views.generic import TemplateView

from mobilpay import views


app_name = "mobilpay"

urlpatterns = [
    path("initialize/<str:order>", views.initialize_payment, name="initialize-payment"),
    path("confirm/<str:order>", views.confirm, name="confirm"),
    path("response/<str:order>", views.response, name="response"),
]
