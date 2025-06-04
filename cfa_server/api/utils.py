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
from api.models import LostVehicle

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
                return cases.distinct()
            # SP level (rank 9)
            elif rank == 9:
                logger.info(f"Exiting SP level logic for officer: {officer}")
                return cases.filter(
                    Q(pid__did_id=officer.pid.did_id) | Q(type="vehicle") |Q(user= user)
                ).distinct()
            # DySP level (rank 6)
            elif rank == 6:
                logger.info(f"Exiting DySP level logic for officer: {officer}")
                stations = officer.policestation_supervisor.values("station")
                return cases.filter(
                    Q(pid_id__in=stations) | Q(type="vehicle") | Q(user=user)
                ).distinct()
            # Inspector level (rank 5)
            elif rank == 5:
                logger.info(f"Exiting Inspector level logic for officer: {officer}")
                return cases.filter(
                    Q(pid_id=officer.pid_id) | Q(type="vehicle") | Q(user = user)
                ).distinct()
            # SI level (rank 4)
            elif rank == 4:
                logger.info(f"Exiting SI level logic for officer: {officer}")
                return cases.filter(
                    #(Q(oid=officer) & ~Q(cstate="pending")) | Q(type="vehicle") | Q(user=user)
                    (Q(oid=officer) | Q(type="vehicle") | Q(user=user))
                ).distinct()
            # Junior officers
            else:
                logger.info(f"Exiting Junior officer logic for officer: {officer}")
                return cases.filter(
                    Q(user=user) | Q(type="vehicle")
                ).distinct()
        else:
            # Police role but no officer record
            logger.info(f" Exiting with no officer record for: {user.username}")
            return cases.filter(
                Q(user=user) | Q(type="vehicle")
            ).distinct()
    elif getattr(user, "role", None) == "SNO":
        logger.info(f"Exiting SNO user logic for user: {user.username}")
        return cases.filter(
            Q(type="drug") | Q(type="vehicle") | Q(user=user)
        ).distinct()
    elif getattr(user, "is_user", False) or getattr(user, "role", None) == "user":
        logger.info(f"Exiting Regular user logic for user: {user.username}")
        return cases.filter(
            Q(user=user) | Q(type="vehicle")
        ).distinct()
    elif getattr(user, "role", None) == "admin" or getattr(user, "is_superuser", False):
        logger.info(f"Exiting Admin user logic for user: {user.username}")
        return cases.distinct()
    # Default: return nothing
    logger.info(f"Exiting with no matching role for user: {user.username}")
    return cases.none()

from django.conf import settings

def get_media_url(media_path):
    """
    Returns the absolute URL for a media file.
    """
    domain = getattr(settings, "DOMAIN_URL", "").rstrip("/")
    media_url = getattr(settings, "MEDIA_URL", "/media/").rstrip("/")
    rel_path = media_path.lstrip("/")
    return f"{domain}{media_url}/{rel_path}"

def generate_pdf_from_cases(cases, output_path):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    import logging
    from django.utils.dateparse import parse_datetime

    logger = logging.getLogger(__name__)
    styles = getSampleStyleSheet()
    Story = []

    Story.append(Paragraph("Case Report", styles["Title"]))
    Story.append(Spacer(1, 12))

    for case in cases:
        Story.append(Paragraph(f"---Case No: {case.get('cid', '')} starts---", styles["Heading2"]))
        Story.append(Spacer(1, 6))

        entry_date = case.get("created") or case.get("entry_date") or case.get("date") or ""
        if entry_date:
            Story.append(Paragraph(f"<b>Reported on:</b> {entry_date}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        # Police Station Name
        police_station = ""
        pid = case.get("pid")
        if isinstance(pid, dict):
            police_station = pid.get("name", "")
        elif hasattr(pid, "name"):
            police_station = getattr(pid, "name", "")
        elif pid:
            try:
                from api.models import PoliceStation
                police_station_obj = PoliceStation.objects.filter(pk=pid).only("name").first()
                if police_station_obj:
                    police_station = police_station_obj.name
            except Exception:
                police_station = ""
        if police_station:
            Story.append(Paragraph(f"<b>Police Station:</b> {police_station}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        # Case Location
        lat = case.get("lat", "")
        long = case.get("long", "")
        if lat and long:
            Story.append(Paragraph(f"<b>Location:</b> Latitude: {lat}, Longitude: {long}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        Story.append(Paragraph(f"<b>Type:</b> {case.get('type', '')}", styles["Normal"]))
        Story.append(Spacer(1, 6))
        Story.append(Paragraph(f"<b>Status:</b> {case.get('cstate', '')}", styles["Normal"]))
        Story.append(Spacer(1, 6))        
        if case.get("description"):
            Story.append(Paragraph(f"<b>Description:</b> {case['description']}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        # LostVehicle details (already fetched in your data, do NOT query here)
        if case.get("type", "") == "vehicle" and case.get("lost_vehicle"):
            lost_vehicle = case["lost_vehicle"]
            Story.append(Paragraph("<b>Vehicle Details:</b>", styles["Heading3"]))
            Story.append(Paragraph(f"Registration Number: {lost_vehicle.get('regNumber', '')}", styles["Normal"]))
            Story.append(Paragraph(f"Engine Number: {lost_vehicle.get('EngineNumber', '')}", styles["Normal"]))
            Story.append(Paragraph(f"Chassis Number: {lost_vehicle.get('ChassisNumber', '')}", styles["Normal"]))
            Story.append(Paragraph(f"Make: {lost_vehicle.get('Make', '')}", styles["Normal"]))
            Story.append(Paragraph(f"Model: {lost_vehicle.get('Model', '')}", styles["Normal"]))
            Story.append(Paragraph(f"Color: {lost_vehicle.get('Color', '')}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        # --- CASE MEDIA SECTION ---
        Story.append(Paragraph(f"<u>Medias</u>", styles["Heading2"]))
        for media in case.get("medias", []):
            mtype = media.get("mtype")
            path = media.get("path")
            Story.append(Paragraph(f"{mtype.capitalize()} Path: {path}", styles["Normal"]))
            Story.append(Spacer(1, 6))

        # --- HISTORY RECORDS ---
        Story.append(Paragraph("<u>History</u>", styles["Heading2"]))
        for hist in case.get("history", []):
            Story.append(Spacer(1, 6))
            entry_date = hist.get('created', '')
            content = hist.get('content', '')
            formatted_date = ""
            if entry_date:
                try:
                    if hasattr(entry_date, "strftime"):
                        formatted_date = entry_date.strftime('%d/%m/%Y %I:%M %p')
                    else:                        
                        dt = parse_datetime(str(entry_date))
                        if dt:
                            formatted_date = dt.strftime('%d/%m/%Y %I:%M %p')
                        else:
                            formatted_date = str(entry_date)
                except Exception:
                    formatted_date = str(entry_date)
            user_role = ""
            user_obj = hist.get("user", None)
            if user_obj and hasattr(user_obj, "role"):
                user_role = getattr(user_obj, "role", "")
            elif isinstance(user_obj, dict) and "role" in user_obj:
                user_role = user_obj["role"]
            Story.append(Paragraph(f"<b>Date:</b>{formatted_date}", styles["Normal"]))
            Story.append(Paragraph(f"<b>Status:</b> {hist.get('cstate', '')}", styles["Normal"]))
            Story.append(Paragraph(f"<b>Description:</b> {content} {user_role}", styles["Normal"]))
            for hmedia in hist.get("medias", []):
                hmtype = hmedia.get("mtype")
                hpath = hmedia.get("path")
                Story.append(Paragraph(f"{hmtype.capitalize()} Path: {hpath}", styles["Normal"]))
            Story.append(HRFlowable(width="100%", thickness=0.2, color="black", spaceBefore=10, spaceAfter=10))

        # --- COMMENT RECORDS ---
        Story.append(Paragraph(f"<u>Comments</u>", styles["Heading2"]))
        for comment in case.get("comments", []):
            Story.append(Spacer(1, 6))
            entry_date = comment.get('created', '')
            content = comment.get('content', '')
            user_role = ""
            user_obj = comment.get("user", None)
            if user_obj and hasattr(user_obj, "role"):
                user_role = getattr(user_obj, "role", "")
            elif isinstance(user_obj, dict) and "role" in user_obj:
                user_role = user_obj["role"]
            Story.append(
                Paragraph(
                    f"<b>Date: </b>{formatted_date}: <br/>"
                    f"{content} "
                    f"{user_role}",
                    styles["Normal"]
                )
            )
            for cmedia in comment.get("medias", []):
                cmtype = cmedia.get("mtype")
                cpath = cmedia.get("path")
                Story.append(Paragraph(f"{cmtype.capitalize()} Path: {cpath}", styles["Normal"]))
            Story.append(HRFlowable(width="100%", thickness=0.2, color="black", spaceBefore=10, spaceAfter=10))

        Story.append(Paragraph(f"---Case No: {case.get('cid', '')} ends---", styles["Heading2"]))
        Story.append(PageBreak())

    try:
        doc = SimpleDocTemplate(output_path, pagesize=LETTER)
        doc.build(Story)
        logger.info(f"PDF successfully generated at: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise


from api.models import Media, CaseHistory, Comment
import logging

logger = logging.getLogger(__name__)


def append_media(data):
    """
    Append media records for each Case.
    Media objects with:
        - source == "case" 
        - parentId in Case.cid
    are attached under the key "medias" in each case dictionary.
    """
    logger.info("Appending media for cases")
    case_ids = [item["cid"] for item in data]
    medias = Media.objects.filter(source="case", parentId__in=case_ids)
    media_dict = {}
    for media in medias:
        parent = media.parentId
        if parent not in media_dict:
            media_dict[parent] = []
        media_dict[parent].append({
            "mtype": media.mtype,
            "path": "/media/" + media.path.name if media.path else None,
        })
    for item in data:
        item["medias"] = media_dict.get(item["cid"], [])
    return data


def append_history(data):
    """
    Append history records for each Case.
    History records are obtained by filtering CaseHistory objects where:
        - case (foreign key) points to a Case whose cid is in the data.
    Each history record is attached (with its id) under the key "history".
    """
    logger.info("Appending history records to response")
    case_ids = [item["cid"] for item in data]
    histories = CaseHistory.objects.filter(case__cid__in=case_ids)
    history_dict = {}
    for hist in histories:
        # Use hist.case.cid as our grouping key. Also include hist.id for reference.
        key = hist.case.cid
        history_dict.setdefault(key, []).append({
            "id": hist.id,               # primary key of the history record
            "content": hist.description, # using description field (change to hist.content if needed)
            "created": hist.created,
            "cstate": hist.cstate,
        })
    for item in data:
        item["history"] = history_dict.get(item["cid"], [])
    return data


def append_history_medias(data):
    """
    For each history record in each case, attach media where:
        - media.source == "history" and
        - media.parentId equals the history record's id.
    The media list is added under the key "medias" of each history record.
    """
    logger.info("Appending history medias to response")
    history_ids = []
    for case in data:
        for hist in case.get("history", []):
            if "id" in hist:
                history_ids.append(hist["id"])
    medias = Media.objects.filter(source="history", parentId__in=history_ids)
    history_media_dict = {}
    for media in medias:
        history_media_dict.setdefault(media.parentId, []).append({
            "mtype": media.mtype,
            "path": "/media/" + media.path.name if media.path else None,
        })
    for case in data:
        for hist in case.get("history", []):
            history_id = hist.get("id")
            hist["medias"] = history_media_dict.get(history_id, [])
    return data


def append_comments(data):
    """
    Append comment records for each Case.
    Comments are obtained by filtering Comment objects where:
        - Comment.cid (foreign key to Case) is in the provided cases.
    They are attached under the key "comments" in each case dictionary.
    """
    logger.info("Appending comments to response")
    case_ids = [item["cid"] for item in data]
    # Since the foreign key field in Comment is 'cid', filter by that
    comments = Comment.objects.filter(cid__cid__in=case_ids)
    comment_dict = {}
    for comment in comments:
        key = comment.cid.cid  # comment.cid is a Case instance
        comment_dict.setdefault(key, []).append({
            "cmtid": comment.cmtid,
            "content": comment.content,
            "created": comment.created,
        })
    for item in data:
        item["comments"] = comment_dict.get(item["cid"], [])
    return data


def append_comment_medias(data):
    """
    For each comment in each case, attach media records where:
         - media.source == "comment" and
         - media.parentId equals comment.cmtid.
    These are attached under the key "medias" for each comment record.
    """
    logger.info("Appending comment medias to response")
    comment_ids = []
    for case in data:
        for comment in case.get("comments", []):
            if "cmtid" in comment:
                comment_ids.append(comment["cmtid"])
    medias = Media.objects.filter(source="comment", parentId__in=comment_ids)
    comment_media_dict = {}
    for media in medias:
        comment_media_dict.setdefault(media.parentId, []).append({
            "mtype": media.mtype,
            "path": "/media/" + media.path.name if media.path else None,
        })
    for case in data:
        for comment in case.get("comments", []):
            cid = comment.get("cmtid")
            comment["medias"] = comment_media_dict.get(cid, [])
    return data


def build_case_list_with_details(data):
    """
    Combine the case data with associated medias, history records (and their medias),
    and comment records (and their medias).
    
    Expected structure:
        - Each case dict must have "cid" key.
        - This function augments each case with:
              "medias"    => from Media with source "case"
              "history"   => a list of history dicts attached using CaseHistory
                              Each history dict gets a "medias" key attached from Media with source "history".
              "comments"  => a list of comment dicts attached using Comment
                              Each comment dict gets a "medias" key attached from Media with source "comment".
    """
    data = append_media(data)
    data = append_history(data)
    data = append_history_medias(data)
    data = append_comments(data)
    data = append_comment_medias(data)
    return data

# Example usage:
# cases = get_cases(user, case_type="drug")
# data = [case.to_dict() for case in cases]  # or however you serialize your case objects to dicts
# detailed_data = build_case_list_with_details(data)

def get_local_media_path(path):
    """
    Converts a media URL path (e.g. /media/uploads/...) to a local filesystem path (./media/uploads/...)
    """
    if path and path.startswith("/media/"):
        return "." + path
    return path
