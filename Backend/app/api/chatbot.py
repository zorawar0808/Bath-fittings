from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.db.session import get_db
from app.models.models import User
from app.api.deps import get_current_user
from app.ai.agent import run_chat_query
from app.services.services import write_audit_log

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

class ChatMessage(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/query", response_model=ChatResponse)
def query_chatbot(
    chat_in: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not chat_in.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
        
    ai_response = run_chat_query(
        db=db,
        message=chat_in.message,
        chat_history=chat_in.chat_history
    )
    
    # Audit log AI interaction (only log metadata, not full content to save DB size)
    write_audit_log(
        db=db,
        user_id=current_user.id,
        action="Consulted AI Chatbot",
        target_type="chatbot",
        target_id=None,
        details={"query_preview": chat_in.message[:50]}
    )
    db.commit()
    
    return ChatResponse(response=ai_response)
