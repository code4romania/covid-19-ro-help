import json

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector, TrigramSimilarity, SearchRank, SearchQuery
from django.core import paginator
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView

from hub import utils
from hub.models import (
    NGO,
    NGONeed,
    NGOHelper,
    KIND,
    RegisterNGORequest,
    ADMIN_GROUP_NAME,
    NGO_GROUP_NAME,
    DSU_GROUP_NAME,
    FFC_GROUP_NAME,
    )
from hub.forms import NGOHelperForm, NGORegisterRequestForm
from mobilpay.forms import PaymentOrderForm
from mobilpay.models import PaymentOrder


class InfoContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(f"static/data/sidebar_{translation.get_language()}.json") as info:
            context["info"] = json.loads(info.read())

        return context


class NGOKindFilterMixin:
    paginated_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_kind"] = self.request.GET.get("kind", KIND.default())

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


class NGONeedListView(InfoContextMixin, NGOKindFilterMixin, ListView):
    allow_filters = ["county", "city", "urgency"]
    paginate_by = 9

    template_name = "ngo/list.html"

    def get_needs(self):
        filters = {
            "kind": self.request.GET.get("kind", KIND.default()),
            "resolved_on": None,
        }

        return NGONeed.objects.filter(**filters).order_by("created")

    def search(self, query, queryset):
        # TODO: it should take into account selected language. Check only romanian for now.

        search_query = SearchQuery(query, config="romanian_unaccent")

        vector = (
            SearchVector("title", weight="A", config="romanian_unaccent")
            + SearchVector("ngo__name", weight="B", config="romanian_unaccent")
            + SearchVector("resource_tags__name", weight="C", config="romanian_unaccent")
        )

        return (
            queryset.annotate(
                rank=SearchRank(vector, search_query),
                similarity=TrigramSimilarity("title", query)
                + TrigramSimilarity("ngo__name", query)
                + TrigramSimilarity("resource_tags__name", query),
            )
            .filter(Q(rank__gte=0.3) | Q(similarity__gt=0.3))
            .order_by("-rank")
        )

    def get_queryset(self):
        needs = self.get_needs().filter(
            **{name: self.request.GET[name] for name in self.allow_filters if name in self.request.GET}
        )

        if self.request.GET.get("q"):
            needs = self.search(self.request.GET.get("q"), needs)

        return needs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        needs = self.get_needs()

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")
        context["current_urgency"] = self.request.GET.get("urgency")
        context["current_search"] = self.request.GET.get("q", "")

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


class NGODetailView(InfoContextMixin, NGOKindFilterMixin, DetailView):
    template_name = "ngo/detail.html"
    context_object_name = "ngo"
    model = NGO


class NGOHelperCreateView(SuccessMessageMixin, InfoContextMixin, NGOKindFilterMixin, CreateView):
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
        need = self.get_object()
        base_path = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"

        for user in ngo.users.all():
            utils.send_email(
                template="mail/new_helper.html",
                context={"helper": cleaned_data, "need": need, "ngo": ngo, "base_path": base_path},
                subject="[RO HELP] Mesaj nou pentru {} ".format(need.title)[:50],
                to=user.email,
            )
        return super().get_success_message(cleaned_data)


class NGORegisterRequestCreateView(SuccessMessageMixin, InfoContextMixin, CreateView):
    template_name = "ngo/register_request.html"
    model = RegisterNGORequest
    form_class = NGORegisterRequestForm
    success_message = _("TODO: add a success message")

    def get_success_url(self):
        return reverse("ngos-register-request")

    def get_success_message(self, cleaned_data):
        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
        for user in User.objects.filter(groups__name__in=authorized_groups):
            print(user)
            cleaned_data["base_path"] = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"
            utils.send_email(
                template="mail/new_ngo.html", context=cleaned_data, subject="[RO HELP] ONG nou", to=user.email
            )

        return super().get_success_message(cleaned_data)


class NGODonateCreateView(SuccessMessageMixin, InfoContextMixin, CreateView):
    template_name = "ngo/donate.html"
    model = PaymentOrder
    form_class = PaymentOrderForm
    success_message = _("TODO: add a success message")

    def get_success_url(self):
        return reverse("mobilpay:initialize-payment", kwargs={"order": self.object.order_id})

    def get_initial(self):
        ngo = self.get_object()
        return {"amount": self.request.GET.get("amount", "0"), "details": f"Donatie catre {ngo.name}"}

    def get_object(self, queryset=None):
        ngo = NGO.objects.filter(pk=self.kwargs["ngo"]).first()
        if not ngo:
            return None

        return ngo

    def form_valid(self, form):
        form.instance.ngo = self.get_object()
        return super().form_valid(form)
