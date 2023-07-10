from rest_framework.viewsets import ModelViewSet

from api.models import Emergency
from api.serializers import EmergencySerializer

class EmergencyViewSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()