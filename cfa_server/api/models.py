from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.geos import fromstr
from api.utl import get_upload_path
from .managers import CustomUserManager
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

from django.db.models import Q


from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


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
    mobile = models.CharField(max_length=26, unique=True)
    is_verified = models.BooleanField(default=False)

    # Role of the user
    role = models.CharField(max_length=10, choices=ROLES, default="user")
    # Address of the user. Optional
    address = models.TextField(null=True)
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
        self.geo_location = fromstr(f"POINT({self.lat} {self.long})", srid=4326)
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


class Case(models.Model):
    cType = (
        ("drug", "Drug"),  # complaint related to drugs
        ("vehicle", "Vehicle"),
        ("extortion", "Extortion"),
    )
    cState = (
        ("pending", "Pending"),  # Complaint lodged for the first time
        ("accepted", "Accepted"),  # Formal case approved
        ("assign", "Assign"),  # Assign case to some other officer
        ("transfer", "Transfer"),  # Complaint being transferred from one ps to another
        ("resolved", "Resolved"),  # Complaint has been resolved
        ("info", "Info"),  # Police officer requires more information from complainant
    )
    cid = models.BigAutoField(primary_key=True)
    # Police station in which case is lodged
    pid = models.ForeignKey(PoliceStation, on_delete=models.DO_NOTHING)
    # Who has lodged complaint
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    # Police officer id
    oid = models.ForeignKey(
        PoliceOfficer, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    # complaint type
    type = models.CharField(max_length=10, choices=cType, default="drug")
    title = models.CharField(max_length=250, null=True)
    # Current state of the case
    cstate = models.CharField(max_length=15, choices=cState, default="pending")
    # Date and time when complaint was reported
    created = models.DateTimeField(auto_now_add=True)
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

    def add_history_and_media(self, description, medias, user):
        history = CaseHistory.objects.create(
            case=self, user=self.user, description=description, cstate=self.cstate
        )
        if medias:
            history.medias.add(*medias)

    def save(self, *args, **kwargs):
        if self.pid:
            if not self.geo_location:
                self.geo_location = fromstr(f"POINT({self.lat} {self.long})", srid=4326)
            # If the case is assigned to a police station, calculate and save the distance
            self.distance = self.geo_location.distance(self.pid.geo_location)

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
        super().save(*args, **kwargs)
        try:
            title = self.title
            body = {
                "case_id": str(self.cid),
                "description": self.description,
                "type": self.type,
                "state": self.cstate,
                "created": str(self.created),
            }
            message = Message(notification=Notification(title=title), data=body)
            if self.oid_id:
                devices = FCMDevice.objects.filter(user_id=self.oid.user_id)
            else:
                devices = FCMDevice.objects.filter(
                    user_id__in=self.pid.policeofficer_set.values("user_id")
                )
            devices.send_message(message)
        except Exception as e:
            pass
        return


class Media(models.Model):
    Mtype = (  # what kind of media is this
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    # media type
    mtype = models.CharField(max_length=10, choices=Mtype, default="Photo")
    # media path
    path = models.FileField(upload_to=get_upload_path)
    description = models.TextField(null=True)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     # Create CaseHistory entry when a new media object is created
    #     if not self.pk:
    #         case_history = CaseHistory.objects.create(
    #             case=self.cid_history.case,
    #             user=self.cid_history.user,
    #             cstate=self.cid_history.cstate,
    #             description="Media uploaded.",
    #         )
    #         case_history.save()
    #         case_history.add(self)


class CaseHistory(models.Model):
    case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    # Who has entered this entry
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    # state of the case during this time
    cstate = models.CharField(max_length=15, choices=Case.cState)
    created = models.DateTimeField(auto_now_add=True)
    # Description added
    description = models.TextField(null=True)
    medias = models.ManyToManyField(Media, related_name="case_histories")


class LostVehicle(models.Model):
    caseId = models.OneToOneField(Case, on_delete=models.DO_NOTHING)
    regNumber = models.CharField(max_length=30)
    chasisNumber = models.CharField(max_length=50, null=True, default="N/A")
    engineNumber = models.CharField(max_length=50, null=True, default="N/A")
    make = models.CharField(max_length=50, null=True, default="N/A")
    model = models.CharField(max_length=50, null=True, default="N/A")
    description = models.CharField(max_length=500, null=True, default="N/A")


class Comment(models.Model):
    cmtid = models.BigAutoField(primary_key=True)
    cid = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey(cUser, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)


# Table for emergency helpline numbers with their name and gps location
class Emergency(models.Model):
    emid = models.BigAutoField(primary_key=True)
    did = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, default="N/A")
    number = models.CharField(max_length=100, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True)


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
    path = models.FileField(upload_to=get_upload_path)
    description = models.TextField(null=True)
