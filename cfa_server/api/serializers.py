import magic
from django.utils import timezone
from rest_framework import serializers
#from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import MethodNotAllowed
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from api.models import *
from django.contrib.auth import authenticate
from api.models import (
    Case,
    PoliceStation,
    cUser,
    PoliceOfficer,
    UserOTPBaseKey,
    District,
    PoliceStationContact,
    Media,
    Comment,
    LostVehicle,
    CaseHistory,
    Privacy,
    TermsCondition,
    AboutPage,
)
from api.npr import detectVehicleNumber
from api.otp import *
from api.mixins import PasswordDecriptionMixin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr
from api.forms import detect_malicious_patterns_in_media
from datetime import datetime
logger = logging.getLogger(__name__)


class CustomTokenObtainSerializer(PasswordDecriptionMixin, TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Unable to login with given credentials"
    }

    def validate(self, data):
        data = super().validate(data)
        user = UserProfileSerializer(
            self.user, context={"request": self.context["request"]}
        )
        data["user"] = user.data
        return data


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class cUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = cUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "role",
        ]


class PoliceStationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceStationContact
        fields = "__all__"


class PoliceStationSerializer(serializers.Serializer):
    pid = serializers.ReadOnlyField()
    did = DistrictSerializer(read_only=True)
    name = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    long = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    distance = serializers.DecimalField(max_digits=9, decimal_places=2, read_only=True)
    contacts = PoliceStationContactSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        logger.info("Entering to_representation")
        logger.debug(f"Converting police station instance: {instance.pid}")
        
        data = super().to_representation(instance)
        data["district"] = data.pop("did")
        
        logger.debug(f"Transformed data: {data}")
        logger.info("Exiting to_representation")
        return data

    # Preserve commented code
    # def get_contact(self, police_station):
    #     contacts = police_station.contacts.all()
    #     serializers = PoliceStationContactSerializer(contacts, many=True)
    #     return serializers


class PoliceOfficerSerializer(serializers.Serializer):
    oid = serializers.ReadOnlyField()
    user = cUserSerializer(read_only=True)
    pid = PoliceStationSerializer(read_only=True)
    rank = serializers.CharField(read_only=True)
    entryDate = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)
    mobile = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        logger.info("Entering to_representation")
        logger.debug(f"Converting police officer instance: {instance.oid}")
        
        data = super().to_representation(instance)
        data["user"] = cUserSerializer(instance.user).data
        data["pid"] = PoliceStationSerializer(instance.pid).data
        
        logger.debug(f"Transformed data: {data}")
        logger.info("Exiting to_representation")
        return data


class MediaSerializer(serializers.ModelSerializer):
   # path=serializers.FileField();
    class Meta:
        model = Media
        fields = [
            #"id",
            #'mtype',
            'path',
            #"description",
        ]
        def to_internal_value(self, data):
            if isinstance(data, dict) and 'path' in data:
                return super().to_internal_value(data)
            if hasattr(data, 'read'):
                return {'path':data}
            raise serializers.ValidationError(" Invalid Media data format ")

        def create(self, validated_data):
            request = self.context.get('request')
            cntx = self.context.get('cntx')
            source =""
            parentId =""
            if cntx is Case:
                source ="case"
                parentId = cntx.cid
            elif cntx is CaseHistory:
                source ="history"
                parentId = cntx.id
            elif cntx is Comment:
                source = "comment"
                parentId = cntx.cmtid
            mtype = magic.from_buffer(data.read(1024), mime=True)
            if 'image' in mtype.split('/'):
                mtype = "photo"
            elif 'video' in mtype.split('/'):
                mtype="video"
                #if mtype == document:
            elif 'application' in mtype.split('/'):
                mtype="document"
            else:
                logger.warning(f" Unrecognized file :{mtype}")
                raise serializers.ValidationError("Invalid file")
            media = Media.objects.create(
                    path = path,
                    mtype = mtype,
                    parentId = parentId,
                    source = source
                )
            return media

    def validate_path(self, data):
        logger.info("Entering validate_path")
        logger.debug(f"Validating media path: {data.name}")
        
        mime_type = magic.from_buffer(data.read(1024), mime=True)
        logger.info(f"Detected MIME type: {mime_type}")
        
        if mime_type not in settings.ALLOWED_FILE_TYPES:
            logger.warning(f"Invalid file type detected: {mime_type}")
            raise serializers.ValidationError("Invalid file.")
            
        data.seek(0)
        logger.info("Exiting validate_path")
        return data


class CaseHistorySerializer(serializers.ModelSerializer):
    user_details = cUserSerializer(source="user")
    #medias = MediaSerializer(many=True)
    distance = serializers.CharField()

    medias = MediaSerializer(many = True, required = False)

    class Meta:
        model = CaseHistory
        fields = [
            "id",
            "case",
            "cstate",
            "created",
            "description",
            "user_details",
            "medias",
            "lat",
            "long",
            "distance",
        ]

    def to_representation(self, instance):
        logger.info(f" Entering ") 
        data = super().to_representation(instance)
        request = self.context["request"]
        medias = Media.objects.filter(source="history", parentId=instance.id)
        data["medias"] = [
                {
                    "mtype": media.mtype,
                    "path": str(media.path) if media.path else None,
                    "url": request.build_absolute_uri(media.path.url) if media.path else None,
                }
                for media in medias
            ]
        logger.info(f" Executing: {data}") 
        return data


    """
    def get_medias(self, obj):
        medias = Media.objects.filter(source="history", parentId = obj.id)
        return [
                {
                    "mtype": media.mtype,
                    "path": media.path.url if media.path else None,
                }
                for media in medias
            ]

    """

class LostVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostVehicle
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    # history = CaseHistorySerializer(many=True)
    # media = MediaSerializer(many=True)

    case_type = serializers.SerializerMethodField()
    case_state = serializers.SerializerMethodField()
    # police_station = serializers.PrimaryKeyRelatedField(queryset=PoliceStation.objects.all())
    police_officer = PoliceOfficerSerializer(source="oid")
    comment_count = serializers.IntegerField()
    user_detail = cUserSerializer(source="user")
    like_count = serializers.IntegerField()
    liked = serializers.BooleanField(required=False, default=False)
    #medias = MediaSerializer(many=True)
    distance = serializers.CharField(
        required=False,
        default=None,
        read_only=True,
    )
    vehicle_detail = LostVehicleSerializer(
        source="lostvehicle", read_only=True, required=False
    )
    can_act = serializers.BooleanField(default=False)

    class Meta:
        model = Case
        fields = [
            "cid",
            "police_officer",
            "user_detail",
            "case_type",
           # "title",
            "case_state",
            "created",
            "lat",
            "long",
            "description",
            "follow",
            "comment_count",
            "like_count",
            "liked",
            "distance",
            #"medias",
            "vehicle_detail",
            "can_act",
            "drug_issue_type",
        ]

    def get_case_type(self, case):
        logger.info("Entering get_case_type")
        logger.debug(f"Getting case type for case: {case.cid}")
        result = dict(Case.cType)[case.type]
        logger.info(f"Case type: {result}")
        logger.info("Exiting get_case_type")
        return result

    def get_case_state(self, case):
        logger.info("Entering get_case_state")
        logger.debug(f"Getting case state for case: {case.cid}")
        result = dict(Case.cState)[case.cstate]
        logger.info(f"Case state: {result}")
        logger.info("Exiting get_case_state")
        return result

    # def get_comment_count(self, case):
    #     return case.comment_set.count()

    # def get_like_count(self, case):
    #     return case.likes.count()

    # def get_liked(self, case):

    #     user = self.context['request'].user

    #     if user.is_authenticated:
    #     # Check if the user has liked the case
    #         return case.likes.filter(user=user).exists()
    #     return False

class FileInfoSerializer(serializers.Serializer):
    #id = serializers.CharField()
    #name = serializers.CharField()
    #uri = serializers.CharField()
    #type = serializers.CharField(required=False)
    #size = serializers.IntegerField(required=False)
    file = serializers.FileField(required=False, write_only=True)

class CaseSerializerCreate(serializers.ModelSerializer):
    pid=serializers.PrimaryKeyRelatedField(
        queryset=PoliceStation.objects.all(), required=False
    )
    distance=serializers.CharField(read_only=True)
    ##docs=serializers.ListField(
    ##        child=serializers.CharField(allow_blank=True),
    ##        required=False, allow_empty=True, write_only=True)
    #docs = serializers.ListField(
    docs = serializers.ListField(
            child=FileInfoSerializer(),
            required=False,
            allow_empty=True
            )
    """medias = serializers.ListField(
            #child=FileInfoSerializer(),
            child = MediaSerializer(),
            #child=serializers.FileField(),
            required=False
            #allow_empty=True
            )"""
    medias = MediaSerializer(many = True, required = False)
    #medias = FileInforSerializer(many=True)'
    """medias = serializers.ListSerializer(
            child = MediaSerializer(many=True, required=False),
            required=False
            )"""


    regNumber=serializers.CharField(required=False, allow_blank=True, write_only=True)
    chasisNumber=serializers.CharField(required=False, allow_blank=True, write_only=True)
    engineNumber=serializers.CharField(required=False, allow_blank=True, write_only=True)
    make=serializers.CharField(required=False, allow_blank=True, write_only=True)
    model=serializers.CharField(required=False, allow_blank=True, write_only=True)
    color=serializers.CharField(required=False, allow_blank=True, write_only=True)
    vehicle_lost_type=serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Case
        fields = [
            "cid",
            "type",
            "lat",
            "long",
            "description",
            "follow",
            "pid",
            "distance",
            "drug_issue_type",
            # Get media
            "medias",
            #  Adding vehicle_detail",
            "docs",
            "regNumber",
            "chasisNumber",
            "engineNumber",
            "make",
            "model",
            "color",
            "vehicle_lost_type"            
        ]

    def create(self, validated_data):
        logger.info("Entering create")
        logger.debug(f"Creating case with data: {validated_data}")
        isDev = settings.DEVENV
     
        logger.info(" DEV ENVIROMENT: {}".format(settings.DEVENV))
        request = self.context["request"]
        drug_issue_type=validated_data.get("drug_issue_type","N/A")
        case = Case(
            type=validated_data["type"],
            drug_issue_type=drug_issue_type,
            lat=validated_data["lat"],
            long=validated_data["long"],
            description=validated_data["description"],
            follow=validated_data["follow"],
        )
        
        geo_location = fromstr(f"POINT({case.long} {case.lat})", srid=4326)
        user_distance = Distance("geo_location", geo_location)
        
        if validated_data.get("pid"):
            logger.info("Using provided police station")
            police_station = validated_data["pid"]
        else:
            logger.info("Finding nearest police station")
            police_station = (
                PoliceStation.objects.annotate(radius=user_distance)
                .order_by("radius")
                .first()
            )
            if not police_station:
                logger.error("No police station found within the radius")
                raise serializers.ValidationError(
                    {"pid": "No police station found within the radius."}
                )
            logger.debug(f"Selected police station: {police_station.pid}")
        
        case.pid = police_station
        case.geo_location = geo_location
        #officer = police_station.policeofficer_set.order_by("-rank").first()
        officer = PoliceOfficer.objects.filter(pid = police_station, report_on_this = True).order_by("-rank").first()
        if not officer:
            raise serializers.ValidationError(
                {"Error": f"No officer configured to receive complain in {police_station.name}  police station."}
            )
        logger.debug(f"Selected officer: {officer.oid}")     
        case.oid = officer
        case.user = request.user
        case.save()  # save this at the end

        from django.db import transaction

        with transaction.atomic():
            #caseId = case  # save this at the end
            #logger.info(f"Case saved with ID: {case.cid}")
            # Create the case history
            try:
                history = CaseHistory(
                    case=case,
                    cstate=case.cstate,
                    description="New Case created",
                    user=case.user,
                    lat=validated_data["lat"],
                    long=validated_data["long"],
                )
                history.save()  # Save the history object to the database
                logger.info(f"Initial Case history created with ID: {history.id}")
            except Exception as e:
                logger.error(f"Error creating case history: {str(e)}")
                raise serializers.ValidationError(
                    {"details": "Failed to create case history."}
                )

            #logger.info(f"Initial Case history created with ID: {history.id}")
            type = validated_data.get("type")
            if type == "vehicle":
                logger.info("Creating lost vehicle details")
                vehicle_detail_data = {
                    "regNumber": validated_data.get("regNumber"),
                    "chasisNumber": validated_data.get("chasisNumber"),
                    "engineNumber": validated_data.get("engineNumber"),
                    "make": validated_data.get("make"),
                    "model": validated_data.get("model"),
                    "color": validated_data.get("color"),
                    "vehicle_lost_type": validated_data.get("vehicle_lost_type"),
                }
                logger.info(" Vehicle details received :")
                #for key, value in vehicle_detail_data.items():
                    #logger.info(f"{key} : {value}")
               # if all(vehicle_detail_data.values()):
                if (validated_data.get("regNumber")) is not None:
                    #case.save()
                    #logger.info(f"Case saved with ID: {case.cid}")
                    #history.save()
                    #logger.info(f"Initial Case history created with ID: {history.id}")
                    try:                        
                        lv = LostVehicle.objects.create(caseId=case, **vehicle_detail_data)
                        logger.info(f" Lost vehicle case created with ID : {lv.id} ")
                    except Exception as e:
                        logger.error(f"Error creating lost vehicle case: {str(e)}")
                        history.delete()
                        case.delete()
                        raise serializers.ValidationError(
                            {"details": "Failed to create lost vehicle case."}
                        )
                else:
                    history.delete()
                    case.delete()
                    raise serializers.ValidationError(
                        {"details": "At least registration number required."}
                    )

        noti_title = f"New case No. {case.cid} of type {case.type} reported at {case.pid}"
        case.send_notification(noti_title, [case.oid.user_id])
        logger.debug(f"Sent app notification to officer :{case.oid.user.mobile}")
        #case.send_notification2(noti_title, [case.oid.user_id])
        #case.send_case_notifications()
        tm = datetime.now()
        d = tm.strftime("%d/%m/%Y")
        t = tm.strftime("%I:%M %p")
        send_new_case_sms(case.oid.user.mobile, case.cid, case.type, case.pid.name,d,t) 
        logger.debug(f"Sent sms notification to officer :{case.oid.user.mobile}")
        #send_sms(case.oid.user.mobile,noti_title)

        supervisor_officers = SuperintendingOfficer.objects.filter(did = case.oid.pid.did)
        supervisors = PoliceOfficer.objects.filter(oid__in=supervisor_officers.values_list("officer_id", flat=True)).values("user_id","user__mobile")
        supervisor_user_ids = [o["user_id"] for o in supervisors]
        if supervisor_user_ids:
            try:
                case.send_notification(noti_title,supervisor_user_ids)
                logger.debug(f"Sent app notification to supervisors : {supervisor_user_ids}")
            except Exception as e:
                logger.debug(f" Error for supervisor : {str(e)}")
        #msg = f"Your case No {case.cid} status is changed to {case.cstate}. For details, please visit Arunachal Crime Report app. From AP Crime Team"
        logger.debug(f"Trying to send sms notification to supervisors")
        for supervisor in supervisors:
            logger.debug(f"Sending sms to supervisor : {supervisor}")
            send_new_case_sms(supervisor["user__mobile"], case.cid, case.type, case.pid.name,d,t) 
            sup_mob = supervisor["user__mobile"]
            logger.debug(f" Sent sms notification to supervisor : {sup_mob}")

        logger.debug(f"Querying SNO users")
        sno_users = cUser.objects.filter(role="SNO")
        logger.debug(f"Trying SMS to SNO users")
        if case.type == "drug" and sno_users is not None:
            #msg = f"Your case No {case.cid} status is changed to {case.cstate}. For details, please visit Arunachal Crime Report app. From AP Crime Team"
            # TO DO: find correct user id for sending app notification
            #user_sno = cUser.objects.filter(id__in = sno_users.values_list("id", flat = True)).values("id","mobile")
            #logger.info(f" USER SNO found :{user_sno}")
            #user_ids = [o["id"] for o in user_sno]
            user_ids = sno_users.values_list("id",flat=True)
            if user_ids is not None:
                case.send_notification(noti_title, list(user_ids))
                logger.info(f" SENT APP NOTIFICATION to user ids : {user_ids}")
            for sno_user in sno_users:
                try:
                #send_update_sms(sno_user.mobile,msg)
                    logger.debug(f"Sent sms to SNO : {sno_user.mobile}")
                    send_new_case_sms(sno_user.mobile, case.cid, case.type, case.pid.name,d,t) 
                except Exception as e:
                    logger.debug(f" Error :{str(e)}")

        logger.info(f"Created case id: {case.cid} and exiting")
        return case


class CaseUpdateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    lat = serializers.CharField(max_length=10, required=False)
    long = serializers.CharField(max_length=10, required=False)
    medias = MediaSerializer(many=True, required=False)
    oid = serializers.CharField(required = False, allow_blank= True)
    pid = serializers.CharField(required = False, allow_blank= True)

    class Meta:
        model = Case
        fields = [
                "cid",
                "cstate",
                "oid",
                "pid",
                "description",
                "medias",
                "lat",
                "long",
            ]

    def validate(self, data):
        logger.info(f" Entering ") 
        state = data["cstate"]
        if state in {"assign",} and not data.get("oid"):
            raise serializers.ValidationError(
                {"oid": "You need to provide oid to assign this case to new officer."}
            )

        if state == "transfer" and not data.get("pid"):
            raise serializers.ValidationError(
                 {"pid": "You need to provide pid to transfer this case."}
            )

        lat = data.get("lat")
        long = data.get("long")
        if state == "visited" and not (lat or long):
            raise serializers.ValidationError(
                "lat and long is required for visited status."
            )
        return data

    def update(self, instance, validated_data):
        logger.debug(" Entering ")
        noti_title = {
            "accepted": "Your case No.{} has been accepted.",
            "rejected": "Your case no.{} has been rejected.",
            "info": "More info required for your case no.{}.",
            "inprogress": "Your case no.{} is in-progress.",
            "resolved": "Your case no.{} is resolved.",
            "visited": "Your case no.{} is visited.",
            "found": "Your case no.{} is found.",
        }
        

        user = self.context["request"].user
        cstate = validated_data["cstate"]
        logger.info(f" Updating Case Id :{instance.pk}, current state : {instance.cstate}, received state : {cstate}")
        instance.cstate = cstate
        orig_officer = instance.oid
        lat = validated_data.get("lat")
        long = validated_data.get("long")
        if lat is not None and long is not None:
            try:
                case_point = Point(float(instance.long), float(instance.lat), srid=4326)
                user_point = Point(float(long), float(lat), srid=4326)
                case_point_m = case_point.transform(3857, clone=True)
                user_point_m = user_point.transform(3857, clone=True)
                distance = user_point_m.distance(case_point_m)/1000 #in km
                instance.distance = round(distance,2)
            except Exception as e:
                logger.error(f" Error calculation geo distance :{str(e)}")

        instance.updated = timezone.now()
        instance.oid = user.policeofficer_set.first()
        description = validated_data.pop("description", "")
        medias = validated_data.pop("medias", [])
        if instance.type == "vehicle" and cstate == "found":
            ofr = PoliceOfficer.objects.filter(user = user,report_on_this=True).first()
            if ofr is not None:
                instance.oid = ofr
                instance.pid = ofr.pid

        if cstate == "transfer":
            offcr = PoliceOfficer.objects.get(user = user)
            if not offcr or offcr.rank not in ("5",):
                logger.info(f" Transfer error. Only inspector can transfer the case ")
                raise serializers.ValidationError(
                        {"details": "Only Police Officer of Inspector Rank can transfer the case"}
                    )
            logger.info(f" Case transering ")
            pid = validated_data.pop("pid",None)
            if pid:
                officer = PoliceOfficer.objects.filter(pid=pid, report_on_this=True).first()
                if not officer:
                    raise serializers.ValidationError(
                            {"details" :"Officers not available in destination police staiton "}
                        )
                pid = PoliceStation.objects.filter(pid = pid).first()
                if pid is None:
                    logger.info(f"Case transferred to {pid.name} police station ")
                    raise serializers.ValidationError(
                            {"details": "Only Police station not found "}
                        )
                    #return None

                opid = instance.pid
                instance.pid = pid
                logger.info(f"Case transferred to {pid.name} police station ")
                instance.oid = officer
                instance.cstate = "pending"
                instance.save()
                #supervisor_officers = SuperintendingOfficer.objects.filter(did = case.oid.pid.did)
                #supervisors = PoliceOfficer.objects.filter(oid__in=supervisor_officers.values_list("officer_id", flat=True)).values("user_id","user__mobile")
                #supervisor_user_ids = [o["user_id"] for o in supervisors]
                noti_title = f"New case No. {instance.cid} of type {instance.type} transferred into {instance.pid.name} from {opid.name}"
                #user_ids= cUser.objects.filter(id__in = instance.oid.user.id).values_list("id",flat=True)
                #user_ids = sno_users.values_list("id",flat=True)
                instance.send_notification(noti_title, [instance.oid.user.id])
                logger.info(f" Sent app notification to new police officer id: {instance.oid.user.id}") 
                
                noti_title = f"Your case No. {instance.cid} of type {instance.type} staransfered to {instance.pid.name}"
                instance.send_notification(noti_title, [instance.user_id])
                logger.info(f" Sent app notification to complainant user: {instance.user}") 
                #message = "Your case No {instance.cid} status is changed to {instance.cstate}"
                #send_update_sms(instance.oid.user.mobile,message)
                tm = datetime.now()
                d = tm.strftime("%d/%m/%Y")
                t = tm.strftime("%I:%M %p")
                send_new_case_sms(instance.oid.user.mobile, instance.cid, instance.type, instance.pid.name,d,t) 
                #send_case_status_sms(instance.oid.user.mobile, instance.cid, instance.cstate)
            else:
                raise serializers.ValidationError(
                        {" Police station not available "}
                    )

        elif cstate == "assign":
            oid = validated_data.get("oid")
            logger.info(f"OID received is : {oid}")
            if oid is None:
                logger.info(f"officer id not received")
                raise serializers.ValidationError(
                        {"details":" police officer not found"}
                    )
            try:
                noid = PoliceOfficer.objects.get(oid = oid)
            except Exception as e:
                logger.info(f" Assign error :{str(e)}")
                raise serializers.ValidationError(
                        {"details":" police officer not found"}
                    )
            logger.info(f"Assin to from {instance.oid.user.mobile} to {noid.user.mobile} and Changing state from : {instance.cstate} to Pending")
            #oi = PoliceOfficer.objects.get(oid = validated_data["oid"])
            #instance.oid = validated_data["oid"]
            if instance.oid == noid:
                raise serializers.ValidationError(
                        {"details":"You are assigning to yourself"}
                    )

            logger.info(f" Case assigned to new officer : {noid} ")
            instance.oid = noid
            instance.cstate = "pending"
            instance.save()
            noti_title = f"You are assigned a new case no.{instance.cid}"
            #user_ids= cUser.objects.filter(user = instance.oid.user).values_list("id",flat=True)
                #user_ids = sno_users.values_list("id",flat=True)
            instance.send_notification(noti_title, [instance.oid.user_id])
            logger.info(f" Sent app notification to new police officer id: {instance.oid.user_id}") 
            #instance.send_notification(noti_title, [instance.oid.user_id])
            tm = datetime.now()
            d = tm.strftime("%d/%m/%Y")
            t = tm.strftime("%I:%M %p")
            send_new_case_sms(instance.oid.user.mobile, instance.cid, instance.type, instance.pid.name,d,t) 
            #Notify case owner
            noti_title = f"Your case no.{instance.cid} asigned to officer"
            instance.send_notification(noti_title, [instance.user_id])
            send_case_status_sms(instance.user.mobile, instance.cid, instance.cstate)
        else:
            instance.save()
            message = f"Case no. {instance.cid} status changed to {instance.cstate}"
            supervisors = PoliceOfficer.objects.filter(
                Q(pid__did=instance.oid.pid.did, rank=9)
                #| Q(oid__in=instance.oid.poiceOfficer.values("officer_id"))
            ).values("user_id", "user__mobile")
            # commenting :serbang
            #instance.send_notitication(message, [o["user_id"] for o in supervisors])

            logger.info(f" Sending notifications to : {instance.user_id}") 
            #user_ids= cUser.objects.filter(user = instance.user).values_list("id",flat=True)
                #user_ids = sno_users.values_list("id",flat=True)
            #instance.send_notification(noti_title, user_ids)
            #user_ids = instance.user.values_list("id",flat=True)
            instance.send_notification(message, [instance.user_id])
            #instance.send_notification(message, list(user_ids))
            logger.info(f" Sent app notification to new police officer id: {instance.user_id}") 
            #message = "Your case No {instance.cid} status is changed to {instance.cstate}"
            #message = f"Your case No {instance.cid} status is changed to {instance.cstate}. For details, please visit Arunachal Crime Report app. From AP Crime Team"
            #send_update_sms(instance.user.mobile,message)
            #send_case_status_sms(instance.oid.user.mobile, instance.cid, instance.cstate)
            send_case_status_sms(instance.user.mobile, instance.cid, instance.cstate)
            logger.info(f" Sent sms to case complainant : {instance.user.mobile}") 
        if instance.type == "vehicle" and instance.cstate == "found":
            lv = LostVehicle.objects.filter(caseId = instance.cid).first()
            if lv is not None:
                send_vehicle_found_sms(instance.user.mobile, lv.regNumber, instance.pid.name)
                message =f"Vehicle Regd.No.{lv.regNumber} found at {instance.pid.name}"
                send_vehicle_found_sms(orig_officer.user.mobile, lv.regNumber, instance.pid.name)
                #user_ids = orig_officer.user.values_list("id",flat=True)
                #instance.send_notification(message, [instance.user_id])
                #instance.send_notification(message, list(user_ids))
                instance.send_notification(message, [orig_officer.user.id])
            #send_sms(instance.user.mobile,noti_title)
                logger.info(f"Sent app notifications to original police officer ") 
        
        supervisor_officers = SuperintendingOfficer.objects.filter(did = instance.oid.pid.did)
        supervisors = PoliceOfficer.objects.filter(oid__in=supervisor_officers.values_list("officer_id", flat=True)).values("user_id","user__mobile")
        supervisor_user_ids = [o["user_id"] for o in supervisors]
        if supervisor_user_ids:
            try:
                case.send_notification(noti_title,supervisor_user_ids)
                logger.debug(f"Sent app notification to supervisors : {supervisor_user_ids}")
            except Exception as e:
                logger.debug(f" Error for supervisor : {str(e)}")
        msg = f"Your case No {instance.cid} status is changed to {instance.cstate}. For details, please visit Arunachal Crime Report app. From AP Crime Team"
        for supervisor in supervisors:
            #send_new_case_sms(supervisor["user__mobile"], case.cid, case.type, case.pid.name,d,t) 
            send_case_status_sms(supervisor["user__mobile"], instance.cid, instance.cstate)
            logger.debug(f" Sent sms notification to supervisor : {supervisor.user.mobile}")

        return instance


class CaseUpdateByReporterSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, required=False)
    class Meta:
        model = Case
        fields = [
            "description",
            "medias",
        ]

    def update(self, instance, validated_data):
        logger.info(f" Entering update of CaseUpdateByReporterSerialzier ") 
        medias = validated_data.pop("medias", [])
        user = self.context["request"].user
        instance.updated = timezone.now()
        instance.cstate = "pending"
        instance.description = validated_data["description"]
        instance.save()
        instance.add_history_and_media(description="", user=user, medias=medias)
        noti_title = f"Additional information provided for your case no.{instance.pk}"
        instance.send_notitication(noti_title, [instance.oid.user_id])
        send_case_status_sms(instance.user.mobile, instance.cid, instance.cstate)
        #send_case_status_sms(instance.oid.user.mobile, instance.cid, instance.cstate)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user_detail = cUserSerializer(source="user", read_only=True)
    medias = MediaSerializer(many = True, required = False)

    class Meta:
        model = Comment
        fields = ["cmtid", "content", "cid", "user_detail", "created", "medias"]

    def to_representation(self, instance):
        logger.info(f" Entering ") 
        data = super().to_representation(instance)
        request = self.context["request"]
        """data["medias"] = MediaSerializer(
            instance.medias.all(), context={"request": request}, many=True
        ).data"""
        medias = Media.objects.filter(source="comment", parentId=instance.cmtid)
        data["medias"] = [
                {
                    "mtype": media.mtype,
                    "path": request.build_absolute_uri(media.path.url) if media.path else None,
                }
                for media in medias
            ]
        logger.info(f" Executing: {data}") 
        return data
    """def get_medias(self, obj):
        medias = Media.objects.filters(source="comment", parentId =obj.cmtid)
        return [
                {
                    "mtype": media.mtype,
                    "path": media.path.url if media.path else None,
                }
                for media in medias
            ]"""



class EmergencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyType
        fields = "__all__"


class EmergencySerializer(serializers.ModelSerializer):
    emergeny_type = EmergencyTypeSerializer(source="tid")
    distance = serializers.FloatField(
        required=False, read_only=True, source="distance.km"
    )

    class Meta:
        model = Emergency
        fields = [
            "emid",
            "emergeny_type",
            "name",
            "number",
            "lat",
            "long",
            "address",
            "distance",
        ]

        def get_distance(self, obj):
            if hasattr(obj,"distance") and obj.distance is not None:
                return obj.distance.km
            return None


class InformationSerializer(serializers.ModelSerializer):
    information_type = serializers.ChoiceField(choices=Information.Itype, required=True)

    class Meta:
        model = Information
        fields = ["inid", "information_type", "heading", "content"]

    # def get_information_type(self, information):
    #     return dict(Information.Itype)[information.information_type]


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=16)

    class Meta:
        model = User
        fields = ["id", "mobile"]

    def validate(self, data):
        if user := cUser.objects.filter(mobile=data["mobile"]).first():
            if user.is_verified:
                raise serializers.ValidationError(
                    {
                        "mobile": "This mobile is already registered",
                        "is_verified": True,
                    }
                )
            else:
                raise serializers.ValidationError(
                    {
                        "mobile": "This mobile is already registered.",
                        "is_verified": False,
                    }
                )
        return data


class UserProfileSerializer(PasswordDecriptionMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, max_length=1000)
    # profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = cUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile",
            "email",
            "address",
            "profile_picture",
            "aadhar_card_no",
            "password",
            "role",
        ]
        read_only_fields = ["role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mobile"].required = False

    def update(self, instance, data):
        password = data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, data)

    def get_profile_picture(self, user):
        request = self.context.get("request")
        if user.profile_picture:
            # Assuming MEDIA_URL is set in your Django settings
            # Make sure to import settings at the beginning of the file: from django.conf import settings
            return request.build_absolute_uri(user.profile_picture.url)
        else:
            return None


class LoginSerializer(PasswordDecriptionMixin, serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        super().validate(attrs)
        mobile = attrs.get("mobile")
        password = attrs.get("password")

        if mobile and password:
            user = authenticate(
                username=mobile, password=password, request=self.context["request"]
            )

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError(
                    "Unable to log in with the provided credentials."
                )
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs["user"] = user
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data["mobile"]
        otp_code = data["otp_code"]

        user = cUser.objects.filter(mobile=mobile).first()
        if user:
            if not UserOTPBaseKey.validate_otp(user, otp_code):
                raise serializers.ValidationError(
                    {"otp_code": "Invalid or expired otp code."}
                )
        else:
            raise serializers.ValidationError({"mobile": "Invalid mobile"})
        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        user.is_verified = True
        user.save()
        #token,_ = Token.objects.filter(user=user).first()
        token = RefreshToken.for_user(user)
        return {
            "message": "Otp verification successful.",
            "user_id": user.id,
            "mobile": user.mobile,
            "token": str(token.access_token),
            "refresh":str(token),
        }


class ResendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)

    def validate(self, data):
        mobile = data["mobile"]
        user, _ = cUser.objects.get_or_create(mobile=mobile)
        if user.is_verified:
            raise serializers.ValidationError({"mobile": "Mobile already verified"})
        try:
            UserOTPBaseKey.send_otp_verification_code(user)
        except:
            raise serializers.ValidationError({"mobile": "Too many attempts"})
        return data


class CheckLostVehicleSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    registration_no = serializers.CharField(required=False)

    def validate(self, data):
        logger.info(f" Entering validate with data :{data}")
        image = data.get("image")
        registration_no = data.get("registration_no")
        if not (image or registration_no):
            raise serializers.ValidationError(
                "Provide either image and/or registration no."
            )
        return data

    def check_vehicle(self, request):
        logger.info(f"Entering check_vehicle with request :{request}")
        image = self.validated_data.get("image", None)
        registration_no = self.validated_data.get("registration_no", None)
        response = []

        is_police = request.user.is_authenticated and request.user.is_police
        found_vechicles = detectVehicleNumber(
            image, registration_no, is_police, request.user
        )
        logger.info(f" Found_vehicle record : {found_vechicles}")
        if found_vechicles:
            case_serializer = CaseSerializer(found_vechicles, many=True)
            response = case_serializer.data
            if not (request.user.is_authenticated and request.user.is_police):
                for item in response:
                    item["vehicle_detail"]["chasisNumber"] = "*******"
                    item["vehicle_detail"]["engineNumber"] = "*******"
        for item in response:
            cid = item.get("cid")
            if cid:
                medias = Media.objects.filter(source = "case", parentId=cid)
                logger.info(f" Appending medias for check_vehicle with response :{medias}")
                request = self.context.get("request")
                item["medias"] = [
                        {
                            "mtype":media.mtype,
                            "path": str(media.path) if media.path else None,
                            "url": request.build_absolute_uri(media.path.url) if media.path and request else None,
                        }
                        for media in medias
                    ]
        logger.info(f"Exiting check_vehicle with response :{response}")
        return response


class VictimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Victim
        fields = "__all__"


class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Privacy
        fields = "__all__"


class TermsConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsCondition
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class CriminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criminal
        fields = "__all__"


class PasswordChangeSerializer(PasswordDecriptionMixin, serializers.Serializer):
    old_password = serializers.CharField()
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()

    def validate(self, data):
        super().validate(data)
        user = self.context["request"].user
        if not user.check_password(data.get("old_password")):
            raise serializers.ValidationError(
                {"old_password": "Your current password is incorrect."}
            )
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Password did not match."}
            )
        try:
            validate_password(password=data["new_password1"], user=user)
        except Exception as e:
            raise serializers.ValidationError({"password": e.messages})
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user


class CommentCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)

    user = serializers.PrimaryKeyRelatedField(
        queryset=cUser.objects.all(), write_only=True
    )
    medias = MediaSerializer(many=True, required= False)

    class Meta:
        model = Comment
        fields = ["cid", "user", "content", "medias"]

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        comment = Comment(
            cid=validated_data["cid"],
            user=validated_data["user"],
            content=validated_data["content"],
        )
        comment.save()
        if validated_data["medias"]:
            comment.medias.add(validated_data["medias"])
        return comment


class PasswordResetOtpSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=16)

    def save(self):
        mobile = self.validated_data["mobile"]
        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            pass
        else:
            try:
                UserOTPBaseKey.send_otp_verification_code(user, verification=False)
            except:
                raise serializers.ValidationError({"mobile": "Too many attempts"})


class PasswordResetSerializer(PasswordDecriptionMixin, serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    mobile = serializers.CharField(max_length=16)
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()

    def validate(self, data):
        super().validate(data)
        mobile = data["mobile"]
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Password did not match."}
            )

        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            raise serializers.ValidationError({"mobile": "Mobile not registered."})
        else:
            try:
                validate_password(password=data["new_password1"], user=user)
            except Exception as e:
                raise serializers.ValidationError({"password": e.messages})

            if UserOTPBaseKey.validate_otp(user=user, otp=data["otp"]):
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    {"otp": "Otp is wrong or has expired."}
                )
        return data

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user


class LikeSerializer(serializers.Serializer):
    case_id = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=cUser.objects.all())
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Like.objects.create(**validated_data)

    def list(self, queryset):
        return queryset

    def retrieve(self, instance):
        return instance

    def delete(self, instance):
        instance.delete()


class LikeCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["case", "user"]


class LikeListSerializer(serializers.ModelSerializer):
    user = cUserSerializer()

    class Meta:
        model = Like
        fields = ["case", "user", "created"]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class EmergencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyType
        fields = "__all__"
        
class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Privacy
        fields = ['id', 'content']

class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsCondition
        fields = ['id', 'content']

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutPage
        fields = ['id', 'content']  