#from view_includes import *

from django.urls import NoReverseMatch
from django.utils import timezone
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages


#from rest_framework.request import Request
from api.view.district_views import *
from api.view.police_views import *
from api.view.case_view import *
from api.view.cuser_views import *

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
        "home": True
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

    return render(request,"emergency.html",vars)

def emergency(request):
    limit = int(request.GET.get("limit",10))
    page = int(request.GET.get("page", 0))
    hospitals = Emergency.objects.all()
    items = []
    for hospital in hospitals:

        number_of_comments = hospital.comment_set.count()

        data = {
            "number":hospital.cid,
            "type":dict(hospital.cType)[hospital.type],
            "status":dict(hospital.cState)[hospital.cstate],

            "reported_date":str(hospital.created)
        }
        items.append(data)

    vars = {
        "items":items,
    }

    return render(request,"information.html",vars)


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
