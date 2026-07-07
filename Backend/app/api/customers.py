from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.models.models import Customer, User
from app.schemas.schemas import CustomerCreate, CustomerResponse
from app.api.deps import get_current_user
from app.services.services import write_audit_log

router = APIRouter(prefix="/customers", tags=["Customer Management"])

@router.get("", response_model=List[CustomerResponse])
def get_customers(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Customer)
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%"))
    return query.all()

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.flush()
    write_audit_log(db, current_user.id, "Created customer record", "customer", customer.id, {"name": customer.name})
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/{id}", response_model=CustomerResponse)
def get_customer(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{id}", response_model=CustomerResponse)
def update_customer(
    id: UUID,
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    for field, val in customer_in.model_dump().items():
        setattr(customer, field, val)
        
    db.add(customer)
    write_audit_log(db, current_user.id, "Updated customer details", "customer", customer.id, {"name": customer.name})
    db.commit()
    db.refresh(customer)
    return customer
