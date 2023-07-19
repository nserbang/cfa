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
    OTPSerializer,
    UpdateProfileSerializer,
)
from api.models import cUser


class UserRegistrationViewApiView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            url = "http://msg.msgclub.net/rest/services/sendSMS/sendGroupSms"
            params = {
                "AUTH_KEY": "eb77c1ab059d9eab77f37e1e2b4b87",
                "message": "OTP CODE :{}".format(user.otp_code),
                "senderId": "mnwalk",
                "routeId": 8,
                "mobileNos": "9729013259",
                "smsContentType": "english",
            }
            x = requests.get(url, params=params)

            return Response({"user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]
        otp_code = serializer.validated_data["otp_code"]

        try:
            user = cUser.objects.get(id=user_id)
        except cUser.DoesNotExist:
            return Response(
                {"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        # if user.otp_code != otp_code:
        if user.otp_code != otp_code:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # OTP verification successful, you can activate the user or perform any other necessary actions
        user.is_active = True
        user.save()

        return Response(
            {"message": "User registration completed successfully"},
            status=status.HTTP_200_OK,
        )


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = cUser.objects.all()

    def get_object(self):
        return self.request.user
