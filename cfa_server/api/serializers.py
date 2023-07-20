import cv2 as cv
from rest_framework import serializers
from django.contrib.gis.geos import fromstr
from django.db.models.functions import Lower
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth import authenticate
from random import randint, randrange
from api.models import Case, PoliceStation, cUser
from api.npr import detectVehicleNumber


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
    user = serializers.PrimaryKeyRelatedField(
        queryset=cUser.objects.all(), write_only=True
    )  # Add user_id field for write-only

    class Meta:
        model = Case
        fields = [
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
        # import pdb; pdb.set_trace()
        case.pid = police_station
        case.geo_location = geo_location
        officier = police_station.policeofficer_set.order_by("-rank").first()
        case.oid = officier
        case.user = validated_data["user"]
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
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "mobile",
            "username",
            "password",
            "role",
            "address",
            "profile_pic",
        ]

    def create(self, validated_data):
        user = User(
            username=validated_data.get("username"),
            mobile=validated_data["mobile"],
            role=validated_data.get("role", "user"),
            address=validated_data.get("address", None),
        )
        if password := validated_data.get("password"):
            user.set_password(password)
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = cUser
        fields = [
            "first_name",
            "last_name",
            "mobile",
            "email",
            "address",
            "profile_picture",
        ]


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


class OTPSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    otp_code = serializers.CharField(max_length=6)


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


class CommentCreateSerializer(serializers.ModelSerializer):

    content = serializers.CharField(required=True)

    user = serializers.PrimaryKeyRelatedField(
        queryset=cUser.objects.all(), write_only=True
    )
    class Meta:
        model = Comment
        fields = [
            'cid',
            'user',
            'content'
        ]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        comment = Comment(
            cid=validated_data['cid'],
            user=validated_data['user'],
            content=validated_data['content']
        )
        comment.save()
        return comment
