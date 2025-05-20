import magic
import requests
from django import forms
from django.db.models import Q
from django.utils import timezone
from django.contrib.gis.geos import fromstr
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from api.models import (
    Case,
    PoliceStation,
    Media,
    LostVehicle,
    CaseHistory,
    PoliceOfficer,
)
from api.otp import send_sms
import logging

logger = logging.getLogger(__name__)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        logger.debug(" Entering with data : {data}")
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CaseForm(forms.ModelForm):
    VEHICLE_LOST_CHOICES = (# Represent criminal type
        ("stolen", "Stolen"),
        ("abandoned", "Abandoned"),
    )
    vehicle_lost_type = forms.ChoiceField(
            choices=VEHICLE_LOST_CHOICES,
            required=False,
            label="Type of Vehicle Lost",
            initial="stolen")
    regNumber = forms.CharField(max_length=30, required=False)
    chasisNumber = forms.CharField(max_length=50, required=False)
    engineNumber = forms.CharField(max_length=50, required=False)
    make = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    color = forms.CharField(max_length=56, required=False)
    documents = MultipleFileField(required=False)

    class Meta:
        model = Case
        fields = [
            "type",
            "drug_issue_type",
            "vehicle_lost_type",
            "regNumber",
            "chasisNumber",
            "engineNumber",
            "make",
            "model",
            "color",
            "lat",
            "long",
            "description",
            "pid",
            "documents",
        ]

    vehicle_fields = [
        "vehicle_lost_type",
        "regNumber",
        "chasisNumber",
        "engineNumber",
        "make",
        "model",
        "color",
    ]

    def clean(self):
        logger.info("Entering CaseForm.clean")
        cd = super().clean()
        case_type = cd["type"]
        logger.debug(f"Validating case type: {case_type}")

        if case_type == "drug" and not cd.get("drug_issue_type"):
            logger.warning("Drug case missing drug_issue_type")
            self.add_error("drug_issue_type", "This field is required")

        if case_type == "vehicle":
            logger.debug("Validating vehicle fields")
            for field in self.vehicle_fields:
                if not cd.get(field):
                    logger.warning(f"Vehicle case missing required field: {field}")
                    self.add_error(field, "This field is required")

        files = cd.get("documents")
        if files:
            logger.info(f"Validating {len(files)} documents")
            for f in files:
                mime_type = magic.from_buffer(f.read(1024), mime=True)
                logger.debug(f"Checking file {f.name}, MIME type: {mime_type}")
                if mime_type not in settings.ALLOWED_DOC_TYPES:
                    logger.warning(f"Invalid file type: {mime_type} for file {f.name}")
                    self.add_error("documents", f"You can't upload this file: {f.name}.")
                    return
                f.seek(0)
        
        logger.info("Exiting CaseForm.clean")
        return cd

    def __init__(self, *args, **kwargs):
        logger.info("Entering CaseForm.__init__")
        self.user = kwargs.pop("user")
        logger.debug(f"Initializing form for user: {self.user}")
        super().__init__(*args, **kwargs)
        self.fields["lat"].widget = forms.widgets.HiddenInput()
        self.fields["long"].widget = forms.widgets.HiddenInput()
        self.fields["pid"].widget = forms.widgets.HiddenInput()
        self.fields["pid"].required = False
        logger.info("Exiting CaseForm.__init__")

    def save(self, commit=False):
        logger.info("Entering CaseForm.save")
        case = super().save(commit=False)
        
        geo_location = fromstr(f"POINT({case.long} {case.lat})", srid=4326)
        logger.debug(f"Created geo location point: ({case.long}, {case.lat})")

        if self.cleaned_data["pid"]:
            police_station = self.cleaned_data["pid"]
            logger.info(f"Using provided police station: {police_station}")
        else:
            user_distance = Distance("geo_location", geo_location)
            police_station = (
                PoliceStation.objects.annotate(radius=user_distance)
                .order_by("radius")
                .first()
            )
            logger.info(f"Found nearest police station: {police_station}")

        case.pid = police_station
        case.geo_location = geo_location
        officier = police_station.policeofficer_set.order_by("-rank").first()
        case.oid = officier
        case.user = self.user
        case.save()
        logger.info(f"Saved case with ID: {case.cid}")

        if case.type == "vehicle":
            logger.info("Processing vehicle case details")
            lost_vehicle_type = self.cleaned_data.pop("vehicle_lost_type", "")
            vehicle = LostVehicle.objects.create(
                caseId=case,
                type=lost_vehicle_type,
                **{
                    f: self.cleaned_data.get(f)
                    for f in self.vehicle_fields
                    if self.cleaned_data.get(f)
                },
            )
            logger.info(f"Created lost vehicle record: {vehicle.id}")

        files = self.cleaned_data.get("documents")
        if files:
            logger.info(f"Processing {len(files)} documents")
            medias = []
            for f in files:
                medias.append(Media(path=f, mtype="document"))
            medias = Media.objects.bulk_create(medias)
            case.medias.add(*medias)
            logger.debug(f"Added {len(medias)} media files to case")

        history = CaseHistory.objects.create(
            case=case,
            user=case.user,
            cstate=case.cstate,
            description="Case created.",
        )
        logger.info(f"Created case history entry: {history.id}")

        desc = f"New case no.{case.cid} of type {case.type} reported at {case.pid}."
        if case.oid_id:
            logger.info(f"Sending SMS to officer: {case.oid.mobile}")
            send_sms(case.oid.mobile, desc)
        else:
            officers = case.pid.policeofficer_set.filter(
                Q(report_on_this=True) | Q(rank="5")
            ).values("user_id", "user__mobile")
            logger.info(f"Sending SMS to {len(officers)} officers")
            for officer in officers:
                send_sms(officer["user__mobile"], desc)

        logger.info("Exiting CaseForm.save")
        return case


class CaseUpdateForm(forms.ModelForm):
    files = MultipleFileField(required=False)
    description = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Case
        fields = ["cstate", "oid"]

    def __init__(self, *args, **kwargs):
        logger.debug(" Entering ")
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        if status := self.request.GET.get("status"):
            self.initial["cstate"] = status
        self.fields["oid"].queryset = PoliceOfficer.objects.filter(
            pid=self.request.user.policeofficer_set.first().pid, rank=4
        ).exclude(user=self.request.user)

    def clean(self):
        logger.debug(" Entering ")
        self.request = kwargs.pop("request")
        cd = super().clean()
        files = cd.get("files")
        for f in files:
            mime_type = magic.from_buffer(f.read(1024), mime=True)
            if mime_type not in settings.ALLOWED_FILE_TYPES:
                self.add_error("files", f"You can't this file: {f.name}.")
                return
            f.seek(0)

        state = cd["cstate"]
        if state == "assign" and not cd.get("oid"):
            raise forms.ValidationError(
                "You need to provide oid to assign this case to new officer."
            )
        return cd

    def save(self, commit=True):
        logger.debug(" Entering ")
        self.request = kwargs.pop("request")
        files = self.cleaned_data.get("files")
        medias = []
        for f in files:
            application_type = magic.from_buffer(f.read(1024), mime=True)
            f.seek(0)
            if application_type in settings.ALLOWED_VIDEO_TYPES:
                document_type = "video"
            elif application_type in settings.ALLOWED_IMAGE_TYPES:
                document_type = "photo"
            elif application_type in settings.ALLOWED_DOC_TYPES:
                document_type = "document"
            elif application_type in settings.ALLOWED_VIDEO_TYPES:
                document_type = "audio"

            medias.append(Media(path=f, mtype=document_type))
        medias = Media.objects.bulk_create(medias)
        case = self.instance
        case.cstate = self.cleaned_data["cstate"]
        case.updated = timezone.now()

        if not self.cleaned_data["oid"]:
            case.oid = self.instance.oid

        noti_title = {
            "accepted": "Your case no.{} has been accepted.",
            "rejected": "Your case no.{} has been rejected.",
            "info": "More info required for your case no.{}.",
            "inprogress": "Your case no.{} is in-progress.",
            "resolved": "Your case no.{} is resolved.",
            "visited": "Your case no.{} is visited.",
            "found": "Your case no.{} is found.",
        }
        if self.cleaned_data["cstate"] in {"assign", "transfer"}:
            case.oid = self.cleaned_data["oid"]
            case.cstate = "pending"
            case.save()
            noti_title = f"You are assigned a new case no.{case.pk}"
            case.send_notitication(noti_title, [case.oid.user_id])
            send_sms(noti_title, case.oid.user.mobile)
        else:
            case.save()
            message = f"Case no. {case.pk} status changed to {case.cstate}"
            supervisors = PoliceOfficer.objects.filter(
                Q(pid__did=case.oid.pid.did, rank=9)
                | Q(oid__in=case.oid.policestation_supervisor.values("officer_id"))
            ).values("user_id", "user__mobile")
            case.send_notitication(message, [o["user_id"] for o in supervisors])
            for supervisor in supervisors:
                send_sms(message, supervisor["user__mobile"])
        description = self.cleaned_data["description"]
        case.add_history_and_media(
            description=description, medias=medias, user=self.request.user
        )
        return case
