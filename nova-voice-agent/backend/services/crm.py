"""
CRM Service - Logs leads to Notion database
"""
from typing import Optional
import httpx

from backend.config import (
    NOTION_TOKEN,
    NOTION_DATABASE_ID,
    NOTION_VERSION,
    HTTP_TIMEOUT
)


async def create_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    service: Optional[str] = None,
    status: str = "new",
    appointment_time: Optional[str] = None,
    notes: str = "",
    call_sid: Optional[str] = None
) -> bool:
    """
    Create a new lead entry in Notion database

    Args:
        name: Customer name
        phone: Customer phone number
        email: Customer email (optional)
        service: Service interest (optional)
        status: Lead status (default: "new")
        appointment_time: Scheduled appointment time (optional)
        notes: Additional notes
        call_sid: Twilio Call SID for reference

    Returns:
        True if lead created successfully, False otherwise
    """
    try:
        print(f"📝 Creating Notion lead for {name}...")

        # Build notes with call information
        full_notes = notes
        if call_sid:
            full_notes = f"Call SID: {call_sid}\n{notes}" if notes else f"Call SID: {call_sid}"
        if appointment_time:
            full_notes = f"{full_notes}\nAppointment: {appointment_time}"

        # Notion API endpoint
        url = "https://api.notion.com/v1/pages"

        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        }

        # Build properties - using rich_text for flexibility with database schema
        properties = {
            "name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        }

        # Add phone number
        if phone:
            properties["phone_number"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": phone
                        }
                    }
                ]
            }

        # Add email if provided
        if email:
            properties["email"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": email
                        }
                    }
                ]
            }

        # Add service if provided
        if service:
            properties["service"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": service
                        }
                    }
                ]
            }

        # Add status - try as select first, fallback to rich_text
        properties["status"] = {
            "rich_text": [
                {
                    "text": {
                        "content": status
                    }
                }
            ]
        }

        # Add date if appointment scheduled
        if appointment_time:
            try:
                # Try to format as ISO date for Notion
                from datetime import datetime
                # Parse various date formats
                properties["date"] = {
                    "date": {
                        "start": appointment_time
                    }
                }
            except:
                # If date parsing fails, add to notes instead
                pass

        # Add notes
        if full_notes:
            properties["notes"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": full_notes[:2000]  # Notion has 2000 char limit
                        }
                    }
                ]
            }

        # Prepare request body
        data = {
            "parent": {
                "database_id": NOTION_DATABASE_ID
            },
            "properties": properties
        }

        # Make API request
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                result = response.json()
                page_id = result.get("id", "unknown")
                print(f"✅ Lead created in Notion! Page ID: {page_id}")
                return True
            else:
                print(f"⚠️ Notion API returned status {response.status_code}")
                print(f"Response: {response.text}")

                # Try with minimal properties if schema mismatch
                if response.status_code == 400:
                    print("📝 Retrying with minimal properties...")
                    return await create_lead_minimal(name, phone, full_notes)

    except Exception as e:
        print(f"❌ Error creating Notion lead: {e}")

    # Don't fail the call if Notion logging fails
    return False


async def create_lead_minimal(name: str, phone: str, notes: str = "") -> bool:
    """
    Create lead with minimal properties (fallback method)

    Args:
        name: Customer name
        phone: Customer phone
        notes: Notes to include

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📝 Creating minimal Notion lead...")

        url = "https://api.notion.com/v1/pages"

        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        }

        # Minimal properties - just title and phone as rich text
        data = {
            "parent": {
                "database_id": NOTION_DATABASE_ID
            },
            "properties": {
                "name": {
                    "title": [
                        {
                            "text": {
                                "content": f"{name} - {phone}"
                            }
                        }
                    ]
                }
            }
        }

        # Add notes if database has that property
        if notes:
            data["properties"]["notes"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": notes[:2000]
                        }
                    }
                ]
            }

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                print(f"✅ Minimal lead created in Notion!")
                return True

    except Exception as e:
        print(f"❌ Error creating minimal lead: {e}")

    return False
