import base64

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes  # only for AES CBC mode

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

import logging


class CustomBackend(ModelBackend):
    def authenticate(self, request, username, password, **kwargs):
        private_key_pem_b64 = request.session.get("private_key")
        if private_key_pem_b64:
            private_key_pem = base64.b64decode(private_key_pem_b64)
            private_key = serialization.load_pem_private_key(
                private_key_pem, password=None
            )
            encrypted_data_b64 = password
            encrypted_data = base64.b64decode(encrypted_data_b64)

            # Decrypt the data
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.PKCS1v15(),
            )

            decrypted_data_str = decrypted_data.decode("utf-8")

            password = decrypted_data_str

        return super().authenticate(request, username, password, **kwargs)
