import magic
from django import forms
from django.contrib.gis.geos import fromstr
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from api.models import Case, PoliceStation, Media


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            "type",
            "title",
            "cstate",
            "lat",
            "long",
            "description",
            "follow",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["cstate"].label = "State"
        self.fields["lat"].widget = forms.widgets.HiddenInput()
        self.fields["long"].widget = forms.widgets.HiddenInput()

    def save(self, commit=False):
        case = super().save(commit=False)
        geo_location = fromstr(f"POINT({case.lat} {case.long})", srid=4326)
        user_distance = Distance("geo_location", geo_location)
        police_station = (
            PoliceStation.objects.annotate(radius=user_distance)
            .order_by("radius")
            .first()
        )
        case.pid = police_station
        case.geo_location = geo_location
        officier = police_station.policeofficer_set.order_by("-rank").first()
        case.oid = officier
        case.user = self.user
        return case.save()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CaseUpdateForm(forms.ModelForm):
    files = MultipleFileField(required=False)
    description = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Case
        fields = ["cstate"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        if status := self.request.GET.get("status"):
            self.initial["cstate"] = status

    def clean(self):
        cd = super().clean()
        files = cd.get("files")
        for f in files:
            mime_type = magic.from_buffer(f.read(1024), mime=True)
            if mime_type not in settings.ALLOWED_FILE_TYPES:
                self.add_error("files", f"You can't this file: {f.name}.")
                return
            f.seek(0)
        return cd

    def save(self, commit=True):
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
        case.save()
        description = self.cleaned_data["description"]
        case.add_history_and_media(
            description=description, medias=medias, user=self.request.user
        )
        return case
