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
from api.models import *

from django.db.models import Q, OuterRef, Exists, Count, Case as MCase, When
#from api.models import Case, Like

import logging
logger = logging.getLogger(__name__)

class CustomBackend(ModelBackend):
    def authenticate(self, request, username, password, **kwargs):
        logger.info("Entering authenticate with username: %s", username)
        if request.path.startswith("/api/v1"):
            return super().authenticate(request, username, password, **kwargs)

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
        logger.info(f("Exiting authenticate with username: {username}"))
        return super().authenticate(request, username, password, **kwargs)




def get_cases(user, base_queryset=None, case_type=None, my_complaints=False):
    """
    Return case records based on user role and permissions:
    1. Regular users: See their own cases plus all vehicle cases
    2. Police officers: See cases they reported or are assigned to with can_act=True plus all vehicle cases
    3. District-level officers (rank 6-10): See all cases in their district with can_act=False plus all vehicle cases
    4. Senior officers (rank>10) or admins: See all cases with can_act=False
    """
    logger.info("Entering get_cases for user: %s", user.username)
    if base_queryset is None:
        cases = Case.objects.all()
    else:
        cases = base_queryset

    # Filter by case type if provided
    if case_type:
        cases = cases.filter(type=case_type)

    # Filter for my-complaints if requested
    if my_complaints:
        cases = cases.filter(user=user)

    # Add liked annotation
    liked = Like.objects.filter(case_id=OuterRef("cid"), user=user)
    cases = cases.annotate(has_liked=Exists(liked))

    # Role-based filtering
    if hasattr(user, "is_police") and user.is_police:
        logger.info(f" User is a police officer: {user}")
        officer = user.policeofficer_set.first()
        if officer:
            rank = int(officer.rank)
            # Senior officers (rank > 9): See all cases
            if rank > 9:
                return cases
            # SP level (rank 9)
            elif rank == 9:
                logger.info(f"Exiting SP level logic for officer: {officer}")
                return cases.filter(
                    Q(pid__did_id=officer.pid.did_id) | Q(type="vehicle") |Q(user= user)
                )
            # DySP level (rank 6)
            elif rank == 6:
                logger.info(f"Exiting DySP level logic for officer: {officer}")
                stations = officer.policestation_supervisor.values("station")
                return cases.filter(
                    Q(pid_id__in=stations) | Q(type="vehicle") | Q(user=user)
                )
            # Inspector level (rank 5)
            elif rank == 5:
                logger.info(f"Exiting Inspector level logic for officer: {officer}")
                return cases.filter(
                    Q(pid_id=officer.pid_id) | Q(type="vehicle") | Q(user = user)
                )
            # SI level (rank 4)
            elif rank == 4:
                logger.info(f"Exiting SI level logic for officer: {officer}")
                return cases.filter(
                    #(Q(oid=officer) & ~Q(cstate="pending")) | Q(type="vehicle") | Q(user=user)
                    (Q(oid=officer) | Q(type="vehicle") | Q(user=user))
                )
            # Junior officers
            else:
                logger.info(f"Exiting Junior officer logic for officer: {officer}")
                return cases.filter(
                    Q(user=user) | Q(type="vehicle")
                )
        else:
            # Police role but no officer record
            logger.info(f" Exiting with no officer record for: {user.username}")
            return cases.filter(
                Q(user=user) | Q(type="vehicle")
            )
    elif getattr(user, "role", None) == "SNO":
        logger.info(f"Exiting SNO user logic for user: {user.username}")
        return cases.filter(
            Q(type="drug") | Q(type="vehicle") | Q(user=user)
        )
    elif getattr(user, "is_user", False) or getattr(user, "role", None) == "user":
        logger.info(f"Exiting Regular user logic for user: {user.username}")
        return cases.filter(
            Q(user=user) | Q(type="vehicle")
        )
    elif getattr(user, "role", None) == "admin" or getattr(user, "is_superuser", False):
        logger.info(f"Exiting Admin user logic for user: {user.username}")
        return cases
    # Default: return nothing
    logger.info(f"Exiting with no matching role for user: {user.username}")
    return cases.none()
