import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    UserSerializer,
    LoginSerializer,
    OTPVerificationSerializer,
    UserProfileSerializer,
    ResendOTPSerializer,
    PasswordChangeSerializer,
)
from api.models import cUser
from api.otp import send_otp_verification_code


class UserRegistrationViewApiView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_otp_verification_code(user)
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
        serializer = UserProfileSerializer(user)
        data = serializer.data
        data["token"] = token.key
        return Response(data=data)


class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = cUser.objects.all()

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password change successful."}, status=200)
