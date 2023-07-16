from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth import authenticate
from random import randint, randrange

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class cUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = cUser
        fields = ['id','email','first_name','last_name']


class PoliceStationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceStationContact
        fields = '__all__'


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
        data['district'] = data.pop('did')
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
        data['user'] = cUserSerializer(instance.user).data
        data['pid'] = PoliceStationSerializer(instance.pid).data
        return data




class CaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseHistory
        fields = '__all__'

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class CaseSerializer(serializers.ModelSerializer):
    #history = CaseHistorySerializer(many=True)
    #media = MediaSerializer(many=True)

    case_type = serializers.SerializerMethodField()
    case_state = serializers.SerializerMethodField()
    # police_station = serializers.PrimaryKeyRelatedField(queryset=PoliceStation.objects.all())
    police_officer = PoliceOfficerSerializer(source='oid')
    comment_count = serializers.SerializerMethodField()
    user_detail = cUserSerializer(source='user')


    class Meta:
        model = Case
        fields = ['cid','police_officer', 'user_detail', 'case_type', 'title', 'case_state', 'created', 'lat', 'long', 'description', 'follow','comment_count']

    def get_case_type(self, case):
        return dict(Case.cType)[case.type]

    def get_case_state(self, case):
        return dict(Case.cState)[case.cstate]

    def get_comment_count(self, case):
        return case.comment_set.count()

class CaseSerializerCreate(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)  # Add user_id field for write-only

    class Meta:
        model = Case
        fields = ['pid', 'user_id', 'oid', 'type','title','cstate']  # Specify the fields to include in the serializer

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)  # Extract the user_id from validated_data
        if user_id:
            user = cUser.objects.get(pk=user_id)  # Retrieve the user object based on the user_id
            validated_data['user'] = user  # Assign the user object to the 'user' field in validated_data
        return super().create(validated_data)


class LostVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostVehicle
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class EmergencySerializer(serializers.ModelSerializer):

    district = DistrictSerializer(source='did')

    class Meta:
        model = Emergency
        fields = [
            'emid',
            'district',
            'name',
            'number',
            'lat',
            'long',
        ]

class InformationSerializer(serializers.ModelSerializer):

    information_type = serializers.ChoiceField(choices=Information.Itype, required=True)

    class Meta:
        model = Information
        fields = [
            'inid',
            'information_type',
            'heading',
            'content'
        ]

    # def get_information_type(self, information):
    #     return dict(Information.Itype)[information.information_type]

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):

        otp_code = randint(100000, 999999)

        user = User(
            username=validated_data.get('username'),
            mobile=validated_data['mobile'],
            role=validated_data.get('role', 'user'),
            address=validated_data.get('address', None),
            pincode=validated_data.get('pincode', ''),
            otp_code=validated_data.get('otp_code', otp_code)
        )
        if password := validated_data.get('password'):
            user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'mobile', 'username', 'password', 'role', 'address', 'pincode', 'otp_code']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with the provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs['user'] = user
        return attrs

class OTPSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    otp_code = serializers.CharField(max_length=6)