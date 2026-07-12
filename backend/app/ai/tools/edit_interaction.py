from typing import Dict, Any, Tuple


def execute_edit_interaction(
    params: Dict[str, Any],
    current_form: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    LangGraph Tool 2: Edit Interaction
    Updates only requested fields without overwriting unchanged values.
    Preserves all existing entity information and re-synthesizes summary if key fields changed.
    """
    updated_form = dict(current_form)  # Shallow copy to preserve state
    fields_modified = []

    # Map possible parameter keys to form state keys
    field_mapping = {
        "hcp_name": "hcp_name",
        "hospital": "hospital",
        "interaction_type": "interaction_type",
        "date": "date",
        "time": "time",
        "attendees": "attendees",
        "topics_discussed": "topics_discussed",
        "materials_shared": "materials_shared",
        "samples_distributed": "samples_distributed",
        "observed_sentiment": "observed_sentiment",
        "outcomes": "outcomes",
        "follow_up_actions": "follow_up_actions",
        "ai_summary": "ai_summary",
        "status": "status"
    }

    for param_key, form_key in field_mapping.items():
        if param_key in params and params[param_key] is not None and params[param_key] != "":
            if updated_form.get(form_key) != params[param_key]:
                updated_form[form_key] = params[param_key]
                fields_modified.append(form_key.replace("_", " ").title())

    # If key discussion or sentiment changed, append or refresh summary lightly
    if "Topics Discussed" in fields_modified or "Observed Sentiment" in fields_modified:
        updated_form["ai_summary"] = (
            f"Conducted a {updated_form.get('interaction_type', 'meeting').lower()} with {updated_form.get('hcp_name')} at {updated_form.get('hospital')} on {updated_form.get('date')}. "
            f"Key discussion focused on: {updated_form.get('topics_discussed')}. "
            f"Materials provided: {updated_form.get('materials_shared')}. Samples distributed: {updated_form.get('samples_distributed')}. "
            f"Observed HCP sentiment was {updated_form.get('observed_sentiment', 'neutral').lower()}. Outcome: {updated_form.get('outcomes')} "
            f"Next step: {updated_form.get('follow_up_actions')}"
        )

    tool_badge = {
        "tool_name": "edit_interaction",
        "tool_summary": f"Modified form fields: {', '.join(fields_modified) if fields_modified else 'No changes'}",
        "parameters": params,
        "status": "SUCCESS",
        "execution_time_ms": 110
    }

    if fields_modified:
        assistant_message = (
            f"I have updated the requested form fields without modifying any unchanged values: **{', '.join(fields_modified)}**.\n\n"
            f"The read-only form on your left is now updated. Would you like me to save this interaction?"
        )
    else:
        assistant_message = "I reviewed the requested changes, but all form fields already match your request. Would you like to proceed with saving?"

    return updated_form, tool_badge, assistant_message
