from django import forms
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance
from api.models import Case, PoliceStation


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            # 'pid',
            # 'user',
            # 'oid',
            'type',
            'title',
            'cstate',
            'lat',
            'long',
            'description',
            'follow',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['cstate'].label = 'State'
        self.fields['lat'].label = 'Latitude'
        self.fields['long'].label = 'Longitude'

    def save(self, commit=False):
        case = super().save(commit=False)
        geo_location = fromstr(f"POINT({self.lat} {self.long})", srid=4326)
        user_distance = Distance("geo_location", geo_location)
        police_station = PoliceStation.objects.annotate(
            distance=user_distance
        ).order_by('distance').first()
        self.pid = police_station.pid
        self.oid = police_station.policeofficer_set.order_by('-rank').first()
        self.user = self.user
        return case.save()
