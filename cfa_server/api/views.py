import base64

from openpyxl import Workbook
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.urls import reverse_lazy
from django.db.models.functions import Coalesce
from django.db.models import Count, Case as MCase, When, Q, OuterRef, Exists
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth.views import LoginView

from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, FormView, ListView, UpdateView
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from .user_forms import (
    UserRegistrationForm,
    VerifyOtpFrom,
    UserRegistrationCompleteForm,
    ResendMobileVerificationOtpForm,
    ForgotPasswordForm,
    ChangePasswordForm,
)


from .otp import send_otp_verification_code
from .mixins import AdminRequiredMixin

from api.models import (
    Case,
    cUser,
    Like,
    Comment,
    CaseHistory,
    Victim,
    Criminal,
    PoliceStation,
    PoliceOfficer,
)

# from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *
from api.forms.user import AddOfficerForm, RemoveOfficerForm, ChangeDesignationForm
from api.forms.case import CaseForm, CaseUpdateForm


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
            .prefetch_related(
                "casehistory_set", "comment_set", "comment_set__user", "medias"
            )
            .order_by("-created")
        )
        lat = self.request.GET.get("lat")
        long = self.request.GET.get("long")
        if lat and long:
            geo_location = fromstr(f"POINT({long} {lat})", srid=4326)
            user_distance = Distance("geo_location", geo_location)
            cases = cases.annotate(radius=user_distance).order_by(
                "radius", Coalesce("created", "updated").desc()
            )
        case_type = self.get_case_type()
        if case_type:
            cases = cases.filter(type=case_type)
        # elif not case_type and user.is_authenticated:
        #     cases = cases.filter(user=user)
        if user.is_authenticated:
            liked = Like.objects.filter(case_id=OuterRef("cid"), user=user)
            cases = cases.annotate(
                has_liked=Exists(liked),
            )  # .filter(user=user)
            if self.kwargs.get("case_type") == "my-complaints":
                cases = cases.filter(user=self.request.user)
            if user.is_police:
                officer = user.policeofficer_set.first()
                if officer:
                    rank = int(officer.rank)
                    if rank < 5:
                        cases = cases.filter(oid=officer)
                    elif rank == 5:
                        cases = cases.filter(pid=officer.pid)
                    elif rank == 9:
                        cases = cases.filter(pid__did__did=officer.pid.did.did)

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


class UserRegistrationCompleteView(LoginRequiredMixin, View):
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
            login(request, user, "axes.backends.AxesBackend")
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


class AddCommentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect("/")

    def post(self, request, *args, **kwargs):
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


class ChangeCaseStateUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "case/case_update.html"
    form_class = CaseUpdateForm
    queryset = Case.objects.all()
    success_url = reverse_lazy("home")

    def get_queryset(self):
        queryset = self.queryset.filter(
            (Q(cstate="pending") & Q(pid__policeofficer__user=self.request.user))
            | Q(oid__user=self.request.user)
        ).distinct()
        return queryset

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["request"] = self.request
        return kw


class GetCaseHistory(View):
    def get(self, request, *args, **kwargs):
        case_id = kwargs["case_id"]
        case_histories = (
            CaseHistory.objects.filter(case_id=case_id)
            .prefetch_related("medias")
            .order_by("created")
        )
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


class ForgotPasswordView(FormView):
    form_class = ForgotPasswordForm
    template_name = "users/forgot_password.html"
    success_url = reverse_lazy("reset_password_web")

    def form_valid(self, form):
        form.save()
        self.request.session["mobile"] = form.cleaned_data["mobile"]
        return super().form_valid(form)


class ResetPasswordView(FormView):
    form_class = ChangePasswordForm
    template_name = "users/reset_password.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.info(self.request, "Password change successful.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["request"] = self.request
        return kw


class NearestPoliceStationsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        lat = request.GET.get("lat")
        long = request.GET.get("long")
        if lat and long:
            location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
            user_distance = Distance("geo_location", location)
            qs = PoliceStation.objects.annotate(radius=user_distance).order_by("radius")
        else:
            qs = PoliceStation.objects.all()
        qs = qs.values("pid", "did", "name", "address")
        return JsonResponse(list(qs), safe=False)


class ExportCrime(View):
    def get(self, request, *args, **kwargs):
        cases = Case.objects.select_related("pid", "oid", "oid__user").prefetch_related(
            "medias", "casehistory_set"
        )
        return self.get_pdf(cases)

    def get_pdf(self, cases):
        font_config = FontConfiguration()
        template_name = "export/pdf.html"
        user = self.request.user
        officer = user.policeofficer_set.first()
        if user.is_superuser:
            header = "Case Report for police stations in Arunachal Pradesh"
        elif officer and officer.rank:
            rank = int(officer.rank)
            if rank < 5:
                header = f"Case Report of {user.get_full_name()}"
                cases = cases.filter(oid=officer)
            elif rank == 5:
                header = f"Case Report of {officer.pid.name}"
                cases = cases.filter(pid=officer.pid)
            elif rank == 9:
                header = f"Case records with in {officer.pid.did.name}"
                cases = cases.filter(pid__did__did=officer.pid.did.did)
            elif rank > 9:
                header = header
        else:
            header = "Case Reports"

        context = {
            "header": header,
            "report_date": timezone.now().date(),
            "cases": cases,
        }
        html_string = render_to_string(template_name, context=context)
        pdf = HTML(string=html_string).write_pdf(font_config=font_config)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=report.pdf"
        return response


class PoliceStationListView(AdminRequiredMixin, ListView):
    template_name = "stations/list.html"
    model = PoliceStation
    queryset = PoliceStation.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        if q := self.request.GET.get("q"):
            qs = qs.filter(Q(name__icontains=q) | Q(address__icontains=q))
        return qs


class ChoosePoliceOfficerView(AdminRequiredMixin, ListView):
    template_name = "stations/choose_police_officers.html"
    model = cUser
    queryset = cUser.objects.filter(is_superuser=False)

    def get_queryset(self):
        qs = super().get_queryset()
        if q := self.request.GET.get("q"):
            qs = qs.filter(mobile__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["station"] = get_object_or_404(
            PoliceStation, pk=self.kwargs["station_id"]
        )
        context["add_officer_form"] = AddOfficerForm
        return context


class PoliceOfficerListView(AdminRequiredMixin, ListView):
    template_name = "stations/police_officers.html"
    model = PoliceOfficer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pid_id=self.kwargs["station_id"])
        if q := self.request.GET.get("q"):
            qs = qs.filter(user__mobile__icontains=q)
        return qs.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["station"] = get_object_or_404(
            PoliceStation, pk=self.kwargs["station_id"]
        )
        context["remove_officer_form"] = RemoveOfficerForm
        return context


class AddOfficerView(View):
    def post(self, request, *args, **kwargs):
        user_id = int(request.POST.get("user"))
        user = cUser.objects.get(pk=user_id)
        user.role = "police"
        user.save()
        pid = get_object_or_404(PoliceStation, pk=kwargs["station_id"])
        rank = request.POST.get("rank")
        PoliceOfficer.objects.update_or_create(
            user=user,
            defaults={
                "pid": pid,
                "rank": rank,
                "mobile": user.mobile,
            },
        )
        messages.success(request, "Succesfully added user to police list.")
        return redirect(reverse("police_officer_list", args=[pid.pk]))


class RemoveOfficerView(View):
    def post(self, request, *args, **kwargs):
        user_id = int(request.POST.get("user"))
        user = cUser.objects.get(pk=user_id)
        user.role = "user"
        user.save()
        user.policeofficer_set.all().delete()
        messages.success(request, "Succesfully removed user from officer list.")
        return redirect(reverse("police_officer_list", args=[kwargs["station_id"]]))


class RemovePoliceOfficerListView(AdminRequiredMixin, ListView):
    template_name = "stations/choose_police_officers_to_remove.html"
    model = PoliceOfficer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(pid_id=self.kwargs["station_id"])
        if q := self.request.GET.get("q"):
            qs = qs.filter(mobile__icontains=q)
        return qs.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["station"] = get_object_or_404(
            PoliceStation, pk=self.kwargs["station_id"]
        )
        context["remove_officer_form"] = RemoveOfficerForm
        return context


class AssignDesignationListView(AdminRequiredMixin, ListView):
    template_name = "stations/police_designation_list.html"
    model = cUser
    queryset = cUser.objects.all()


class ChangeDesignation(AdminRequiredMixin, FormView):
    form_class = ChangeDesignationForm
    template_name = "stations/change_designation.html"

    def form_valid(self, form):
        form.save()
        return redirect(reverse("assign_designation_list"))

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = get_object_or_404(cUser, pk=self.kwargs["user_id"])
        return kw


class CustomLoginView(LoginView):
    template_name = "admin/login.html"  # Use your custom login template


class CustomAdminPasswordChangeForm(PasswordChangeForm):
    template_name = "admin/custom_password_change.html"

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        self.cleaned_data["old_password"] = old_password
        return super().clean_old_password()

    def clean_new_password2(self):
        new_password1 = self.cleaned_data["new_password1"]
        new_password2 = self.cleaned_data["new_password2"]

        self.cleaned_data["new_password1"] = new_password1
        self.cleaned_data["new_password2"] = new_password2

        return super().clean_new_password2()


class CustomPasswordChangeView(PasswordChangeView):
    # Customize the view as needed

    form_class = CustomAdminPasswordChangeForm
    template_name = (
        "admin/custom_password_change.html"  # Replace with your custom template path
    )
    success_url = reverse_lazy(
        "admin:index"
    )  # Redirect to the admin index page after password change

    def post(self, request, *args, **kwargs):
        private_key_pem_b64 = request.session["private_key"]
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        form = self.get_form()
        data = form.data.copy()

        old_password_encrypted_data_b64 = form["old_password"].data
        old_password_encrypted_data = base64.b64decode(old_password_encrypted_data_b64)

        old_password_decrypted = private_key.decrypt(
            old_password_encrypted_data,
            padding.PKCS1v15(),
        )
        old_password = old_password_decrypted.decode("utf-8")
        data["old_password"] = old_password

        new_password1_encrypted_data_b64 = form["new_password1"].data
        new_password1_encrypted_data = base64.b64decode(
            new_password1_encrypted_data_b64
        )

        new_password1_decrypted = private_key.decrypt(
            new_password1_encrypted_data,
            padding.PKCS1v15(),
        )

        new_password1 = new_password1_decrypted.decode("utf-8")
        data["new_password1"] = new_password1

        new_password2_encrypted_data_b64 = form["new_password2"].data
        new_password2_encrypted_data = base64.b64decode(
            new_password2_encrypted_data_b64
        )

        new_password2_decrypted = private_key.decrypt(
            new_password2_encrypted_data,
            padding.PKCS1v15(),
        )

        new_password2 = new_password2_decrypted.decode("utf-8")
        data["new_password2"] = new_password2

        user = request.user
        modified_form = self.form_class(user, data=data)
        if modified_form.is_valid():
            return self.form_valid(modified_form)
        else:
            return self.form_invalid(modified_form)

    def form_valid(self, form):
        return super().form_valid(form)  # Proceed with the password


def custom_404_view(request, exception):
    return render(request, "custom_error.html", status=404)


def custom_400_view(request, exception=None):
    return render(request, "custom_error.html", status=400)


def custom_401_view(request, exception=None):
    return render(request, "custom_error.html", status=401)


def custom_403_view(request, exception=None):
    return render(request, "custom_error.html", status=403)
