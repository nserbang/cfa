from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from api.models import District
from api.serializers import DistrictSerializer

class NoPagination(PageNumberPagination):
    page_size = None

class DistrictViewSet(ModelViewSet):
    serializer_class = DistrictSerializer
    pagination_class = NoPagination
    queryset = District.objects.all()