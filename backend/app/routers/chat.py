from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.pydantic_schemas import ChatRequest, ChatResponse
from app.ai.agent import process_chat_message

router = APIRouter(tags=["AI Chat Assistant (/chat)"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    POST /chat - Primary conversational AI endpoint.
    Receives user natural language message along with the current state of the read-only form.
    Executes the LangGraph state machine (`router_node` -> Groq `gemma2-9b-it` -> tool selection -> DB execution).
    Returns the updated form state, tool diagnostic badge, and natural language response.
    """
    try:
        current_form_dict = payload.current_form_data.model_dump()
        response = process_chat_message(
            session_id=payload.session_id,
            user_message=payload.message,
            current_form_data=current_form_dict,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangGraph execution failed: {str(e)}"
        )
