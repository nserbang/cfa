from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from django.db.models import OuterRef, Count, Exists
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Case, CaseHistory, LostVehicle, Comment, Media, Like
from django.db.models import Q

from api.serializers import (
    CaseSerializer,
    CaseHistorySerializer,
    CaseSerializerCreate,
    CommentCreateSerializer,
    CommentSerializer,
    LikeCreateDeleteSerializer,
    LikeListSerializer,
    LikeSerializer,
    LostVehicleSerializer,
    MediaSerializer,
    CaseUpdateSerializer,
)
from api.mixins import UserMixin


class CaseViewSet(UserMixin, ModelViewSet):
    serializer_class = CaseSerializer
    # queryset = Case.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.request.query_params.get("search", None)
        my_case = self.request.query_params.get("my_case", None)
        a = self.request.query_params.get("q")
        data = (
            Case.objects.all()
            .annotate(
                comment_count=Count("comment", distinct=True),
                like_count=Count("likes", distinct=True),
            )
            .select_related("pid", "oid", "oid__user", "oid__pid")
        )
        if self.request.user.is_authenticated:
            liked = Like.objects.filter(case_id=OuterRef("cid"), user=self.request.user)
            data = data.annotate(
                liked=Exists(liked),
            )
        if search:
            data = data.filter(
                Q(title__contains=search)
                | Q(cid__contains=search)
                | Q(description__contains=search)
            )
        if my_case is not None and my_case.lower() == "true":
            request_user_id = self.request.user.id
            data = data.filter(Q(user=request_user_id) | Q(oid__user=request_user_id))

        return data


class CaseHistoryViewSet(UserMixin, ReadOnlyModelViewSet):
    serializer_class = CaseHistorySerializer
    queryset = CaseHistory.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        case_id = int(self.kwargs["case_id"])
        qs = CaseHistory.objects.filter(cid=case_id)
        return qs


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
    serializer_class = CaseSerializerCreate

    def post(self, request, format=None):
        serializer = CaseSerializerCreate(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CaseUpdaateAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CaseUpdateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Case.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(user__role="police")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CaseUpdateSerializer(
            data=request.data, instance=instance, context={"request": request}
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


class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return LikeListSerializer
        elif self.action == "create":
            return LikeCreateDeleteSerializer
        elif self.action == "delete":
            return LikeCreateDeleteSerializer
        return LikeListSerializer  # Use LikeListSerializer for other actions

    def get_queryset(self):
        # Fetch the case_id from the URL
        case_id = self.kwargs["case_id"]
        # Filter the queryset to get likes for the specific case_id
        queryset = Like.objects.filter(case_id=case_id)
        return queryset

    def create(self, request, *args, **kwargs):
        # Fetch the case_id from the URL
        case_id = self.kwargs.get("case_id")
        # Add the case_id to the request data
        request.data["case"] = case_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        case_id = self.kwargs.get("case_id")
        user_id = request.data.get(
            "user"
        )  # Assuming user_id is passed as 'user' in the request body

        if not user_id:
            return Response(
                {"user": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = get_object_or_404(Like, case_id=case_id, user_id=user_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
