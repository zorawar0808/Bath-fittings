from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.db.session import get_db
from app.models.models import Alert, User, Variant
from app.schemas.schemas import AlertResponse
from app.api.deps import get_current_user
from app.services.services import write_audit_log

router = APIRouter(prefix="/alerts", tags=["Inventory Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    unresolved_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert).join(Variant)
    if unresolved_only:
        query = query.filter(Alert.is_resolved == False)
        
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    response = []
    for a in alerts:
        res = AlertResponse.model_validate(a)
        res.sku = a.variant.SKU
        response.append(res)
        
    return response

@router.post("/{id}/resolve", response_model=AlertResponse)
def resolve_alert(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.add(alert)
    
    write_audit_log(
        db,
        current_user.id,
        "Manually resolved alert",
        "alert",
        alert.id,
        {"sku": alert.variant.SKU}
    )
    db.commit()
    db.refresh(alert)
    
    res = AlertResponse.model_validate(alert)
    res.sku = alert.variant.SKU
    return res
