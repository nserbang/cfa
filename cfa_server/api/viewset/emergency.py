from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.gis.geos import fromstr
from rest_framework.pagination import PageNumberPagination

from django.contrib.gis.db.models.functions import Distance

from api.models import Emergency, EmergencyType
from api.serializers import EmergencySerializer, EmergencyTypeSerializer
from api.viewset.permission import IsReadOnly


class EmergencyViewSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()
    permission_classes = (IsReadOnly,)

    def get_queryset(self):
        emergency_type_id = self.kwargs["emergency_type_id"]
        queryset = Emergency.objects.filter(tid=emergency_type_id)
        lat = self.request.query_params.get("lat")
        long = self.request.query_params.get("long")
        if lat and long:
            geo_location = fromstr(f"POINT({long} {lat})", srid=4326)
            user_distance = Distance("geo_location", geo_location)
            queryset = queryset.annotate(distance=user_distance)
        return queryset


class EmergencyViewListSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()
    permission_classes = (IsReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        lat = self.request.query_params.get("lat")
        long = self.request.query_params.get("long")
        if lat and long:
            geo_location = fromstr(f"POINT({long} {lat})", srid=4326)
            user_distance = Distance("geo_location", geo_location)
            queryset = queryset.annotate(distance=user_distance)
        return queryset

class NoPagination(PageNumberPagination):
    page_size = None

class EmergencyTypeViewSet(ModelViewSet):
    serializer_class = EmergencyTypeSerializer
    queryset = EmergencyType.objects.all()
    permission_classes = (IsReadOnly,)
    pagination_class = NoPagination

