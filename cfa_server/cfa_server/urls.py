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
from django.conf import settings
from django.contrib.auth import views as auth_views
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from api.viewset.case import *  # noqa
from api.viewset.district import *
from api.viewset.police import *
from api.viewset.emergency import *
from api.viewset.information import *
from api.viewset.user import *
from api.viewset.lost_vehicle import CheckLostVehicle
from api.viewset.victim import *
from api.viewset.criminal import *
from api.views import (
    index,
    emergency,
    information,
    logout_view,
    UserRegistrationView,
    VerifyOtpView,
    HomePageView,
    CaseAddView,
    UserRegistrationCompleteView,
    ResendMobileVerificationOtpView,
    AddCommentView,
    AddLikeView,
    ChangeCaseStateUpdateView,
)
from api.viewset.privacy import PrivacyViewSet
from api.viewset.termscondition import TermsConditionViewSet
from api.viewset.contact import ContactViewSet

router = routers.DefaultRouter()
router.register("district", DistrictViewSet, basename="district")
router.register("police-station", PoliceStationViewSet, basename="police-station")
router.register("police-officer", PoliceOfficerViewSet, basename="police-officer")
router.register(
    "police-station-contact", PoliceStationContactViewSet, basename="police-contact"
)
router.register(r"case", CaseViewSet, basename="case")
# router.register(r'case/create', CaseCreateAPIView.as_view(), basename= 'case-create')
# router.register("case-history", CaseHistoryViewSet, basename="case-history")
router.register("media", MediaViewSet, basename="media")
router.register("lost-vehicle", LostVehicleViewSet, basename="lost-vehicle")
# router.register('comment', CommentViewSet, basename='comments')
router.register("emergency", EmergencyViewListSet, basename="emergency")
router.register("information", InformationViewSet, basename="information")
router.register("victim", VictimViewSet, basename="victim")
router.register("privacy", PrivacyViewSet, basename="privacy")
router.register("terms-condition", TermsConditionViewSet, basename="terms-condition")
router.register("contact", ContactViewSet, basename="contact")
router.register("criminal", CriminalViewSet, basename="criminal")
router.register(
    r"case/(?P<case_id>\d+)/history", CaseHistoryViewSet, basename="case-history"
)
router.register(
    r"case/(?P<case_id>\d+)/comment", CommentViewSet, basename="case-comment"
)
router.register(
    r"district/(?P<district_id>\d+)/emergency", EmergencyViewSet, basename="emergencies"
)
router.register(
    r"district/(?P<district_id>\d+)/police-station",
    DistrictPoliceStationViewSet,
    basename="district-police-station",
)
router.register("comment", CommentCUDViewSet, basename="comment")
router.register("devices", FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "api/v1/register/",
        UserRegistrationViewApiView.as_view(),
        name="user_registration",
    ),
    path(
        "api/v1/verify-otp/",
        VerifyOtpAPIView.as_view(),
        name="verify_otp",
    ),
    path(
        "api/v1/resend-otp/",
        ResendOtpAPIView.as_view(),
        name="resend_otp",
    ),
    path("api/v1/login/", UserLoginView.as_view(), name="user-login"),
    path(
        "api/v1/change-password/",
        ChangePasswordAPIView.as_view(),
        name="change_password",
    ),
    path(
        "api/v1/send-reset-password-otp/",
        PasswordResetOtpAPIView.as_view(),
        name="send_reset_password_otp",
    ),
    path(
        "api/v1/reset-password/",
        PasswordResetAPIView.as_view(),
        name="reset_password",
    ),
    path(
        "api/v1/profile/update/", UserProfileUpdateView.as_view(), name="profile_update"
    ),
    path("api/v1/check-vehicle/", CheckLostVehicle.as_view(), name="check_vehicle"),
    # path('', index, name='index'),
    path("", HomePageView.as_view(), name="home"),
    path("home/", HomePageView.as_view(), name="home"),
    path("emergency/", emergency, name="emergency"),
    path("information/", information, name="information"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="api/login.html"),
        name="login",
    ),
    path(
        "accounts/signup/",
        UserRegistrationView.as_view(),
        name="signup",
    ),
    path(
        "accounts/verify-mobile/",
        VerifyOtpView.as_view(),
        name="verify_mobile",
    ),
    path(
        "accounts/resend-verification-otp/",
        ResendMobileVerificationOtpView.as_view(),
        name="resend_verification_otp",
    ),
    path(
        "accounts/complete-signup/",
        UserRegistrationCompleteView.as_view(),
        name="complete_signup",
    ),
    path("case/add/", CaseAddView.as_view(), name="add_case"),
    path("comment/add/<int:case_id>/", AddCommentView.as_view(), name="add_comment"),
    path("like/add/<int:case_id>/", AddLikeView.as_view(), name="add_like"),
    path(
        "change-status/<int:case_id>/",
        ChangeCaseStateUpdateView.as_view(),
        name="change_status",
    ),
    path("logout/", logout_view, name="logout"),
    path("api/cases/create/", CaseCreateAPIView.as_view(), name="case-create"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    # User URL
    # path(r'register/', user_create, name="register"),
    # path(r'user-update/<str:pk>', user_update, name="user-update"),
    # District URL begins --
    # path('district-list/', district_list, name= "district-list"),
    # path('district-get/<int:pk>', district_get, name= "district-get"),
    # path('district-create/', district_create, name= "district-create"),
    # path('district-delete/<int:pk>', district_delete, name= "district-delete"),
    # path('district-update/<int:pk>', district_update, name= "district-update"),
    # District url ends --
    # PoliceStation URL begins --
    # path('police-station-list/', policeStation_list, name= "police-station-list"),
    # path('police-station-get/<int:pk>', policeStation_get, name= "police-station-get"),
    # path('police-station-create/', policeStation_create, name= "police-station-create"),
    # path('police-station-delete/<int:pk>', policeStation_delete, name= "police-station-delete"),
    # path('polices-station-update/', policeStation_update, name= "police-station-update"),
    # PoliceStation url ends --
    # policeStationContact URL begins --
    # path('police-station-contact-list/', policeStationContact_list, name= "police-station-contact-list"),
    # path('police-station-contact-get/<int:pk>', policeStationContact_get, name= "police-station-contact-get"),
    # path('police-station-contact-create/', policeStationContact_create, name= "police-station-contact-create"),
    # path('police-station-contact-delete/<int:pk>', policeStationContact_delete, name= "police-station-contact-delete"),
    # path('police-station-contact-update/', policeStationContact_update, name= "police-station-contact-update"),
    # policeStationContact url ends --
    # policeOfficer URL begins --
    # path('police-officer-list/', policeOfficer_list, name= "police-officer-list"),
    # path('police-officer-get/<int:pk>', policeOfficer_get, name= "police-officer-get"),
    # path('police-officer-create/', policeOfficer_create, name= "police-officer-create"),
    # path('police-officer-delete/<int:pk>', policeOfficer_delete, name= "police-officer-delete"),
    # path('police-officer-update/', policeOfficer_update, name= "police-officer-update"),
    # policeOfficer url ends --
    # case URL begins --
    # path('case-list/', case_list, name= "case-list"),
    # path('case-get/<int:pk>', case_get, name= "case-get"),
    # path('case-create/', case_create, name= "case-create"),
    # path('case-delete/<int:pk>', case_delete, name= "case-delete"),
    # path('case-update/<int:pk>', case_update, name= "case-update"),
    # case url ends --
    # caseHistory URL begins --
    # path('case-history-list/', caseHistory_list, name= "case-history-list"),
    # path('case-history-get/<int:pk>', caseHistory_get, name= "case-history-get"),
    # path('case-history-create/', caseHistory_create, name= "case-history-create"),
    # path('case-history-delete/<int:pk>', caseHistory_delete, name= "case-history-delete"),
    # path('case-history-update/<int:pk>', caseHistory_update, name= "case-history-update"),
    # caseHistory url ends --
    # media URL begins --
    # path('media-list/', media_list, name= "media-list"),
    # path('media-get/<int:pk>', media_get, name= "media-get"),
    # path('media-create/', media_create, name= "media-create"),
    # path('media-delete/<int:pk>', media_delete, name= "media-delete"),
    # path('media-update/', media_update, name= "media-update"),
    # media url ends --
    # media URL begins --
    # path('lost-vehicle-list/', lostVehicle_list, name= "lostVehicle-list"),
    # path('lost-vehicle-get/<int:pk>', lostVehicle_get, name= "lostVehicle-get"),
    # path('lost-vehicle-create/', lostVehicle_create, name= "lostVehicle-create"),
    # path('lost-vehicle-delete/<int:pk>', lostVehicle_delete, name= "lostVehicle-delete"),
    # path('lost-vehicle-update/<int:pk>', lostVehicle_update, name= "lostVehicle-update"),
    # media url ends --
    #          #media URL begins --
    # path('comment-list/', comment_list, name= "comment-list"),
    # path('comment-get/<int:pk>', comment_get, name= "comment-get"),
    # path('comment-create/', comment_create, name= "comment-create"),
    # path('comment-delete/<int:pk>', comment_delete, name= "comment-delete"),
    # path('comment-update/<int:pk>', comment_update, name= "comment-update"), # no update for comment. Only delete
    # media url ends --
    path("<str:case_type>/", HomePageView.as_view(), name="case"),
]


if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
