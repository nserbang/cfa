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
from django.db import transaction
from api.forms import print_formatted_records
from django.forms.models import model_to_dict
logger = logging.getLogger(__name__)
from django.contrib.gis.geos import Point
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
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from api.utils import get_cases

class CaseViewSet(UserMixin, ModelViewSet):
    serializer_class = CaseSerializer
    # queryset = Case.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        logger.info("Entering get_queryset")
        user = self.request.user
        if user.is_authenticated is None or user.is_authenticated is False:
            logger.info("unauthenticated")
            return "unauthenticated"
        
        search = self.request.query_params.get("search", None)
        my_case = self.request.query_params.get("my_case", None) 
        #if my_case is None:
                #return None;
        lat = self.request.query_params.get("lat")
        long = self.request.query_params.get("long")
        
        logger.debug(f"Query params - search: {search}, my_case: {my_case}, lat: {lat}, long: {long}")
        #if user is not None and hasattr(user,'mobile'):dd
        if user.is_authenticated and hasattr(user,'mobile'):
            logger.info(f"User: {user.mobile}, is_authenticated: {user.is_authenticated}")
        else:
            logger.info(f"User.mobile not exist")

        data = (
            Case.objects.all()
            .annotate(
                comment_count=Count("comment", distinct=True),
                like_count=Count("likes", distinct=True),
            )
            .select_related("pid", "oid", "oid__user", "oid__pid", "oid__pid__did")
            #.prefetch_related("medias") need to add the result of medias if any in reqult
        ).order_by("-created")
        
        logger.debug("Base queryset created with annotations and related fields")

        if user.is_authenticated:
            liked = Like.objects.filter(case_id=OuterRef("cid"), user=self.request.user)
            data = data.annotate(liked=Exists(liked))
            logger.debug("Added liked annotation for authenticated user")
            """ 
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
                    logger.debug("Officer rank  = 9")
                    data.filter(pid__did_id=officer.pid.did_id)
                elif rank == 6:
                    logger.debug("Officer rank  = 6")
                    data = data.filter(
                        pid_id__in=officer.policestation_supervisor.values("station")
                    )
                    logger.debug(f"Filtered by police station supervisor values")
                elif rank == 5:
                    logger.debug("Officer rank  = 5")
                    data = data.filter(pid_id=officer.pid_id)
                elif rank == 4:
                    logger.debug("Officer rank  = 4")
                    data = data.filter(oid=officer).exclude(cstate="pending")
                else:
                    data = data.filter(Q(user=user) | Q(type="vehicle"))
                    logger.debug("Applied regular user filters")

            elif user.is_user:
                data = data.filter(Q(user=user) | Q(type="vehicle"))
                logger.debug("Applied regular user filters") """
        if search:
            logger.info(f"Applying search filter: {search}")
            data = data.filter(
                  Q(cid__contains=search)
                | Q(description__contains=search)
            )
        
        #case_type = self.get_case_type()
        #my_complaints = self.kwargs.get("case_type") == "my-complaints"
        data = get_cases(user, data, case_type= None, my_complaints=my_case)

        logger.info(f"Exiting get_queryset query data: {data.exists()}")
        return data

    def list(self, request, *args, **kwargs):
        logger.info("Entering list")
        queryset = self.filter_queryset(self.get_queryset())
        logger.info(f"Queryset : {queryset}")
        if queryset is None:
            return Response([])
        if queryset is "unauthenticated":
            return Response({"details":" Login required"}, status = 403)
        if not queryset.exists():
            logger.debug("Query set is empty")
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response([])
            return Response([])
        page = self.paginate_queryset(queryset)
        if page is not None:
            logger.debug(f"Paginating results, page size: {len(page)}")
            self.add_distances(page)
            serializer = self.get_serializer(page, many=True)
            response_data = serializer.data
            #logger.debug(f"Response data before append: {response_data}")
            #print_formatted_records(response_data)        
            self.append_media(response_data)
            #logger.debug(f"Response data after append: {response_data}")
            print_formatted_records(response_data)
            logger.info(f"Exiting list with paginated response with response data")
            #return self.get_paginated_response(serializer.data)
            return self.get_paginated_response(response_data)

        logger.debug("No pagination, processing full queryset")
        self.add_distances(queryset)
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        #logger.debug(f"Response data before append: {response_data}")
        #print_formatted_records(response_data)        
        self.append_media(response_data)
        #logger.debug(f"Response data after append: {response_data}")
        print_formatted_records(response_data)  
        logger.info(f"Exiting list with full response with response data")
        #return Response(serializer.data)
        return Response(response_data)

    def append_media(self, data):
        logger.info(" Appending medias to response ")
        case_ids = [item["cid"] for item in data]
        logger.info(f"Case IDs: {case_ids}")
        medias = Media.objects.filter(source="case", parentId__in=case_ids)
        #for media in medias:
            #logger.info(f"Media details - ID: {media.id}, Source: {media.source}, Parent ID: {media.parentId}, Type: {media.mtype}, Path: {media.path}")
        media_dict = {}
        for media in medias:
            #logger.debug(f" ParentID type : {type(media.parentId)}")
            #logger.info(f" Apppeinding file : {media.path}, type : {media.mtype}, type : {media.source}, parentId : {media.parentId}")
            if media.parentId not in media_dict:
                media_dict[media.parentId] = []
            media_dict[media.parentId].append({
                "mtype":media.mtype,
                "path":media.path.url if media.path else None,
            }
            )
        for item in data:
            item["medias"] = media_dict.get(item["cid"], [])
            #logger.debug(f" CID type type : {type(item['cid'])}")
            #for media in item["medias"]:
                #logger.info(f"Media details - Type: {media['mtype']}, Path: {media['path']}")
            #logger.info("Media appended succcefully")


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
        logger.info(f"Entering CaseHistoryViewSet case id:")
        case_id = int(self.kwargs["case_id"])
        qs = CaseHistory.objects.filter(case_id=case_id).order_by("-created")
        return qs
        """
        # Append medias to each case history
        history_ids = qs.values_list("id", flat=True)
        medias = Media.objects.filter(source="history", parentId__in=history_ids)
        media_dict = {}
        for media in medias:
            if media.parentId not in media_dict:
                media_dict[media.parentId] = []
            media_dict[media.parentId].append({
                "mtype": media.mtype,
                "path": media.path.url if media.path else None,
            })

        for history in qs:
            setattr(history, "medias", media_dict.get(history.id,[]))
            #history.medias = media_dict.get(history.id, [])

        records = [model_to_dict(history) for history in qs]
        print_formatted_records(records)
        logger.info(f"Exiting CaseHistoryViewSet case result: {qs}")
        return qs
        """

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
        logger.info(f" Returning from LostVehicleViewSet with result :{qs}")
        return qs


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        logger.info(f" Entering. request : {self.request}, data : {self.request.data}, files : {self.request.FILES} ")
        comment = serializer.save(user=self.request.user)
        medias = self.request.FILES.getlist('medias')
        logger.info(f"Media Received: {medias}")
        for media in medias:
            ct = media.content_type
            if 'image' in ct:
                mtyper = "photo"
            elif 'video' in ct:
                mtyper = "video"
            elif 'application' in ct:
                mtyper = "document"
            else:
                logger.warning(f" Unknown medi type: {ct}")

            Media.objects.create(
                    source="comment",
                    parentId = comment.cmtid,
                    mtype = mtyper,
                    path = media,
                )
        logger.info(" Exiting ")

    def get_queryset(self):
        logger.info("Entering comment")
        case_id = self.kwargs["case_id"]
        qs = Comment.objects.filter(cid=case_id).order_by("-created")
        return qs

        """
        # Append medias to each comment
        comment_ids = qs.values_list("cmtid", flat=True)
        medias = Media.objects.filter(source="comment", parentId__in=comment_ids)
        media_dict = {}
        for media in medias:
            if media.parentId not in media_dict:
                media_dict[media.parentId] = []
            media_dict[media.parentId].append({
                "mtype": media.mtype,
                "path": media.path.url if media.path else None,
            })

        for comment in qs:
            setattr(comment, "medias", media_dict.get(comment.cmtid,[]))
            #comment.medias = media_dict.get(comment.cmtid, [])

        records = [model_to_dict(comment) for comment in qs]
        print_formatted_records(records)
        #print_formatted_records(qs)
        logger.info("Exiting comment")
        return qs """


import os
from django.conf import settings
from rest_framework.exceptions import ValidationError

class CaseCreateAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CaseSerializerCreate

    def post(self, request, format=None):
        logger.info(f"ENTERING post with request: {request}, data: {request.data}")

        # Check if user is authenticated
        if request.user.is_anonymous:
            return Response(
                {"detail": "You must be logged in to create a case."}, status=403
            )

        ctype = request.data.get("type")
        if ctype is None:
            return Response({"type": ["This field is required."]}, status=400)

        logger.info(f"UPLOADED FILES: {request.FILES}")

        # Create basic case entity
        case_serializer = CaseSerializerCreate(
            data=request.data, context={"request": request}
        )

        if case_serializer.is_valid():
            logger.info("Case data is valid")
            try:
                with transaction.atomic():
                    case_instance = case_serializer.save()
                    if not case_instance:
                        logger.error("Case creation failed")
                        return Response(
                            {"detail": "Case creation failed."}, status=400
                        )

                    # Handle media files
                    medias = request.FILES.getlist('medias')
                    logger.info(f"Medias Received: {medias}")

                    #media_dir = os.path.join(settings.MEDIA_ROOT, "case_media")
                    #media_dir = os.path.join(settings.MEDIA_ROOT, "case_media")
                    #os.makedirs(media_dir, exist_ok=True)

                    for media in medias:
                        # Save the file to the media directory
                        #file_path = os.path.join(media_dir, media.name)
                        #with open(file_path, "wb") as f:
                            #for chunk in media.chunks():
                                #f.write(chunk)
                        #logger.info(f"File saved to: {file_path}")

                        # Determine media type
                        if 'image' in media.content_type:
                            mtyper = "photo"
                        elif 'video' in media.content_type:
                            mtyper = "video"
                        elif 'application' in media.content_type:
                            mtyper = "document"
                        else:
                            logger.warning(f"Unknown media type: {media.content_type}")
                            continue

                        # Create Media object
                        Media.objects.create(
                            source="case",
                            parentId=case_instance.cid,
                            mtype=mtyper,
                            path=media,
                           # name=media.name,
                        )

                    logger.info(f"Case created successfully: {case_instance.cid}")
                    return Response(case_serializer.data, status=201)
            except Exception as e:
                logger.error(f"Case creation failed with exception: {str(e)}")
                return Response(
                    {"detail": f"Case creation failed: {str(e)}"}, status=400
                )
        else:
            logger.error(f"Case data validation failed: {case_serializer.errors}")
            return Response(case_serializer.errors, status=400)


class CaseUpdaateAPIView(UpdateAPIView):
    permission_classes = (IsPoliceOfficer,)
    serializer_class = CaseUpdateSerializer
    queryset = Case.objects.all()

    def put(self, request, *args, **kwargs):
        logger.info(f" Entering. request : {request}, data : {request.data}, files : {request.FILES} ")
        lat = request.data.get("lat",None)
        ll = request.data.get("long",None)
        if lat is None or ll is None:
            logger.info(f"user location not available")
            return Response({"details":"Your location is not enabled"}, status=403)

        if hasattr(request, "user") is None:
            logger.info(f"user is not available in request")
            return Response({"details":"You are required to log in"}, status=403)
        
        if not request.user.is_authenticated:
            logger.info(f"user not authenticated")
            return Response({"details":"You are required to authenticated "}, status=403)

        instance = self.get_object()
        if instance is None:
            logger.info(f"Case not found")
            return Response({"details":"Record not found"}, status=404)
        user = request.user
        cstate = request.data.get("cstate")

        if user.role == "police" and user == instance.user:
            if instance.type != "vehicle" and cstate not in ["transfer","assign"]:
                logger.info(f"Complaint and police are same")
                return Response({"details":"You cannot change your own case"}, status=403)

        try:
            serializer = CaseUpdateSerializer(data=request.data, instance=instance, context={"request": request})
        except Exception as e:
            logger.info(f"Serialization error: {serializer.errors}")
            return Response({f"details":str(e)}, status=404)

        username = request.user.get_username() if hasattr(request.user, 'get_username') else str(request.user)
        
        description = " N/A "
        if cstate == "pending":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "accepted":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "found":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "assign":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "visited":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "inprogress":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "transfer":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "resolved":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "info":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        elif cstate == "rejected":
            description = f"Case status being changed from: {instance.cstate} to : {cstate} by : {request.user}"
        else:
            description = f"Case status being changed to {cstate} by : {request.user}"

        logger.debug(f"Case update request received for : {cstate} for cid : {instance.cid}")
        if serializer.is_valid():
            updated_case = serializer.save()

            case_point = Point(float(updated_case.long), float(updated_case.lat), srid=4326)
            user_point = Point(float(ll), float(lat), srid=4326)
            case_point_m = case_point.transform(3857, clone=True)
            user_point_m = user_point.transform(3857, clone=True)
            distance = user_point_m.distance(case_point_m)/1000 #in km


            logger.debug(f" Recorded updated for case id :{updated_case.cid}")
            if cstate == "transfer":
                # Record transient state Transfer before cstate is set to Pending
                case_history = CaseHistory.objects.create(
                        case = updated_case,
                        user = request.user,
                        description = description,
                        cstate = cstate,
                        lat = request.data.get("lat",None),
                        long = request.data.get("long",None),
                        distance = distance,
                    )

            # Record actual case history now    
            case_history = CaseHistory.objects.create(
                    case = updated_case,
                    user = request.user,
                    description = request.data.get("description"),
                    cstate = updated_case.cstate,
                    lat = request.data.get("lat",None),
                    long = request.data.get("long",None),
                    distance = distance,
                )

            medias = request.FILES.getlist('medias')
            logger.info(f"Media Received: {medias}")
            for media in medias:
                ct = media.content_type
                if 'image' in ct:
                    mtyper = "photo"
                elif 'video' in ct:
                    mtyper = "video"
                elif 'application' in ct:
                    mtyper = "document"
                else:
                    logger.warning(f" Unknown medi type: {ct}")

                Media.objects.create(
                        source="history",
                        parentId = case_history.id,
                        mtype = mtyper,
                        path = media,
                    )
            logger.info(f"Case updated succefuly for cid : {updated_case.cid}") 
            return Response(serializer.data, status=200)
        else :
            logger.debug(f" Case updated failed with : {str(serializer.errors)}")
        return Response({f"details":serializer.errors}, status=400)


class CaseUpdaateByReporterAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CaseUpdateByReporterSerializer
    queryset = Case.objects.filter(cstate="info")

    def put(self, request, *args, **kwargs):
        logger.info(f" Entering. request : {request}, data : {request.data}, files : {reqiest.FILES} ")
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Permission Denied."}, status=403)
        serializer = CaseUpdateByReporterSerializer(
            data=request.data, instance=instance, context={"request": request}
        )
        if serializer.is_valid():
            #serializer.save()
            updated_case = serializer.save()
            case_history = CaseHistory.objects.create(
                    case = updated_case,
                    user = request.user,
                    description = request.data.get("description"),
                    cstate = updated_case.cstate,
                    lat = request.data.get("lat",None),
                    long = request.data.get("long",None)
                )

            logger.info(f" Case history saved: {updated_case.cid}")
            medias = request.FILES.getlist('medias')
            logger.info(f"Media Received: {medias}")
            for media in medias:
                ct = media.content_type
                if 'image' in ct:
                    mtyper = "photo"
                elif 'video' in ct:
                    mtyper = "video"
                elif 'application' in ct:
                    mtyper = "document"
                else:
                    logger.warning(f" Unknown medi type: {ct}")

                Media.objects.create(
                        source="history",
                        parentId = case_history.id,
                        mtype = mtyper,
                        path = media,
                    )
            logger.info(f"Case updated succefuly for cid : {updated_case.cid}") 
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class CaseAcceptAPIView(UpdateAPIView):
    queryset = Case.objects.all()
    permission_classes = (IsPoliceOfficer,)

    def put(self, request, *args, **kwargs):
        logger.info(f" Entering CaseAcceAPIView put. request : {request}, data : {request.data}, files : {reqiest.FILES} ")
        case = self.get_object()
        case.oid = request.user.policeofficer_set.first()
        case.save()
        """case_history = CaseHistory.objects.create(
                case = case,
                user = request.user,
                description = request.data.get("description"),
                cstate = case.cstate,
                lat = request.data.get("lat",None),
                long = request.data.get("long",None)
            )"""
        return Response({"message": "Succesfull"}, status=200)


class CommentCUDViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Comment.objects.all()

        # Append medias to each comment
        comment_ids = qs.values_list("cmtid", flat=True)
        medias = Media.objects.filter(source="comment", parentId__in=comment_ids)
        media_dict = {}
        for media in medias:
            if media.parentId not in media_dict:
                media_dict[media.parentId] = []
            media_dict[media.parentId].append({
                "mtype": media.mtype,
                "path": media.path.url if media.path else None,
            })

        for comment in qs:
            setattr(comment, "medias", media_dict.get(comment.cmtid,[]))
            #comment.medias = media_dict.get(comment.cmtid, [])
        
        records = [model_to_dict(comment) for comment in qs]
        print_formatted_records(records)
        #print_formatted_records(qs)
        logger.info("Exiting comment")
        #logger.info(f"Exiting Comment queryset: {qs}")

        return qs

    def create(self, request, *args, **kwargs):
        logger.info(f" Entering. request : {request}, data : {request.data}, files : {reqiest.FILES} ")
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
        logger.info("Entering queryset")
        # Fetch the case_id from the URL
        case_id = self.kwargs["case_id"]
        # Filter the queryset to get likes for the specific case_id
        queryset = Like.objects.filter(case_id=case_id)
        return queryset

    def create(self, request, *args, **kwargs):
        logger.info("Entering create")
        # Fetch the case_id from the URL
        case_id = self.kwargs.get("case_id")
        # Add the case_id to the request data
        request.data["case"] = case_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def retrieve(self, request, *args, **kwargs):
        logger.info("Entering retrieve")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        logger.info("Entering delete")
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
