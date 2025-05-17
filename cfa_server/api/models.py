import imghdr
import re
import logging
from django.contrib.gis.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.contrib.gis.geos import Point
from geopy import distance
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.geos import fromstr
from api.utl import get_upload_path
from api.forms import detect_malicious_patterns_in_media
from api.otp import send_sms
from .managers import CustomUserManager
from firebase_admin import messaging
from fcm_django.models import FCMDevice
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import magic
from pyotp import TOTP, random_base32
from firebase_admin.exceptions import InvalidArgumentError
from django.core.validators import RegexValidator

# Initialize logger
logger = logging.getLogger(__name__)


def mobile_validator(value):
    logger.info("Entering mobile_validator")
    pattern = re.compile(r"^[6-9]\d{9}$")
    message = "Enter a valid mobile number."

    logger.info(f"Validating mobile number: {value}")
    if value == "9999999999":
        logger.warning("Invalid mobile number: 9999999999 is not allowed")
        raise ValidationError(message)
    if not pattern.match(value):
        logger.warning(f"Invalid mobile number pattern: {value}")
        raise ValidationError(message)

    logger.info("Exiting mobile_validator - validation successful")
    return


MobileValidator = mobile_validator


def file_type_validator(f):
    logger.info("Entering file_type_validator")
    logger.info(f"Validating file: {f.name}")

    f.seek(0)
    mime_type = magic.from_buffer(f.read(), mime=True)
    logger.info(f"Detected MIME type: {mime_type}")

    if mime_type not in settings.ALLOWED_FILE_TYPES:
        logger.warning(f"Invalid file type: {mime_type} for file {f.name}")
        raise ValidationError(f"You can't upload this file: {f.name}.")
    f.seek(0)

    logger.info("Exiting file_type_validator - validation successful")
    return


class District(models.Model):
    did = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        logger.info("Entering District.__str__")
        logger.info(f"District name: {self.name}")
        logger.info("Exiting District.__str__")
        return self.name


class cUser(AbstractUser):
    username = None
    ROLES = (
        ("user", "User"),
        ("police", "Police"),
        ("admin", "Admin"),
    )
    # mobile = models.CharField(max_length=26, unique=True, validators=[MobileValidator])
    mobile = models.CharField(max_length=26, unique=True, validators=[MobileValidator])
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLES, default="user")
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(blank=True, null=True)
    aadhar_card_no = models.CharField(max_length=56, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "mobile"

    objects = CustomUserManager()

    @property
    def is_police(self):
        return self.role == "police"

    @property
    def is_user(self):
        return self.role == "user"

    @property
    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        return self.mobile


class PoliceStation(models.Model):
    pid = models.BigAutoField(primary_key=True)
    did = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.TextField()
    address = models.TextField(null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    long = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    geo_location = models.PointField(blank=True, null=True, srid=4326)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        try:
            self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
            super().save(**kwargs)
            logger.info(
                f"Saved police station {self.pid} at location {self.lat}, {self.long}"
            )
        except Exception as e:
            logger.critical(
                f"Failed to save police station - ID: {self.pid}, Error: {str(e)}"
            )
            raise


class PoliceStationContact(models.Model):
    ps_cid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    contactName = models.CharField(max_length=50, null=True)
    number = models.CharField(max_length=15)


class PoliceOfficer(models.Model):
    RANKS = (
        ("1", "Constable"),
        ("2", "Head Constable"),
        ("3", "ASI"),
        ("4", "SI"),
        ("5", "Inspector"),
        ("6", "DySP"),
        ("7", "ASP"),
        ("9", "SP"),
        ("10", "SSP"),
        ("11", "DIGP"),
        ("12", "IGP"),
        ("13", "ADG"),
        ("14", "DGP"),
    )
    oState = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    oid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation, on_delete=models.DO_NOTHING)
    rank = models.CharField(max_length=10, choices=RANKS, default="Inspector")
    entryDate = models.DateField(auto_now=True)
    status = models.CharField(max_length=10, choices=oState, default="active")
    mobile = models.CharField(max_length=55, null=True)
    report_on_this = models.BooleanField(default=False)


class PoliceStationSupervisor(models.Model):
    officer = models.ForeignKey(
        PoliceOfficer, on_delete=models.CASCADE, related_name="policestation_supervisor"
    )
    station = models.ForeignKey(
        PoliceStation, on_delete=models.CASCADE, related_name="policestation_supervisor"
    )

    class Meta:
        unique_together = ["officer", "station"]


class Case(models.Model):
    cType = (
        ("drug", "Drug"),
        ("vehicle", "Vehicle"),
        ("extortion", "Extortion"),
    )
    cState = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("found", "Found"),
        ("assign", "Assign"),
        ("visited", "Visited"),
        ("inprogress", "Inprogress"),
        ("transfer", "Transfer"),
        ("resolved", "Resolved"),
        ("info", "Info"),
        ("rejected", "Rejected"),
    )
    DRUG_ISSUE_TYPE = (
        ("drug_peddling", "Drug Peddling"),
        ("drug_consumption", "Drug Consumption"),
        ("drug_cultivation", "Drug Cultivation"),
        ("needs_counselling", "Needs Counselling"),
        ("needs_rehabilitation", "Needs Rehabilitation"),
    )

    cid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    oid = models.ForeignKey(
        PoliceOfficer, on_delete=models.SET_NULL, null=True, blank=True
    )
    type = models.CharField(max_length=10, choices=cType, default="drug")
    #title = models.CharField(max_length=250, null=True)
    cstate = models.CharField(max_length=15, choices=cState, default="pending")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)
    distance = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True
    )
    description = models.TextField(null=True)
    follow = models.BooleanField(default=False)
    #medias = models.ManyToManyField("Media", related_name="cases", blank=True)
    drug_issue_type = models.CharField(
        max_length=20, choices=DRUG_ISSUE_TYPE, blank=True, default=""
    )
    #This function is used in ase update method to update the case status and send notification to the user
    def add_history_and_media(self, description, medias, user, cstate=None, **kwargs):
        flag = None
        try:
            cstate = cstate or self.cstate
            logger.info(f"Adding history for case {self.cid} with state {cstate}")

            history = CaseHistory.objects.create(
                case=self,
                user=user,
                description=description,
                cstate=cstate,
                lat=kwargs.get("lat") if cstate == "visited" else None,
                long=kwargs.get("long") if cstate == "visited" else None,
            )

            if medias:
                for media in medias:
                    if detect_malicious_patterns_in_media(media['uri']):
                        logger.critical(
                            f"SECURITY ALERT: Malicious media detected in case {self.cid}, file: {media['uri']}"
                        )
                        raise ValidationError("Malicious media file detected.")
                    mtype = media.type
                    if 'image' in mtype.split('/'):
                        mtype="photo"
                    #if mtype == "video":
                    if 'video' in mtype.split('/'):
                        mtype="video"
                    #if mtype == "document":
                    if 'application' in mtype.split('/'):
                        mtype="document"

                    md=Media.objects.create(
                            source="history",
                            parentId=history.id,
                            mtype=mtype,
                            path=media['uri'],
                        )
                try:
                    #history.medias.add(*medias)
                    flag = True
                except Exception as e:
                    logger.error(f"Failed to add medias to case history {history.id}: {str(e)}")
                    # Delete all medias added to the history so far
                   # history.medias.clear()
                    raise
                logger.info(
                    f"Added {len(medias)} media files to case history {history.id}"
                )

        except Exception as e:
            logger.critical(f"Failed to add history to case {self.cid}: {str(e)}")
            raise
        return flag

    def save(self, *args, **kwargs):
        try:
            if self.pid:
                if not self.geo_location:
                    self.geo_location = fromstr(
                        f"POINT({self.long} {self.lat})", srid=4326
                    )

                point_one = (self.geo_location.y, self.geo_location.x)
                point_two = (self.pid.geo_location.y, self.pid.geo_location.x)
                self.distance = distance.great_circle(point_one, point_two).km
                logger.debug(
                    f"Calculated distance for case {self.cid}: {self.distance} km"
                )
            """ # Saving media is being handled in CaseCreateView and CaseUpdateView save/update methods
            if not self.pk:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                    logger.info(f"Created new case {self.cid} of type {self.type}")

                    CaseHistory.objects.create(
                        case=self,
                        user=self.user,
                        cstate=self.cstate,
                        description="Case created.",
                    )
                    logger.debug(f"Created initial history record for case {self.cid}")

                    try:
                        self._send_case_notifications()
                    except Exception as e:
                        logger.error(
                            f"Error sending notifications for case {self.cid}: {str(e)}",
                            exc_info=True,
                        )
                return self.cid # Return the case ID after saving
            """

            super().save(*args, **kwargs)
            return self.cid # Return the case ID after saving

        except Exception as e:
            logger.critical(
                f"Error saving case {getattr(self, 'cid', 'new')}: {str(e)}",
                exc_info=True,
            )
            #raise # Uncomment this line to raise the error again after logging
            return None # Return None if an error occurs. This is used for removing case object if antying wrong happens

    def _send_case_notifications(self):
        logger.info(f"Beginning notification process for case {self.cid}")
        desc = f"New case no.{self.cid} of type {self.type} reported at {self.pid}."
        data = {
            "case_id": str(self.cid),
            "description": desc,
            "type": self.type,
            "state": self.cstate,
            "created": str(self.created),
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
        }
        logger.debug(f"Notification data prepared: {data}")

        if self.oid_id:
            self._notify_assigned_officer(desc, data)
        else:
            self._notify_station_officers(desc, data)

    def _notify_assigned_officer(self, desc, data):
        logger.info(f"Notifying assigned officer for case {self.cid}")
        try:
            devices = FCMDevice.objects.filter(user_id=self.oid.user_id)
            registration_tokens = list(
                devices.values_list("registration_id", flat=True)
            )

            if not registration_tokens:
                logger.warning(f"No FCM devices found for officer {self.oid.user_id}")
                return

            for token in registration_tokens:
                try:
                    messaging.send(
                        messaging.Message(
                            notification=messaging.Notification(
                                title=f"New Case : {self.type}", body=desc
                            ),
                            data=data,
                            token=token,
                        )
                    )
                    logger.info(
                        f"Successfully sent notification to token {token[:10]}..."
                    )
                except Exception as e:
                    logger.error(f"Failed to send to token {token[:10]}...: {str(e)}")

            if self.oid.mobile:
                send_sms(self.oid.mobile, desc)
                logger.info(f"SMS sent to officer {self.oid.mobile}")

        except Exception as e:
            logger.critical(
                f"Critical failure in officer notification system: {str(e)}"
            )
            raise

    def _notify_station_officers(self, desc, data):
        logger.info(f"Notify relevant officers at the police station")
        try:
            officers = self.pid.policeofficer_set.filter(
                Q(report_on_this=True) | Q(rank="5")
            ).values("user_id", "user__mobile")

            user_ids = [o["user_id"] for o in officers]
            devices = FCMDevice.objects.filter(user_id__in=user_ids)
            registration_tokens = list(
                devices.values_list("registration_id", flat=True)
            )

            if registration_tokens:
                notification = messaging.Notification(
                    title=f"New Case: {self.type}", body=desc
                )
                logger.info(f" Notification: {notification}")
                response = messaging.send_multicast(
                    messaging.MulticastMessage(
                        notification=notification, data=data, tokens=registration_tokens
                    )
                )
                logger.info(
                    f"Sent FCM to {len(registration_tokens)} officers. "
                    f"Success: {response.success_count}, Failures: {response.failure_count}"
                )

            for officer in officers:
                if officer["user__mobile"]:
                    send_sms(officer["user__mobile"], desc)
                    logger.info(f"SMS sent to officer {officer['user__mobile']}")

        except Exception as e:
            logger.error(f"Error notifying station officers: {str(e)}", exc_info=True)

    def send_notification(self, title, user_ids: list):
        logger.debug("Send notification to specific users")
        try:
            desc = self.description or "New update on your case"
            data = {
                "case_id": str(self.cid),
                "description": desc,
                "type": self.type,
                "state": self.cstate,
                "created": str(self.created),
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
            }

            devices = FCMDevice.objects.filter(user_id__in=user_ids)
            registration_tokens = list(
                devices.values_list("registration_id", flat=True)
            )

            if registration_tokens:
                notification = messaging.Notification(title=title, body=desc)
                response = messaging.send_multicast(
                    messaging.MulticastMessage(
                        notification=notification, data=data, tokens=registration_tokens
                    )
                )
                logger.info(
                    f"Sent notification to {len(user_ids)} users for case {self.cid}. "
                    f"Success: {response.success_count}, Failures: {response.failure_count}"
                )
                return True

            logger.warning(f"No devices found for users {user_ids}")
            return False

        except Exception as e:
            logger.error(
                f"Error sending notification for case {self.cid}: {str(e)}",
                exc_info=True,
            )
            return False




#This model stores the media files uploaded by the user. It can be a video, photo, audio or document.
class Media(models.Model):
    Mtype = (
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    sourceType = (
            ("case","case"),
            ("history","history"),
            ("comment","comment"),
            )
    #mid = models.BigAutoField(primary_key=True)
    source = models.CharField(max_length=10, choices=sourceType, default="case")
    #parentId = models.CharField(max_length=10,blank=True,null=True)
    parentId = models.BigIntegerField(blank=True,null=True)
    mtype = models.CharField(max_length=10, choices=Mtype, default="photo")
    path = models.FileField(upload_to=get_upload_path, validators=[file_type_validator])
    created = models.DateTimeField(auto_now_add=True)
    #description = models.TextField(null=True)
    def save(self, **kwargs):
        try:
            super().save(**kwargs)
            logger.info(f"Saved media file of type {self.mtype}")
            return self.id  # Return the media ID after saving
        except Exception as e:
            logger.error(f"Error saving media file: {str(e)}", exc_info=True)
            raise   
        return None  # Return None if an error occurs 




class CaseHistory(models.Model): 
    case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    cstate = models.CharField(max_length=15, choices=Case.cState)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    long = models.CharField(max_length=10, blank=True, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)
    ##medias = models.ManyToManyField(Media, related_name="case_histories", blank=True)

    def distance(self):
        if self.case.geo_location and self.geo_location:
            return self.geo_location.distance(self.case.geo_location)
        return None

    def save(self, **kwargs):
        try:
            if self.lat and self.long:
                self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
            super().save(**kwargs)
            logger.debug(f"Saved case history for case {self.case_id}")
            return self.id  # Return the case history ID after saving
        except Exception as e:
            logger.error(f"Error saving case history: {str(e)}", exc_info=True)
            raise
        return None  # Return None if an error occurs


class LostVehicle(models.Model):
    type = (
        ("stolen", "Stolen"),
        ("abandoned", "Abandoned"),
    )
    #lvId = models.BigAutoField(primary_key=True)    
    caseId = models.OneToOneField(Case, on_delete=models.CASCADE, null=True)
    regNumber = models.CharField(max_length=30)
    chasisNumber = models.CharField(max_length=50, null=True, default="N/A")
    engineNumber = models.CharField(max_length=50, null=True, default="N/A")
    make = models.CharField(max_length=50, null=True, default="N/A")
    model = models.CharField(max_length=50, null=True, default="N/A")
    description = models.CharField(max_length=500, null=True, default="N/A")
    color = models.CharField(max_length=56, blank=True, default="")
    vehicle_lost_type = models.CharField(max_length=10, choices=type, null=False, default="stolen")
    def save(self, **kwargs):
        try:
            super().save(**kwargs)
            logger.info(f"Saved lost vehicle {self.id} with reg number {self.regNumber}")
            return self.id  # Return the lost vehicle ID after saving
        except Exception as e:
            logger.error(f"Error saving lost vehicle: {str(e)}", exc_info=True)
            raise
        return None  # Return None if an error occurs


class Comment(models.Model):
    cmtid = models.BigAutoField(primary_key=True)
    cid = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey(cUser, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    medias = models.ManyToManyField(Media, related_name="comments", blank=True)


class EmergencyType(models.Model):
    emtid = models.BigAutoField(primary_key=True)
    service_type = models.CharField(max_length=30, blank=False)

    def __str__(self):
        logger.info("Entering EmergencyType.__str__")
        logger.info(f"Service type: {self.service_type}")
        logger.info("Exiting EmergencyType.__str__")
        return self.service_type


class Emergency(models.Model):
    emid = models.BigAutoField(primary_key=True)
    tid = models.ForeignKey(EmergencyType, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, default="N/A")
    number = models.CharField(max_length=100, null=True)
    address = models.TextField(null=True, blank=True)  # New field for address
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=False, blank=False
    )  # Mandatory
    long = models.DecimalField(
        max_digits=9, decimal_places=6, null=False, blank=False
    )  # Mandatory

    def save(self, *args, **kwargs):
        logger.info("Entering Emergency.save")
        logger.info(
            f"Saving Emergency - Name: {self.name}, Lat: {self.lat}, Long: {self.long}"
        )

        if self.lat is not None:
            original_lat = self.lat
            self.lat = float(str(self.lat)[:9])
            logger.info(f"Truncated latitude from {original_lat} to {self.lat}")

        if self.long is not None:
            original_long = self.long
            self.long = float(str(self.long)[:9])
            logger.info(f"Truncated longitude from {original_long} to {self.long}")

        super().save(*args, **kwargs)
        logger.info("Exiting Emergency.save")

    def __str__(self):
        logger.info("Entering Emergency.__str__")
        result = f"{self.name} - {self.tid.service_type if self.tid else 'No Type'}"
        logger.info(f"Emergency string representation: {result}")
        logger.info("Exiting Emergency.__str__")
        return result


class Information(models.Model):
    inid = models.BigAutoField(primary_key=True)
    Itype = (
        ("drug", "Drug"),
        ("extortion", "Extortion"),
        ("Vehicle", "Vehicle"),
    )
    information_type = models.CharField(
        max_length=15, choices=Itype, default="drug", blank=False
    )
    heading = models.TextField(blank=False, null=False)
    content = models.TextField(blank=False, null=True)


class Victim(models.Model):
    Vtype = (
        ("missing_children", "Missing Children"),
        ("children_found", "Children Found"),
        ("missing_person", "Missing Person"),
        ("dead_body", "Dead Bodied Found"),
        ("other", "Any other case"),
    )

    type = models.CharField(
        max_length=25, choices=Vtype, default="missing_children", blank=False
    )
    created = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField()


class Criminal(models.Model):
    Ctype = (
        ("offender", "Habitual offender"),
        ("wanted", "Wanted"),
        ("proclaimed", "Proclaimed Offender"),
    )

    type = models.CharField(
        max_length=25, choices=Ctype, default="offender", blank=False
    )
    created = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField()


class Privacy(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = RichTextUploadingField()


class TermsCondition(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = RichTextUploadingField()


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = RichTextUploadingField()


class Like(models.Model):
    case = models.ForeignKey(Case, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(cUser, related_name="likes", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("case", "user")


class Banner(models.Model):
    bid = models.BigAutoField(primary_key=True)
    Mtype = (
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    mtype = models.CharField(max_length=10, choices=Mtype, default="Photo")
    path = models.FileField(upload_to=get_upload_path, validators=[file_type_validator])
    description = models.TextField(null=True)


class LoggedInUser(models.Model):
    user = models.OneToOneField(
        cUser, related_name="logged_in_user", on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.user.mobile


class UserOTPBaseKey(models.Model):
    user = models.OneToOneField(
        cUser, related_name="user_otp", on_delete=models.CASCADE, unique=True
    )
    base_32_secret_key = models.CharField(max_length=32, null=True, blank=True)
    otp_generation_count = models.IntegerField(default=0)
    last_otp_generation_time = models.DateTimeField(null=True, blank=True)

    @classmethod
    def generate_otp(cls, user, digits=6) -> int:
        try:
            if cls.should_reset_otp_generation_count(user):
                logger.info(f"Resetting OTP count for user {user.mobile}")
                cls.objects.filter(user=user).update(
                    otp_generation_count=0, last_otp_generation_time=timezone.now()
                )

            if not cls.is_otp_generation_allowed(user):
                logger.critical(
                    f"SECURITY ALERT: Excessive OTP attempts for user {user.mobile}"
                )
                raise Exception("Too many OTP generation attempts")
            user_opt = getattr(user, "user_opt", None)
            current_count = 0
            if user_opt:
                current_count = getattr(user_opt, "otp_generation_count", 0)
            logger.info(
                f"OTP generation attempt {current_count + 1}/5 for user {user.mobile}"
            )

            secret_key = random_base32()
            user_otp_key, created = cls.objects.update_or_create(
                user=user,
                defaults={
                    "base_32_secret_key": secret_key,
                    "last_otp_generation_time": timezone.now(),
                },
            )

            if not created:
                user_otp_key.otp_generation_count = models.F("otp_generation_count") + 1
                user_otp_key.save()

            otp = TOTP(
                secret_key, interval=settings.OTP_VALIDITY_TIME, digits=digits
            ).now()

            logger.info(f"OTP generated successfully for user {user.mobile}")
            return otp

        except Exception as e:
            logger.critical(
                f"OTP generation failed for user {getattr(user, 'mobile', 'unknown')}: {str(e)}"
            )
            raise

    @classmethod
    def should_reset_otp_generation_count(cls, user) -> bool:
        if hasattr(user, "user_otp"):
            last_otp_generation_time = user.user_otp.last_otp_generation_time
        else:
            last_otp_generation_time = None

        if not last_otp_generation_time:
            return False

        current_time = timezone.now()
        one_hour_ago = current_time - timezone.timedelta(hours=1)
        return last_otp_generation_time < one_hour_ago

    @classmethod
    def is_otp_generation_allowed(cls, user) -> bool:
        if hasattr(user, "user_otp"):
            otp_generation_count = user.user_otp.otp_generation_count
        else:
            otp_generation_count = 0
        return otp_generation_count < 5

    @classmethod
    def validate_otp(cls, user, otp: int, digits=6) -> bool:
        try:
            user_otp_key, created = cls.objects.get_or_create(user=user)

            if user_otp_key.base_32_secret_key is None:
                secret_key = random_base32()
                user_otp_key.base_32_secret_key = secret_key
                user_otp_key.save()

            return TOTP(
                user_otp_key.base_32_secret_key,
                interval=settings.OTP_VALIDITY_TIME,
                digits=digits,
            ).verify(otp)
        except Exception as e:
            logger.error(
                f"Error validating OTP for user {getattr(user, 'mobile', 'unknown')}: {str(e)}",
                exc_info=True,
            )
            return False

    @classmethod
    def send_otp_verification_code(cls, user, verification=True):
        try:
            logger.info(f"Starting OTP send process for user {user.mobile}")

            otp_code = cls.generate_otp(user)
            print("OTTTTTPPPPPPP", otp_code)
            text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"

            logger.debug(f"Sending SMS to {user.mobile}: {text[:30]}...")
            send_sms(user.mobile, text)

            logger.info(f"OTP sent successfully to user {user.mobile}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to send OTP to user {user.mobile}: {str(e)}", exc_info=True
            )
            return False


class AboutPage(models.Model):
    content = RichTextField()

    def __str__(self):
        return "About Page Content"  # A simple representation
