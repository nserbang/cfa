from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from api.viewset.permission import IsPoliceOfficer

from api.models import PoliceStation, PoliceStationContact, PoliceOfficer

from api.serializers import (
    PoliceStationSerializer,
    PoliceStationContactSerializer,
    PoliceOfficerSerializer,
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

    @action(detail=False, methods=["GET"], permission_classes=[IsPoliceOfficer])
    def others(self, request):
        current_officer = request.user.policeofficer_set.first()
        officers = PoliceOfficer.objects.filter(pid=current_officer.pid)
        serializer = PoliceOfficerSerializer(
            officers, many=True, context={"request": request}
        )
        return Response(status=200, data=serializer.data)


class DistrictPoliceStationViewSet(ReadOnlyModelViewSet):
    serializer_class = PoliceStationSerializer
    queryset = PoliceStation.objects.all()

    def get_queryset(self):
        district_id = self.kwargs["district_id"]
        queryset = PoliceStation.objects.filter(did=district_id)
        return queryset
