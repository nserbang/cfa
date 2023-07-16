from django.db import models
from django.contrib.auth.models import AbstractUser
from geopy.distance import distance
from api.utl import get_upload_path
# Create your models here.

#Holds list of districts
class District(models.Model):
    did = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

# Holds user database
#username will be the primary key which will be the mobile number of the user

class cUser(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": ("A user with that username already exists."),
        },
        null=True,
        blank=True,
    )

    ROLES = (
        ('user','User'),
        ('police','Police'),
        ('admin','Admin'),
    )
    mobile = models.CharField(max_length=26, unique=True)

    # Role of the user
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    # Address of the user. Optional
    address = models.TextField(null=True)
    # Pin code of the user. Optional
    pincode = models.CharField(max_length=10, blank=True)
    otp_code = models.CharField(max_length=6, default=None, null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'mobile'

# Holds list of police stations
class PoliceStation(models.Model):
    pid = models.BigAutoField(primary_key=True)
    # district in which police station is located
    did = models.ForeignKey(District,to_field="did",db_column="district_did",on_delete=models.CASCADE)
    # Name of the police station
    name = models.TextField()
    # address of the police station
    address = models.TextField(null=True)
    # GPS location of the police station
    lat = models.DecimalField(max_digits=9,decimal_places=6,default=0.0)
    long = models.DecimalField(max_digits=9,decimal_places=6, default=0.0)
    distance = models.DecimalField(max_digits=9, decimal_places=2, null = True)

    def __str__(self):
        return self.name

# Holds various contacts in the police station
class PoliceStationContact(models.Model):
    ps_cid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation,to_field="pid",db_column="police_station_pid", on_delete=models.CASCADE)
    # Designation associated with the number
    contactName = models.CharField(max_length=50, null=True)
    # Mobile number or phone number
    number = models.CharField(max_length=15)

class PoliceOfficer(models.Model):
    RANKS = (
            ('1','Constable'),
            ('2','Head Constable'),
            ('3','ASI'),
            ('4','SI'),
            ('5','Inspector'),
            ('6','DySP'),
            ('7','ASP'),
            ('9','SP'),
            ('10','SSP'),
            ('11','DIGP'),
            ('12','IGP'),
            ('13','ADG'),
            ('14','DGP'),
    )
    oState = (
        ('active','Active'),
        ('inactive','Inactive'),
        )
    user = models.ForeignKey(cUser,to_field="username",db_column="cuser_username",on_delete=models.DO_NOTHING)
    oid = models.BigAutoField(primary_key=True)
    pid = models.ForeignKey(PoliceStation,to_field="pid",db_column="police_station_pid", on_delete=models.DO_NOTHING)
    #name = models.CharField(max_length=30,default=None)
    rank = models.CharField(max_length=10, choices=RANKS, default='Inspector')
    entryDate= models.DateField(auto_now=True)
    status = models.CharField(max_length=10, choices=oState, default='active')
    mobile = models.CharField(max_length=55, null=True)

class Case(models.Model):
    cType = (
        ('drug','Drug'), # complaint related to drugs
        ('vehicle','Vehicle'),
        ('extortion', 'Extortion'),
    )
    cState = (
        ('pending','Pending'), # Complaint lodged for the first time
        ('accepted','Accepted'), # Formal case approved
        ('assign','Assign'), # Assign case to some other officer
        ('transfer','Transfer'), # Complaint being transferred from one ps to another
        ('resolved','Resolved'), # Complaint has been resolved
        ('info','Info'),    # Police officer requires more information from complainant
    )
    cid = models.BigAutoField(primary_key=True)
    # Police station in which case is lodged
    pid = models.ForeignKey(PoliceStation, to_field="pid", db_column="police_station_pid", on_delete=models.DO_NOTHING)
    # Who has lodged complaint
    user = models.ForeignKey(cUser, to_field="username",db_column="cuser_username", on_delete=models.DO_NOTHING)
    # Police officer id
    oid = models.ForeignKey(PoliceOfficer, to_field="oid",db_column="police_officer_oid",on_delete=models.DO_NOTHING)
    # complaint type
    type = models.CharField(max_length=10, choices=cType, default='drug')
    title = models.CharField(max_length=250,null=True)
    # Current state of the case
    cstate = models.CharField(max_length=15, choices=cState, default='pending')
    # Date and time when complaint was reported
    created = models.DateTimeField(auto_now_add=True)
    lat = models.DecimalField(max_digits=9,decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9,decimal_places=6, null=True)
    # Text description of the complaint
    description = models.TextField(null=True)
    # Follow me flag
    follow = models.BooleanField(default=False)


class CaseHistory(models.Model):
    chid = models.BigAutoField(primary_key=True)
    # which case history
    cid = models.ForeignKey(Case, to_field="cid", db_column="case_cid",on_delete=models.DO_NOTHING)
    # Who has entered this entry
    user = models.ForeignKey(cUser, to_field="username",db_column="user_username",on_delete=models.DO_NOTHING)
    # state of the case during this time
    cstate = models.CharField(max_length=15,choices= Case.cState)
    # Date and time when complaint was reported
    created = models.DateTimeField(auto_now_add=True)
    # Description added
    description = models.TextField(null=True)

class Media(models.Model):
    mid = models.BigAutoField(primary_key=True)
    #chid =  models.ForeignKey(CaseHistory, to_field="chid",db_column="case_history_chid",on_delete=models.CASCADE)
    pid = models.BigIntegerField(default= 0)
    Mtype = ( # what kind of media is this
        ('video','Video'),
        ('photo','Photo'),
        ('audio','Audio'),
        ('document','Document'),
    )
    # media type
    mtype = models.CharField(max_length=10,choices=Mtype,default="Photo")
    Ptype = (#
        ('case','Case'),
        ('history','History'),
        ('comment','Comment'),
    )
    ptype = models.CharField(max_length=10, choices=Ptype,default='case')
    # media path
    path = models.FileField(upload_to=get_upload_path)
    description = models.TextField(null= True)

class LostVehicle(models.Model):
    caseId = models.OneToOneField(Case,to_field="cid",db_column="Case_cid",on_delete=models.DO_NOTHING)
    regNumber = models.CharField(max_length=30)
    chasisNumber = models.CharField(max_length=50, null=True, default="N/A")
    engineNumber = models.CharField(max_length=50, null=True,default="N/A")
    make = models.CharField(max_length=50, null=True, default="N/A")
    model = models.CharField(max_length=50, null=True, default="N/A")
    description = models.CharField(max_length=500, null=True, default="N/A")

class Comment(models.Model):
    cmtid = models.BigAutoField(primary_key=True)
    cid = models.ForeignKey(Case,to_field="cid", db_column="case_cid",on_delete= models.CASCADE)
    user = models.ForeignKey(cUser,to_field="username",db_column="cuser_username",on_delete=models.CASCADE)
    content = models.TextField(null=True)

""" cmtid, cid, content, user
class CommentMedia(models.Model):
    cmmid = models.BigAutoField(primary_key=True)
    chid = models.ForeignKey(Comments, to_field="cmtid",db_column="comment_cmtid",on_delete=models.CASCADE)
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
    did = models.ForeignKey(District,to_field="did",db_column="district_did",on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, default="N/A")
    number = models.CharField(max_length=100, null=True)
    lat = models.DecimalField(max_digits=9,decimal_places=6, null=True)
    long = models.DecimalField(max_digits=9,decimal_places=6, null=True)

class Information(models.Model):
    inid = models.BigAutoField(primary_key=True)
    Itype = ( # Represent information type
        ('drug','Drug'), # information related drug offenses
        ('extortion','Extortion'), # Information related to Extortion Offenses
        ('Vehicle','Vehicle'), # Rules/information related to vehicle theft
    )
    information_type = models.CharField(max_length=15, choices=Itype,default='drug', blank=False)
    heading = models.TextField(blank=False,null=False)
    content = models.TextField(blank=False, null=True)
