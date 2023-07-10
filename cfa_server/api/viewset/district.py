from rest_framework.viewsets import ModelViewSet

from api.models import District
from api.serializers import DistrictSerializer

class DistrictViewSet(ModelViewSet):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()