import base64

import requests
from django.conf import settings
from pyotp import TOTP

OTP_VALIDITY_TIME: int = 60 * 15


def get_base32_key(user) -> str:
    key = settings.SECRET_KEY + str(user.pk)
    key = bytes(key, encoding="UTF-8")
    val = base64.b32encode(key)
    val = str(val)
    return val.split("'")[1]


def generate_otp(user, digits=6) -> int:
    base32_key = get_base32_key(user)
    otp = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).now()
    return otp


def validate_otp(user, otp: int, digits=6) -> bool:
    base32_key = get_base32_key(user)
    return TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).verify(otp)


def send_sms(mobile, text):
    url = "http://msg.msgclub.net/rest/services/sendSMS/sendGroupSms"
    params = {
        "AUTH_KEY": "eb77c1ab059d9eab77f37e1e2b4b87",
        "message": text,
        "senderId": "tmvict",
        "routeId": 8,
        "mobileNos": (mobile),
        "smsContentType": "english",
        "templateid": 1707169220338609309,
        "entityid": 1701169193114468940,
    }
    requests.get(url, params=params)


def send_otp_verification_code(user, verification=True):
    otp_code = generate_otp(user)
    print(otp_code, "OTPPPPPPPPPPPPPPPP")

    if verification:
        text = f"Victory Trading Agency user registration authentication verification OTP is {otp_code}"
    else:
        text = f"Victory Trading Agency user registration authentication verification OTP is {otp_code}"

    send_sms(user.mobile, text)
