from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.schema import HCP, Interaction


def execute_search_hcp(
    params: Dict[str, Any],
    current_form: Dict[str, Any],
    db: Session
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    LangGraph Tool 3: Search HCP
    Searches the database for a doctor by name, hospital, or specialty.
    Returns profile details and recent interactions.
    """
    query_str = params.get("query", params.get("hcp_name", current_form.get("hcp_name", "")))
    if not query_str:
        return (
            current_form,
            {
                "tool_name": "search_hcp",
                "tool_summary": "Search aborted: No search query provided",
                "parameters": params,
                "status": "ERROR",
                "execution_time_ms": 40
            },
            "Please specify a doctor name or hospital to search for (e.g., 'Search for Dr. Rakesh Sharma')."
        )

    clean_query = query_str.strip()
    if " at " in clean_query.lower():
        parts = clean_query.split(" at ", 1)
        name_part = parts[0].strip()
        hosp_part = parts[1].strip()
    elif " in " in clean_query.lower():
        parts = clean_query.split(" in ", 1)
        name_part = parts[0].strip()
        hosp_part = parts[1].strip()
    else:
        name_part = clean_query
        hosp_part = clean_query

    name_no_dr = name_part.replace("Dr. ", "").replace("Dr ", "").strip()
    name_with_dot = f"Dr. {name_no_dr}"

    hcps = db.query(HCP).filter(
        (HCP.name.ilike(f"%{clean_query}%")) |
        (HCP.name.ilike(f"%{name_part}%")) |
        (HCP.name.ilike(f"%{name_no_dr}%")) |
        (HCP.name.ilike(f"%{name_with_dot}%")) |
        (HCP.hospital.ilike(f"%{clean_query}%")) |
        (HCP.hospital.ilike(f"%{hosp_part}%")) |
        (HCP.specialty.ilike(f"%{clean_query}%")) |
        (HCP.specialty.ilike(f"%{name_no_dr}%"))
    ).limit(5).all()

    if not hcps:
        tool_badge = {
            "tool_name": "search_hcp",
            "tool_summary": f"No HCP found matching '{query_str}'",
            "parameters": params,
            "status": "SUCCESS",
            "execution_time_ms": 95
        }
        return (
            current_form,
            tool_badge,
            f"I searched the Supabase PostgreSQL database for **'{query_str}'**, but found no matching Healthcare Professionals. You can still log the interaction, and we can register a new HCP record if needed."
        )

    best_match = hcps[0]
    recent_interactions = db.query(Interaction).filter(
        Interaction.hcp_id == best_match.id
    ).order_by(Interaction.interaction_date.desc()).limit(3).all()

    # If form is empty/default, we can auto-fill doctor name and hospital
    updated_form = dict(current_form)
    if not updated_form.get("hcp_name") or updated_form.get("hcp_name") == "":
        updated_form["hcp_id"] = best_match.id
        updated_form["hcp_name"] = best_match.name
        updated_form["hospital"] = best_match.hospital

    interactions_summary = ""
    if recent_interactions:
        interactions_summary = "\n\n**Recent Interactions:**\n" + "\n".join([
            f"- **{i.interaction_date}**: {i.interaction_type} regarding *{i.topics_discussed[:60] if i.topics_discussed else 'General visit'}* ({i.observed_sentiment} sentiment)"
            for i in recent_interactions
        ])
    else:
        interactions_summary = "\n\n*No prior interactions recorded for this doctor.*"

    tool_badge = {
        "tool_name": "search_hcp",
        "tool_summary": f"Found {len(hcps)} profile(s) matching '{query_str}'. Best match: {best_match.name}",
        "parameters": params,
        "status": "SUCCESS",
        "execution_time_ms": 135
    }

    assistant_message = (
        f"I located **{best_match.name}** ({best_match.specialty}) at **{best_match.hospital}** in the database.\n"
        f"- **Contact Email:** {best_match.contact_email or 'N/A'}\n"
        f"- **Phone:** {best_match.phone or 'N/A'}\n"
        f"- **City:** {best_match.city or 'N/A'}"
        f"{interactions_summary}\n\n"
        f"Would you like to log a new interaction for {best_match.name}?"
    )

    return updated_form, tool_badge, assistant_message
