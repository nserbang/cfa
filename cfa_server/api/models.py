from django.contrib.gis.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.geos import fromstr
from api.utl import get_upload_path
from .managers import CustomUserManager


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
    oid = models.ForeignKey(PoliceOfficer, on_delete=models.DO_NOTHING)
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
    # Text description of the complaint
    description = models.TextField(null=True)
    # Follow me flag
    follow = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            # If the instance is being created, record the creation in CaseHistory
            with transaction.atomic():
                super().save(*args, **kwargs)
                case_history = CaseHistory.objects.create(
                    cid=self,
                    user=self.user,
                    cstate=self.cstate,
                    description="Case created.",
                )
                case_history.save()
        else:
            original_case = Case.objects.get(pk=self.pk)

            # Check for changes in cstate, pid, and oid
            cstate_changed = self.cstate != original_case.cstate
            pid_changed = self.pid_id != original_case.pid_id
            oid_changed = self.oid_id != original_case.oid_id

            with transaction.atomic():
                super().save(*args, **kwargs)

                # Create CaseHistory entry for each change
                if cstate_changed:
                    case_history = CaseHistory.objects.create(
                        cid=self,
                        user=self.user,
                        cstate=self.cstate,
                        description="Case state updated from {} to {}".format(
                            original_case.cstate, self.cstate
                        ),
                    )
                    case_history.save()

                if pid_changed:
                    case_history = CaseHistory.objects.create(
                        cid=self,
                        user=self.user,
                        pid=self.pid,
                        description="Police station updated.",
                    )
                    case_history.save()

                if oid_changed:
                    case_history = CaseHistory.objects.create(
                        cid=self,
                        user=self.user,
                        oid=self.oid,
                        description="Police officer updated.",
                    )
                    case_history.save()

        # Update the geo_location field based on lat and long
        self.geo_location = fromstr(f"POINT({self.lat} {self.long})", srid=4326)

        return super().save(*args, **kwargs)

class Media(models.Model):
    mid = models.BigAutoField(primary_key=True)
    # chid =  models.ForeignKey(CaseHistory,,db_column="case_history_chid",on_delete=models.CASCADE)
    pid = models.BigIntegerField(default=0)
    Mtype = (  # what kind of media is this
        ("video", "Video"),
        ("photo", "Photo"),
        ("audio", "Audio"),
        ("document", "Document"),
    )
    # media type
    mtype = models.CharField(max_length=10, choices=Mtype, default="Photo")
    Ptype = (  #
        ("case", "Case"),
        ("history", "History"),
        ("comment", "Comment"),
    )
    ptype = models.CharField(max_length=10, choices=Ptype, default="case")
    # media path
    path = models.FileField(upload_to=get_upload_path)
    description = models.TextField(null=True)

class CaseHistory(models.Model):
    chid = models.BigAutoField(primary_key=True)
    # which case history
    cid = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    # Who has entered this entry
    user = models.ForeignKey(cUser, on_delete=models.DO_NOTHING)
    # state of the case during this time
    cstate = models.CharField(max_length=15, choices=Case.cState)
    # Date and time when complaint was reported
    created = models.DateTimeField(auto_now_add=True)
    # Description added
    description = models.TextField(null=True)
    
    media = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True)


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


""" cmtid, cid, content, user
class CommentMedia(models.Model):
    cmmid = models.BigAutoField(primary_key=True)
    chid = models.ForeignKey(Comments,,db_column="comment_cmtid",on_delete=models.CASCADE)
    mtype = (
        ('video','Video'),
        ('photo','Photo'),
        ('audio','Audio'),
        ('document','Document'),
    )
    # media type
    type = models.CharField(max_length=10,choices=mtype,default="Photo")
    # media path
    path = models.CharField(max_length=50,null=True) """


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
