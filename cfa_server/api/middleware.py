from django.contrib.sessions.models import Session
from django.http import HttpResponseNotAllowed
from csp.middleware import CSPMiddleware
from django.conf import settings

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
from django.http import HttpResponse, HttpResponseRedirect
from urllib.parse import urlparse, parse_qs, urlencode
from api.models import LoggedInUser
import logging

logger = logging.getLogger(__name__)


class OneSessionPerUserMiddleware:
    async_capable = False

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
            logger.info(
                f"User {request.user.username} is authenticated, checking session."
            )
            logged_in_user, created = LoggedInUser.objects.get_or_create(
                user=request.user,
                defaults={"session_key": request.session.session_key},
            )
            if created:
                request.user.logged_in_user = logged_in_user
                logger.info(
                    f"Created logged_in_user for {request.user.username} with session key {request.session.session_key}."
                )
            stored_session_key = request.user.logged_in_user.session_key
            logger.info(
                f"Stored session key for user {request.user.username}: {stored_session_key}"
            )

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            if stored_session_key and stored_session_key != request.session.session_key:
                logger.info(
                    f"Stored session key is different from current session key, deleting old session."
                )
                session = Session.objects.filter(session_key=stored_session_key).first()
                if session:
                    session.delete()
                    logger.info(f"Deleted old session with key {stored_session_key}.")

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()
            logger.info(
                f"Updated logged_in_user session key to {request.session.session_key} and saved."
            )

        response = self.get_response(request)
        logger.info(f"Exiting OneSessionPerUserMiddleware __call__ with response : {response}")
        return response


class DisableOptionsMiddleware:
    async_capable = False

    def __init__(self, get_response):
        logger.info("DisableOptionsMiddleware initializing")
        self.get_response = get_response
        logger.info("DisableOptionsMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering DisableOptionsMiddleware __call__")
        if request.method == "OPTIONS":
            logger.warning(
                "Received OPTIONS request, returning HttpResponseNotAllowed."
            )
            return HttpResponseNotAllowed(["GET", "POST", "HEAD"])
        response = self.get_response(request)
        logger.info(f"Exiting DisableOptionsMiddleware __call__ with response :{response}")
        #return self.get_response(request)
        return response


class HSTSMiddleware:
    async_capable = False

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
        logger.info(f"Exiting HSTSMiddleware __call__ with response :{response}")
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
        try:
            private_key_pem_b64 = request.session["private_key"]
            private_key_pem = base64.b64decode(private_key_pem_b64)
            private_key = serialization.load_pem_private_key(private_key_pem, password=None)
            request.POST._mutable = True
            post_data = request.POST.copy()
            for key in password_fields:
                if key in post_data.keys():
                    logger.info(f"Decrypting password field: {key}")
                    b64_encrypted_value = post_data[key]

                    encrypted_value = base64.b64decode(b64_encrypted_value)
                    try:
                        decrypted_value = private_key.decrypt(
                            encrypted_value,
                            padding.PKCS1v15(),
                        )
                        decrypted_value = decrypted_value.decode("utf-8")
                        post_data[key] = decrypted_value
                    except Exception as e:
                        logger.error(f"Failed to decrypt {key}: {e}")
                    logger.info(f"Decrypted {key} successfully.")
        except Exception as ex:
            logger.info(f"Description error : {str(ex)}")
        request.POST = post_data
        request.POST._mutable = False
    logger.info(f"Exiting decrypt_password with request data: {request.POST}")


class RSAMiddleware:
    async_capable = False

    def __init__(self, get_response):
        logger.info("RSAMiddleware initializing")
        self.get_response = get_response
        logger.info("RSAMiddleware initialized")

    def __call__(self, request):
        logger.info("Entering RSAMiddleware __call__")
        #if request.path.startswith("/login") or request.path.startswith("/account/login"):
            #return self.get_response(request)
        #if "private_key" in request.session and not request.path.startswith("/api/"):
        if request.path.startswith("favicon.ico"):
            return self.get_response(request)
        if "private_key" in request.session and not request.path.startswith("/api/"):
            logger.info(
                "Private key found in session and not an API request, decrypting password."
            )
            decrypt_password(request)
        else:
            logger.info(f" RSAMiddleware __call__. private_key {request.session} path : {request.path}")
        response = self.get_response(request)
        # loop break code starts
        if(isinstance(response,HttpResponseRedirect) and response.url.startswith("/login")):
            parsed = urlparse(response.url)
            qs = parse_qs(parsed.query)
            next_param = qs.get("next",[""])[0]
            if next_param.startswith("/login"):
                logger.warning("detected recursive login redirect. Breaking the loop")
                response = HttpResponseRedirect("/login/")
        # loop break code ends

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
                secure=True,
            )
            logger.info("Set rsa_public_key cookie.")
        logger.info(f"Exiting RSAMiddleware __call__ with response :{response} and request :{request}")
        return response

class CustomCSPMiddleware(CSPMiddleware):
    async_capable = False

    def __init__(self, get_response):
        super().__init__(get_response)
        logger.info("CustomCSPMiddleware initializing")

    def process_response(self, request, response):
        logger.info(f"Entering CustomCSPMiddleware process_response with response: {response}")
        if isinstance(response, HttpResponseRedirect):
            if not response.url:
                return HttpResponse("No redirect needed ",status=200)
        if request.path.startswith("/admin/api"):
            logger.info("Request path starts with /admin/api, skipping CSP processing.")
            return response
        logger.info("Processing CSP headers.")
        response = super().process_response(request, response)
        logger.info(f"Exiting CustomCSPMiddleware process_response with response :{response}")
        return response
