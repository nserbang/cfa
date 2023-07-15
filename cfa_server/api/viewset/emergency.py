from rest_framework.viewsets import ModelViewSet

from api.models import Emergency
from api.serializers import EmergencySerializer
from api.viewset.permission import IsAuthenticatedOrWriteOnly

class EmergencyViewSet(ModelViewSet):
    serializer_class = EmergencySerializer
    queryset = Emergency.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        district_id = self.kwargs['district_id']

        queryset = Emergency.objects.filter(did=district_id).all()

        return queryset
