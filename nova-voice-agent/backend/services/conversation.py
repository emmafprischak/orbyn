"""
Conversation Service - Handles AI conversation using OpenAI GPT-4
"""
import json
import re
from typing import Dict, Optional, Tuple
from openai import AsyncOpenAI

from backend.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    NOVA_SYSTEM_PROMPT
)
from backend.models import ConversationState, Message, ExtractedData

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# In-memory storage for active conversations
# Key: call_sid, Value: ConversationState
active_conversations: Dict[str, ConversationState] = {}


def get_conversation(call_sid: str) -> ConversationState:
    """
    Get or create a conversation state for a call

    Args:
        call_sid: Twilio Call SID

    Returns:
        ConversationState object
    """
    if call_sid not in active_conversations:
        print(f"📞 Creating new conversation for call: {call_sid}")
        active_conversations[call_sid] = ConversationState(call_sid=call_sid)
    return active_conversations[call_sid]


def cleanup_conversation(call_sid: str) -> None:
    """
    Remove conversation from memory when call ends

    Args:
        call_sid: Twilio Call SID
    """
    if call_sid in active_conversations:
        print(f"🗑️ Cleaning up conversation: {call_sid}")
        del active_conversations[call_sid]


def extract_json_from_response(response: str) -> Tuple[str, Optional[ExtractedData]]:
    """
    Extract JSON data from OpenAI response

    Args:
        response: Raw response from OpenAI

    Returns:
        Tuple of (clean_response, extracted_data)
    """
    # Try to find JSON in the response
    json_pattern = r'\{[^{}]*"name"[^{}]*\}'
    match = re.search(json_pattern, response, re.DOTALL)

    if match:
        try:
            json_str = match.group(0)
            data = json.loads(json_str)

            # Remove JSON from response text
            clean_response = response.replace(json_str, "").strip()

            # Create ExtractedData object
            extracted = ExtractedData(
                name=data.get("name"),
                phone=data.get("phone"),
                email=data.get("email"),
                service=data.get("service"),
                ready_to_book=data.get("ready_to_book", False)
            )

            print(f"📊 Extracted data: {extracted.model_dump()}")
            return clean_response, extracted

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return response, None

    return response, None


async def generate_response(call_sid: str, user_input: str) -> Tuple[str, ConversationState]:
    """
    Generate AI response using OpenAI GPT-4

    Args:
        call_sid: Twilio Call SID
        user_input: What the user said

    Returns:
        Tuple of (ai_response, updated_conversation_state)
    """
    try:
        # Get conversation state
        conversation = get_conversation(call_sid)

        # Add user message to history
        conversation.messages.append(Message(role="user", content=user_input))
        print(f"🗣️ User said: {user_input}")

        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": NOVA_SYSTEM_PROMPT}
        ]

        # Add conversation history
        for msg in conversation.messages:
            messages.append({"role": msg.role, "content": msg.content})

        # Call OpenAI API
        print(f"🤖 Calling OpenAI with {len(messages)} messages...")
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )

        # Extract response
        ai_response = response.choices[0].message.content

        # Extract JSON data and clean response
        clean_response, extracted_data = extract_json_from_response(ai_response)

        # Update conversation state with extracted data
        if extracted_data:
            if extracted_data.name:
                conversation.call_data.name = extracted_data.name
            if extracted_data.phone:
                conversation.call_data.phone = extracted_data.phone
            if extracted_data.email:
                conversation.call_data.email = extracted_data.email
            if extracted_data.service:
                conversation.call_data.service = extracted_data.service

        # Add assistant response to history (without JSON)
        conversation.messages.append(Message(role="assistant", content=clean_response))

        # Update conversation stage based on collected data
        if conversation.call_data.name and conversation.call_data.phone:
            if extracted_data and extracted_data.ready_to_book:
                conversation.stage = "booking"
            else:
                conversation.stage = "collecting_info"

        print(f"🤖 Nova says: {clean_response}")
        print(f"📊 Current data: name={conversation.call_data.name}, phone={conversation.call_data.phone}, service={conversation.call_data.service}")
        print(f"🎯 Stage: {conversation.stage}")

        return clean_response, conversation

    except Exception as e:
        print(f"❌ Error generating response: {e}")
        error_response = "I'm having trouble understanding right now. Could you please repeat that?"

        # Still return conversation state even on error
        conversation = get_conversation(call_sid)
        return error_response, conversation


def is_ready_to_book(conversation: ConversationState) -> bool:
    """
    Check if we have enough information to book an appointment

    Args:
        conversation: Current conversation state

    Returns:
        True if ready to book, False otherwise
    """
    has_name = conversation.call_data.name is not None
    has_phone = conversation.call_data.phone is not None
    is_booking_stage = conversation.stage == "booking"

    ready = has_name and has_phone and is_booking_stage

    if ready:
        print(f"✅ Ready to book appointment for {conversation.call_data.name}")

    return ready
