from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.schema import HCP, Interaction, FollowUp


def execute_hcp_history(
    params: Dict[str, Any],
    current_form: Dict[str, Any],
    db: Session
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    LangGraph Tool 4: HCP History
    Retrieves detailed past meetings, products discussed, summaries, follow-ups, and sentiment trends.
    """
    hcp_id = params.get("hcp_id", current_form.get("hcp_id"))
    hcp_name = params.get("hcp_name", current_form.get("hcp_name", ""))

    hcp = None
    if hcp_id:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp and hcp_name:
        clean_name = hcp_name.strip()
        if " at " in clean_name.lower():
            clean_name = clean_name.split(" at ", 1)[0].strip()
        name_no_dr = clean_name.replace("Dr. ", "").replace("Dr ", "").strip()
        name_with_dot = f"Dr. {name_no_dr}"
        hcp = db.query(HCP).filter(
            (HCP.name.ilike(f"%{clean_name}%")) |
            (HCP.name.ilike(f"%{name_no_dr}%")) |
            (HCP.name.ilike(f"%{name_with_dot}%"))
        ).first()

    if not hcp:
        return (
            current_form,
            {
                "tool_name": "hcp_history",
                "tool_summary": "HCP not found for history lookup",
                "parameters": params,
                "status": "ERROR",
                "execution_time_ms": 60
            },
            f"I couldn't find an HCP matching '**{hcp_name or hcp_id}**' to check their history. Try searching for their hospital first."
        )

    interactions = db.query(Interaction).filter(
        Interaction.hcp_id == hcp.id
    ).order_by(Interaction.interaction_date.desc()).all()

    follow_ups = db.query(FollowUp).filter(
        FollowUp.hcp_id == hcp.id
    ).order_by(FollowUp.due_date.asc()).all()

    if not interactions:
        return (
            current_form,
            {
                "tool_name": "hcp_history",
                "tool_summary": f"Retrieved history for {hcp.name} (0 meetings)",
                "parameters": params,
                "status": "SUCCESS",
                "execution_time_ms": 115
            },
            f"**{hcp.name}** ({hcp.specialty}, {hcp.hospital}) is registered in the CRM, but has no historical interaction logs recorded yet."
        )

    # Compute Sentiment Trend and Product Frequency
    sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
    products = set()
    for i in interactions:
        if i.observed_sentiment in sentiments:
            sentiments[i.observed_sentiment] += 1
        if i.topics_discussed:
            for prod in ["CardioPlus", "OncoBoost", "GlucoFix", "NeuroCalm", "DermaGlow"]:
                if prod.lower() in i.topics_discussed.lower():
                    products.add(prod)

    meetings_text = "\n".join([
        f"- **{i.interaction_date} ({i.interaction_type})**: *{i.ai_summary or i.topics_discussed[:100]}* (Sentiment: **{i.observed_sentiment}**)"
        for i in interactions[:5]
    ])

    follow_ups_text = "\n".join([
        f"- **Due {fu.due_date} ({fu.status})**: {fu.action_description}"
        for fu in follow_ups[:3]
    ]) if follow_ups else "*No pending follow-ups.*"

    tool_badge = {
        "tool_name": "hcp_history",
        "tool_summary": f"Loaded {len(interactions)} meetings & sentiment trend for {hcp.name}",
        "parameters": params,
        "status": "SUCCESS",
        "execution_time_ms": 160
    }

    assistant_message = (
        f"### Historical Profile for **{hcp.name}** ({hcp.specialty})\n"
        f"**Hospital:** {hcp.hospital} | **Total Interactions:** {len(interactions)}\n\n"
        f"📊 **Sentiment Trend:** {sentiments['Positive']} Positive, {sentiments['Neutral']} Neutral, {sentiments['Negative']} Negative\n"
        f"💊 **Products Discussed:** {', '.join(products) if products else 'General Therapeutics'}\n\n"
        f"**Past Meetings:**\n{meetings_text}\n\n"
        f"**Pending Follow-ups:**\n{follow_ups_text}"
    )

    return current_form, tool_badge, assistant_message
