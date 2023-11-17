import base64

from django import forms
from django.forms import ValidationError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from .models import cUser
from .otp import validate_otp, send_otp_verification_code

from cryptography.hazmat.primitives import serialization

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

        private_key_pem_b64 = self.request.session['private_key']
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)


        new_password1_encrypted_data_b64 = cd["password"]
        new_password1_encrypted_data = base64.b64decode(new_password1_encrypted_data_b64)

        new_password1_decrypted = private_key.decrypt(
            new_password1_encrypted_data,
            padding.PKCS1v15(),
        )

        new_password1 = new_password1_decrypted.decode('utf-8')
        new_password2_encrypted_data_b64 = cd["repeat_password"]
        new_password2_encrypted_data = base64.b64decode(new_password2_encrypted_data_b64)

        new_password2_decrypted = private_key.decrypt(
            new_password2_encrypted_data,
            padding.PKCS1v15(),
        )

        new_password2 = new_password2_decrypted.decode('utf-8')

        password = new_password1
        repeat_password = new_password2

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
            cd["password"] = password
            cd["repeat_password"] = repeat_password
        return cd

    def save(self, **kwargs):
        user = self.cleaned_data["user"]
        user.set_password(self.cleaned_data["password"])
        user.save()
