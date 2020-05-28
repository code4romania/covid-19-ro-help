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
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView

from hub import utils
from hub.models import (
    ADMIN_GROUP_NAME,
    DSU_GROUP_NAME,
    FFC_GROUP_NAME,
    KIND,
    NGO,
    NGOHelper,
    NGONeed,
    NGO_GROUP_NAME,
    RegisterNGORequest,
    URGENCY,
)
from hub.forms import NGOHelperForm, NGORegisterRequestForm
from mobilpay.forms import PaymentOrderForm
from mobilpay.models import PaymentOrder


NEEDS_PER_PAGE = 3
DONATIONS_PER_PAGE = 10


class InfoContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(f"static/data/sidebar_{translation.get_language()}.json") as info:
            context["info"] = json.loads(info.read())

        return context


class NGOKindFilterMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_kind"] = self.request.GET.get("kind")

        if not self.request.GET.get("q"):
            context["current_kind"] = context["current_kind"] or KIND.default()

        ngo = kwargs.get("ngo", context.get("ngo"))
        if not ngo:
            return context

        needs = ngo.needs.filter(resolved_on=None)
        if "need" in kwargs:
            needs = needs.exclude(pk=kwargs["need"].pk)
            context["current_need"] = kwargs["need"]

        for kind in KIND.to_list():
            kind_needs = needs.filter(kind=kind)
            needs_paginator = paginator.Paginator(kind_needs, NEEDS_PER_PAGE)
            page = self.request.GET.get(f"{kind}_page")

            # Catch invalid page numbers
            try:
                needs_page_obj = needs_paginator.page(page)
            except (paginator.PageNotAnInteger, paginator.EmptyPage):
                needs_page_obj = needs_paginator.page(1)

            context[f"{kind}_page_obj"] = needs_page_obj

        return context


class NGODonationsReportsMixin:
    """
    Class used for separately paginating the donations and the reports.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ngo = kwargs.get("ngo", context.get("ngo"))

        if not ngo:
            return context
        donations_page = self.request.GET.get("donations_page")
        # Donations paginator.
        ngo_donations = ngo.get_funders()
        donations_paginator = paginator.Paginator(ngo_donations.order_by("-created"), DONATIONS_PER_PAGE)

        try:
            donations_page_obj = donations_paginator.page(donations_page)
        except (paginator.PageNotAnInteger, paginator.EmptyPage):
            donations_page_obj = donations_paginator.page(1)
        context["donations_page_obj"] = donations_page_obj

        report_item_page = self.request.GET.get("report_items_page")
        # Report items paginator.
        ngo_report_items = ngo.report_items.all()
        report_items_paginator = paginator.Paginator(ngo_report_items.order_by("-created"), DONATIONS_PER_PAGE)

        try:
            report_items_page_obj = report_items_paginator.page(report_item_page)
        except (paginator.PageNotAnInteger, paginator.EmptyPage):
            report_items_page_obj = report_items_paginator.page(1)
        context["report_items_page_obj"] = report_items_page_obj

        return context


class NGONeedListView(InfoContextMixin, NGOKindFilterMixin, ListView):

    allow_filters = ["county", "city", "urgency"]
    paginate_by = 9

    template_name = "ngo/list.html"

    def get_needs(self):
        if hasattr(self, "needs"):
            return self.needs

        filters = {
            "resolved_on": None,
        }

        kind = self.request.GET.get("kind")
        if not self.request.GET.get("q"):
            kind = kind or KIND.default()

        if kind:
            filters["kind"] = kind

        self.needs = (
            NGONeed.objects.filter(**filters)
            .order_by("ngo__name")
            .select_related("ngo")
            .prefetch_related("resource_tags")
        )

        return self.needs

    def search(self, queryset):
        # TODO: it should take into account selected language. Check only romanian for now.
        query = self.request.GET.get("q")
        if not query:
            return queryset

        if hasattr(self, "search_cache") and query in self.search_cache:
            return self.search_cache[query]

        search_query = SearchQuery(query, config="romanian_unaccent")

        vector = SearchVector("title", weight="A", config="romanian_unaccent") + SearchVector(
            "ngo__name", weight="B", config="romanian_unaccent"
        )

        result = (
            queryset.annotate(
                rank=SearchRank(vector, search_query),
                similarity=TrigramSimilarity("title", query) + TrigramSimilarity("ngo__name", query),
            )
            .filter(Q(rank__gte=0.3) | Q(similarity__gt=0.3))
            .order_by("title", "-rank")
            .distinct("title")
        )
        if not hasattr(self, "search_cache"):
            self.search_cache = {}

        self.search_cache[query] = result

        return result

    def get_queryset(self):
        needs = self.search(self.get_needs())
        filters = {name: self.request.GET[name] for name in self.allow_filters if name in self.request.GET}

        tags = [tag for tag in self.request.GET.getlist("tag", []) if tag]
        if tags:
            filters["resource_tags__name__in"] = tags

        return needs.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        needs = self.search(self.get_needs())

        context["current_county"] = self.request.GET.get("county")
        context["current_city"] = self.request.GET.get("city")
        context["current_urgency"] = self.request.GET.get("urgency")
        context["current_search"] = self.request.GET.get("q", "")
        context["current_tags"] = self.request.GET.getlist("tag", "")
        context["counties"] = needs.order_by("county").values_list("county", flat=True).distinct("county")
        context["tags"] = sorted(set([n for n in needs.values_list("resource_tags__name", flat=True) if n]))

        if self.request.GET.get("county"):
            needs = needs.filter(county=self.request.GET.get("county"))

        context["cities"] = set(needs.values_list("city", flat=True))
        context["urgencies"] = [
            urgency for urgency, _ in sorted(URGENCY.ORDER.items(), key=lambda item: item[1], reverse=True)
        ]

        return context


class NGODetailView(InfoContextMixin, NGOKindFilterMixin, NGODonationsReportsMixin, DetailView):
    template_name = "ngo/detail.html"
    context_object_name = "ngo"
    model = NGO


class NGOHelperCreateView(
    SuccessMessageMixin, InfoContextMixin, NGOKindFilterMixin, NGODonationsReportsMixin, CreateView
):

    template_name = "ngo/detail.html"
    model = NGOHelper
    form_class = NGOHelperForm
    success_message = _("Thank you for your help!")

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
        need = self.get_object()
        reverse_url = reverse("ngo-need", kwargs={"ngo": need.ngo.pk, "need": need.pk})
        return f"{reverse_url}?kind={need.kind}"

    def get_success_message(self, cleaned_data):
        ngo = self._get_ngo()
        need = self.get_object()
        base_path = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"

        for user in ngo.users.all():
            utils.send_email(
                template="mail/new_helper.html",
                context={"helper": cleaned_data, "need": need, "ngo": ngo, "base_path": base_path},
                subject="[RO HELP] Mesaj nou pentru {} ".format(need.title.replace("\n", ""))[:50],
                to=user.email,
            )

        return super().get_success_message(cleaned_data)


class NGORegisterRequestCreateView(SuccessMessageMixin, InfoContextMixin, CreateView):
    template_name = "ngo/register_request.html"
    model = RegisterNGORequest
    form_class = NGORegisterRequestForm
    success_message = _(
        "Thank you for signing up! The form you filled in has reached us. Someone from the RoHelp team will reach out to you as soon as your organization is validated. If you have any further questions, e-mail us at rohelp@code4.ro"
    )

    def get_success_url(self):
        return reverse("ngos-register-request")

    def get_success_message(self, cleaned_data):
        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]

        for user in User.objects.filter(groups__name__in=authorized_groups):
            cleaned_data["base_path"] = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}"
            utils.send_email(
                template="mail/new_ngo.html", context=cleaned_data, subject="[RO HELP] ONG nou", to=user.email
            )

        return super().get_success_message(cleaned_data)


class NGODonateCreateView(SuccessMessageMixin, InfoContextMixin, CreateView):
    template_name = "ngo/donate.html"
    model = PaymentOrder
    form_class = PaymentOrderForm
    success_message = _("Thank you for your donation!")

    def get_success_url(self):
        return reverse("mobilpay:initialize-payment", kwargs={"order": self.object.order_id})

    def get_initial(self):
        return {"amount": self.request.GET.get("amount", "0")}

    def get_object(self, queryset=None):
        ngo = NGO.objects.filter(pk=self.kwargs["ngo"]).first()

        if not ngo:
            return None

        return ngo

    def form_valid(self, form):
        form.instance.ngo = self.get_object()
        return super().form_valid(form)
