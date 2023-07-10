from rest_framework import serializers
from .models import *

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


class PoliceStationSerializer(serializers.ModelSerializer):

    district = DistrictSerializer(source='did')
    contacts = PoliceStationContactSerializer(source='policestationcontact_set', many=True)

    class Meta:
        model = PoliceStation
        fields = [
            'pid',
            'did',
            'name',
            'address',
            'lat',
            'long',
            'distance',
            'contacts',
            'district'
        ]

    # def get_contact(self, police_station):
    #     contacts = police_station.contacts.all()
    #     serializers = PoliceStationContactSerializer(contacts, many=True)
    #     return serializers

class PoliceOfficerSerializer(serializers.ModelSerializer):

    police_station = PoliceStationSerializer(source='pid')

    class Meta:
        model = PoliceOfficer
        fields = '__all__'


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

    information_type = serializers.SerializerMethodField()

    class Meta:
        model = Information
        fields = [
            'inid',
            'information_type',
            'heading',
            'content'
        ]

    def get_information_type(self, information):
        return dict(Information.Itype)[information.information_type]

