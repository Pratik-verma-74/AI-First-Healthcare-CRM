from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FormState(BaseModel):
    """
    Represents the UI state of the read-only form on the left pane.
    Communicates between frontend, backend, and LangGraph AI agent.
    """
    id: Optional[int] = None
    hcp_id: Optional[int] = None
    hcp_name: Optional[str] = ""
    hospital: Optional[str] = ""
    interaction_type: str = "Meeting"
    date: Optional[str] = ""
    time: Optional[str] = "12:00"
    attendees: Optional[str] = ""
    topics_discussed: Optional[str] = ""
    materials_shared: Optional[str] = ""
    samples_distributed: Optional[str] = ""
    observed_sentiment: str = "Neutral"
    outcomes: Optional[str] = ""
    follow_up_actions: Optional[str] = ""
    ai_summary: Optional[str] = ""
    status: str = "Draft"


class HCPResponse(BaseModel):
    id: int
    name: str
    specialty: str
    hospital: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_type: str = "Meeting"
    interaction_date: date
    interaction_time: str = "12:00"
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    observed_sentiment: str = "Neutral"
    outcomes: Optional[str] = None
    ai_summary: Optional[str] = None
    status: str = "Saved"
    follow_up_action: Optional[str] = None
    follow_up_date: Optional[date] = None


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    observed_sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    ai_summary: Optional[str] = None
    status: Optional[str] = None


class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    hcp: Optional[HCPResponse] = None
    interaction_type: str
    interaction_date: date
    interaction_time: str
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    observed_sentiment: str
    outcomes: Optional[str] = None
    ai_summary: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FollowUpResponse(BaseModel):
    id: int
    interaction_id: int
    hcp_id: int
    action_description: str
    due_date: date
    status: str

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: str = "default-session"
    message: str
    current_form_data: FormState


class ToolExecutionBadgeInfo(BaseModel):
    tool_name: str
    tool_summary: str
    parameters: Dict[str, Any]
    status: str = "SUCCESS"
    execution_time_ms: int = 150


class ChatResponse(BaseModel):
    response: str
    updated_form_data: FormState
    tool_execution: Optional[ToolExecutionBadgeInfo] = None
    needs_confirmation: bool = False
    saved_interaction_id: Optional[int] = None
