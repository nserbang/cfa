from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Banner

from api.serializers import (
    BannerSerializer
)
from django.db.models import Q


class BannerViewSet(ReadOnlyModelViewSet):

    serializer_class = BannerSerializer
    queryset = Banner