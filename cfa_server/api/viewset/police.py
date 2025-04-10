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
import logging

logger = logging.getLogger(__name__)

class PoliceStationViewSet(ModelViewSet):
    serializer_class = PoliceStationSerializer
    queryset = PoliceStation.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        logger.info("Entering PoliceStationViewSet.list")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Retrieved {len(response.data)} police stations")
        logger.info("Exiting PoliceStationViewSet.list")
        return response


class PoliceStationContactViewSet(ModelViewSet):
    serializer_class = PoliceStationContactSerializer
    queryset = PoliceStationContact.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        logger.info("Entering PoliceStationContactViewSet.create")
        logger.debug(f"Creating contact with data: {request.data}")
        response = super().create(request, *args, **kwargs)
        logger.info(f"Created police station contact with ID: {response.data.get('ps_cid')}")
        logger.info("Exiting PoliceStationContactViewSet.create")
        return response


class PoliceOfficerViewSet(ModelViewSet):
    serializer_class = PoliceOfficerSerializer
    queryset = PoliceOfficer.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        logger.info("Entering PoliceOfficerViewSet.list")
        response = super().list(request, *args, **kwargs)
        logger.info(f"Retrieved {len(response.data)} police officers")
        logger.info("Exiting PoliceOfficerViewSet.list")
        return response

    @action(detail=False, methods=["GET"], permission_classes=[IsPoliceOfficer])
    def others(self, request):
        logger.info("Entering PoliceOfficerViewSet.others")
        
        current_officer = request.user.policeofficer_set.first()
        logger.debug(f"Current officer ID: {current_officer.oid}, Station: {current_officer.pid}")
        
        officers = PoliceOfficer.objects.filter(pid=current_officer.pid)
        logger.info(f"Found {officers.count()} officers in same police station")
        
        serializer = PoliceOfficerSerializer(
            officers, many=True, context={"request": request}
        )
        logger.info("Exiting PoliceOfficerViewSet.others")
        return Response(status=200, data=serializer.data)


class DistrictPoliceStationViewSet(ReadOnlyModelViewSet):
    serializer_class = PoliceStationSerializer
    queryset = PoliceStation.objects.all()

    def get_queryset(self):
        logger.info("Entering DistrictPoliceStationViewSet.get_queryset")
        
        district_id = self.kwargs["district_id"]
        logger.debug(f"Filtering police stations for district_id: {district_id}")
        
        queryset = PoliceStation.objects.filter(did=district_id)
        logger.info(f"Found {queryset.count()} police stations in district {district_id}")
        
        logger.info("Exiting DistrictPoliceStationViewSet.get_queryset")
        return queryset
