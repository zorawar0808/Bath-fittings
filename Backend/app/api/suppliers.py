from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.models.models import Supplier, SupplierOrder, SupplierOrderItem, User, Variant
from app.schemas.schemas import (
    SupplierCreate, SupplierResponse,
    SupplierOrderCreate, SupplierOrderResponse,
    SupplierOrderItemResponse
)
from app.api.deps import get_current_user
from app.services.services import complete_supplier_order, write_audit_log

router = APIRouter(prefix="/suppliers", tags=["Supplier Management"])

# Suppliers CRUD
@router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Supplier).all()

@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    sup_in: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Supplier).filter(Supplier.name == sup_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier name already exists")
        
    supplier = Supplier(**sup_in.model_dump())
    db.add(supplier)
    db.flush()
    write_audit_log(db, current_user.id, "Created supplier record", "supplier", supplier.id, {"name": supplier.name})
    db.commit()
    db.refresh(supplier)
    return supplier

# Supplier Orders
@router.get("/orders", response_model=List[SupplierOrderResponse])
def get_supplier_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(SupplierOrder).order_by(SupplierOrder.order_date.desc()).all()
    
    response = []
    for o in orders:
        res = SupplierOrderResponse.model_validate(o)
        res.supplier_name = o.supplier.name
        
        # Populate item SKUs
        items_res = []
        for i in o.items:
            i_res = SupplierOrderItemResponse.model_validate(i)
            i_res.sku = i.variant.SKU
            items_res.append(i_res)
        res.items = items_res
        
        response.append(res)
        
    return response

@router.post("/orders", response_model=SupplierOrderResponse, status_code=status.HTTP_201_CREATED)
def create_supplier_order(
    order_in: SupplierOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(Supplier).filter(Supplier.id == order_in.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    # 1. Create base order
    order = SupplierOrder(
        supplier_id=order_in.supplier_id,
        expected_delivery=order_in.expected_delivery,
        status="Pending",
        notes=order_in.notes
    )
    db.add(order)
    db.flush()
    
    # 2. Add individual items
    for item in order_in.items:
        variant = db.query(Variant).filter(Variant.id == item.variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Variant ID {item.variant_id} not found")
            
        order_item = SupplierOrderItem(
            supplier_order_id=order.id,
            variant_id=item.variant_id,
            quantity_ordered=item.quantity_ordered
        )
        db.add(order_item)
        
    write_audit_log(
        db,
        current_user.id,
        "Created supplier purchase order",
        "order",
        order.id,
        {"supplier_name": supplier.name, "item_count": len(order_in.items)}
    )
    db.commit()
    db.refresh(order)
    
    # Format response
    res = SupplierOrderResponse.model_validate(order)
    res.supplier_name = supplier.name
    
    items_res = []
    for i in order.items:
        i_res = SupplierOrderItemResponse.model_validate(i)
        i_res.sku = i.variant.SKU
        items_res.append(i_res)
    res.items = items_res
    
    return res

@router.post("/orders/{id}/receive", response_model=SupplierOrderResponse)
def receive_supplier_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Call service business logic to receive order and increment variant quantities
    order = complete_supplier_order(db=db, order_id=id, user_id=current_user.id)
    db.commit()
    db.refresh(order)
    
    res = SupplierOrderResponse.model_validate(order)
    res.supplier_name = order.supplier.name
    
    items_res = []
    for i in order.items:
        i_res = SupplierOrderItemResponse.model_validate(i)
        i_res.sku = i.variant.SKU
        items_res.append(i_res)
    res.items = items_res
    
    return res
