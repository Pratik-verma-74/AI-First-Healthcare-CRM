import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import Interaction, FollowUp, AuditLog, HCP
from app.models.pydantic_schemas import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse
)

router = APIRouter(tags=["Interaction CRUD"])


@router.post("/interaction", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db)
):
    """
    POST /interaction - Create a new HCP Interaction record in the database.
    Optionally creates associated Follow-up action if provided.
    """
    # Verify HCP exists
    hcp = db.query(HCP).filter(HCP.id == payload.hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail=f"HCP with ID {payload.hcp_id} not found")

    new_interaction = Interaction(
        hcp_id=payload.hcp_id,
        interaction_type=payload.interaction_type,
        interaction_date=payload.interaction_date,
        interaction_time=payload.interaction_time,
        attendees=payload.attendees,
        topics_discussed=payload.topics_discussed,
        materials_shared=payload.materials_shared,
        samples_distributed=payload.samples_distributed,
        observed_sentiment=payload.observed_sentiment,
        outcomes=payload.outcomes,
        ai_summary=payload.ai_summary,
        status=payload.status
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    # Create follow-up if specified
    if payload.follow_up_action and payload.follow_up_date:
        follow_up = FollowUp(
            interaction_id=new_interaction.id,
            hcp_id=new_interaction.hcp_id,
            action_description=payload.follow_up_action,
            due_date=payload.follow_up_date,
            status="Pending"
        )
        db.add(follow_up)

    # Record Audit Log
    audit = AuditLog(
        entity_type="Interaction",
        entity_id=new_interaction.id,
        action="MANUAL_CREATE" if payload.status != "Saved" else "AI_SAVE",
        changes=json.dumps(payload.model_dump(mode='json'))
    )
    db.add(audit)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction


@router.get("/interaction", response_model=List[InteractionResponse])
def list_interactions(
    hcp_id: Optional[int] = Query(None, description="Filter interactions by specific HCP ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Draft, Confirmed, Saved)"),
    db: Session = Depends(get_db)
):
    """
    GET /interaction - Retrieve all interactions or filter by HCP ID / Status.
    """
    query = db.query(Interaction)
    if hcp_id:
        query = query.filter(Interaction.hcp_id == hcp_id)
    if status_filter:
        query = query.filter(Interaction.status == status_filter)
    
    return query.order_by(Interaction.interaction_date.desc()).all()


@router.get("/interaction/{id}", response_model=InteractionResponse)
def get_interaction_by_id(id: int, db: Session = Depends(get_db)):
    """
    GET /interaction/{id} - Retrieve detailed information of a specific interaction by ID.
    """
    interaction = db.query(Interaction).filter(Interaction.id == id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail=f"Interaction with ID {id} not found")
    return interaction


@router.put("/interaction/{id}", response_model=InteractionResponse)
def update_interaction(
    id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db)
):
    """
    PUT /interaction/{id} - Update specific fields of an existing interaction without overwriting unchanged values.
    """
    interaction = db.query(Interaction).filter(Interaction.id == id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail=f"Interaction with ID {id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return interaction

    for key, value in update_data.items():
        if value is not None:
            setattr(interaction, key, value)

    # Record Audit Log
    audit = AuditLog(
        entity_type="Interaction",
        entity_id=interaction.id,
        action="UPDATE",
        changes=json.dumps(update_data, default=str)
    )
    db.add(audit)
    db.commit()
    db.refresh(interaction)

    return interaction


@router.delete("/interaction/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(id: int, db: Session = Depends(get_db)):
    """
    DELETE /interaction/{id} - Delete an interaction log from the database.
    """
    interaction = db.query(Interaction).filter(Interaction.id == id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail=f"Interaction with ID {id} not found")

    # Record Audit Log before deletion
    audit = AuditLog(
        entity_type="Interaction",
        entity_id=id,
        action="DELETE",
        changes=json.dumps({"deleted_interaction_id": id})
    )
    db.add(audit)
    db.delete(interaction)
    db.commit()
    return None
