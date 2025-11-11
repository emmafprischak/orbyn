"""
Calendar Service - Handles appointment booking via Cal.com API
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx

from backend.config import (
    CAL_API_KEY,
    CAL_API_BASE,
    CAL_EVENT_TYPE,
    DEFAULT_TIMEZONE,
    HTTP_TIMEOUT
)


async def get_available_slots() -> List[str]:
    """
    Get available appointment slots from Cal.com

    Returns:
        List of available time slots as formatted strings
    """
    try:
        print("📅 Fetching available slots from Cal.com...")

        # Calculate date range (next 7 days)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        # Format dates for API
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Build API URL
        url = f"{CAL_API_BASE}/slots"
        params = {
            "startTime": start_str,
            "endTime": end_str,
            "eventTypeId": CAL_EVENT_TYPE,
        }

        headers = {
            "Authorization": f"Bearer {CAL_API_KEY}",
            "Content-Type": "application/json"
        }

        # Make API request
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                slots = data.get("slots", [])

                if slots:
                    # Format first 5 slots for voice
                    formatted_slots = []
                    for slot in slots[:5]:
                        dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
                        # Format for natural speech: "Friday at 10 AM"
                        formatted = dt.strftime("%A at %I %p").replace(" 0", " ")
                        formatted_slots.append(formatted)

                    print(f"✅ Found {len(formatted_slots)} available slots")
                    return formatted_slots

            print(f"⚠️ Cal.com API returned status {response.status_code}")

    except Exception as e:
        print(f"❌ Error fetching Cal.com slots: {e}")

    # Fallback: Return dynamic sample slots
    print("📅 Using fallback slots (Cal.com unavailable)")
    return get_fallback_slots()


def get_fallback_slots() -> List[str]:
    """
    Generate fallback appointment slots when Cal.com is unavailable

    Returns:
        List of formatted time slot strings
    """
    # Generate slots for tomorrow and day after
    tomorrow = datetime.now() + timedelta(days=1)
    day_after = datetime.now() + timedelta(days=2)

    slots = [
        tomorrow.replace(hour=10, minute=0).strftime("%A at %I %p").replace(" 0", " "),
        tomorrow.replace(hour=14, minute=0).strftime("%A at %I %p").replace(" 0", " "),
        day_after.replace(hour=10, minute=0).strftime("%A at %I %p").replace(" 0", " "),
        day_after.replace(hour=14, minute=0).strftime("%A at %I %p").replace(" 0", " "),
        day_after.replace(hour=16, minute=0).strftime("%A at %I %p").replace(" 0", " "),
    ]

    return slots


async def book_appointment(
    name: str,
    email: Optional[str],
    phone: str,
    start_time: str,
    notes: str = ""
) -> Dict[str, any]:
    """
    Book an appointment via Cal.com API

    Args:
        name: Customer name
        email: Customer email (optional)
        phone: Customer phone
        start_time: Appointment time (ISO format or human readable)
        notes: Additional notes

    Returns:
        Dict with booking status and details
    """
    try:
        print(f"📅 Booking appointment for {name}...")

        # Use email or generate placeholder
        booking_email = email if email else f"{phone.replace('+', '').replace('-', '')}@placeholder.com"

        url = f"{CAL_API_BASE}/bookings"

        headers = {
            "Authorization": f"Bearer {CAL_API_KEY}",
            "Content-Type": "application/json"
        }

        # Prepare booking data
        booking_data = {
            "eventTypeId": CAL_EVENT_TYPE,
            "start": start_time,
            "responses": {
                "name": name,
                "email": booking_email,
                "phone": phone,
                "notes": notes
            },
            "timeZone": DEFAULT_TIMEZONE,
            "language": "en",
            "metadata": {
                "source": "nova-voice-agent"
            }
        }

        # Make API request
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(url, json=booking_data, headers=headers)

            if response.status_code in [200, 201]:
                data = response.json()
                print(f"✅ Appointment booked successfully!")

                return {
                    "success": True,
                    "booking_id": data.get("id"),
                    "start_time": start_time,
                    "message": "Appointment confirmed"
                }
            elif response.status_code == 401:
                print(f"⚠️ Cal.com authentication failed (401)")
            else:
                print(f"⚠️ Cal.com booking failed with status {response.status_code}")
                print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error booking appointment: {e}")

    # Fallback: Mark as pending manual scheduling
    print("📅 Marking appointment as PENDING (will schedule manually)")
    return {
        "success": False,
        "booking_id": None,
        "start_time": start_time,
        "message": "Appointment pending - will be scheduled manually",
        "status": "pending"
    }


def format_slots_for_speech(slots: List[str], max_slots: int = 3) -> str:
    """
    Format available slots into natural speech

    Args:
        slots: List of formatted time slots
        max_slots: Maximum number of slots to present

    Returns:
        Natural language string describing available slots
    """
    if not slots:
        return "I don't have any available slots right now."

    # Take first N slots
    selected_slots = slots[:max_slots]

    if len(selected_slots) == 1:
        return f"I have an opening on {selected_slots[0]}."
    elif len(selected_slots) == 2:
        return f"I have openings on {selected_slots[0]}, or {selected_slots[1]}."
    else:
        # Join all but last with commas, last with "or"
        all_but_last = ", ".join(selected_slots[:-1])
        return f"I have openings on {all_but_last}, or {selected_slots[-1]}."
