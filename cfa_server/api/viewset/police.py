from rest_framework.viewsets import ModelViewSet
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
