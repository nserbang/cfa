import base64
import requests
from django.conf import settings
from pyotp import TOTP
import logging

logger = logging.getLogger(__name__)

OTP_VALIDITY_TIME = 5 * 60  # 5 minutes


def get_base32_key(user) -> str:
    logger.info("Entering get_base32_key")
    logger.debug(f"Generating base32 key for user_id: {user.pk}")

    key = settings.SECRET_KEY + str(user.pk)
    key = bytes(key, encoding="UTF-8")
    val = base64.b32encode(key)
    val = str(val)
    result = val.split("'")[1]

    logger.debug(f"Generated base32 key length: {len(result)}")
    logger.info("Exiting get_base32_key")
    return result


def generate_otp(user, digits=6) -> int:
    logger.info("Entering generate_otp")
    base32_key = get_base32_key(user)
    otp = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).now()
    logger.info(f"Generated OTP for {user.mobile}: {otp}")
    logger.info("Exiting generate_otp")
    return otp


def validate_otp(user, otp: int, digits=6) -> bool:
    logger.info("Entering validate_otp")
    base32_key = get_base32_key(user)
    is_valid = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).verify(otp)
    logger.info(f"OTP validation {'succeeded' if is_valid else 'failed'} for {user.mobile}")
    logger.info("Exiting validate_otp")
    return is_valid


def send_sms(mobile: str, message: str, template_id: str):
    logger.info(f"Sending SMS to {mobile[:6]}**** with Template ID {template_id}")
    params = {
        "UserID": settings.SMS_USER_ID,
        "Password": settings.SMS_PASSWORD,
        "SenderID": settings.SMS_SENDER_ID,
        "Phno": mobile,
        "Msg": message,
        "EntityID": settings.SMS_ENTITY_ID,
        "TemplateID": template_id,
    }

    try:
        response = requests.get(settings.SMS_URL, params=params, timeout=10)
        logger.info(f"SMS sent. Status: {response.status_code}")
        logger.debug(f"SMS response: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Error sending SMS: {e}")


# 1️⃣ Vehicle Found SMS
def send_vehicle_found_sms(mobile: str, RegNo: str, policestation: str):
    message = f"Vehicle No. {RegNo} found at {policestation} police station. From Arunachal Pradesh Police"
    send_sms(mobile, message, settings.TEMPLATE_VEHICLE)


# 2️⃣ New Case SMS
def send_new_case_sms(mobile: str, case_number: str, case_type: str, police_station: str, date: str, time: str):
    message = (
        f"New case No. {case_number} of type: {case_type} reported at {police_station} police station "
        f"on {date} at {time}. From Arunachal Pradesh Police"
    )
    send_sms(mobile, message, settings.TEMPLATE_NEW_CASE)


# 3️⃣ Case Status Update SMS
def send_case_status_sms(mobile: str, case_number: str, status: str):
    message = (
        f"Your case No {case_number} status is changed to {status}. "
        f"For details, please visit Arunachal Crime Report App.\nFrom AP Crime Team"
    )
    send_sms(mobile, message, settings.TEMPLATE_CASE_STATUS)


# 4️⃣ OTP SMS
def send_otp_verification_code(user, verification=True):
    otp_code = generate_otp(user)
    message = f"User Registration OTP for AP Crime Report is: {otp_code}\nAP Crime Team"
    send_sms(user.mobile, message, settings.TEMPLATE_OTP)
