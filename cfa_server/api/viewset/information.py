from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from api.models import Information
from api.serializers import InformationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class InformationViewSet(ModelViewSet):
    serializer_class = InformationSerializer
    queryset = Information.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['inid', 'information_type']
    search_fields = ['information_type', 'intro']
    ordering_fields = ['information_type', 'inid']
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return super().get_queryset()
