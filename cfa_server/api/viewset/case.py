from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Case, CaseHistory, LostVehicle, Comment, Media
from django.db.models import Q

from api.serializers import (
    CaseSerializer,
    CaseHistorySerializer,
    CaseSerializerCreate,
    CommentCreateSerializer,
    CommentSerializer,
    LostVehicleSerializer,
    MediaSerializer,
)
from api.mixins import UserMixin


class CaseViewSet(UserMixin, ModelViewSet):
    serializer_class = CaseSerializer
    # queryset = Case.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.request.query_params.get("search", None)

        data = Case.objects.all()
        if search:
            data = data.filter(
                Q(title__contains=search)
                | Q(cid__contains=search)
                | Q(description__contains=search)
            )
        return data


class CaseHistoryViewSet(UserMixin, ModelViewSet):
    serializer_class = CaseHistorySerializer
    queryset = CaseHistory.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class MediaViewSet(ModelViewSet):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class LostVehicleViewSet(ModelViewSet):
    serializer_class = LostVehicleSerializer
    queryset = LostVehicle.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.filter(caseId__user=self.request.user)
        return qs


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        case_id = self.kwargs["case_id"]
        qs = Comment.objects.filter(cid=case_id)
        return qs


class CaseCreateAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, format=None):
        serializer = CaseSerializerCreate(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CommentCUDViewSet(ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Comment.objects.all()
        return qs

    def create(self, request, *args, **kwargs):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)