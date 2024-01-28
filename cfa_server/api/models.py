import re
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
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from django.core.exceptions import ValidationError
from django.conf import settings

from django.db.models import Q


from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import magic

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from pyotp import TOTP, random_base32

# MobileValidator = RegexValidator(
#     regex='^[6-9]\d{9}$',
#     message='Enter a valid mobile number.',
#     code='invalid_mobile_no',
# )


def mobile_validator(value):
    pattern = re.compile(r"^[6-9]\d{9}$")
    message = ("Enter a valid mobile number.",)
    if value == "9999999999":
        raise ValidationError(message)
    if not pattern.match(value):
        raise ValidationError(message)


MobileValidator = mobile_validator


def file_type_validator(f):
    mime_type = magic.from_buffer(f.read(1024), mime=True)
    if mime_type not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(f"You can't upload this file: {f.name}.")
    f.seek(0)
    return


# Holds list of districts
class District(models.Model):
    did = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# Holds user database
# username will be the primary key which will be the mobile number of the user


class cUser(AbstractUser):
    username = None
    ROLES = (
        ("user", "User"),
        ("police", "Police"),
        ("admin", "Admin"),
    )
    mobile = models.CharField(max_length=26, unique=True, validators=[MobileValidator])
    is_verified = models.BooleanField(default=False)

    # Role of the user
    role = models.CharField(max_length=10, choices=ROLES, default="user")
    # Address of the user. Optional
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


# Holds list of police stations
class PoliceStation(models.Model):
    pid = models.BigAutoField(primary_key=True)
    # district in which police station is located
    did = models.ForeignKey(District, on_delete=models.CASCADE)
    # Name of the police station
    name = models.TextField()
    # address of the police station
    address = models.TextField(null=True)
    # GPS location of the police station
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    long = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    distance = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
        super().save(**kwargs)


# Holds various contacts in the police station
class PoliceStationContact(models.Model):
    ps_cid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    # Designation associated with the number
    contactName = models.CharField(max_length=50, null=True)
    # Mobile number or phone number
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
    # name = models.CharField(max_length=30,default=None)
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
        ("drug", "Drug"),  # complaint related to drugs
        ("vehicle", "Vehicle"),
        ("extortion", "Extortion"),
    )
    cState = (
        ("pending", "Pending"),  # Complaint lodged for the first time
        ("accepted", "Accepted"),  # Formal case approved
        ("found", "Found"),
        ("assign", "Assign"),  # Assign case to some other officer
        ("visited", "Visited"),
        ("inprogress", "Inprogress"),
        ("transfer", "Transfer"),  # Complaint being transferred from one ps to another
        ("resolved", "Resolved"),  # Complaint has been resolved
        ("info", "Info"),  # Police officer requires more information from complainant
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
    # Police station in which case is lodged
    pid = models.ForeignKey(PoliceStation, on_delete=models.DO_NOTHING)
    # Who has lodged complaint
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    # Police officer id
    oid = models.ForeignKey(
        PoliceOfficer, on_delete=models.SET_NULL, null=True, blank=True
    )
    # complaint type
    type = models.CharField(max_length=10, choices=cType, default="drug")
    title = models.CharField(max_length=250, null=True)
    # Current state of the case
    cstate = models.CharField(max_length=15, choices=cState, default="pending")
    # Date and time when complaint was reported
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)
    distance = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True
    )
    # Text description of the complaint
    description = models.TextField(null=True)
    # Follow me flag
    follow = models.BooleanField(default=False)
    medias = models.ManyToManyField("Media", related_name="cases", blank=True)
    drug_issue_type = models.CharField(
        max_length=20, choices=DRUG_ISSUE_TYPE, blank=True, default=""
    )

    def add_history_and_media(self, description, medias, user, cstate=None, **kwargs):
        cstate = cstate or self.cstate
        history = CaseHistory.objects.create(
            case=self,
            user=self.user,
            description=description,
            cstate=cstate,
            lat=kwargs.get("lat") if cstate == "visited" else None,
            long=kwargs.get("long") if cstate == "visited" else None,
        )
        if medias:
            for media in medias:
                if detect_malicious_patterns_in_media(media.path.path):
                    raise ValidationError("Malicious media file detected.")
            history.medias.add(*medias)

    def save(self, *args, **kwargs):
        if self.pid:
            if not self.geo_location:
                self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
            # If the case is assigned to a police station, calculate and save the
            point_one = (self.geo_location.y, self.geo_location.x)
            point_two = (self.pid.geo_location.y, self.pid.geo_location.x)

            d = distance.great_circle(point_one, point_two).km
            self.distance = d

        if not self.pk:
            # If the instance is being created, record the creation in CaseHistory
            with transaction.atomic():
                super().save(*args, **kwargs)
                CaseHistory.objects.create(
                    case=self,
                    user=self.user,
                    cstate=self.cstate,
                    description="Case created.",
                )
                try:
                    desc = f"New case no.{self.cid} of type {self.type} reported at {self.pid}."
                    data = {
                        "case_id": str(self.cid),
                        "description": desc,
                        "type": self.type,
                        "state": self.cstate,
                        "created": str(self.created),
                    }
                    message = Message(data=data)
                    if self.oid_id:
                        devices = FCMDevice.objects.filter(user_id=self.oid.user_id)
                        print("sending sms")
                        send_sms(self.oid.mobile, desc)
                    else:
                        officers = self.pid.policeofficer_set.filter(
                            Q(report_on_this=True) | Q(rank="5")
                        ).values("user_id", "user__mobile")
                        devices = FCMDevice.objects.filter(
                            user_id__in=[o["user_id"] for o in officers]
                        )
                        for officer in officers:
                            send_sms(officer["user__mobile"], desc)
                    print("sending notification")
                    devices.send_message(message)
                except Exception as e:
                    pass
            return
        super().save(*args, **kwargs)

    def send_notitication(self, title, user_ids: list):
        try:
            data = {
                "case_id": str(self.cid),
                "description": self.description,
                "type": self.type,
                "state": self.cstate,
                "created": str(self.created),
            }
            message = Message(notification=Notification(title=title), data=data)
            devices = FCMDevice.objects.filter(user_id__in=user_ids)
            devices.send_message(message)
        except Exception as e:
            pass


class Media(models.Model):
    Mtype = (  # what kind of media is this
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    # media type
    mtype = models.CharField(max_length=10, choices=Mtype, default="photo")
    # media path
    path = models.FileField(upload_to=get_upload_path, validators=[file_type_validator])
    description = models.TextField(null=True)


class CaseHistory(models.Model):
    case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    # Who has entered this entry
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    # state of the case during this time
    cstate = models.CharField(max_length=15, choices=Case.cState)
    created = models.DateTimeField(auto_now_add=True)
    # Description added
    description = models.TextField(null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    long = models.CharField(max_length=10, blank=True, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)
    medias = models.ManyToManyField(Media, related_name="case_histories")

    def distance(self):
        if self.case.geo_location and self.geo_location:
            return self.geo_location.distance(self.case.geo_location)
        return None

    def save(self, **kwargs):
        if self.lat and self.long:
            self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
        super().save(**kwargs)


class LostVehicle(models.Model):
    type = (  # Represent criminal type
        ("stolen", "Stolen"),
        ("abandoned", "Abandoned"),
    )

    caseId = models.OneToOneField(Case, on_delete=models.DO_NOTHING)
    regNumber = models.CharField(max_length=30, unique=True)
    chasisNumber = models.CharField(max_length=50, null=True, default="N/A")
    engineNumber = models.CharField(max_length=50, null=True, default="N/A")
    make = models.CharField(max_length=50, null=True, default="N/A")
    model = models.CharField(max_length=50, null=True, default="N/A")
    description = models.CharField(max_length=500, null=True, default="N/A")
    color = models.CharField(max_length=56, blank=True, default="")
    type = models.CharField(max_length=10, choices=type, null=False, default="stolen")


class Comment(models.Model):
    cmtid = models.BigAutoField(primary_key=True)
    cid = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey(cUser, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    medias = models.ManyToManyField(Media, related_name="comments", blank=True)

    # def save(self, **kwargs):
    #     if hasattr(self, "cid"):
    #         self.cid.updated = timezone.now()
    #         self.cid.save()
    #     return super().save(**kwargs)


class EmergencyType(models.Model):
    emtid = models.BigAutoField(primary_key=True)
    service_type = models.CharField(max_length=30, blank=False)


# Table for emergency helpline numbers with their name and gps location
class Emergency(models.Model):
    emid = models.BigAutoField(primary_key=True)
    tid = models.ForeignKey(EmergencyType, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, default="N/A")
    number = models.CharField(max_length=100, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    geo_location = models.PointField(blank=True, null=True, srid=4326)

    def save(self, **kwargs):
        if self.lat and self.long:
            self.geo_location = fromstr(f"POINT({self.long} {self.lat})", srid=4326)
        super().save(**kwargs)

    def tid_display(self):
        return self.tid.service_type

    tid_display.short_description = "Emergency Type"


class Information(models.Model):
    inid = models.BigAutoField(primary_key=True)
    Itype = (  # Represent information type
        ("drug", "Drug"),  # information related drug offenses
        ("extortion", "Extortion"),  # Information related to Extortion Offenses
        ("Vehicle", "Vehicle"),  # Rules/information related to vehicle theft
    )
    information_type = models.CharField(
        max_length=15, choices=Itype, default="drug", blank=False
    )
    heading = models.TextField(blank=False, null=False)
    content = models.TextField(blank=False, null=True)


class Victim(models.Model):
    Vtype = (  # Represent victim type
        (
            "missing_children",
            "Missing Children",
        ),  # information related Missing Children
        (
            "children_found",
            "Children Found",
        ),  # Information related to children lost found
        ("missing_person", "Missing Person"),  # information related to missing person
        ("dead_body", "Dead Bodied Found"),  # Information related to dead bodies found
        ("other", "Any other case "),  # Information related to any other case
    )

    type = models.CharField(
        max_length=25, choices=Vtype, default="missing_children", blank=False
    )
    created = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField()


class Criminal(models.Model):
    Ctype = (  # Represent criminal type
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
    Mtype = (  # what kind of media is this
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    # media type
    mtype = models.CharField(max_length=10, choices=Mtype, default="Photo")
    # media path
    path = models.FileField(upload_to=get_upload_path, validators=[file_type_validator])
    description = models.TextField(null=True)


class LoggedInUser(models.Model):
    user = models.OneToOneField(
        cUser, related_name="logged_in_user", on_delete=models.CASCADE
    )
    # Session keys are 32 characters long
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
        # Check if OTP generation count should be reset
        if cls.should_reset_otp_generation_count(user):
            cls.objects.filter(user=user).update(
                otp_generation_count=0, last_otp_generation_time=timezone.now()
            )

        # Check if OTP generation is allowed
        if cls.is_otp_generation_allowed(user):
            secret_key = random_base32()
            user_otp_key, created = cls.objects.get_or_create(
                user=user,
                defaults={
                    "base_32_secret_key": secret_key,
                    "last_otp_generation_time": timezone.now(),
                },
            )

            # Increment the otp_generation_count for an existing record
            if not created:
                user_otp_key.otp_generation_count = models.F("otp_generation_count") + 1
                user_otp_key.save()
            otp = TOTP(
                secret_key, interval=settings.OTP_VALIDITY_TIME, digits=digits
            ).now()
            return otp
        else:
            # If OTP generation limit is reached, you can handle it accordingly
            raise Exception("Too many attempts")

    @classmethod
    def should_reset_otp_generation_count(cls, user) -> bool:
        # Check if the related UserOTPBaseKey object exists
        if hasattr(user, "user_otp"):
            last_otp_generation_time = user.user_otp.last_otp_generation_time
        else:
            # Handle the case where the related object doesn't exist
            last_otp_generation_time = None

        # Check if it's been more than an hour since the last OTP generation
        if not last_otp_generation_time:
            return False  # No need to reset if no OTP generated yet

        current_time = timezone.now()
        one_hour_ago = current_time - timezone.timedelta(hours=1)

        return last_otp_generation_time < one_hour_ago

    @classmethod
    def is_otp_generation_allowed(cls, user) -> bool:
        # Check if the related UserOTPBaseKey object exists
        if hasattr(user, "user_otp"):
            otp_generation_count = user.user_otp.otp_generation_count
        else:
            # Handle the case where the related object doesn't exist
            otp_generation_count = 0

        # Check if OTP generation count is less than 5 within the last hour
        return otp_generation_count < 5

    @classmethod
    def validate_otp(cls, user, otp: int, digits=6) -> bool:
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

    @classmethod
    def send_otp_verification_code(cls, user, verification=True):
        otp_code = cls.generate_otp(user)
        print(otp_code)
        if verification:
            text = f"Victory Trading Agency user registration authentication verification OTP is {otp_code}"
        else:
            text = f"Victory Trading Agency user registration authentication verification OTP is {otp_code}"

        send_sms(user.mobile, text)
