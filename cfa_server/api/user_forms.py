from django import forms
from django.forms import ValidationError
from .models import cUser
from .otp import validate_otp, send_otp_verification_code


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = cUser
        fields = ["mobile"]


class UserRegistrationCompleteForm(forms.ModelForm):
    password = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={"type": "password"}),
    )

    class Meta:
        model = cUser
        fields = [
            "first_name",
            "last_name",
            "password",
            "email",
            "address",
            "profile_picture",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        return super().save(commit=True)


class VerifyOtpFrom(forms.Form):
    otp = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        self.mobile = kwargs.pop("mobile", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        self.user = cUser.objects.filter(mobile=self.mobile.strip()).first()
        if not validate_otp(self.user, cd["otp"]):
            raise ValidationError("Otp is Invalid or expired.")
        return cd

    def save(self, **kwargs):
        # self.user.is_verified = True
        self.user.save()
        return self.user


class ResendMobileVerificationOtpForm(forms.Form):
    mobile = forms.CharField(max_length=16)

    def save(self, **kwargs):
        try:
            user = cUser.objects.get(mobile=self.cleaned_data["mobile"])
        except cUser.DoesNotExist:
            user = None
        else:
            send_otp_verification_code(user)
        return None


class ForgotPasswordForm(forms.Form):
    mobile = forms.CharField(max_length=16)

    def save(self, **kwargs):
        mobile = self.cleaned_data["mobile"]
        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            pass
        else:
            send_otp_verification_code(user, verification=False)


class ChangePasswordForm(forms.Form):
    otp = forms.CharField(max_length=6)
    password = forms.CharField(widget=forms.PasswordInput())
    repeat_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        password = cd["password"]
        repeat_password = cd["repeat_password"]

        if password != repeat_password:
            raise forms.ValidationError("Passwords did not match.")
        mobile = self.request.session.get("mobile")
        try:
            user = cUser.objects.get(mobile=mobile)
        except cUser.DoesNotExist:
            return forms.ValidationError("User does not exists.")
        else:
            if not validate_otp(user, self.cleaned_data["otp"]):
                self.add_error("otp", "Otp expired or invalid.")
            cd["user"] = user
        return cd

    def save(self, **kwargs):
        user = self.cleaned_data["user"]
        user.set_password(self.cleaned_data["password"])
        user.save()
