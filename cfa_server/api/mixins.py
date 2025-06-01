from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from rest_framework import serializers

from api.middleware import decrypt_password
import logging
logger = logging.getLogger(__name__)


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        logger.info("Entering AdminRequiredMixin dispatch")
        if not request.user.is_authenticated:
            logger.warning("User is not authenticated, handling no permission.")
            result = self.handle_no_permission()
            logger.info("Exiting AdminRequiredMixin dispatch (not authenticated)")
            return result
        if not request.user.is_admin:
            logger.warning("User is not an admin, raising PermissionDenied.")
            raise PermissionDenied("Permission Denied")
        logger.info("User is authenticated and is an admin, proceeding.")
        result = super().dispatch(request, *args, **kwargs)
        logger.info(f"Exiting AdminRequiredMixin dispatch (success): {result}")
        return result


class UserMixin:
    def get_queryset(self):
        logger.info("Entering UserMixin get_queryset")
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            logger.info(f"User {self.request.user.username} is authenticated, filtering queryset.")
            qs = qs.filter(user=self.request.user)
            logger.info(f"Queryset filtered for user {self.request.user.username}.")
        else:
            logger.info("User is not authenticated, returning unfiltered queryset.")
        logger.info(f"Exiting UserMixin get_queryset with data: {qs}")
        return qs


class PasswordDecriptionMixin(serializers.Serializer):
    def validate(self, data):
        logger.info(f"Entering PasswordDecriptionMixin validate with data: {data}")
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
                logger.info(f"Decrypting password field: {key}")
                b64_encrypted_value = data[key]

                encrypted_value = base64.b64decode(b64_encrypted_value)
                decrypted_value = private_key.decrypt(
                    encrypted_value,
                    padding.PKCS1v15(),
                )
                decrypted_value = decrypted_value.decode("utf-8")
                data[key] = decrypted_value
                logger.info(f"Decrypted {key} successfully.")
        validated_data = super().validate(data)
        logger.info(f"Exiting PasswordDecriptionMixin validate with validated_data: {validated_data}")
        return validated_data
