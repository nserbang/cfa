"""cfa_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.endpoints import *
from django.contrib import admin
from rest_framework import routers





router = routers.DefaultRouter()
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace= "rest_framework")),
    #path('admin/', admin.site.urls),

    #User URL
    path(r'register/', user_create, name="register"),

    #District URL begins --
    path('district-list/', district_list, name= "district-list"),
    path('district-get/<int:did>', district_get, name= "district-get"),
    path('district-create/', district_create, name= "district-create"),
    path('district-delete/<int:did>', district_delete, name= "district-delete"),
    path('district-update/<int:did>', district_update, name= "district-update"),
    #District url ends --

       #PoliceStation URL begins --
    path('police-station-list/', policeStation_list, name= "police-station-list"),
    path('police-station-get/<int:did>', policeStation_get, name= "police-station-get"),
    path('police-station-create/', policeStation_create, name= "police-station-create"),
    path('police-station-delete/<int:did>', policeStation_delete, name= "police-station-delete"),
    path('polices-station-update/', policeStation_update, name= "police-station-update"),
    #PoliceStation url ends --

        #policeStationContact URL begins --
    path('police-station-contact-list/', policeStationContact_list, name= "police-station-contact-list"),
    path('police-station-contact-get/<int:did>', policeStationContact_get, name= "police-station-contact-get"),
    path('police-station-contact-create/', policeStationContact_create, name= "police-station-contact-create"),
    path('police-station-contact-delete/<int:did>', policeStationContact_delete, name= "police-station-contact-delete"),
    path('police-station-contact-update/', policeStationContact_update, name= "police-station-contact-update"),
    #policeStationContact url ends --

        #policeOfficer URL begins --
    path('police-officer-list/', policeOfficer_list, name= "police-officer-list"),
    path('police-officer-get/<int:did>', policeOfficer_get, name= "police-officer-get"),
    path('police-officer-create/', policeOfficer_create, name= "police-officer-create"),
    path('police-officer-delete/<int:did>', policeOfficer_delete, name= "police-officer-delete"),
    path('police-officer-update/', policeOfficer_update, name= "police-officer-update"),
        #policeOfficer url ends --

        #case URL begins --
    path('case-list/', case_list, name= "case-list"),
    path('case-get/<int:did>', case_get, name= "case-get"),
    path('case-create/', case_create, name= "case-create"),
    path('case-delete/<int:did>', case_delete, name= "case-delete"),
    path('case-update/', case_update, name= "case-update"),
        #case url ends --

     #caseHistory URL begins --
    path('case-history-list/', caseHistory_list, name= "case-history-list"),
    path('case-history-get/<int:did>', caseHistory_get, name= "case-history-get"),
    path('case-history-create/', caseHistory_create, name= "case-history-create"),
    path('case-history-delete/<int:did>', caseHistory_delete, name= "case-history-delete"),
    path('case-history-update/', caseHistory_update, name= "case-history-update"),
     #caseHistory url ends --

        #media URL begins --
    path('media-list/', media_list, name= "media-list"),
    path('media-get/<int:did>', media_get, name= "media-get"),
    path('media-create/', media_create, name= "media-create"),
    path('media-delete/<int:did>', media_delete, name= "media-delete"),
    path('media-update/', media_update, name= "media-update"),
     #media url ends --

        #media URL begins --
    path('lostVehicle-list/', lostVehicle_list, name= "lostVehicle-list"),
    path('lostVehicle-get/<int:did>', lostVehicle_get, name= "lostVehicle-get"),
    path('lostVehicle-create/', lostVehicle_create, name= "lostVehicle-create"),
    path('lostVehicle-delete/<int:did>', lostVehicle_delete, name= "lostVehicle-delete"),
    path('lostVehicle-update/', lostVehicle_update, name= "lostVehicle-update"),
     #media url ends --
]








