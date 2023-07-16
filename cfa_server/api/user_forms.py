from django import forms
from django.forms import ValidationError
from .models import cUser
from .otp import validate_otp


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={"type": "password"}),
    )

    class Meta:
        model = cUser
        fields = [
            'username',
            'password',
            'mobile',
            'first_name',
            'last_name',
            'email',
            'role',
            'address',
            'pincode',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = (('user', "User"), ('police', 'Police'))
        self.fields['username'].required = True
        self.fields['last_name'].required = True
        self.fields['last_name'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        return super().save(commit=True)


class VerifyOtpFrom(forms.Form):
    otp = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        self.mobile = kwargs.pop('mobile', None)
        print(self.mobile, "JDLKFJDKLFJL")
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        self.user = cUser.objects.get(mobile=self.mobile.strip())
        if not validate_otp(self.user, cd['otp']):
            raise ValidationError("Otp is Invalid or expired.")
        return cd

    def save(self):
        self.user.is_verified = True
        self.user.save()
        return self.user

