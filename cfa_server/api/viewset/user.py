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
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        UserOTPBaseKey.send_otp_verification_code(user)
        return Response(serializer.data)


class VerifyOtpAPIView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            data,
            status=status.HTTP_200_OK,
        )


class ResendOtpAPIView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Verification otp resent."},
            status=status.HTTP_200_OK,
        )


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user, context={"request": request})
        data = serializer.data
        data["token"] = token.key
        return Response(data=data)


class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = cUser.objects.all()

    def get_object(self):
        print(self.request.user.pk, "JJFKLDSFJKLS")
        return self.request.user


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password change successful."}, status=200)


class PasswordResetOtpAPIView(APIView):
    permission_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_reset_password_otp"

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Otp for password reset sent."})


class PasswordResetAPIView(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful."})


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        logout(request)
        return Response(status=status.HTTP_200_OK)
