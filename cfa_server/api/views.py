import base64
import logging

from openpyxl import Workbook
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from csp.decorators import csp_exempt
from django.urls import reverse_lazy
from django.db.models.functions import Coalesce
from django.db.models import Count, Case as MCase, When, Q, OuterRef, Exists
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, reverse, redirect, get_object_or_404, Http404
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

from .user_forms import (
    UserRegistrationForm,
    VerifyOtpFrom,
    UserRegistrationCompleteForm,
    ResendMobileVerificationOtpForm,
    ForgotPasswordForm,
    ChangePasswordForm,
)

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
    UserOTPBaseKey,
)

# from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *
from api.forms.user import AddOfficerForm, RemoveOfficerForm, ChangeDesignationForm
from api.forms.case import CaseForm, CaseUpdateForm

logger = logging.getLogger(__name__)

def information(request):
    logger.info("Entering information function")
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
    logger.info("Exiting information function")
    return render(request, "information.html", vars)


from django.shortcuts import render
from .models import Emergency, EmergencyType
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

def emergency(request):
    logger.info("Entering emergency function")
    # Get user's latitude and longitude from the request
    user_lat = request.GET.get("lat")
    user_long = request.GET.get("long")
    selected_emergency_type = request.GET.get("emergency_type")

    logger.debug(
        f"Request parameters - lat: {user_lat}, long: {user_long}, type: {selected_emergency_type}"
    )

    try:
        emergencies = Emergency.objects.all()
        logger.info("Retrieved all emergencies")

        if user_lat and user_long:
            try:
                # Convert latitude and longitude to a Point object
                user_location = Point(float(user_long), float(user_lat), srid=4326)
                logger.info(f"Created Point object at ({user_lat}, {user_long})")

                # Annotate emergencies with distance and order by distance
                emergencies = emergencies.annotate(
                    distance=Distance("geo_location", user_location)
                ).order_by("distance")
                logger.info("Annotated emergencies with distances")
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing coordinates: {str(e)}")
                raise ValidationError("Invalid coordinates provided")

        # Filter by emergency type if selected
        if selected_emergency_type:
            emergencies = emergencies.filter(tid_id=selected_emergency_type)
            logger.info(f"Filtered emergencies by type: {selected_emergency_type}")

        # Get all emergency types for the dropdown
        emergency_types = EmergencyType.objects.all()
        logger.info(f"Retrieved {emergency_types.count()} emergency types")

        # Check if it's an AJAX request
        is_ajax = request.headers.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        logger.debug(f"Is AJAX request: {is_ajax}")

        if is_ajax:
            logger.info("Rendering emergency list template for AJAX request")
            return render(
                request,
                "emergency_list.html",
                {
                    "items": emergencies,
                },
            )
        else:
            logger.info("Rendering full emergency template")
            return render(
                request,
                "emergency.html",
                {
                    "items": emergencies,
                    "emergency_types": emergency_types,
                    "selected_emergency_type": selected_emergency_type,
                },
            )

    except Exception as e:
        logger.exception(f"Unexpected error in emergency function: {str(e)}")
        raise
    finally:
        logger.info("Exiting emergency function")


def logout_view(request):
    logger.info("Entering logout_view function")
    logout(request)
    logger.info("Exiting logout_view function")
    return redirect("/")  # Replace 'home' with the URL name of your home page


class HomePageView(View):
    def get_header(self):
        logger.info("Entering get_header")
        header_map = {
            "my-complaints": "My complaints",
            "stolen_vechicle": "Stollen Vehicle",
            "drug_case": "Drug Case Reported",
            "extortion_case": "Extortion Case Reported",
        }
        return header_map.get(self.kwargs.get("title"), "Case Listings")

    def get_case_type(self):
        logger.info("Entering get_case_type")
        case_type = {
            "stolen-vehicle": "vehicle",
            "drug-case": "drug",
            "extortion-case": "extortion",
        }
        return case_type.get(self.kwargs.get("case_type"))

    def get_template_name(self):
        logger.info("Entering get_template_name")
        template = self.get_case_type()
        if template:
            logger.info("Exiting get_template_name with template: {template}")
            return f"case/{template}.html"
        logger.info("Exiting get_template_name with default home.html")
        return "home.html"

    def get_queryset(self):
        logger.info("Entering get_queryset in HomePageView")
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
            .select_related("pid", "oid", "oid__user", "oid__pid", "oid__pid__did")
            #.prefetch_related(
            #    "casehistory_set", "comment_set", "comment_set__user", "medias"
            #)
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
                    cases = cases.annotate(
                        can_act=MCase(
                            When(
                                (Q(cstate="pending") & Q(oid__rank=5))
                                | (
                                    ~Q(cstate="pending")
                                    & Q(oid__rank=4)
                                    & Q(oid=officer)
                                ),
                                then=True,
                            ),
                            default=False,
                        )
                    )
                    rank = int(officer.rank)
                    if rank > 9:
                        pass
                    elif rank == 9:
                        cases.filter(pid__did_id=officer.pid.did_id)
                    elif rank == 6:
                        cases = cases.filter(
                            pid_id__in=officer.policestation_supervisor.values(
                                "station"
                            )
                        )
                    elif rank == 5:
                        cases = cases.filter(pid_id=officer.pid_id)
                    elif rank == 4:
                        cases = cases.filter(oid=officer).exclude(cstate="pending")
                    else:
                        cases = cases.filter(Q(user=user) | Q(type="vehicle"))
            elif user.is_user:
                cases = cases.filter(Q(user=user) | Q(type="vehicle"))
        else:
            cases = cases.filter(type="vehicle")

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
        logger.info(f"Entering get with request: {request}")
        cases = self.get_queryset()
        header = self.get_header()
        template_name = self.get_template_name()
        logger.info(f"Exiting get case :{cases}, headers: {header}, temmplate :{template_name}")
        return render(request, template_name, {"cases": cases, "header": header})


class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        logger.info(f"Entering get with request: {request}")
        form = UserRegistrationForm
        # with open("/cfa_server/api.log","a") as file:
        #   file.write(" Entering user sign up ")
        return render(request, "api/signup.html", {"form": form})

    def post(self, request, *args, **kwargs):
        logger.info(f"Entering post with request: {request}")
        form = UserRegistrationForm(request.POST)
        #import ipdb

        #ipdb.set_trace()
        if form.is_valid():
            user = form.save()
            UserOTPBaseKey.send_otp_verification_code(user)
            request.session["mobile"] = user.mobile
            return redirect(reverse("verify_mobile") + f"?mobile={user.mobile}")
        else:
            mobile = request.POST.get("mobile")
            try:
                user = cUser.objects.get(mobile=mobile)
            except cUser.DoesNotExist:
                pass
            else:
                return redirect(
                    reverse("verify_mobile") + f"?mobile={request.POST['mobile']}"
                )
                # if user.is_verified:
                #     messages.info(
                #         request,
                #         "A user with this mobile is already registered. "
                #         "If this is your mobile please login.",
                #     )
                # else:
                #     request.session["mobile"] = user.mobile
                #     messages.info(
                #         request,
                #         "A user with this mobile is already registered. "
                #         "But the mobile is not verified yet. If this is"
                #         " your mobile please verify it. You can resend verification"
                #         " otp from <a href='/accounts/resend-verification-otp/'>"
                #         "here</a>.",
                #     )
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
            data=request.POST,
            files=request.FILES,
            instance=request.user,
            request=request,
        )
        if form.is_valid():
            user = form.save()
            # UserOTPBaseKey.send_otp_verification_code(user)
            # login(request, user)
            return redirect(reverse("login"))
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

    @csp_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
        logger.info("Entering get with request: {request}")
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
        logger.info("Entering get_queryset")
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
            #.prefetch_related("medias") # Need to add the result of medias if any 
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
        logger.info("Entering get_queryset")
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
        logger.info("Entering get_model")
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
        logger.info("Entering get_template_names")
        crime_type = self.get_crime_type() or "missing_children"
        return [f"case/{crime_type}.html"]


class ForgotPasswordView(FormView):
    form_class = ForgotPasswordForm
    template_name = "users/forgot_password.html"
    success_url = reverse_lazy("reset_password_web")

    def form_valid(self, form):
        form.save()
        self.request.session["mobile"] = form.cleaned_data["mobile"]
        self.request.session["password_reset"] = True
        return super().form_valid(form)


class ResetPasswordView(FormView):
    form_class = ChangePasswordForm
    template_name = "users/reset_password.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.get("password_reset"):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

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
        logger.info("Entering get nearest police staiton view")
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
        logger.info("Entering get_pdg")
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
        logger.info("Entering get_queryset in police station list view")
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
        logger.info("Entering get_queryset police officer list view ")
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
        logger.info("Entering post in addOfficerView")
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
        logger.info("Entering post in RemoveOfficerView")
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
        logger.info("Entering get_queryset RemovePoliceOfficerListView")
        qs = super().get_queryset()
        qs = qs.filter(pid_id=self.kwargs["station_id"])
        if q := self.request.GET.get("q"):
            qs = qs.filter(mobile__icontains=q)
        return qs.select_related("user")

    def get_context_data(self, **kwargs):
        logger.info("Entering get_context_data RemovePoliceOfficerListView")
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


class CustomPasswordChangeView(PasswordChangeView):
    # Customize the view as needed

    form_class = CustomAdminPasswordChangeForm
    template_name = (
        "admin/custom_password_change.html"  # Replace with your custom template path
    )
    success_url = reverse_lazy(
        "admin:index"
    )  # Redirect to the admin index page after password change


def custom_404_view(request, exception):
    return render(request, "custom_error.html", status=404)


def custom_400_view(request, exception=None):
    return render(request, "custom_error.html", status=400)


def custom_401_view(request, exception=None):
    return render(request, "custom_error.html", status=401)


def custom_403_view(request, exception=None):
    return render(request, "custom_error.html", status=403)


from django.shortcuts import render
from .models import AboutPage


def about(request):
    logger.info("Entering about function")
    about_content = (
        AboutPage.objects.first()
    )  # Get the first (and only) AboutPage object
    logger.info("Exiting about function")
    return render(request, "about.html", {"about_content": about_content})


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Case
from django.db.models import Count

class dboardView(View):
    def get(self, request, *arg, **kwargs):
        logger.debug(f"DASHBOARDH GET ENTERING : {request}")
        return(request, "dashboard.html")

@login_required
def dashboard(request):
    logger.info(f"Entering dashboard function with request: {request}")
    if not request.user.is_authenticated:
        return render(request, "admin/login.html")
    # Ensure only users with the "Police" role can access this view
    if not request.user.is_police:
        logger.warning("Unauthorized access attempt to dashboard_view")
        #return render(request, '403.html', status=403)  # Render a 403 Forbidden page

    # Get filter parameter from the request
    ctype = request.GET.get('ctype', None)

    # Filter cases based on the selected `Ctype`
    cases = Case.objects.all().order_by('-created')

    if ctype:
        cases = cases.filter(type=ctype)

    case_summary = Case.objects.values('type').annotate(count=Count('cid')).order_by('type')

    drug_status_summary = Case.objects.filter(type='drug').values('cstate').annotate(
            count= Count('cid')).order_by('cstate')

    extortion_status_summary = Case.objects.filter(type='extortion').values('cstate').annotate(
            count= Count('cid')).order_by('cstate')

    vehicle_status_summary = Case.objects.filter(type='vehicle').values('cstate').annotate(
            count= Count('cid')).order_by('cstate')


    """
    # Group cases by `Ctype` for the pie chart
    case_summary = (
        cases.values('type')
        .annotate(count=Count('type'))
        .order_by('type')
    )
    """

    # Paginate the cases (10 cases per page)
    #paginator = Paginator(cases, 10)
    #page_number = request.GET.get('page')
    #cases = paginator.get_page(page_number)
    """
    context = {
        'cases': page_obj,  # Paginated cases
        'case_summary': case_summary,  # Data for the pie chart
        'ctype_filter': ctype_filter,  # Current filter
    }
    """

    colors ={
            'pending':'#FF9800',
            'accepted':'#4CAF50',
            'found':'#2196F3',
            'assign':'#9C27B0',
            'visited':'#FF5722',
            'inprogress':'#03A9F4',
            'transfer':'#795548',
            'resolved':'#8BC34A',
            'info':'#607D8B',
            'rejected':'#F44336'
        }


    context = {
        #'cases': cases,
        'case_summary': case_summary,
        'ctype_filter': ctype,
        'drug_status_summary':drug_status_summary,
        'extortion_status_summary':extortion_status_summary,
        'vehicle_status_summary':vehicle_status_summary,
        'colors': colors,
    }

    logger.info("Exiting dashboard function")
    return render(request, 'dashboard.html', context)
    #return render(request, 'dash.html', context)
