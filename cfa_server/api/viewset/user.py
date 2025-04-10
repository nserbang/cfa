import requests
from django.contrib.auth import logout
from django.db.models import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
import logging

logger = logging.getLogger(__name__)

from api.serializers import (
    UserSerializer,
    LoginSerializer,
    OTPVerificationSerializer,
    UserProfileSerializer,
    ResendOTPSerializer,
    PasswordChangeSerializer,
    PasswordResetOtpSerializer,
    PasswordResetSerializer,
)

from api.models import cUser, UserOTPBaseKey


class UserRegistrationViewApiView(APIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_reset_password_otp"

    def post(self, request):
        logger.info("Entering UserRegistrationViewApiView.post")
        logger.debug(f"Registration request data: {request.data}")
        
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"Created new user with mobile: {user.mobile}")
        
        UserOTPBaseKey.send_otp_verification_code(user)
        logger.info(f"Sent OTP verification code to user: {user.mobile}")
        
        logger.info("Exiting UserRegistrationViewApiView.post")
        return Response(serializer.data)


class VerifyOtpAPIView(APIView):
    def post(self, request):
        logger.info("Entering VerifyOtpAPIView.post")
        logger.debug(f"OTP verification request data: {request.data}")
        
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        logger.info(f"OTP verification successful for mobile: {request.data.get('mobile')}")
        
        logger.info("Exiting VerifyOtpAPIView.post")
        return Response(data, status=status.HTTP_200_OK)


class ResendOtpAPIView(APIView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_reset_password_otp"

    def post(self, request):
        logger.info("Entering ResendOtpAPIView.post")
        logger.debug(f"OTP resend request data: {request.data}")
        
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info(f"Resent OTP to mobile: {request.data.get('mobile')}")
        
        logger.info("Exiting ResendOtpAPIView.post")
        return Response(
            {"message": "Verification otp resent."},
            status=status.HTTP_200_OK,
        )


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        logger.info("Entering UserLoginView.post")
        logger.debug(f"Login request for user: {request.data.get('mobile')}")
        
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        token, created = Token.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new token for user: {user.mobile}")
        else:
            logger.info(f"Retrieved existing token for user: {user.mobile}")
            
        serializer = UserProfileSerializer(user, context={"request": request})
        data = serializer.data
        data["token"] = token.key
        
        logger.info("Exiting UserLoginView.post")
        return Response(data=data)


class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = cUser.objects.all()

    def get_object(self):
        logger.info("Entering UserProfileUpdateView.get_object")
        logger.info(f"Getting profile for user ID: {self.request.user.pk}")
        logger.info("Exiting UserProfileUpdateView.get_object")
        return self.request.user


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Entering ChangePasswordAPIView.post")
        logger.debug(f"Password change request for user: {request.user.mobile}")
        
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Password changed successfully for user: {request.user.mobile}")
        
        logger.info("Exiting ChangePasswordAPIView.post")
        return Response({"message": "Password change successful."}, status=200)


class PasswordResetOtpAPIView(APIView):
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_reset_password_otp"

    def post(self, request, *args, **kwargs):
        logger.info("Entering PasswordResetOtpAPIView.post")
        logger.debug(f"Password reset OTP request data: {request.data}")
        
        serializer = PasswordResetOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Password reset OTP sent to mobile: {request.data.get('mobile')}")
        
        logger.info("Exiting PasswordResetOtpAPIView.post")
        return Response({"message": "Otp for password reset sent."})


class PasswordResetAPIView(APIView):
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_reset_password_otp"

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful."})


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Entering LogoutAPIView.post")
        logger.info(f"Logout request for user: {request.user.mobile}")
        
        try:
            request.user.auth_token.delete()
            logger.info(f"Deleted auth token for user: {request.user.mobile}")
        except (AttributeError, ObjectDoesNotExist):
            logger.warning(f"No auth token found for user: {request.user.mobile}")
            
        logout(request)
        logger.info(f"User logged out successfully: {request.user.mobile}")
        
        logger.info("Exiting LogoutAPIView.post")
        return Response(status=status.HTTP_200_OK)
