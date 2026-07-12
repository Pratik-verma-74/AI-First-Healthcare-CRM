import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import Interaction, HCP, FollowUp

router = APIRouter(tags=["Analytics Dashboard (/analytics)"])
logger = logging.getLogger(__name__)


@router.get("/analytics")
def get_analytics_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /analytics - Retrieves comprehensive field analytics for the Recharts dashboard.
    Includes sentiment breakdown, samples distributed per product, interaction types, and KPI summaries.
    """
    interactions = db.query(Interaction).all()
    total_interactions = len(interactions)
    total_hcps = db.query(HCP).count()
    pending_follow_ups = db.query(FollowUp).filter(FollowUp.status == "Pending").count()

    # 1. Sentiment Breakdown
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for i in interactions:
        s = (i.observed_sentiment or "Neutral").strip().capitalize()
        if s in sentiment_counts:
            sentiment_counts[s] += 1
        else:
            sentiment_counts["Neutral"] += 1

    sentiment_breakdown = [
        {"name": "Positive", "value": sentiment_counts["Positive"], "color": "#10b981"},
        {"name": "Neutral", "value": sentiment_counts["Neutral"], "color": "#3b82f6"},
        {"name": "Negative", "value": sentiment_counts["Negative"], "color": "#f43f5e"}
    ]

    # 2. Samples Distributed Aggregation
    product_totals: Dict[str, int] = {}
    for i in interactions:
        raw_samples = i.samples_distributed
        if raw_samples and raw_samples != "No samples distributed":
            try:
                # Try parsing JSON string like {"product": "CardioPlus 50mg", "quantity": 15}
                data = json.loads(raw_samples)
                if isinstance(data, dict):
                    prod = data.get("product", "General Sample")
                    qty = int(data.get("quantity", 1))
                    product_totals[prod] = product_totals.get(prod, 0) + qty
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            prod = item.get("product", "General Sample")
                            qty = int(item.get("quantity", 1))
                            product_totals[prod] = product_totals.get(prod, 0) + qty
            except Exception:
                # If natural text or non-json string, count as 1 or extract digits
                import re
                nums = re.findall(r"\d+", raw_samples)
                qty = int(nums[0]) if nums else 5
                product_totals[raw_samples[:25]] = product_totals.get(raw_samples[:25], 0) + qty

    samples_distributed = [
        {"product": k, "quantity": v} for k, v in sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    # 3. Interaction Types
    type_counts: Dict[str, int] = {}
    for i in interactions:
        t = (i.interaction_type or "Meeting").strip()
        type_counts[t] = type_counts.get(t, 0) + 1

    interaction_types = [
        {"name": k, "count": v} for k, v in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # 4. Top Specialties
    hcps = db.query(HCP).all()
    spec_counts: Dict[str, int] = {}
    for h in hcps:
        sp = (h.specialty or "General Medicine").strip()
        spec_counts[sp] = spec_counts.get(sp, 0) + 1

    top_specialties = [
        {"name": k, "count": v} for k, v in sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "total_interactions": total_interactions,
        "total_hcps": total_hcps,
        "total_follow_ups_pending": pending_follow_ups,
        "sentiment_breakdown": sentiment_breakdown,
        "samples_distributed": samples_distributed,
        "interaction_types": interaction_types,
        "top_specialties": top_specialties
    }
