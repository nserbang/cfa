from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
    CaseSerializerCreate,
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


class CaseCreateAPIView(APIView):

    def post(self, request, format=None):
        serializer = CaseSerializerCreate(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
