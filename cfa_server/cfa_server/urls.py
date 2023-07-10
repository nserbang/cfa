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
# from api.endpoints import *
from django.contrib import admin
from rest_framework import routers

from api.viewset.case import *
from api.viewset.district import *
from api.viewset.police import *

router = routers.DefaultRouter()
router.register('district', DistrictViewSet, basename='district')
router.register('police-station', PoliceStationViewSet, basename='police-station')
router.register('police-officer', PoliceOfficerViewSet, basename='police-officer')
router.register('police-station-contact', PoliceStationContactViewSet, basename='police-contact')
router.register('case', CaseViewSet, basename='case')
router.register('case-history', CaseHistoryViewSet, basename='case-history')
router.register('media', MediaViewSet, basename='media')
router.register('lost-vehicle', LostVehicleViewSet, basename='lost-vehicle')
router.register('comment', CommentViewSet, basename='comments')

# router.register()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace= "rest_framework")),


    #User URL
    # path(r'register/', user_create, name="register"),
    # path(r'user-update/<str:pk>', user_update, name="user-update"),

    #District URL begins --
    # path('district-list/', district_list, name= "district-list"),
    # path('district-get/<int:pk>', district_get, name= "district-get"),
    #path('district-create/', district_create, name= "district-create"),
    #path('district-delete/<int:pk>', district_delete, name= "district-delete"),
    #path('district-update/<int:pk>', district_update, name= "district-update"),
    #District url ends --

    #PoliceStation URL begins --
    # path('police-station-list/', policeStation_list, name= "police-station-list"),
    # path('police-station-get/<int:pk>', policeStation_get, name= "police-station-get"),
    #path('police-station-create/', policeStation_create, name= "police-station-create"),
    #path('police-station-delete/<int:pk>', policeStation_delete, name= "police-station-delete"),
    #path('polices-station-update/', policeStation_update, name= "police-station-update"),
    #PoliceStation url ends --

        #policeStationContact URL begins --
    # path('police-station-contact-list/', policeStationContact_list, name= "police-station-contact-list"),
    # path('police-station-contact-get/<int:pk>', policeStationContact_get, name= "police-station-contact-get"),
    #path('police-station-contact-create/', policeStationContact_create, name= "police-station-contact-create"),
    #path('police-station-contact-delete/<int:pk>', policeStationContact_delete, name= "police-station-contact-delete"),
    #path('police-station-contact-update/', policeStationContact_update, name= "police-station-contact-update"),
    #policeStationContact url ends --

    #policeOfficer URL begins --
    # path('police-officer-list/', policeOfficer_list, name= "police-officer-list"),
    # path('police-officer-get/<int:pk>', policeOfficer_get, name= "police-officer-get"),
    #path('police-officer-create/', policeOfficer_create, name= "police-officer-create"),
    #path('police-officer-delete/<int:pk>', policeOfficer_delete, name= "police-officer-delete"),
    #path('police-officer-update/', policeOfficer_update, name= "police-officer-update"),
    #policeOfficer url ends --

    #case URL begins --
    # path('case-list/', case_list, name= "case-list"),
    # path('case-get/<int:pk>', case_get, name= "case-get"),
    # path('case-create/', case_create, name= "case-create"),
    # path('case-delete/<int:pk>', case_delete, name= "case-delete"),
    # path('case-update/<int:pk>', case_update, name= "case-update"),
        #case url ends --

    #caseHistory URL begins --
    # path('case-history-list/', caseHistory_list, name= "case-history-list"),
    # path('case-history-get/<int:pk>', caseHistory_get, name= "case-history-get"),
    # path('case-history-create/', caseHistory_create, name= "case-history-create"),
    # path('case-history-delete/<int:pk>', caseHistory_delete, name= "case-history-delete"),
    # path('case-history-update/<int:pk>', caseHistory_update, name= "case-history-update"),
     #caseHistory url ends --

    #media URL begins --
    # path('media-list/', media_list, name= "media-list"),
    # path('media-get/<int:pk>', media_get, name= "media-get"),
    # path('media-create/', media_create, name= "media-create"),
    # path('media-delete/<int:pk>', media_delete, name= "media-delete"),
    # path('media-update/', media_update, name= "media-update"),
    #media url ends --

    #media URL begins --
    # path('lost-vehicle-list/', lostVehicle_list, name= "lostVehicle-list"),
    # path('lost-vehicle-get/<int:pk>', lostVehicle_get, name= "lostVehicle-get"),
    # path('lost-vehicle-create/', lostVehicle_create, name= "lostVehicle-create"),
    # path('lost-vehicle-delete/<int:pk>', lostVehicle_delete, name= "lostVehicle-delete"),
    # path('lost-vehicle-update/<int:pk>', lostVehicle_update, name= "lostVehicle-update"),
    #media url ends --

    #          #media URL begins --
    # path('comment-list/', comment_list, name= "comment-list"),
    # path('comment-get/<int:pk>', comment_get, name= "comment-get"),
    # path('comment-create/', comment_create, name= "comment-create"),
    # path('comment-delete/<int:pk>', comment_delete, name= "comment-delete"),
    #path('comment-update/<int:pk>', comment_update, name= "comment-update"), # no update for comment. Only delete
     #media url ends --
]








