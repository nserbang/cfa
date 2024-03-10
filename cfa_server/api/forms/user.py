from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from api.models import cUser, District, PoliceStation, PoliceOfficer
from captcha.fields import CaptchaField


class cUserCreationForm(UserCreationForm):
    class Meta:
        model = cUser
        fields = ("mobile",)


class cUserChangeForm(UserChangeForm):
    class Meta:
        model = cUser
        fields = ("mobile", "email")
        error_messages = {"mobile": {"unique": ("This mobile is already registered.")}}


class cUserAuthenticationForm(AuthenticationForm):
    captcha = CaptchaField()


class AddOfficerForm(forms.Form):
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
    user = forms.ModelChoiceField(
        queryset=cUser.objects.all(), widget=forms.HiddenInput
    )
    rank = forms.ChoiceField(choices=RANKS)


class RemoveOfficerForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=cUser.objects.all(), widget=forms.HiddenInput
    )


class ChangeDesignationForm(forms.Form):
    RANKS = (
        ("6", "DySP"),
        ("7", "ASP"),
        ("9", "SP"),
        ("10", "SSP"),
        ("11", "DIGP"),
        ("12", "IGP"),
        ("13", "ADG"),
        ("14", "DGP"),
    )
    rank = forms.ChoiceField(choices=RANKS)
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        officer = self.user.policeofficer_set.first()
        if officer:
            officer.rank = self.cleaned_data["rank"]
            officer.save()
        else:
            police_station = PoliceStation.objects.filter(
                did=self.cleaned_data["district"]
            ).first()
            PoliceOfficer.objects.update_or_create(
                user=self.user,
                defaults={
                    "pid": police_station,
                    "mobile": self.user.mobile,
                    "rank": self.cleaned_data["rank"],
                },
            )
        return officer
