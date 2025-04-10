from django.contrib.sessions.models import Session
from django.http import HttpResponseNotAllowed
from csp.middleware import CSPMiddleware
from django.conf import settings

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

from api.models import LoggedInUser
import logging
logger = logging.getLogger(__name__)


class OneSessionPerUserMiddleware:
    # Called only once when the web server starts
    def __init__(self, get_response):
        logger.info("OneSessionPerUserMiddleware initializing")
        self.get_response = get_response
        logger.info("OneSessionPerUserMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering OneSessionPerUserMiddleware __call__")
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path.startswith("/api/v1"):
            logger.info("Request path starts with /api/v1, skipping session check.")
            pass
        elif request.user.is_authenticated:
            logger.info(f"User {request.user.username} is authenticated, checking session.")
            if not hasattr(request.user, "logged_in_user"):
                # If the user doesn't have a related logged_in_user instance, create one
                logger.info(f"User {request.user.username} doesn't have logged_in_user, creating one.")
                logged_in_user = LoggedInUser.objects.create(
                    user=request.user, session_key=request.session.session_key
                )
                request.user.logged_in_user = logged_in_user
                logger.info(f"Created logged_in_user for {request.user.username} with session key {request.session.session_key}.")
            stored_session_key = request.user.logged_in_user.session_key
            logger.info(f"Stored session key for user {request.user.username}: {stored_session_key}")

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            if stored_session_key and stored_session_key != request.session.session_key:
                logger.info(f"Stored session key is different from current session key, deleting old session.")
                session = Session.objects.filter(session_key=stored_session_key)
                if session:
                    session.delete()
                    logger.info(f"Deleted old session with key {stored_session_key}.")

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()
            logger.info(f"Updated logged_in_user session key to {request.session.session_key} and saved.")

        response = self.get_response(request)
        logger.info("Exiting OneSessionPerUserMiddleware __call__")
        return response


class DisableOptionsMiddleware:
    def __init__(self, get_response):
        logger.info("DisableOptionsMiddleware initializing")
        self.get_response = get_response
        logger.info("DisableOptionsMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering DisableOptionsMiddleware __call__")
        if request.method == "OPTIONS":
            logger.warning("Received OPTIONS request, returning HttpResponseNotAllowed.")
            return HttpResponseNotAllowed(["GET", "POST", "HEAD"])
        logger.info("Exiting DisableOptionsMiddleware __call__")
        return self.get_response(request)


class HSTSMiddleware:
    def __init__(self, get_response):
        logger.info("HSTSMiddleware initializing")
        self.get_response = get_response
        logger.info("HSTSMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering HSTSMiddleware __call__")
        response = self.get_response(request)
        response[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; preload"
        response["X-XSS-Protection"] = "1; mode=block"
        logger.info("Added HSTS and X-XSS-Protection headers.")
        logger.info("Exiting HSTSMiddleware __call__")
        return response


def decrypt_password(request):
    logger.info("Entering decrypt_password")
    if request.method in ["POST", "PUT", "PATCH"]:
        logger.info(f"Request method is {request.method}, proceeding with decryption.")
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
                logger.info(f"Decrypting password field: {key}")
                b64_encrypted_value = post_data[key]

                encrypted_value = base64.b64decode(b64_encrypted_value)
                decrypted_value = private_key.decrypt(
                    encrypted_value,
                    padding.PKCS1v15(),
                )
                decrypted_value = decrypted_value.decode("utf-8")
                request.POST[key] = decrypted_value
                logger.info(f"Decrypted {key} successfully.")
        request.POST._mutable = False
        logger.info("Exiting decrypt_password")


class RSAMiddleware:
    def __init__(self, get_response):
        logger.info("RSAMiddleware initializing")
        self.get_response = get_response
        logger.info("RSAMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering RSAMiddleware __call__")
        if "private_key" in request.session and not request.path.startswith("/api/"):
            logger.info("Private key found in session and not an API request, decrypting password.")
            decrypt_password(request)
        response = self.get_response(request)
        if "private_key" not in request.session:
            logger.info("Private key not found in session, generating new keys.")
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
            logger.info("Generated and stored new RSA key pair in session.")
            response.set_cookie(
                "rsa_public_key",
                request.session["public_key"],
                httponly=not settings.DEBUG,
            )
            logger.info("Set rsa_public_key cookie.")

        logger.info("Exiting RSAMiddleware __call__")
        return response


class CustomCSPMiddleware(CSPMiddleware):
    def __init__(self, get_response):
        logger.info("CustomCSPMiddleware initializing")
        self.get_response = get_response
        logger.info("CustomCSPMiddleware initialized")

    def process_response(self, request, response):
        logger.info("Entering CustomCSPMiddleware process_response")
        if request.path.startswith("/admin/api"):
            logger.info("Request path starts with /admin/api, skipping CSP processing.")
            return response
        logger.info("Processing CSP headers.")
        response = super().process_response(request, response)
        logger.info("Exiting CustomCSPMiddleware process_response")
        return response
