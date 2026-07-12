import operator
from typing import TypedDict, Annotated, Sequence, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    LangGraph State Machine representation for the AI-First Healthcare CRM Assistant.
    Maintains conversation flow, form state synchronization, active doctor match, and tool execution diagnostics.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_form_data: Dict[str, Any]
    active_hcp_id: Optional[int]
    executed_tool: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    needs_confirmation: bool
    saved_interaction_id: Optional[int]
    error_message: Optional[str]
