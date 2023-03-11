from django.shortcuts import render
from http import HTTPStatus
from datetime import datetime
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from .serializers import *
import json
from functools import partial
from django.db.models import Q
from rest_framework.filters import SearchFilter

# Create your views here.