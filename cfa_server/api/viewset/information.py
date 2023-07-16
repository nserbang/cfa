from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from api.models import Information
from api.serializers import InformationSerializer
from api.viewset.permission import IsAuthenticatedOrWriteOnly

class InformationViewSet(ModelViewSet):
    serializer_class = InformationSerializer
    queryset = Information.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['inid', 'information_type']
    search_fields = ['information_type', 'intro']
    ordering_fields = ['information_type', 'inid']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        return super().get_queryset()
