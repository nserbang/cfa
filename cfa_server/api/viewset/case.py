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
from api.viewset.permission import IsAuthenticatedOrWriteOnly

class CaseViewSet(ModelViewSet):
    serializer_class = CaseSerializer
    queryset = Case.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

class CaseHistoryViewSet(ModelViewSet):
    serializer_class = CaseHistorySerializer
    queryset = CaseHistory.objects.all()


class MediaViewSet(ModelViewSet):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class LostVehicleViewSet(ModelViewSet):
    serializer_class = LostVehicleSerializer
    queryset = LostVehicle.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


class CommentViewSet(ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedOrWriteOnly]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        case_id = self.kwargs['case_id']
        return Comment.objects.filter(cid=case_id).all()
