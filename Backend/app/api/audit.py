from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.models.models import AuditLog, User
from app.schemas.schemas import AuditLogResponse
from app.api.deps import get_admin_user

router = APIRouter(prefix="/audit", tags=["Security & Audits"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    target_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    query = db.query(AuditLog).outerjoin(User).order_by(AuditLog.timestamp.desc())
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
        
    logs = query.limit(100).all()
    
    response = []
    for l in logs:
        res = AuditLogResponse.model_validate(l)
        res.username = l.user.username if l.user else "System"
        response.append(res)
        
    return response
