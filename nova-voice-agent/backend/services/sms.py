"""
SMS Service - Sends confirmation messages via Twilio
"""
from twilio.rest import Client
from typing import Optional

from backend.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


async def send_confirmation_sms(
    to_phone: str,
    name: str,
    appointment_time: str
) -> bool:
    """
    Send SMS confirmation for booked appointment

    Args:
        to_phone: Customer phone number
        name: Customer name
        appointment_time: Formatted appointment time

    Returns:
        True if SMS sent successfully, False otherwise
    """
    try:
        print(f"📱 Sending SMS confirmation to {to_phone}...")

        # Create confirmation message
        message_body = f"""Hi {name}!

Your free consultation with Orbyn.ai is confirmed for {appointment_time}.

We'll call you at this number. Looking forward to speaking with you!

- The Orbyn.ai Team"""

        # Send SMS via Twilio
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"✅ SMS sent successfully! SID: {message.sid}")
        return True

    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        # Don't fail the booking if SMS fails
        return False


async def send_generic_sms(
    to_phone: str,
    message: str
) -> bool:
    """
    Send a generic SMS message

    Args:
        to_phone: Recipient phone number
        message: Message content

    Returns:
        True if SMS sent successfully, False otherwise
    """
    try:
        print(f"📱 Sending SMS to {to_phone}...")

        sms = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )

        print(f"✅ SMS sent! SID: {sms.sid}")
        return True

    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return False
