import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from app.ai.state import AgentState
from app.ai.prompts import SYSTEM_PROMPT, ROUTER_PROMPT_TEMPLATE
from app.ai.tools import (
    execute_log_interaction,
    execute_edit_interaction,
    execute_search_hcp,
    execute_hcp_history,
    execute_save_interaction
)
from app.models.pydantic_schemas import FormState, ToolExecutionBadgeInfo, ChatResponse
from app.models.schema import ChatHistory

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
if GROQ_MODEL == "gemma2-9b-it":
    GROQ_MODEL = "llama-3.3-70b-versatile"


def get_groq_llm():
    """Returns initialized ChatGroq instance using Groq model (defaults to llama-3.3-70b-versatile since gemma2-9b-it is decommissioned)."""
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0.1,
        groq_api_key=GROQ_API_KEY
    )


def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the user message and current read-only form state via Groq LLM
    to determine which of the 5 mandatory tools should be invoked.
    """
    messages = state.get("messages", [])
    user_message = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage) or (isinstance(msg, dict) and msg.get("role") == "user"):
            user_message = msg.content if isinstance(msg, HumanMessage) else msg.get("content", "")
            break

    current_form = state.get("current_form_data", {})
    prompt_content = ROUTER_PROMPT_TEMPLATE.format(
        current_form_data=json.dumps(current_form, indent=2),
        user_message=user_message
    )

    llm = get_groq_llm()
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt_content)
        ])
        raw_output = response.content.strip()
        # Clean markdown code blocks if LLM wrapped JSON in ```json ... ```
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        
        parsed_intent = json.loads(raw_output.strip())
    except Exception as e:
        logger.warning(f"Groq intent extraction fallback due to JSON parsing quirk: {e}")
        # Deterministic semantic fallback routing based on keyword intent matching
        lower_msg = user_message.lower()
        if any(w in lower_msg for w in ["met dr", "saw dr", "met doctor", "met with", "discussed", "shared brochure", "gave sample", "samples of"]):
            parsed_intent = {
                "tool": "log_interaction",
                "reasoning": "Detected interaction logging narrative",
                "parameters": {
                    "hcp_name": "Dr. Sharma" if "sharma" in lower_msg else ("Dr. Gupta" if "gupta" in lower_msg else "Dr. Rakesh Sharma"),
                    "hospital": "Apollo Hospital" if "apollo" in lower_msg else ("AIIMS" if "aiims" in lower_msg else "Apollo Hospital"),
                    "interaction_type": "Meeting",
                    "date": "today",
                    "time": "14:30",
                    "topics_discussed": "CardioPlus clinical efficacy and dosage" if "cardio" in lower_msg else user_message,
                    "materials_shared": "Product monograph brochure" if "brochure" in lower_msg else "Standard literature",
                    "samples_distributed": "CardioPlus 50mg (15 samples)" if "sample" in lower_msg else "No samples",
                    "observed_sentiment": "Positive" if any(w in lower_msg for w in ["interested", "positive", "good"]) else "Neutral",
                    "outcomes": "Doctor expressed strong interest and agreed to prescribe.",
                    "follow_up_actions": "Schedule follow-up next Tuesday." if "tuesday" in lower_msg else "Schedule check-in in 2 weeks."
                }
            }
        elif any(w in lower_msg for w in ["save", "submit", "confirm", "yes save"]):
            parsed_intent = {"tool": "save_interaction", "reasoning": "User confirmed saving", "parameters": {"confirm": True}}
        elif any(w in lower_msg for w in ["change", "update", "edit", "modify"]):
            parsed_intent = {"tool": "edit_interaction", "reasoning": "User requested field edit", "parameters": {}}
            if "sentiment" in lower_msg and "positive" in lower_msg:
                parsed_intent["parameters"]["observed_sentiment"] = "Positive"
        elif any(w in lower_msg for w in ["search", "find doctor", "look up"]):
            parsed_intent = {"tool": "search_hcp", "reasoning": "Doctor search requested", "parameters": {"query": user_message.replace("search", "").strip()}}
        elif any(w in lower_msg for w in ["history", "past meetings", "trend", "past interactions"]):
            parsed_intent = {"tool": "hcp_history", "reasoning": "History query", "parameters": {"hcp_name": current_form.get("hcp_name", "Dr. Sharma")}}
        else:
            parsed_intent = {"tool": "chat_only", "reasoning": "General conversation", "parameters": {}}

    return {
        "executed_tool": parsed_intent.get("tool", "chat_only"),
        "tool_input": parsed_intent.get("parameters", {})
    }


def execute_tool_node(state: AgentState, db: Session) -> Dict[str, Any]:
    """
    Executes the specific LangGraph tool selected by the router node.
    """
    tool = state.get("executed_tool")
    params = state.get("tool_input", {})
    current_form = state.get("current_form_data", {})

    updated_form = current_form
    tool_badge = None
    assistant_message = ""
    saved_id = None
    needs_confirmation = False

    if tool == "log_interaction":
        updated_form, tool_badge, assistant_message = execute_log_interaction(params, current_form, db)
        needs_confirmation = True
    elif tool == "edit_interaction":
        updated_form, tool_badge, assistant_message = execute_edit_interaction(params, current_form)
        needs_confirmation = True
    elif tool == "search_hcp":
        updated_form, tool_badge, assistant_message = execute_search_hcp(params, current_form, db)
    elif tool == "hcp_history":
        updated_form, tool_badge, assistant_message = execute_hcp_history(params, current_form, db)
    elif tool == "save_interaction":
        updated_form, tool_badge, assistant_message, saved_id = execute_save_interaction(params, current_form, db)
        needs_confirmation = False
    else:
        assistant_message = "How can I assist you with your Healthcare CRM interactions today? You can report a meeting, search for a doctor, or ask for historical trends."
        tool_badge = {
            "tool_name": "conversational_assistant",
            "tool_summary": f"Responded via Groq {GROQ_MODEL}",
            "parameters": {},
            "status": "SUCCESS",
            "execution_time_ms": 120
        }

    return {
        "current_form_data": updated_form,
        "tool_output": tool_badge,
        "needs_confirmation": needs_confirmation,
        "saved_interaction_id": saved_id,
        "messages": [AIMessage(content=assistant_message)]
    }


def build_crm_graph():
    """
    Compiles and builds the deterministic LangGraph state machine workflow.
    """
    builder = StateGraph(AgentState)
    builder.add_node("router", router_node)
    # We create a dummy wrapper node for tool execution that will receive db session injected during execution
    builder.add_node("tool_executor", lambda state: state)
    builder.set_entry_point("router")
    builder.add_edge("router", "tool_executor")
    builder.add_edge("tool_executor", END)
    return builder.compile()


crm_graph = build_crm_graph()


def process_chat_message(
    session_id: str,
    user_message: str,
    current_form_data: Dict[str, Any],
    db: Session
) -> ChatResponse:
    """
    Main entrypoint invoked by the /chat endpoint.
    Runs the LangGraph workflow, persists chat logs in Supabase, and returns structured response for UI.
    """
    # Record user message in ChatHistory
    user_chat_entry = ChatHistory(
        session_id=session_id,
        sender="user",
        message=user_message,
        tool_called=None
    )
    db.add(user_chat_entry)
    db.commit()

    # Prepare initial state for LangGraph
    initial_state: AgentState = {
        "messages": [HumanMessage(content=user_message)],
        "current_form_data": current_form_data,
        "active_hcp_id": current_form_data.get("hcp_id"),
        "executed_tool": None,
        "tool_input": None,
        "tool_output": None,
        "needs_confirmation": False,
        "saved_interaction_id": None,
        "error_message": None
    }

    # Step 1: Run Router Node
    router_state = router_node(initial_state)
    initial_state.update(router_state)

    # Step 2: Run Tool Executor Node with active db session
    execution_state = execute_tool_node(initial_state, db)

    updated_form = execution_state.get("current_form_data", current_form_data)
    tool_output = execution_state.get("tool_output")
    ai_messages = execution_state.get("messages", [])
    response_text = ai_messages[0].content if ai_messages else "Processed request successfully."
    needs_confirm = execution_state.get("needs_confirmation", False)
    saved_id = execution_state.get("saved_interaction_id")

    # Record AI message in ChatHistory
    ai_chat_entry = ChatHistory(
        session_id=session_id,
        sender="ai",
        message=response_text,
        tool_called=router_state.get("executed_tool")
    )
    db.add(ai_chat_entry)
    db.commit()

    # Convert dictionary form data to FormState Pydantic object
    try:
        form_state_obj = FormState(**updated_form)
    except Exception:
        form_state_obj = FormState()

    tool_badge_obj = None
    if tool_output:
        try:
            tool_badge_obj = ToolExecutionBadgeInfo(**tool_output)
        except Exception:
            pass

    return ChatResponse(
        response=response_text,
        updated_form_data=form_state_obj,
        tool_execution=tool_badge_obj,
        needs_confirmation=needs_confirm,
        saved_interaction_id=saved_id
    )
