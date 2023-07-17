#from view_includes import *

from django.urls import reverse_lazy
from django.db.models import Count, Value
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView

from .user_forms import UserRegistrationForm, VerifyOtpFrom
from .otp import send_otp_verification_code

from api.models import Case

#from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *
from api.forms.user import cUserCreationForm
from api.forms.case import CaseForm

case = {
    "number":1,
    "type":"Extortion",
    "status":"Accepted",
    "likes":10,
    "comments":15,
    "reported_date":"2022-10-15"
}

case2 = {
    "number":2,
    "type":"Drug",
    "status":"Ongoing",
    "likes":12,
    "comments":15,
    "reported_date":"2022-10-15"
}

cases = [case, case2]

def index(request):

    limit = int(request.GET.get("limit",10))
    page = int(request.GET.get("page", 0))
    cases = Case.objects.all()
    items = []
    for case in cases:

        number_of_comments = case.comment_set.count()

        case = {
            "number":case.cid,
            "type":dict(Case.cType)[case.type],
            "status":dict(Case.cState)[case.cstate],
            "likes": 10,
            "comments": number_of_comments,
            "reported_date":str(case.created)
        }
        items.append(case)

    vars = {
        "items":items,
        "home": True,
        "user": request.user if request.user else {}
    }

    return render(request,"index.html",vars)

def information(request):
    limit = int(request.GET.get("limit",10))
    page = int(request.GET.get("page", 0))
    cases = Case.objects.all()
    items = []
    for case in cases:

        number_of_comments = case.comment_set.count()

        case = {
            "number":case.cid,
            "type":dict(Case.cType)[case.type],
            "status":dict(Case.cState)[case.cstate],
            "likes": 10,
            "comments": number_of_comments,
            "reported_date":str(case.created)
        }
        items.append(case)

    vars = {
        "items":items,
        "home": True
    }

    return render(request,"information.html",vars)

def emergency(request):
    limit = int(request.GET.get("limit",10))
    page = int(request.GET.get("page", 0))
    hospitals = Emergency.objects.all()
    items = [
        {
            "name":"Police Station - 1",
            "contact_number": 2442112,
            "type":"Police Station",
            "away": 120
        },
        {
            "name":"Police Station - 2",
            "contact_number": 2442113,
            "type":"Police Station",
            "away": 60
        },
        {
            "name":"Hospital - 1",
            "contact_number": 2442912,
            "type":"Hospital",
            "away": 27
        },
        {
            "name":"Hospital - 2",
            "contact_number": 2443112,
            "type":"Hospital",
            "away": 24
        },
    ]

    vars = {
        "items":items,
    }

    return render(request,"emergency.html",vars)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with the URL name of your home page
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = cUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Replace 'home' with the URL name of your home page
    else:
        form = cUserCreationForm()

    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Replace 'home' with the URL name of your home page



class HomePageView(View):

    def get_header(self):
        header_map = {
            "complaints": "My complaints",
            "stolen_vechicle": "Stollen Vehicle",
            "seized_vehicle": "Unclaimed/Seized Vehicle",
            "drug_case": "Drug Case Reported",
            "extortion_case": "Extortion Case Reported",
            "missing_child": "Missing Children",
            "unidentified_child": "Un-identified Children Found",
            "missing_person": "Missing Persons",
            "unindentified_daad": "Unidentified Dead Bodies",
            "unidentified_person": "Unidentified Person",
        }
        return header_map.get(self.request.GET.get('title', "complaints"))

    def get_case_type(self):
        case_type = {
            "stolen-vehicle": "vehicle",
            "drug-case": "drug",
            "extortion-case": "extortion",
        }
        return case_type.get(self.kwargs.get('case_type'))

    def get_template_name(self):
        template = self.get_case_type()
        if template:
            return f'case/{template}.html'
        return 'home.html'

    def get_queryset(self):
        cases = Case.objects.annotate(
            comments=Count('comment'), likes=Value(0),
        ).select_related('pid')
        case_type = self.get_case_type()
        if case_type:
            cases = cases.filter(type=case_type)
        if self.request.user.is_authenticated:
            cases = cases.filter(user=self.request.user)
        return cases

    def get(self, request, *args, **kwargs):
        cases = self.get_queryset()
        header = self.get_header()
        template_name = self.get_template_name()
        return render(request, template_name, {'cases': cases, 'header': header})


class UserRegistrationView(View):

    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm
        return render(request, 'api/signup.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_otp_verification_code(user)
            return redirect(reverse('verify_otp') + f"?mobile={user.mobile}")
        return render(request, 'api/signup.html', {"form": form})


class VerifyOtpView(View):

    def get(self, request, *args, **kwargs):
        form = VerifyOtpFrom(mobile=request.GET.get('mobile', ""))
        return render(request, 'api/verify_otp.html', {"form": form})

    def post(self, request, *args, **kwargs):
        mobile = request.GET.get('mobile', "")
        form = VerifyOtpFrom(request.POST, mobile=mobile)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))
        return render(request, 'api/verify_otp.html', {"form": form})


class CaseAddView(LoginRequiredMixin, CreateView):
    form_class = CaseForm
    model = Case
    template_name = 'case/add_case.html'
    success_url = '/'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw

    def form_valid(self, form):
        form.save()
        return redirect(reverse("home"))
