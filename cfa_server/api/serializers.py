from rest_framework import serializers
from .models import *

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class cUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = cUser
        fields = '__all__'


class PoliceStationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceStationContact
        fields = '__all__'


class PoliceStationSerializer(serializers.ModelSerializer):
   # contact = PoliceStationSerializer(many=True)
    class Meta:
        model = PoliceStation
        fields = '__all__'


class PoliceOfficerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PoliceOfficer
        fields = '__all__'


class CaseHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CaseHistory
        fields = '__all__'


class MediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class CaseSerializer(serializers.HyperlinkedModelSerializer):
    history = CaseHistorySerializer(many=True)
    media = MediaSerializer(many=True)

    class Meta:
        model = Case
        fields = '__all__'


class LostVehicleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LostVehicle
        fields = '__all__'
