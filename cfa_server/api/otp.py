import base64

import requests
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pyotp import TOTP

OTP_VALIDITY_TIME: int = 60 * 15


def get_base32_key(user) -> str:
    key = settings.SECRET_KEY + str(user.pk)
    key = bytes(key, encoding="UTF-8")
    val = base64.b32encode(key)
    val = str(val)
    return val.split("'")[1]


def generate_otp(user, digits=4) -> int:
    base32_key = get_base32_key(user)
    otp = TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).now()
    return otp


def validate_otp(user, otp: int, digits=4) -> bool:
    base32_key = get_base32_key(user)
    return TOTP(base32_key, interval=OTP_VALIDITY_TIME, digits=digits).verify(otp)


def send_otp_verification_code(user):
    otp_code = generate_otp(user)
    print(otp_code, 'OTPPPPPPP')
    text = f"{otp_code}. Use this opt code to verify your mobile"
    url = "http://msg.msgclub.net/rest/services/sendSMS/sendGroupSms"
    params = {
        "AUTH_KEY": "eb77c1ab059d9eab77f37e1e2b4b87",
        "message": text,
        "senderId": "mnwalk",
        "routeId": 8,
        "mobileNos": f'{user.mobile}',
        "smsContentType": "english"
    }

    requests.post(url, json=params)
