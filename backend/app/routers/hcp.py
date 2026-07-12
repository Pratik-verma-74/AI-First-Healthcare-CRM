from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import HCP, Interaction, FollowUp
from app.models.pydantic_schemas import HCPResponse, InteractionResponse

router = APIRouter(tags=["HCP & History"])


@router.get("/hcp", response_model=List[HCPResponse])
def get_all_hcps(
    search: Optional[str] = Query(None, description="Search by HCP name, hospital, or specialty"),
    db: Session = Depends(get_db)
):
    """
    GET /hcp - Retrieve all Healthcare Professionals (Doctors) or filter by search query.
    """
    query = db.query(HCP)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            (HCP.name.ilike(search_term)) |
            (HCP.hospital.ilike(search_term)) |
            (HCP.specialty.ilike(search_term)) |
            (HCP.city.ilike(search_term))
        )
    return query.order_by(HCP.name).all()


@router.get("/hcp/{id}", response_model=HCPResponse)
def get_hcp_by_id(id: int, db: Session = Depends(get_db)):
    """
    GET /hcp/{id} - Retrieve detailed profile of a specific Healthcare Professional.
    """
    hcp = db.query(HCP).filter(HCP.id == id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail=f"HCP with ID {id} not found")
    return hcp


@router.get("/history/{id}")
def get_hcp_history(id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /history/{id} - Retrieve comprehensive historical interaction timeline for an HCP,
    including past meetings, products discussed, summaries, follow-ups, and sentiment trend.
    """
    hcp = db.query(HCP).filter(HCP.id == id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail=f"HCP with ID {id} not found")

    interactions = db.query(Interaction).filter(
        Interaction.hcp_id == id
    ).order_by(Interaction.interaction_date.desc()).all()

    follow_ups = db.query(FollowUp).filter(
        FollowUp.hcp_id == id
    ).order_by(FollowUp.due_date.asc()).all()

    # Calculate sentiment distribution and trend
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    history_records = []
    products_discussed_list = set()

    for idx in interactions:
        if idx.observed_sentiment in sentiment_counts:
            sentiment_counts[idx.observed_sentiment] += 1
        else:
            sentiment_counts["Neutral"] += 1

        if idx.topics_discussed:
            # Extract basic product names if mentioned
            for prod in ["CardioPlus", "OncoBoost", "GlucoFix", "NeuroCalm", "DermaGlow"]:
                if prod.lower() in idx.topics_discussed.lower():
                    products_discussed_list.add(prod)

        history_records.append({
            "interaction_id": idx.id,
            "interaction_type": idx.interaction_type,
            "date": str(idx.interaction_date),
            "time": idx.interaction_time,
            "attendees": idx.attendees,
            "topics_discussed": idx.topics_discussed,
            "materials_shared": idx.materials_shared,
            "samples_distributed": idx.samples_distributed,
            "observed_sentiment": idx.observed_sentiment,
            "outcomes": idx.outcomes,
            "ai_summary": idx.ai_summary,
            "status": idx.status
        })

    follow_up_records = [
        {
            "id": fu.id,
            "interaction_id": fu.interaction_id,
            "action_description": fu.action_description,
            "due_date": str(fu.due_date),
            "status": fu.status
        }
        for fu in follow_ups
    ]

    return {
        "hcp": {
            "id": hcp.id,
            "name": hcp.name,
            "specialty": hcp.specialty,
            "hospital": hcp.hospital,
            "city": hcp.city,
            "email": hcp.contact_email,
            "phone": hcp.phone
        },
        "total_interactions": len(interactions),
        "sentiment_trend": sentiment_counts,
        "frequently_discussed_products": list(products_discussed_list),
        "interactions": history_records,
        "follow_ups": follow_up_records
    }
