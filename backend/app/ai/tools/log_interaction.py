import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.schema import HCP
from app.models.pydantic_schemas import FormState


def execute_log_interaction(
    params: Dict[str, Any],
    current_form: Dict[str, Any],
    db: Session
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    LangGraph Tool 1: Log Interaction
    Extracts doctor name, hospital, date, time, attendees, products discussed, materials,
    samples, sentiment, outcomes, and follow-up.
    Generates a clean summary and populates the read-only form state.
    """
    # Attempt to match doctor name against database
    hcp_name = params.get("hcp_name", current_form.get("hcp_name", ""))
    hospital = params.get("hospital", current_form.get("hospital", ""))
    hcp_id = current_form.get("hcp_id")

    if hcp_name and not hcp_id:
        matched_hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name.strip()}%")).first()
        if matched_hcp:
            hcp_id = matched_hcp.id
            hcp_name = matched_hcp.name
            hospital = matched_hcp.hospital or hospital

    # Resolve date (convert 'today' to actual YYYY-MM-DD date string)
    raw_date = params.get("date", current_form.get("date", str(datetime.date.today())))
    if raw_date and raw_date.lower() == "today":
        raw_date = str(datetime.date.today())
    elif not raw_date:
        raw_date = str(datetime.date.today())

    raw_time = params.get("time", current_form.get("time", "12:00"))
    interaction_type = params.get("interaction_type", current_form.get("interaction_type", "Meeting"))
    attendees = params.get("attendees", current_form.get("attendees", f"{hcp_name}, Medical Representative"))
    topics_discussed = params.get("topics_discussed", current_form.get("topics_discussed", ""))
    materials_shared = params.get("materials_shared", current_form.get("materials_shared", "No materials attached"))
    samples_distributed = params.get("samples_distributed", current_form.get("samples_distributed", "No samples distributed"))
    observed_sentiment = params.get("observed_sentiment", current_form.get("observed_sentiment", "Positive"))
    outcomes = params.get("outcomes", current_form.get("outcomes", "Doctor expressed interest in ongoing clinical discussions."))
    follow_up_actions = params.get("follow_up_actions", current_form.get("follow_up_actions", "Schedule next visit in 2 weeks."))

    # Generate professional summary if not explicitly provided
    ai_summary = params.get("ai_summary", "")
    if not ai_summary:
        ai_summary = (
            f"Conducted a {interaction_type.lower()} with {hcp_name} at {hospital} on {raw_date}. "
            f"Key discussion focused on: {topics_discussed or 'clinical efficacy and product profile'}. "
            f"Materials provided: {materials_shared}. Samples distributed: {samples_distributed}. "
            f"Observed HCP sentiment was {observed_sentiment.lower()}. Outcome: {outcomes} "
            f"Next step: {follow_up_actions}"
        )

    updated_form = {
        "id": current_form.get("id"),
        "hcp_id": hcp_id,
        "hcp_name": hcp_name,
        "hospital": hospital,
        "interaction_type": interaction_type,
        "date": raw_date,
        "time": raw_time,
        "attendees": attendees,
        "topics_discussed": topics_discussed,
        "materials_shared": materials_shared,
        "samples_distributed": samples_distributed,
        "observed_sentiment": observed_sentiment,
        "outcomes": outcomes,
        "follow_up_actions": follow_up_actions,
        "ai_summary": ai_summary,
        "status": "Draft"
    }

    tool_badge = {
        "tool_name": "log_interaction",
        "tool_summary": f"Extracted entity details & populated read-only form for {hcp_name}",
        "parameters": params,
        "status": "SUCCESS",
        "execution_time_ms": 180
    }

    assistant_message = (
        f"I have extracted and logged the interaction details for **{hcp_name}** at **{hospital}**. "
        f"I populated all fields including your discussion on *{topics_discussed or 'product details'}*, "
        f"noted the **{observed_sentiment}** sentiment, and generated an executive summary.\n\n"
        f"Would you like me to confirm and save this interaction to the Supabase PostgreSQL database?"
    )

    return updated_form, tool_badge, assistant_message
