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
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
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
    GetCaseHistory,
    CrimeListView,
)
from api.viewset.privacy import PrivacyViewSet
from api.viewset.termscondition import TermsConditionViewSet
from api.viewset.contact import ContactViewSet
from api.viewset.banner import BannerViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

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
router.register(r"case/(?P<case_id>\d+)/like", LikeViewSet, basename="case-like")
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
router.register("banner", BannerViewSet, basename="banner")
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
        "get/case-history/<int:case_id>/",
        GetCaseHistory.as_view(),
        name="get_case_hsitory",
    ),
    path(
        "change-status/<pk>/",
        ChangeCaseStateUpdateView.as_view(),
        name="change_status",
    ),
    path(
        "page/<str:crime_type>/",
        CrimeListView.as_view(),
        name="crime_list",
    ),
    path("logout/", logout_view, name="logout"),
    path("api/v1/cases/create/", CaseCreateAPIView.as_view(), name="case_create"),
    path("api/v1/cases/update/<pk>/", CaseUpdaateAPIView.as_view(), name="case_update"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("<str:case_type>/", HomePageView.as_view(), name="case"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Swagger
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
