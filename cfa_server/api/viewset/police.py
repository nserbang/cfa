from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.models import (
    PoliceStation,
    PoliceStationContact,
    PoliceOfficer
)

from api.serializers import (
    PoliceStationSerializer,
    PoliceStationContactSerializer,
    PoliceOfficerSerializer
)

class PoliceStationViewSet(ModelViewSet):
    serializer_class = PoliceStationSerializer
    queryset = PoliceStation.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

# View cor Police Station Contact
class PoliceStationContactViewSet(ModelViewSet):

    serializer_class = PoliceStationContactSerializer
    queryset = PoliceStationContact.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

# Views for Police Officers
class PoliceOfficerViewSet(ModelViewSet):
    serializer_class = PoliceOfficerSerializer
    queryset = PoliceOfficer.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

class DistrictPoliceStationViewSet(ReadOnlyModelViewSet):

    serializer_class = PoliceStationSerializer
    queryset = PoliceStation.objects.all()

    def get_queryset(self):
        district_id = self.kwargs['district_id']
        queryset = PoliceStation.objects.filter(did=district_id)
        return queryset
