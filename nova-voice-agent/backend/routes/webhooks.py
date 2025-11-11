"""
Webhook Routes - Handle Twilio Voice API callbacks
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from typing import Optional

from backend.services.conversation import (
    generate_response,
    is_ready_to_book,
    cleanup_conversation,
    get_conversation
)
from backend.services.calendar import (
    get_available_slots,
    format_slots_for_speech,
    book_appointment
)
from backend.services.sms import send_confirmation_sms
from backend.services.crm import create_lead

router = APIRouter()


def create_twiml_response(say_text: str, gather: bool = True, action: str = "/webhooks/voice/process") -> str:
    """
    Create TwiML response for Twilio

    Args:
        say_text: Text for Nova to speak
        gather: Whether to gather user input
        action: URL for next action

    Returns:
        TwiML XML string
    """
    if gather:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" timeout="auto" action="{action}" language="en-US" speechTimeout="auto">
        <Say voice="Polly.Joanna">{say_text}</Say>
    </Gather>
    <Say voice="Polly.Joanna">I didn't catch that. Please call back when you're ready.</Say>
    <Hangup/>
</Response>'''
    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{say_text}</Say>
    <Hangup/>
</Response>'''

    return twiml


@router.post("/voice/incoming")
async def incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    """
    Handle incoming phone call

    Returns:
        TwiML response with greeting
    """
    print(f"📞 Incoming call: {CallSid} from {From}")

    # Initial greeting
    greeting = "Hi! This is Nova from Orbyn dot A I. Thanks for calling! How can I help you today?"

    # Return TwiML with greeting and gather input
    twiml = create_twiml_response(greeting, gather=True)

    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/process")
async def process_speech(
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    From: str = Form(...)
):
    """
    Process user speech and generate response

    Returns:
        TwiML response with Nova's reply
    """
    print(f"📞 Processing speech for call: {CallSid}")

    # Handle case where no speech detected
    if not SpeechResult:
        print("⚠️ No speech detected")
        twiml = create_twiml_response(
            "I didn't hear anything. Could you please repeat that?",
            gather=True
        )
        return Response(content=twiml, media_type="application/xml")

    try:
        # Generate AI response
        ai_response, conversation = await generate_response(CallSid, SpeechResult)

        # Check if ready to book appointment
        if is_ready_to_book(conversation):
            print("📅 Customer ready to book - fetching available slots...")

            # Get available slots
            slots = await get_available_slots()

            if slots:
                # Format slots for speech
                slots_text = format_slots_for_speech(slots, max_slots=3)

                # Create response offering slots
                booking_text = f"{ai_response} Great! Let me check my calendar. {slots_text} Which time works best for you?"

                # Store slots in conversation for booking
                conversation.call_data.notes = f"Available slots: {', '.join(slots)}"

                # Change action to booking endpoint
                twiml = create_twiml_response(
                    booking_text,
                    gather=True,
                    action="/webhooks/voice/book"
                )
            else:
                # No slots available
                fallback_text = f"{ai_response} I'll have someone from our team reach out to you within 24 hours to schedule your consultation. Thank you for your interest!"

                # Log lead even without booking
                await create_lead(
                    name=conversation.call_data.name,
                    phone=conversation.call_data.phone or From,
                    email=conversation.call_data.email,
                    service=conversation.call_data.service,
                    status="needs_callback",
                    notes="No slots available - needs callback",
                    call_sid=CallSid
                )

                twiml = create_twiml_response(fallback_text, gather=False)

        else:
            # Continue conversation
            twiml = create_twiml_response(ai_response, gather=True)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"❌ Error processing speech: {e}")

        # Error fallback
        error_text = "I'm having trouble right now. Please try calling back in a few minutes."
        twiml = create_twiml_response(error_text, gather=False)

        return Response(content=twiml, media_type="application/xml")


@router.post("/voice/book")
async def book_appointment_handler(
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    From: str = Form(...)
):
    """
    Handle appointment booking

    Returns:
        TwiML response confirming booking
    """
    print(f"📅 Booking appointment for call: {CallSid}")

    if not SpeechResult:
        twiml = create_twiml_response(
            "I didn't hear which time you prefer. Let me transfer you to our scheduling team.",
            gather=False
        )
        return Response(content=twiml, media_type="application/xml")

    try:
        # Get conversation state
        conversation = get_conversation(CallSid)

        # Extract time preference from speech
        # For simplicity, book first available slot
        # In production, would parse user's time preference
        print(f"🗣️ Customer said: {SpeechResult}")

        # Get available slots
        slots = await get_available_slots()

        if not slots:
            error_text = "I'm having trouble accessing the calendar. Our team will call you back to confirm a time. Thank you!"

            # Log as needs callback
            await create_lead(
                name=conversation.call_data.name,
                phone=conversation.call_data.phone or From,
                email=conversation.call_data.email,
                service=conversation.call_data.service,
                status="needs_callback",
                notes=f"Customer requested: {SpeechResult}",
                call_sid=CallSid
            )

            twiml = create_twiml_response(error_text, gather=False)
            return Response(content=twiml, media_type="application/xml")

        # Use first slot for demo (in production, would match user preference)
        selected_slot = slots[0]
        conversation.call_data.appointment_time = selected_slot

        # Book appointment
        booking_result = await book_appointment(
            name=conversation.call_data.name,
            email=conversation.call_data.email,
            phone=conversation.call_data.phone or From,
            start_time=selected_slot,
            notes=f"Booked via Nova Voice Agent. Call SID: {CallSid}"
        )

        # Send SMS confirmation
        await send_confirmation_sms(
            to_phone=conversation.call_data.phone or From,
            name=conversation.call_data.name,
            appointment_time=selected_slot
        )

        # Log to Notion CRM
        booking_status = "booked" if booking_result.get("success") else "pending"
        await create_lead(
            name=conversation.call_data.name,
            phone=conversation.call_data.phone or From,
            email=conversation.call_data.email,
            service=conversation.call_data.service,
            status=booking_status,
            appointment_time=selected_slot,
            notes=f"Booking ID: {booking_result.get('booking_id', 'N/A')}. {booking_result.get('message', '')}",
            call_sid=CallSid
        )

        # Confirmation message
        confirmation_text = f"Perfect! I've scheduled your consultation for {selected_slot}. Check your phone for a confirmation text. We're looking forward to speaking with you. Goodbye!"

        twiml = create_twiml_response(confirmation_text, gather=False)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"❌ Error booking appointment: {e}")

        # Error fallback - still log the lead
        try:
            conversation = get_conversation(CallSid)
            await create_lead(
                name=conversation.call_data.name or "Unknown",
                phone=conversation.call_data.phone or From,
                email=conversation.call_data.email,
                service=conversation.call_data.service,
                status="needs_callback",
                notes=f"Error during booking: {str(e)}",
                call_sid=CallSid
            )
        except:
            pass

        error_text = "I had trouble completing your booking. Our team will call you back shortly to confirm your appointment. Thank you!"
        twiml = create_twiml_response(error_text, gather=False)

        return Response(content=twiml, media_type="application/xml")


@router.post("/voice/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """
    Handle call status updates from Twilio

    Returns:
        Empty response
    """
    print(f"📊 Call status update: {CallSid} -> {CallStatus}")

    # Clean up conversation when call ends
    if CallStatus in ["completed", "busy", "no-answer", "failed", "canceled"]:
        cleanup_conversation(CallSid)

    return {"status": "received"}
