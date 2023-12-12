from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from rest_framework import serializers

from api.middleware import decrypt_password


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            raise PermissionDenied("Permission Denied")
        return super().dispatch(request, *args, **kwargs)


class UserMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs


class PasswordDecriptionMixin(serializers.Serializer):
    def validate(self, data):
        password_fields = [
            "password",
            "password1",
            "password2",
            "confirm_password",
            "repeat_password",
            "old_password",
            "new_password",
            "new_password1",
            "new_password2",
        ]
        request = self.context["request"]
        private_key_pem_b64 = request.session["private_key"]
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        for key in password_fields:
            if key in data.keys():
                b64_encrypted_value = data[key]

                encrypted_value = base64.b64decode(b64_encrypted_value)
                decrypted_value = private_key.decrypt(
                    encrypted_value,
                    padding.PKCS1v15(),
                )
                decrypted_value = decrypted_value.decode("utf-8")
                data[key] = decrypted_value
        return super().validate(data)
