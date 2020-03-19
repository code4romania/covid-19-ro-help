import json

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User, Group
from django.core import paginator
from django.http import Http404
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from hub.models import NGO, NGONeed, NGOHelper, KIND, RegisterNGORequest
from hub.forms import NGOHelperForm, NGORegisterRequestForm


class NGOKindFilterMixin:
    paginated_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_kind"] = self.request.GET.get("kind", KIND.default())

        with open(f"static/data/sidebar_{translation.get_language()}.json") as info:
            context["info"] = json.loads(info.read())

        ngo = kwargs.get("ngo", context.get("ngo"))
        if not ngo:
            return context

        page = self.request.GET.get("page")
        needs = ngo.needs.resource()
        needs_paginator = paginator.Paginator(needs, self.paginated_by)

        # Catch invalid page numbers
        try:
            needs_page_obj = needs_paginator.page(page)
        except (paginator.PageNotAnInteger, paginator.EmptyPage):
            needs_page_obj = needs_paginator.page(1)

        context["resource_page_obj"] = needs_page_obj

        return context


class NGOListView(NGOKindFilterMixin, ListView):
    allow_filters = ["county", "city"]
    paginate_by = 9

    template_name = "ngo/list.html"

    def get_queryset(self):
        ngos = NGO.objects.all()

        filters = {name: self.request.GET[name] for name in self.allow_filters if name in self.request.GET}

        filters["needs__kind"] = self.request.GET.get("kind", KIND.default())
        filters["needs__resolved_on"] = None

        return ngos.order_by("name").filter(**filters).distinct("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")

        ngos = NGO.objects.filter(
            needs__kind=context["current_kind"], needs__resolved_on=None, needs__closed_on=None
        ).distinct("name")

        context["counties"] = ngos.order_by("county").values_list("county", flat=True).distinct("county")

        cities = ngos.order_by("city")
        if self.request.GET.get("county"):
            cities = cities.filter(county=self.request.GET.get("county"))

        context["cities"] = cities.values_list("city", flat=True).distinct("city")

        return context


class NGODetailView(NGOKindFilterMixin, DetailView):
    template_name = "ngo/detail.html"
    context_object_name = "ngo"
    model = NGO


class NGOHelperCreateView(SuccessMessageMixin, NGOKindFilterMixin, CreateView):
    template_name = "ngo/detail.html"
    model = NGOHelper
    form_class = NGOHelperForm
    # fields = ["name", "email", "message", "phone"]
    success_message = _("TODO: add a success message")

    def get_object(self, queryset=None):
        # return from local cache, if any
        if hasattr(self, "need"):
            return self.need

        ngo = NGO.objects.filter(pk=self.kwargs["ngo"]).first()
        if not ngo:
            return None

        need = ngo.needs.filter(pk=self.kwargs["need"]).first()
        if not need or need.resolved_on:
            return None

        self.need = need

        return need

    def get_context_data(self, **kwargs):
        need = self.get_object()
        if not need:
            raise Http404(_("Missing or invalid NGO need."))

        context = super().get_context_data(**{**kwargs, **{"ngo": need.ngo}})

        context["ngo"] = need.ngo
        context["current_need"] = need

        return context

    def form_valid(self, form):
        form.instance.ngo_need = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("ngo-detail", kwargs={"pk": self.kwargs["ngo"]})

    def get_success_message(self, cleaned_data):
        html = get_template("mail/new_helper.html")
        data = cleaned_data
        ngo = NGO.objects.get(pk=self.kwargs["ngo"])
        data["ngo"] = ngo
        html_content = html.render(data)

        subject, from_email, to = "[RO HELP] Mesaj nou", "noreply@rohelp.ro", ngo.email
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return super().get_success_message(cleaned_data)


class NGORegisterRequestCreateView(SuccessMessageMixin, CreateView):
    template_name = "ngo/register_request.html"
    model = RegisterNGORequest
    form_class = NGORegisterRequestForm
    success_message = _("TODO: add a success message")

    def get_success_url(self):
        return reverse("ngos-register-request")

    def get_success_message(self, cleaned_data):
        html = get_template("mail/new_ngo.html")
        html_content = html.render(cleaned_data)
        for admin in User.objects.filter(groups__name="Admin"):
            subject, from_email, to = "[RO HELP] ONG nou", "noreply@rohelp.ro", admin.email
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return super().get_success_message(cleaned_data)
