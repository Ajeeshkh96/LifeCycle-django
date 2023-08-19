from __future__ import annotations

from django.conf import settings
from twilio.rest import Client


def send_otp(phone_number):
    # otp = str(random.randint(100000, 999999))

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    verification = client.verify.v2.services(
        settings.TWILIO_VERIFY_SID
    ).verifications.create(to=phone_number, channel="sms")

    print(verification.status)
    return verification