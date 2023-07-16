#from view_includes import *

from django.urls import NoReverseMatch
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, reverse, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View

from django.contrib.auth.forms import UserCreationForm
from .user_forms import UserRegistrationForm
from .otp import send_otp_verification_code

from api.models import cUser

#from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *
from api.forms.user import cUserCreationForm

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

    def get(self, request, *args, **kwargs):
        pass


class UserRegistrationView(View):

    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm
        return render(request, 'api/signup.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_otp_verification_code(user)
            return redirect(reverse('veryfy_otp') + f"?mobile={user.mobile}")
        return render(request, 'api/signup.html', {"form": form})


class VerifyOtpView(View):
    pass