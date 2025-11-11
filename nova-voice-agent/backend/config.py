"""
Configuration for Nova Voice Agent
Loads environment variables and defines system constants
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 150

# Cal.com Configuration
CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_EVENT_TYPE = os.getenv("CAL_EVENT_TYPE", "free-consultation")
CAL_API_BASE = "https://api.cal.com/v1"

# Notion Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_VERSION = "2022-06-28"

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Nova's Personality - System Prompt for OpenAI
NOVA_SYSTEM_PROMPT = """You are Nova, a friendly AI voice assistant for Orbyn.ai. Your job is to:
1. Greet callers warmly
2. Ask for their name and phone number
3. Ask what service they're interested in
4. Offer to schedule a free consultation

Keep responses SHORT and conversational - you're on a phone call (under 3 sentences).
Be professional but friendly. Always confirm information by repeating it back.

After each response, include a JSON object at the end with any information you extracted:
{
  "name": "extracted name or null",
  "phone": "extracted phone or null",
  "email": "extracted email or null",
  "service": "extracted service or null",
  "ready_to_book": true/false
}

Set ready_to_book to true only when you have collected the name and phone, and the customer has expressed interest in booking."""

# HTTP Client Configuration
HTTP_TIMEOUT = 10.0  # seconds

# Timezone
DEFAULT_TIMEZONE = "America/New_York"
