"""
Pydantic data models for Nova Voice Agent
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class CallData(BaseModel):
    """Data collected during a phone call"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service: Optional[str] = None
    appointment_time: Optional[str] = None
    status: str = "new"
    notes: str = ""


class Message(BaseModel):
    """A single message in the conversation"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ConversationState(BaseModel):
    """Complete state of an ongoing conversation"""
    call_sid: str = Field(..., description="Twilio Call SID")
    messages: List[Message] = Field(default_factory=list, description="Conversation history")
    call_data: CallData = Field(default_factory=CallData, description="Collected customer data")
    stage: str = Field(default="greeting", description="Current conversation stage")

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! This is Nova from Orbyn dot A I."}
                ],
                "call_data": {
                    "name": "John Doe",
                    "phone": "+15551234567",
                    "email": "john@example.com",
                    "service": "AI consulting",
                    "appointment_time": None,
                    "status": "new",
                    "notes": ""
                },
                "stage": "collecting_info"
            }
        }


class ExtractedData(BaseModel):
    """Data extracted from conversation by OpenAI"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service: Optional[str] = None
    ready_to_book: bool = False
