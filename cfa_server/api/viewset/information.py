from rest_framework.viewsets import ModelViewSet

from api.models import Information
from api.serializers import InformationSerializer
from api.viewset.permission import IsAuthenticatedOrWriteOnly

class InformationViewSet(ModelViewSet):
    serializer_class = InformationSerializer
    queryset = Information.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]
