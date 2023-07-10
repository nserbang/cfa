from rest_framework.viewsets import ViewSet, ModelViewSet
from api.models import (
    Case,
    CaseHistory,
    LostVehicle,
    Comment,
    Media
    )
from api.serializers import (
    CaseSerializer,
    CaseHistorySerializer,
    CommentSerializer,
    LostVehicleSerializer,
    MediaSerializer,
)

class CaseViewSet(ModelViewSet):
    serializer_class = CaseSerializer
    queryset = Case.objects.all()


class CaseHistoryViewSet(ModelViewSet):
    serializer_class = CaseHistorySerializer
    queryset = CaseHistory.objects.all()


class MediaViewSet(ModelViewSet):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class LostVehicleViewSet(ModelViewSet):
    serializer_class = LostVehicleSerializer
    queryset = LostVehicle.objects.all()


class CommentViewSet(ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
