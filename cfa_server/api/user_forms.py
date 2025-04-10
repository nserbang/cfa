import base64
import re
import logging
from django import forms
from django.forms import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import cUser, MobileValidator, UserOTPBaseKey
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

# from django.core.validators import RegexValidator


# # mobile_pattern = re.compile(r'^[6-9]\d{9}$')

# class MobileValidator(RegexValidator):
#     regex = r'^[6-9]\d{9}$'


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = cUser
        fields = ["mobile"]


class UserRegistrationCompleteForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"type": "password"}),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"type": "password"}),
    )

    class Meta:
        model = cUser
        fields = [
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "email",
            "address",
            "profile_picture",
        ]

    def __init__(self, *args, **kwargs):
        logger.info("Entering UserRegistrationCompleteForm.__init__")
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        logger.info("Exiting UserRegistrationCompleteForm.__init__")

    def clean(self):
        logger.info("Entering UserRegistrationCompleteForm.clean")
        cd = super().clean()
        password = cd["password"]
        confirm_password = cd["confirm_password"]
        
        logger.debug("Validating password match")
        if password != confirm_password:
            logger.warning("Passwords did not match")
            raise forms.ValidationError("Passwords did not match.")
            
        cd["password"] = password
        cd["repeat_password"] = cd["confirm_password"]
        logger.info("Exiting UserRegistrationCompleteForm.clean")
        return cd

    def save(self, commit=True):
        logger.info("Entering UserRegistrationCompleteForm.save")
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        logger.info(f"Setting password for user: {user.mobile}")
        result = super().save(commit=True)
        logger.info("Exiting UserRegistrationCompleteForm.save")
        return result


class VerifyOtpFrom(forms.Form):
    otp = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        logger.info("Entering VerifyOtpFrom.__init__")
        self.mobile = kwargs.pop("mobile", None)
        logger.info(f"Initializing OTP verification for mobile: {self.mobile}")
        super().__init__(*args, **kwargs)
        logger.info("Exiting VerifyOtpFrom.__init__")

    def clean(self):
        logger.info("Entering VerifyOtpFrom.clean")
        cd = super().clean()
        
        logger.debug(f"Finding user with mobile: {self.mobile}")
        self.user = cUser.objects.filter(mobile=self.mobile.strip()).first()
        
        if not self.user:
            logger.warning(f"User not found for mobile: {self.mobile}")
            raise ValidationError("User not found")
            
        if not UserOTPBaseKey.validate_otp(self.user, cd["otp"]):
            logger.warning(f"Invalid OTP for user: {self.user.mobile}")
            raise ValidationError("Otp is Invalid or expired.")
            
        logger.info("Exiting VerifyOtpFrom.clean")
        return cd

    def save(self, **kwargs):
        logger.info("Entering VerifyOtpFrom.save")
        self.user.save()
        logger.info(f"Saved user after OTP verification: {self.user.mobile}")
        logger.info("Exiting VerifyOtpFrom.save")
        return self.user


class ResendMobileVerificationOtpForm(forms.Form):
    mobile = forms.CharField(max_length=16, validators=[MobileValidator])

    def save(self, **kwargs):
        logger.info("Entering ResendMobileVerificationOtpForm.save")
        try:
            user = cUser.objects.get(mobile=self.cleaned_data["mobile"])
            logger.info(f"Found user for OTP resend: {user.mobile}")
            UserOTPBaseKey.send_otp_verification_code(user)
            logger.info(f"Sent new OTP to user: {user.mobile}")
        except cUser.DoesNotExist:
            logger.warning(f"User not found for mobile: {self.cleaned_data['mobile']}")
            user = None
        logger.info("Exiting ResendMobileVerificationOtpForm.save")
        return None


class ForgotPasswordForm(forms.Form):
    mobile = forms.CharField(max_length=16, validators=[MobileValidator])

    def save(self, **kwargs):
        logger.info("Entering ForgotPasswordForm.save")
        mobile = self.cleaned_data["mobile"]
        try:
            user = cUser.objects.get(mobile=mobile)
            logger.info(f"Found user for password reset: {user.mobile}")
            UserOTPBaseKey.send_otp_verification_code(user, verification=False)
            logger.info(f"Sent password reset OTP to user: {user.mobile}")
        except cUser.DoesNotExist:
            logger.warning(f"User not found for mobile: {mobile}")
            pass
        logger.info("Exiting ForgotPasswordForm.save")


class ChangePasswordForm(forms.Form):
    otp = forms.CharField(max_length=6)
    password = forms.CharField(widget=forms.PasswordInput())
    repeat_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        logger.info("Entering ChangePasswordForm.__init__")
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        logger.info("Exiting ChangePasswordForm.__init__")

    def clean(self):
        logger.info("Entering ChangePasswordForm.clean")
        cd = super().clean()

        password = cd["password"]
        repeat_password = cd["repeat_password"]
        
        if password != repeat_password:
            logger.warning("Passwords did not match")
            raise forms.ValidationError("Passwords did not match.")
            
        mobile = self.request.session.get("mobile")
        logger.debug(f"Validating password change for mobile: {mobile}")
        
        try:
            user = cUser.objects.get(mobile=mobile)
            logger.info(f"Found user for password change: {user.mobile}")
            
            validate_password(password=password, user=user)
            logger.debug("Password validation successful")
            
            if not UserOTPBaseKey.validate_otp(user, self.cleaned_data["otp"]):
                logger.warning(f"Invalid OTP for user: {user.mobile}")
                self.add_error("otp", "Otp expired or invalid.")
                
            cd["user"] = user
            cd["password"] = password
            cd["repeat_password"] = repeat_password
            
        except cUser.DoesNotExist:
            logger.warning(f"User not found for mobile: {mobile}")
            return forms.ValidationError("User does not exists.")
        except Exception as e:
            logger.error(f"Password validation error: {str(e)}")
            self.add_error("password", e.messages)
            
        logger.info("Exiting ChangePasswordForm.clean")
        return cd

    def save(self, **kwargs):
        logger.info("Entering ChangePasswordForm.save")
        user = self.cleaned_data["user"]
        user.set_password(self.cleaned_data["password"])
        user.save()
        logger.info(f"Password changed successfully for user: {user.mobile}")
        
        del self.request.session["mobile"]
        del self.request.session["password_reset"]
        logger.info("Cleaned up session data")
        
        logger.info("Exiting ChangePasswordForm.save")
