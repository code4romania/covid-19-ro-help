import json

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.core import paginator
from django.http import Http404
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from hub.models import NGO, NGONeed, NGOHelper, KIND, RegisterNGORequest, ADMIN_GROUP_NAME
from hub.forms import NGOHelperForm, NGORegisterRequestForm
from mobilpay.models import PaymentOrder


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

        needs = ngo.needs.filter(resolved_on=None)
        if "need" in kwargs:
            needs = needs.exclude(pk=kwargs["need"].pk)
            context["current_need"] = kwargs["need"]

        for kind in KIND.to_list():
            kind_needs = needs.filter(kind=kind)
            needs_paginator = paginator.Paginator(kind_needs, self.paginated_by)

            # Catch invalid page numbers
            try:
                needs_page_obj = needs_paginator.page(page)
            except (paginator.PageNotAnInteger, paginator.EmptyPage):
                needs_page_obj = needs_paginator.page(1)

            context[f"{kind}_page_obj"] = needs_page_obj

        return context


class NGONeedListView(NGOKindFilterMixin, ListView):
    allow_filters = ["county", "city", "urgency"]
    paginate_by = 9

    template_name = "ngo/list.html"

    def get_needs(self):
        filters = {
            "kind": self.request.GET.get("kind", KIND.default()),
            "resolved_on": None,
        }

        return NGONeed.objects.filter(**filters).order_by("created")

    def get_queryset(self):
        return self.get_needs().filter(
            **{name: self.request.GET[name] for name in self.allow_filters if name in self.request.GET}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        needs = self.get_needs()

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")
        context["current_urgency"] = self.request.GET.get("urgency")

        context["counties"] = needs.order_by("county").values_list("county", flat=True).distinct("county")

        cities = needs.order_by("city")
        if self.request.GET.get("county"):
            cities = cities.filter(county=self.request.GET.get("county"))

        context["cities"] = cities.values_list("city", flat=True).distinct("city")

        urgencies = cities
        if self.request.GET.get("city"):
            urgencies = urgencies.filter(city=self.request.GET.get("city"))

        context["urgencies"] = urgencies.order_by("urgency").values_list("urgency", flat=True).distinct("urgency")

        return context


class NGODetailView(NGOKindFilterMixin, DetailView):
    template_name = "ngo/detail.html"
    context_object_name = "ngo"
    model = NGO


class NGOHelperCreateView(SuccessMessageMixin, NGOKindFilterMixin, CreateView):
    template_name = "ngo/detail.html"
    model = NGOHelper
    form_class = NGOHelperForm
    success_message = _("TODO: add a success message")

    def get_object(self, queryset=None):
        # return from local cache, if any
        if hasattr(self, "need"):
            return self.need

        ngo = self._get_ngo()
        if not ngo:
            return None

        need = ngo.needs.filter(pk=self.kwargs["need"]).first()
        if not need or need.resolved_on:
            return None

        self.need = need

        return need

    def _get_ngo(self):
        # return from local cache, if any
        if hasattr(self, "ngo"):
            return self.ngo

        ngo = NGO.objects.filter(pk=self.kwargs["ngo"]).first()
        if not ngo:
            return None

        self.ngo = ngo
        return ngo

    def get_context_data(self, **kwargs):
        need = self.get_object()
        if not need:
            raise Http404(_("Missing or invalid NGO need."))

        context = super().get_context_data(**{**kwargs, **{"ngo": need.ngo, "need": need}})
        context["ngo"] = need.ngo

        return context

    def form_valid(self, form):
        form.instance.ngo_need = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("ngo-detail", kwargs={"pk": self.kwargs["ngo"]})

    def get_success_message(self, cleaned_data):
        ngo = self._get_ngo()
        cleaned_data["ngo"] = ngo

        html = get_template("mail/new_helper.html")
        html_content = html.render(cleaned_data)

        for user in ngo.users.all():
            subject, from_email, to = "[RO HELP] Mesaj nou", settings.NO_REPLY_EMAIL, user.email

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

        for admin in User.objects.filter(groups__name=ADMIN_GROUP_NAME):
            subject, from_email, to = "[RO HELP] ONG nou", settings.NO_REPLY_EMAIL, admin.email

            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        return super().get_success_message(cleaned_data)


class NGODonateCreateView(SuccessMessageMixin, CreateView):
    template_name = "ngo/donate.html"
    model = PaymentOrder
    fields = ["first_name", "last_name", "phone", "email", "address", "details", "amount"]
    success_message = _("TODO: add a success message")

    def get_success_url(self):
        return reverse("ngos")

    def get_initial(self):
        return {
            "amount": self.request.GET.get("amount", "0")
        }

    def get_object(self, queryset=None):
        ngo = NGO.objects.filter(pk=self.kwargs["ngo"]).first()
        if not ngo:
            return None

        return ngo

    def form_valid(self, form):
        form.instance.ngo = self.get_object()
        return super().form_valid(form)
