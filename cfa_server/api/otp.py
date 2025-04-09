import base64

import requests
from django.conf import settings
from pyotp import TOTP

OTP_VALIDITY_TIME: int = 5 * 60


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
    #url = "http://msg.msgclub.net/rest/services/sendSMS/sendGroupSms"
    url = "https://nimbusit.biz/api/SmsApi/SendSingleApi";
    """  params = {
        "AUTH_KEY": "eb77c1ab059d9eab77f37e1e2b4b87",
        "message": text,
        "senderId": "tmvict",
        "routeId": 8,
        "mobileNos": (mobile),
        "smsContentType": "english",
        "templateid": 1707169220338609309,
        "entityid": 1701169193114468940,
    }
    """
    params = {
           "UserID":"StateCouncilbiz",
           "Password":"nivf5520NI",
           "SenderID":"APCRIM",
           "Phno": (mobile),
           #"Msg": f"User Registration OTP for AP Crime Report is : 666661 AP Crime Team",
           "Msg":text,
           "EntityID": 1401463230000034964,
           "TemplateID": 1407173761078561168,
    }
   # with open("/cfa_server/api.log","w") as file:
    #    file.write(" ENTERING ")
    requests.get(url, params=params)
    #with open("/cfa_server/api.log","a") as file:
    #   file.write("OTP EXIT ")

def send_otp_verification_code(user, verification=True):
   # with open("/cfa_server/api.log","w") as file:
    #    file.write(" \nENTERING OTP VERIFICAITON CODE \n")
    otp_code = generate_otp(user)
    print(otp_code, "OTPPPPPPPPPPPPPPPP")

    if verification:
        text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"
        #text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"

    else:
        #text = f"Victory Trading Agency user registration authentication verification OTP is {otp_code}"
        text = f"User Registration OTP for AP Crime Report is: {otp_code} AP Crime Team"

    send_sms(user.mobile, text)
