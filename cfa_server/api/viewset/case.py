import requests
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Case as MCase, When
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from django.db.models import OuterRef, Count, Exists
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Case, CaseHistory, LostVehicle, Comment, Media, Like
from django.db.models import Q
from api.viewset.permission import IsPoliceOfficer
import logging

logger = logging.getLogger(__name__)

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
    CaseUpdateByReporterSerializer,
)
from api.mixins import UserMixin


class CaseViewSet(UserMixin, ModelViewSet):
    serializer_class = CaseSerializer
    # queryset = Case.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        logger.info("Entering get_queryset")
        
        search = self.request.query_params.get("search", None)
        my_case = self.request.query_params.get("my_case", None)
        lat = self.request.query_params.get("lat")
        long = self.request.query_params.get("long")
        user = self.request.user
        
        logger.debug(f"Query params - search: {search}, my_case: {my_case}, lat: {lat}, long: {long}")
        logger.info(f"User: {user.mobile}, is_authenticated: {user.is_authenticated}")

        data = (
            Case.objects.all()
            .annotate(
                comment_count=Count("comment", distinct=True),
                like_count=Count("likes", distinct=True),
            )
            .select_related("pid", "oid", "oid__user", "oid__pid", "oid__pid__did")
            .prefetch_related("medias")
        ).order_by("-created")
        
        logger.debug("Base queryset created with annotations and related fields")

        if user.is_authenticated:
            liked = Like.objects.filter(case_id=OuterRef("cid"), user=self.request.user)
            data = data.annotate(liked=Exists(liked))
            logger.debug("Added liked annotation for authenticated user")

            if user.is_police:
                officer = user.policeofficer_set.first()
                rank = int(officer.rank)
                logger.info(f"Police officer rank: {rank}")

                data = data.annotate(
                    can_act=MCase(
                        When(
                            (Q(cstate="pending") & Q(oid__rank=5))
                            | (~Q(cstate="pending") & Q(oid__rank=4) & Q(oid=officer)),
                            then=True,
                        ),
                        default=False,
                    )
                )
                if rank > 9:
                    logger.debug("Officer rank > 9, no additional filters")
                elif rank == 9:
                    data.filter(pid__did_id=officer.pid.did_id)
                    logger.debug(f"Filtered by district ID: {officer.pid.did_id}")
                elif rank == 6:
                    data = data.filter(
                        pid_id__in=officer.policestation_supervisor.values("station")
                    )
                    logger.debug(f"Filtered by police station supervisor values")
                elif rank == 5:
                    data = data.filter(pid_id=officer.pid_id)
                    logger.debug(f"Filtered by police station ID: {officer.pid_id}")
                elif rank == 4:
                    data = data.filter(oid=officer).exclude(cstate="pending")
                    logger.debug(f"Filtered by officer ID: {officer.id}")
                else:
                    data = data.filter(Q(user=user) | Q(type="vehicle"))
                    logger.debug("Applied regular user filters")

            elif user.is_user:
                data = data.filter(Q(user=user) | Q(type="vehicle"))
                logger.debug("Applied regular user filters")

        if search:
            logger.info(f"Applying search filter: {search}")
            data = data.filter(
                Q(title__contains=search)
                | Q(cid__contains=search)
                | Q(description__contains=search)
            )

        logger.info("Exiting get_queryset")
        return data

    def list(self, request, *args, **kwargs):
        logger.info("Entering list")
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            logger.debug(f"Paginating results, page size: {len(page)}")
            self.add_distances(page)
            serializer = self.get_serializer(page, many=True)
            logger.info("Exiting list with paginated response")
            return self.get_paginated_response(serializer.data)

        logger.debug("No pagination, processing full queryset")
        self.add_distances(queryset)
        serializer = self.get_serializer(queryset, many=True)
        logger.info("Exiting list with full response")
        return Response(serializer.data)

    def add_distances(self, data):
        logger.info("Entering add_distances")
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("long")
        
        if lat and lng:
            logger.debug(f"Calculating distances from coordinates: {lat}, {lng}")
            origin_str = f"{lat},{lng}"
            destinations = []
            
            for item in data:
                if loc := item.geo_location:
                    destinations.append(f"{loc.coords[1]},{loc.coords[0]}")
            
            logger.debug(f"Processing {len(destinations)} destinations")
            destinations_str = "|".join(destinations)
            
            url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
            params = {
                "origins": origin_str,
                "destinations": destinations_str,
                "key": settings.GOOGLE_MAP_API_KEY,
            }
            
            try:
                response = requests.get(url, params=params)
                if response.ok:
                    distances = response.json()
                    logger.info("Successfully retrieved distances from Google API")
                    
                    for i, item in enumerate(data):
                        try:
                            item.distance = distances["rows"][0]["elements"][i]["distance"]["text"]
                            logger.debug(f"Set distance for item {item.cid}: {item.distance}")
                        except (KeyError, ValueError) as e:
                            logger.warning(f"Could not set distance for item {item.cid}: {str(e)}")
                            item.distance = "Not available"
                else:
                    logger.error(f"Google API request failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Error calculating distances: {str(e)}")
        
        logger.info("Exiting add_distances")


class CaseHistoryViewSet(UserMixin, ReadOnlyModelViewSet):
    serializer_class = CaseHistorySerializer
    queryset = CaseHistory.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        case_id = int(self.kwargs["case_id"])
        qs = CaseHistory.objects.filter(case_id=case_id)
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    permission_classes = (IsPoliceOfficer,)
    serializer_class = CaseUpdateSerializer
    queryset = Case.objects.all()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CaseUpdateSerializer(
            data=request.data, instance=instance, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class CaseUpdaateByReporterAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CaseUpdateByReporterSerializer
    queryset = Case.objects.filter(cstate="info")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Permission Denied."}, status=403)
        serializer = CaseUpdateByReporterSerializer(
            data=request.data, instance=instance, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class CaseAcceptAPIView(UpdateAPIView):
    queryset = Case.objects.all()
    permission_classes = (IsPoliceOfficer,)

    def put(self, request, *args, **kwargs):
        case = self.get_object()
        case.oid = request.user.policeofficer_set.first()
        case.save()
        return Response({"message": "Succesfull"}, status=200)


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
