from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth import authenticate
from api.models import Case, PoliceStation, cUser
from api.npr import detectVehicleNumber
from api.otp import validate_otp, send_otp_verification_code


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class cUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = cUser
        fields = ["id", "email", "first_name", "last_name"]


class PoliceStationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceStationContact
        fields = "__all__"


class PoliceStationSerializer(serializers.Serializer):
    pid = serializers.ReadOnlyField()
    did = DistrictSerializer(read_only=True)
    name = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    long = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    distance = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True)
    contacts = PoliceStationContactSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["district"] = data.pop("did")
        return data

    # def get_contact(self, police_station):
    #     contacts = police_station.contacts.all()
    #     serializers = PoliceStationContactSerializer(contacts, many=True)
    #     return serializers


class PoliceOfficerSerializer(serializers.Serializer):
    oid = serializers.ReadOnlyField()
    user = cUserSerializer(read_only=True)
    pid = PoliceStationSerializer(read_only=True)
    rank = serializers.CharField(read_only=True)
    entryDate = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)
    mobile = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = cUserSerializer(instance.user).data
        data["pid"] = PoliceStationSerializer(instance.pid).data
        return data


class CaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseHistory
        fields = "__all__"


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    # history = CaseHistorySerializer(many=True)
    # media = MediaSerializer(many=True)

    case_type = serializers.SerializerMethodField()
    case_state = serializers.SerializerMethodField()
    # police_station = serializers.PrimaryKeyRelatedField(queryset=PoliceStation.objects.all())
    police_officer = PoliceOfficerSerializer(source="oid")
    comment_count = serializers.SerializerMethodField()
    user_detail = cUserSerializer(source="user")

    class Meta:
        model = Case
        fields = [
            "cid",
            "police_officer",
            "user_detail",
            "case_type",
            "title",
            "case_state",
            "created",
            "lat",
            "long",
            "description",
            "follow",
            "comment_count",
        ]

    def get_case_type(self, case):
        return dict(Case.cType)[case.type]

    def get_case_state(self, case):
        return dict(Case.cState)[case.cstate]

    def get_comment_count(self, case):
        return case.comment_set.count()


class CaseSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "cid",
            "user",
            "type",
            "title",
            "cstate",
            "lat",
            "long",
            "description",
            "follow",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        case = Case(
            type=validated_data["type"],
            title=validated_data["title"],
            cstate=validated_data["cstate"],
            lat=validated_data["lat"],
            long=validated_data["long"],
            description=validated_data["description"],
            follow=validated_data["follow"],
        )
        geo_location = fromstr(f"POINT({case.lat} {case.long})", srid=4326)
        user_distance = Distance("geo_location", geo_location)
        police_station = (
            PoliceStation.objects.annotate(radius=user_distance)
            .order_by("radius")
            .first()
        )
        case.pid = police_station
        case.geo_location = geo_location
        officier = police_station.policeofficer_set.order_by("-rank").first()
        case.oid = officier
        case.user = request.user
        case.save()
        return case


class LostVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostVehicle
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class EmergencySerializer(serializers.ModelSerializer):
    district = DistrictSerializer(source="did")

    class Meta:
        model = Emergency
        fields = [
            "emid",
            "district",
            "name",
            "number",
            "lat",
            "long",
        ]


class InformationSerializer(serializers.ModelSerializer):
    information_type = serializers.ChoiceField(choices=Information.Itype, required=True)

    class Meta:
        model = Information
        fields = ["inid", "information_type", "heading", "content"]

    # def get_information_type(self, information):
    #     return dict(Information.Itype)[information.information_type]


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=16)

    class Meta:
        model = User
        fields = ["id", "mobile"]

    def validate(self, data):
        if user := cUser.objects.filter(mobile=data["mobile"]).first():
            if user.is_verified:
                raise serializers.ValidationError(
                    {
                        "mobile": "This mobile is already registered",
                        "is_verified": True,
                    }
                )
            else:
                raise serializers.ValidationError(
                    {
                        "mobile": "This mobile is already registered.",
                        "is_verified": False,
                    }
                )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = cUser
        fields = [
            "first_name",
            "last_name",
            "mobile",
            "email",
            "address",
            "profile_picture",
            "aadhar_card_no",
            "password",
        ]

    def update(self, instance, data):
        password = data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, data)


class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        mobile = attrs.get("mobile")
        password = attrs.get("password")

        if mobile and password:
            user = authenticate(username=mobile, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError(
                    "Unable to log in with the provided credentials."
                )
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs["user"] = user
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data["mobile"]
        otp_code = data["otp_code"]

        user = cUser.objects.filter(mobile=mobile).first()
        if user:
            if not validate_otp(user, otp_code):
                raise serializers.ValidationError(
                    {"otp_code": "Invalid or expired otp code."}
                )
        else:
            raise serializers.ValidationError({"mobile": "Invalid mobile"})
        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        user.is_verified = True
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return {
            "message": "Otp verification successful.",
            "user_id": user.id,
            "mobile": user.mobile,
            "token": token.key,
        }


class ResendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)

    def validate(self, data):
        mobile = data["mobile"]
        user, _ = cUser.objects.get_or_create(mobile=mobile)
        if user.is_verified:
            raise serializers.ValidationError({"mobile": "Mobile already verified"})
        send_otp_verification_code(user)
        return data


class CheckLostVehicleSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    registration_no = serializers.CharField(required=False)

    def validate(self, data):
        image = data.get("image")
        registration_no = data.get("registration_no")
        if not (image or registration_no):
            raise serializers.ValidationError(
                "Provide either image and/or registration no."
            )
        return data

    def check_vehicle(self):
        image = self.validated_data.get("image", None)
        registration_no = self.validated_data.get("registration_no", None)
        registration_numbers = []
        registration_numbers = detectVehicleNumber(image, registration_no)
        return registration_numbers


class VictimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Victim
        fields = "__all__"


class CriminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criminal
        fields = "__all__"


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data.get("old_password")):
            raise serializers.ValidationError(
                {"old_password": "Your current password is incorrect."}
            )
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Password did not match."}
            )
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user
