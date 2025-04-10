import base64
import requests
from django.conf import settings
from pyotp import TOTP
import logging

logger = logging.getLogger(__name__)

OTP_VALIDITY_TIME: int = 5 * 60

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
    logger.info(f"Generating {digits}-digit OTP for user: {user.mobile}")
    
    base32_key = get_base32_key(user)
    otp = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).now()
    
    logger.info(f"Generated OTP validity time: {OTP_VALIDITY_TIME} seconds")
    logger.info("Exiting generate_otp")
    return otp

def validate_otp(user, otp: int, digits=6) -> bool:
    logger.info("Entering validate_otp")
    logger.info(f"Validating {digits}-digit OTP for user: {user.mobile}")
    
    base32_key = get_base32_key(user)
    is_valid = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).verify(otp)
    
    if is_valid:
        logger.info(f"OTP validation successful for user: {user.mobile}")
    else:
        logger.warning(f"OTP validation failed for user: {user.mobile}")
    
    logger.info("Exiting validate_otp")
    return is_valid

def send_sms(mobile, text):
    logger.info("Entering send_sms")
    logger.info(f"Sending SMS to mobile: {mobile[:6]}****")
    
    url = "https://nimbusit.biz/api/SmsApi/SendSingleApi"
    params = {
           "UserID":"StateCouncilbiz",
           "Password":"nivf5520NI",
           "SenderID":"APCRIM",
           "Phno": (mobile),
           "Msg":text,
           "EntityID": 1401463230000034964,
           "TemplateID": 1407173761078561168,
    }
    requests.get(url, params=params)
    logger.info("Exiting send_sms")

def send_otp_verification_code(user, verification=True):
    otp_code = generate_otp(user)
    logger.info(f"Generated OTP: {otp_code} for user: {user.mobile}")

    if verification:
        text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"
    else:
        text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"

    send_sms(user.mobile, text)
    logger.info("Exiting send_otp_verification_code")
