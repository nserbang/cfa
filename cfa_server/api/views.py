# from view_includes import *

from django.urls import reverse_lazy
from django.db.models import Count, Value, Case as MCase, When, Q, OuterRef, Exists
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, FormView, ListView

from .user_forms import (
    UserRegistrationForm,
    VerifyOtpFrom,
    UserRegistrationCompleteForm,
    ResendMobileVerificationOtpForm,
)
from .otp import send_otp_verification_code

from api.models import Case, cUser, Like, Comment, CaseHistory, Victim, Criminal

# from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *
from api.forms.user import cUserCreationForm
from api.forms.case import CaseForm

case = {
    "number": 1,
    "type": "Extortion",
    "status": "Accepted",
    "likes": 10,
    "comments": 15,
    "reported_date": "2022-10-15",
}

case2 = {
    "number": 2,
    "type": "Drug",
    "status": "Ongoing",
    "likes": 12,
    "comments": 15,
    "reported_date": "2022-10-15",
}

cases = [case, case2]


def index(request):
    limit = int(request.GET.get("limit", 10))
    page = int(request.GET.get("page", 0))
    cases = Case.objects.all()
    items = []
    for case in cases:
        number_of_comments = case.comment_set.count()

        case = {
            "number": case.cid,
            "type": dict(Case.cType)[case.type],
            "status": dict(Case.cState)[case.cstate],
            "likes": 10,
            "comments": number_of_comments,
            "reported_date": str(case.created),
        }
        items.append(case)

    vars = {"items": items, "home": True, "user": request.user if request.user else {}}

    return render(request, "index.html", vars)


def information(request):
    limit = int(request.GET.get("limit", 10))
    page = int(request.GET.get("page", 0))
    cases = Case.objects.all()
    items = []
    for case in cases:
        number_of_comments = case.comment_set.count()

        case = {
            "number": case.cid,
            "type": dict(Case.cType)[case.type],
            "status": dict(Case.cState)[case.cstate],
            "likes": 10,
            "comments": number_of_comments,
            "reported_date": str(case.created),
        }
        items.append(case)

    vars = {"items": items, "home": True}

    return render(request, "information.html", vars)


def emergency(request):
    limit = int(request.GET.get("limit", 10))
    page = int(request.GET.get("page", 0))
    hospitals = Emergency.objects.all()
    items = [
        {
            "name": "Police Station - 1",
            "contact_number": 2442112,
            "type": "Police Station",
            "away": 120,
        },
        {
            "name": "Police Station - 2",
            "contact_number": 2442113,
            "type": "Police Station",
            "away": 60,
        },
        {
            "name": "Hospital - 1",
            "contact_number": 2442912,
            "type": "Hospital",
            "away": 27,
        },
        {
            "name": "Hospital - 2",
            "contact_number": 2443112,
            "type": "Hospital",
            "away": 24,
        },
    ]

    vars = {
        "items": items,
    }

    return render(request, "emergency.html", vars)


def logout_view(request):
    logout(request)
    return redirect("/")  # Replace 'home' with the URL name of your home page


class HomePageView(View):
    def get_header(self):
        header_map = {
            "my-complaints": "My complaints",
            "stolen_vechicle": "Stollen Vehicle",
            "drug_case": "Drug Case Reported",
            "extortion_case": "Extortion Case Reported",
        }
        return header_map.get(self.kwargs.get("title", "my-complaints"))

    def get_case_type(self):
        case_type = {
            "stolen-vehicle": "vehicle",
            "drug-case": "drug",
            "extortion-case": "extortion",
        }
        return case_type.get(self.kwargs.get("case_type"))

    def get_template_name(self):
        template = self.get_case_type()
        if template:
            return f"case/{template}.html"
        return "home.html"

    def get_queryset(self):
        user = self.request.user
        cases = (
            Case.objects.annotate(
                comment_count=Count("comment", distinct=True),
                like_count=Count("likes", distinct=True),
                is_location_visible=MCase(
                    When(
                        cstate="pending",
                        pid__policeofficer__user_id=user.id,
                        then=True,
                    ),
                    default=False,
                ),
            )
            .select_related("pid", "oid")
            .prefetch_related("pid__oid")
        )
        case_type = self.get_case_type()
        print(case_type, "sdjflskdfjlksdfjslkdfjlksdfjkdlsfjksdlfjlks")
        if case_type:
            cases = cases.filter(type=case_type)
        elif not case_type and user.is_authenticated:
            cases = cases.filter(user=user)
        if user.is_authenticated:
            liked = Like.objects.filter(case_id=OuterRef("cid"), user=user)
            cases = cases.annotate(
                has_liked=Exists(liked),
            )  # .filter(user=user)
        if q := self.request.GET.get("q"):
            search_filter = (
                Q(lostvehicle__regNumber=q)
                | Q(lostvehicle__chasisNumber=q)
                | Q(lostvehicle__engineNumber=q)
            )
            try:
                int(q)
                search_filter |= Q(cid=q)
            except ValueError:
                pass
            cases = cases.filter(search_filter)
        return cases

    def get(self, request, *args, **kwargs):
        cases = self.get_queryset()
        header = self.get_header()
        template_name = self.get_template_name()
        return render(request, template_name, {"cases": cases, "header": header})


class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm
        return render(request, "api/signup.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_otp_verification_code(user)
            request.session["mobile"] = user.mobile
            return redirect(reverse("verify_mobile") + f"?mobile={user.mobile}")
        else:
            mobile = request.POST.get("mobile")
            try:
                user = cUser.objects.get(mobile=mobile)
            except cUser.DoesNotExist:
                pass
            else:
                if user.is_verified:
                    messages.info(
                        request,
                        "A user with this mobile is already registered. "
                        "If this is your mobile please login.",
                    )
                else:
                    request.session["mobile"] = user.mobile
                    messages.info(
                        request,
                        "A user with this mobile is already registered. "
                        "But the mobile is not verified yet. If this is"
                        " your mobile please verify it. You can resend verification"
                        " otp from <a href='/accounts/resend-verification-otp/'>"
                        "here</a>.",
                    )
        return render(request, "api/signup.html", {"form": form})


class ResendMobileVerificationOtpView(FormView):
    template_name = "api/resend_mobile_verificatio_otp.html"
    form_class = ResendMobileVerificationOtpForm
    success_url = reverse_lazy("verify_mobile")

    def form_valid(self, form):
        user = form.save()
        if user:
            self.request.session["mobile"] = user.mobile
        return HttpResponseRedirect(self.get_success_url())


class UserRegistrationCompleteView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegistrationCompleteForm
        return render(request, "api/signup_complete.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationCompleteForm(
            data=request.POST, files=request.FILES, instance=request.user
        )
        if form.is_valid():
            user = form.save()
            send_otp_verification_code(user)
            login(request, user)
            return redirect("/")
        return render(request, "api/signup_complete.html", {"form": form})


class VerifyOtpView(View):
    def get(self, request, *args, **kwargs):
        form = VerifyOtpFrom(mobile=request.session.get("mobile"))
        return render(request, "api/verify_otp.html", {"form": form})

    def post(self, request, *args, **kwargs):
        mobile = request.session.get("mobile")
        form = VerifyOtpFrom(request.POST, mobile=mobile)
        if form.is_valid():
            user = form.save()
            messages.info(
                request,
                "Mobile verification successful."
                " Complete your registration and add your password now.",
            )
            try:
                del request.session["mobile"]
            except KeyError:
                pass
            login(request, user)
            return redirect(reverse("complete_signup"))
        return render(request, "api/verify_otp.html", {"form": form})


class CaseAddView(LoginRequiredMixin, CreateView):
    form_class = CaseForm
    model = Case
    template_name = "case/add_case.html"
    success_url = "/"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        form.save()
        return redirect(reverse("home"))


class AddCommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Login to add comment.")
            return redirect("/")
        data = request.POST
        case_id = kwargs["case_id"]
        comment = data["comment"]
        Comment.objects.create(cid_id=case_id, content=comment, user=request.user)
        return redirect("/")


class AddLikeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        case_id = kwargs["case_id"]
        Like.objects.get_or_create(case_id=case_id, user=request.user)
        messages.success(request, "Your like is added.")
        return redirect("/")


class ChangeCaseStateUpdateView(View):
    def get(self, request, *args, **kwargs):
        case_id = kwargs["case_id"]
        status = request.GET.get("status")
        case = get_object_or_404(Case, pk=case_id)
        case.cstate = status
        case.save()
        messages.success(request, f"Status changed sucesfully to {case.cstate}.")
        return redirect("/")


class GetCaseHistory(View):
    def get(self, request, *args, **kwargs):
        case_id = kwargs["case_id"]
        case_histories = CaseHistory.objects.filter(cid=case_id).order_by("created")
        from itertools import pairwise

        history_pairs = list(pairwise(case_histories))
        context = {"history_pairs": history_pairs}
        html = render_to_string(
            "case/case_history_json.html", request=request, context=context
        )
        return JsonResponse({"html": html})


class CrimeListView(ListView):
    def get_queryset(self):
        model = self.get_model()
        qs = model.objects.all()
        crime_type = self.get_crime_type()
        if crime_type:
            qs = qs.filter(type=crime_type)
        return qs

    def get_crime_type(self):
        crime_type = {
            "missing-children": "missing_children",
            "children-found": "children_found",
            "missing-person": "missing_person",
            "dead-body": "dead_body",
            "other": "other",
            "offender": "offender",
            "wanted": "wanted",
            "proclaimed": "proclaimed",
        }
        return crime_type.get(self.kwargs["crime_type"])

    def get_model(self):
        crime_type = self.get_crime_type()
        victims = [
            "missing_children",
            "children_found",
            "missing_person",
            "dead_body",
            "other",
        ]
        if crime_type is None or crime_type in victims:
            return Victim
        else:
            return Criminal

    def get_template_names(self):
        crime_type = self.get_crime_type() or "missing_children"
        return [f"case/{crime_type}.html"]
