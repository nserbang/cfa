from rest_framework.viewsets import ModelViewSet

from api.models import Information
from api.serializers import InformationSerializer

class InformationViewSet(ModelViewSet):
    serializer_class = InformationSerializer
    queryset = Information.objects.all()