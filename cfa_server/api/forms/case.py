from django import forms
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance
from api.models import Case, PoliceStation


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
        # import pdb; pdb.set_trace()
        case.pid = police_station
        case.geo_location = geo_location
        officier = police_station.policeofficer_set.order_by("-rank").first()
        case.oid = officier
        case.user = self.user
        return case.save()
