from datetime import timezone
from django.contrib.sessions.models import Session
from django.http import HttpResponseNotAllowed
from rest_framework.request import Request as RestRequest

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

from api.models import LoggedInUser


class OneSessionPerUserMiddleware:
    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path.startswith("/api/v1"):
            pass
        elif request.user.is_authenticated:
            if not hasattr(request.user, "logged_in_user"):
                # If the user doesn't have a related logged_in_user instance, create one
                logged_in_user = LoggedInUser.objects.create(
                    user=request.user, session_key=request.session.session_key
                )
                request.user.logged_in_user = logged_in_user
            stored_session_key = request.user.logged_in_user.session_key

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            if stored_session_key and stored_session_key != request.session.session_key:
                session = Session.objects.filter(session_key=stored_session_key)
                if session:
                    session.delete()

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()

        response = self.get_response(request)

        # This is where you add any extra code to be executed for each request/response after
        # the view is called.
        # For this tutorial, we're not adding any code so we just return the response

        return response


class DisableOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            return HttpResponseNotAllowed(["GET", "POST", "HEAD"])
        return self.get_response(request)


class HSTSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; preload"
        response["X-XSS-Protection"] = "1; mode=block"

        return response


def decrypt_password(request):
    if request.method in ["POST", "PUT", "PATCH"]:
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
        post_data = request.POST
        private_key_pem_b64 = request.session["private_key"]
        private_key_pem = base64.b64decode(private_key_pem_b64)
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        request.POST._mutable = True
        for key in password_fields:
            if key in post_data.keys():
                b64_encrypted_value = post_data[key]

                encrypted_value = base64.b64decode(b64_encrypted_value)
                decrypted_value = private_key.decrypt(
                    encrypted_value,
                    padding.PKCS1v15(),
                )
                decrypted_value = decrypted_value.decode("utf-8")
                request.POST[key] = decrypted_value
        request.POST._mutable = False


class RSAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "private_key" in request.session and not request.path.startswith("/api/"):
            decrypt_password(request)
        response = self.get_response(request)
        if "private_key" not in request.session:
            # If private key is not in session, generate keys and store them
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_key = private_key.public_key()
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            request.session["private_key"] = base64.b64encode(private_key_pem).decode(
                "utf-8"
            )
            request.session["public_key"] = base64.b64encode(public_key_pem).decode(
                "utf-8"
            )
            response.set_cookie("rsa_public_key", request.session["public_key"])

        return response
