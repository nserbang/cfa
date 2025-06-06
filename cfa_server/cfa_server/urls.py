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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.viewset.case import *  # noqa
from api.viewset.district import *
from api.viewset.police import *
from api.viewset.emergency import *
from api.viewset.information import *
from api.viewset.dashboard import *
from api.viewset.user import *
from api.viewset.lost_vehicle import CheckLostVehicle
from api.viewset.victim import *
from api.viewset.criminal import *
from api.views import (
    CustomLoginView,
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
    ForgotPasswordView,
    ResetPasswordView,
    NearestPoliceStationsView,
    ExportCrime,
    PoliceStationListView,
    AssignDesignationListView,
    ChoosePoliceOfficerView,
    PoliceOfficerListView,
    AddOfficerView,
    RemovePoliceOfficerListView,
    RemoveOfficerView,
    ChangeDesignation,
    about_page,
    dashboard,
    get_case_history,
    get_case_comments,
    get_media,
    get_case_media,
    protected_media,
    UploadLostVehicleView,
    privacy_page,
    terms_page,
    #dboardView,
    #dashboard_view
)
from api.viewset.privacy import PrivacyAPIView
from api.viewset.termscondition import TermsConditionViewSet
from api.viewset.user import (
    UserRegistrationViewApiView,
    VerifyOtpAPIView,
    ResendOtpAPIView,
    ChangePasswordAPIView,
    PasswordResetOtpAPIView,
    PasswordResetAPIView,
)
from api.viewset.contact import ContactViewSet
from api.viewset.banner import BannerViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views import CustomPasswordChangeView
from api.views import custom_404_view, custom_400_view, custom_401_view, custom_403_view

from api.forms.user import cUserAuthenticationForm

admin.autodiscover()
admin.site.login_form = cUserAuthenticationForm

router = routers.SimpleRouter()
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
#router.register("dashboard", DashboardViewSet, basename="dashboard")
router.register("victim", VictimViewSet, basename="victim")
#router.register("privacy", PrivacyViewSet, basename="privacy")
router.register("terms-condition", TermsConditionViewSet, basename="terms-condition")
router.register("contact", ContactViewSet, basename="contact")
router.register("criminal", CriminalViewSet, basename="criminal")
router.register("emergency-type", EmergencyTypeViewSet, basename="emergency-types")
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
    r"emergency-type/(?P<emergency_type_id>\d+)/emergency",
    EmergencyViewSet,
    basename="emergencies-type",
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
    path("captcha/", include("captcha.urls")),
    path(
        "admin/password_change/",
        CustomPasswordChangeView.as_view(),
        name="custom_admin_password_change",
    ),
    path("admin/", admin.site.urls),
    path("admin/login/", CustomLoginView.as_view(), name="custom_admin_login"),
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
    # path("api/v1/login/", UserLoginView.as_view(), name="user-login"),
    # path("api/v1/logout/", LogoutAPIView.as_view(), name="user-logout"),
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
    #path("", HomePageView.as_view(), name="home"),
    path("login/",auth_views.LoginView.as_view(template_name="api/login.html"), name = "login"),
    path("", dashboard, name="dashboard"),
    path("home/", HomePageView.as_view(), name="home"),
    path("about_page/", about_page, name="about_page"),
    path("emergency/", emergency, name="emergency"),
    path("information/", information, name="information"),
    path('dashboard/', dashboard, name='dashboard'),
        path('uploadlostvehicle/', UploadLostVehicleView.as_view(), name='uploadlostvehicle'),
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
        "accounts/forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot_password_web",
    ),
    path(
        "accounts/reset-password/",
        ResetPasswordView.as_view(),
        name="reset_password_web",
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
    path("case/export/", ExportCrime.as_view(), name="case_export"),
    path(
        "police/stations/", PoliceStationListView.as_view(), name="police_station_list"
    ),
    path(
        "assign/designation/list/",
        AssignDesignationListView.as_view(),
        name="assign_designation_list",
    ),
    path(
        "change/designation/<int:user_id>/",
        ChangeDesignation.as_view(),
        name="change_designation",
    ),
    path(
        "police/officer-add/<int:station_id>/",
        AddOfficerView.as_view(),
        name="add_officer",
    ),
    path(
        "police/officer-remove/<int:station_id>/",
        RemoveOfficerView.as_view(),
        name="remove_officer",
    ),
    path(
        "choose/officer/<int:station_id>/",
        ChoosePoliceOfficerView.as_view(),
        name="choose_police_officer",
    ),
    path(
        "remove/officer/<int:station_id>/list/",
        RemovePoliceOfficerListView.as_view(),
        name="remove_police_officer_list",
    ),
    path(
        "police/officer-list/<int:station_id>/",
        PoliceOfficerListView.as_view(),
        name="police_officer_list",
    ),
    path("police/officer-add/", AddOfficerView.as_view(), name="police_officer_list"),
    path("police/officer-add/", AddOfficerView.as_view(), name="police_officer_list"),
    path("police/officer-add/", AddOfficerView.as_view(), name="police_officer_list"),
    path("police/officer-add/", AddOfficerView.as_view(), name="police_officer_list"),
    path("comment/add/<int:case_id>/", AddCommentView.as_view(), name="add_comment"),
    path("like/add/<int:case_id>/", AddLikeView.as_view(), name="add_like"),
    #path("get/case-history/<int:case_id>/", GetCaseHistory.as_view(), name="get_case_history"),
    path('get/case-history/<int:cid>/', get_case_history, name='get_case_history'),
    path('get/case-comments/<int:cid>/', get_case_comments, name='get_case_comments'),
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
    path(
        "nearest/police/stations/",
        NearestPoliceStationsView.as_view(),
        name="nearest_police_station",
    ),
    path("api/v1/cases/create/", CaseCreateAPIView.as_view(), name="case_create"),
    path("api/v1/cases/update/<pk>/", CaseUpdaateAPIView.as_view(), name="case_update"),
    path("api/v1/cases/update/reporter/<pk>/",
        CaseUpdaateByReporterAPIView.as_view(),
        name="case_update_by_reporter",
    ),
    path("api/v1/cases/accept/<pk>/", CaseAcceptAPIView.as_view(), name="case_accept"),
    path("ckeditor/", include("ckeditor_uploader.urls")),  
    # jwt
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path('get/media/', get_media, name='get_media'),
    path('get/case-media/<int:cid>/', get_case_media, name='get_case_media'),
    path('privacy-page/', privacy_page, name='privacy_page'),
     path('terms-page/', terms_page, name='terms_page'),
    path('protected_media/<path:path>/', protected_media, name='protected_media'),
    path("<str:case_type>/",HomePageView.as_view(), name= "case"),
    # path('', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Swagger
if settings.ENVIRONMENT != "PRODUCTION":
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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

admin.site.site_header = "Crime Reporting"
admin.site.site_title = "Crime Reporting"
admin.site.site_url = ""

handler404 = custom_404_view
handler400 = custom_400_view
handler401 = custom_401_view
handler403 = custom_403_view
