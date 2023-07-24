from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import MethodNotAllowed
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




class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"

class CaseHistorySerializer(serializers.ModelSerializer):
    user_details = cUserSerializer(source="user")
    media_details = MediaSerializer(source="media")
    class Meta:
        model = CaseHistory
        fields = [
            "chid",
            "cid",
            "cstate",
            "created",
            "description",
            "user_details",
            "media_details"
        ]

class CaseSerializer(serializers.ModelSerializer):
    # history = CaseHistorySerializer(many=True)
    # media = MediaSerializer(many=True)

    case_type = serializers.SerializerMethodField()
    case_state = serializers.SerializerMethodField()
    # police_station = serializers.PrimaryKeyRelatedField(queryset=PoliceStation.objects.all())
    police_officer = PoliceOfficerSerializer(source="oid")
    comment_count = serializers.IntegerField()
    user_detail = cUserSerializer(source="user")
    like_count = serializers.IntegerField()
    liked = serializers.BooleanField(required=False, default=False)

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
            "like_count",
            "liked",
            "distance",
        ]

    def get_case_type(self, case):
        return dict(Case.cType)[case.type]

    def get_case_state(self, case):
        return dict(Case.cState)[case.cstate]

    # def get_comment_count(self, case):
    #     return case.comment_set.count()

    # def get_like_count(self, case):
    #     return case.likes.count()

    # def get_liked(self, case):

    #     user = self.context['request'].user

    #     if user.is_authenticated:
    #     # Check if the user has liked the case
    #         return case.likes.filter(user=user).exists()
    #     return False


class CaseSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            "cid",
            "type",
            "lat",
            "long",
            "description",
            "follow",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        case = Case(
            type=validated_data["type"],
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
    user_detail = cUserSerializer(source="user")

    class Meta:
        model = Comment
        fields = ["cmtid", "content", "cid", "user_detail", "created"]


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
    profile_picture = serializers.SerializerMethodField()
    class Meta:
        model = cUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile",
            "email",
            "address",
            "profile_picture",
            "aadhar_card_no",
            "password",
            "role",
        ]
        read_only_fields = ["role"]

    def update(self, instance, data):
        password = data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, data)

    def get_profile_picture(self, user):
        request = self.context.get("request")
        if user.profile_picture:
            # Assuming MEDIA_URL is set in your Django settings
            # Make sure to import settings at the beginning of the file: from django.conf import settings
            return request.build_absolute_uri(user.profile_picture.url)
        else:
            return None

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


class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Privacy
        fields = "__all__"


class TermsConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsCondition
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
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


class CommentCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)

    user = serializers.PrimaryKeyRelatedField(
        queryset=cUser.objects.all(), write_only=True
    )

    class Meta:
        model = Comment
        fields = ["cid", "user", "content"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        comment = Comment(
            cid=validated_data["cid"],
            user=validated_data["user"],
            content=validated_data["content"],
        )
        comment.save()
        return comment


class PasswordResetOtpSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)

    def save(self):
        mobile = self.validated_data["mobile"]
        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            pass
        else:
            send_otp_verification_code(user, verification=False)


class PasswordResetSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    mobile = serializers.CharField(max_length=16)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        mobile = data["mobile"]
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Password did not match."}
            )

        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            raise serializers.ValidationError({"mobile": "Mobile not registered."})
        else:
            if validate_otp(user=user, otp=data["otp"]):
                data["user"] = user

            else:
                raise serializers.ValidationError(
                    {"otp": "Otp is wrong or has expired."}
                )
        return data

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user


class LikeSerializer(serializers.Serializer):
    case_id = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=cUser.objects.all())
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Like.objects.create(**validated_data)

    def list(self, queryset):
        return queryset

    def retrieve(self, instance):
        return instance

    def delete(self, instance):
        instance.delete()


class LikeCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["case", "user"]


class LikeListSerializer(serializers.ModelSerializer):
    user = cUserSerializer()

    class Meta:
        model = Like
        fields = ["case", "user", "created"]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
