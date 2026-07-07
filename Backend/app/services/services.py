from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.models.models import (
    Variant,
    InventoryTransaction,
    Job,
    JobMaterial,
    SupplierOrder,
    SupplierOrderItem,
    Alert,
    AuditLog,
    User,
)
from app.schemas.schemas import TransactionCreate

def write_audit_log(
    db: Session,
    user_id: Optional[UUID],
    action: str,
    target_type: str,
    target_id: Optional[UUID],
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {}
    )
    db.add(log_entry)
    db.flush()  # flush to get ID, but don't commit here so it rolls back with outer transaction
    return log_entry

def check_low_stock_alert(db: Session, variant: Variant) -> None:
    # Check if quantity is below threshold
    if variant.quantity <= variant.reorder_threshold:
        # Check if an unresolved alert already exists
        existing_alert = db.query(Alert).filter(
            Alert.variant_id == variant.id,
            Alert.is_resolved == False
        ).first()

        if not existing_alert:
            alert = Alert(
                variant_id=variant.id,
                alert_type="low_stock",
                message=f"Stock for variant SKU {variant.SKU} ({variant.dimensions or ''} {variant.color or ''}) is low: {variant.quantity} {variant.unit} left. Threshold is {variant.reorder_threshold}.",
                is_resolved=False
            )
            db.add(alert)
            db.flush()
            
            # Log the alert trigger in audit logs
            write_audit_log(
                db=db,
                user_id=None,
                action="Low stock alert triggered",
                target_type="alert",
                target_id=alert.id,
                details={"sku": variant.SKU, "quantity": variant.quantity}
            )
    else:
        # If quantity is above threshold, resolve any open alerts
        open_alerts = db.query(Alert).filter(
            Alert.variant_id == variant.id,
            Alert.is_resolved == False
        ).all()

        for alert in open_alerts:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            db.add(alert)
            
            write_audit_log(
                db=db,
                user_id=None,
                action="Low stock alert resolved",
                target_type="alert",
                target_id=alert.id,
                details={"sku": variant.SKU, "quantity": variant.quantity}
            )

def create_transaction(
    db: Session,
    variant_id: UUID,
    quantity: float,
    action_type: str,
    user_id: Optional[UUID],
    notes: Optional[str] = None
) -> InventoryTransaction:
    # 1. Fetch the variant
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )

    # 2. Prevent negative stock if the action consumes items
    if quantity < 0 and variant.quantity + quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for SKU {variant.SKU}. Available: {variant.quantity} {variant.unit}, Requested adjustment: {quantity} {variant.unit}."
        )

    # 3. Create the transaction entry
    transaction = InventoryTransaction(
        variant_id=variant_id,
        quantity=quantity,
        action_type=action_type,
        user_id=user_id,
        notes=notes
    )
    db.add(transaction)

    # 4. Update the cached quantity balance on the variant
    variant.quantity += quantity
    db.add(variant)
    db.flush()

    # 5. Check if stock alert is triggered or resolved
    check_low_stock_alert(db, variant)

    # 6. Log in Audit logs
    username = "System"
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            username = user.username
            
    write_audit_log(
        db=db,
        user_id=user_id,
        action=f"Stock updated ({action_type})",
        target_type="variant",
        target_id=variant_id,
        details={
            "sku": variant.SKU,
            "quantity_adjusted": quantity,
            "new_balance": variant.quantity,
            "performed_by": username,
            "notes": notes
        }
    )

    return transaction

def record_damaged_stock(
    db: Session,
    variant_id: UUID,
    quantity: float,
    user_id: Optional[UUID],
    notes: Optional[str] = None
) -> InventoryTransaction:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Damaged quantity must be positive"
        )
    return create_transaction(
        db=db,
        variant_id=variant_id,
        quantity=-quantity,
        action_type="damaged",
        user_id=user_id,
        notes=notes
    )

def assign_material_to_job(
    db: Session,
    job_id: UUID,
    variant_id: UUID,
    quantity: float,
    user_id: Optional[UUID],
    notes: Optional[str] = None
) -> JobMaterial:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned quantity must be positive"
        )

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Call stock reduction transaction
    create_transaction(
        db=db,
        variant_id=variant_id,
        quantity=-quantity,
        action_type="job_used",
        user_id=user_id,
        notes=f"Assigned to job: {job.name}. {notes or ''}"
    )

    # Check if this variant is already listed in job materials
    job_material = db.query(JobMaterial).filter(
        JobMaterial.job_id == job_id,
        JobMaterial.variant_id == variant_id
    ).first()

    if job_material:
        job_material.quantity_assigned += quantity
    else:
        job_material = JobMaterial(
            job_id=job_id,
            variant_id=variant_id,
            quantity_assigned=quantity,
            quantity_consumed=0.0,
            status="Assigned"
        )
        db.add(job_material)

    db.flush()

    write_audit_log(
        db=db,
        user_id=user_id,
        action="Material assigned to job",
        target_type="job",
        target_id=job_id,
        details={
            "job_name": job.name,
            "sku": variant.SKU,
            "quantity_assigned": quantity
        }
    )

    return job_material

def return_material_from_job(
    db: Session,
    job_id: UUID,
    variant_id: UUID,
    quantity: float,
    user_id: Optional[UUID],
    notes: Optional[str] = None
) -> JobMaterial:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Returned quantity must be positive"
        )

    job_material = db.query(JobMaterial).filter(
        JobMaterial.job_id == job_id,
        JobMaterial.variant_id == variant_id
    ).first()

    if not job_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This variant is not assigned to the specified job"
        )

    # Validate that we don't return more than what was assigned
    max_returnable = job_material.quantity_assigned - job_material.quantity_consumed
    if quantity > max_returnable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot return more materials than are currently unconsumed in the job. Assigned unconsumed: {max_returnable}."
        )

    job = db.query(Job).filter(Job.id == job_id).first()
    variant = db.query(Variant).filter(Variant.id == variant_id).first()

    # Call stock replenishment transaction
    create_transaction(
        db=db,
        variant_id=variant_id,
        quantity=quantity,
        action_type="job_returned",
        user_id=user_id,
        notes=f"Returned from job: {job.name}. {notes or ''}"
    )

    job_material.quantity_assigned -= quantity
    if job_material.quantity_assigned <= 0 and job_material.quantity_consumed <= 0:
        db.delete(job_material)
    else:
        # Update status if all assigned have been consumed or deleted
        if job_material.quantity_assigned == job_material.quantity_consumed:
            job_material.status = "Consumed"
        db.add(job_material)

    db.flush()

    write_audit_log(
        db=db,
        user_id=user_id,
        action="Material returned from job",
        target_type="job",
        target_id=job_id,
        details={
            "job_name": job.name,
            "sku": variant.SKU,
            "quantity_returned": quantity
        }
    )

    return job_material

def consume_material_for_job(
    db: Session,
    job_id: UUID,
    variant_id: UUID,
    quantity: float,
    user_id: Optional[UUID]
) -> JobMaterial:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumed quantity must be positive"
        )

    job_material = db.query(JobMaterial).filter(
        JobMaterial.job_id == job_id,
        JobMaterial.variant_id == variant_id
    ).first()

    if not job_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This variant is not assigned to the specified job"
        )

    unconsumed = job_material.quantity_assigned - job_material.quantity_consumed
    if quantity > unconsumed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot consume more materials than assigned. Unconsumed: {unconsumed}."
        )

    job = db.query(Job).filter(Job.id == job_id).first()
    variant = db.query(Variant).filter(Variant.id == variant_id).first()

    job_material.quantity_consumed += quantity
    if job_material.quantity_consumed >= job_material.quantity_assigned:
        job_material.status = "Consumed"
    
    db.add(job_material)
    db.flush()

    write_audit_log(
        db=db,
        user_id=user_id,
        action="Material consumed in job",
        target_type="job",
        target_id=job_id,
        details={
            "job_name": job.name,
            "sku": variant.SKU,
            "quantity_consumed": quantity
        }
    )

    return job_material

def complete_supplier_order(
    db: Session,
    order_id: UUID,
    user_id: Optional[UUID]
) -> SupplierOrder:
    order = db.query(SupplierOrder).filter(SupplierOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier order not found"
        )

    if order.status == "Received":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier order has already been marked as Received"
        )

    if order.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot receive a cancelled order"
        )

    # 1. Update order status
    order.status = "Received"
    db.add(order)

    # 2. Replenish stock for all items
    for item in order.items:
        create_transaction(
            db=db,
            variant_id=item.variant_id,
            quantity=item.quantity_ordered,
            action_type="added",
            user_id=user_id,
            notes=f"Replenished from Supplier Order: {order.id}"
        )

    db.flush()

    write_audit_log(
        db=db,
        user_id=user_id,
        action="Supplier order received",
        target_type="order",
        target_id=order_id,
        details={"supplier_name": order.supplier.name}
    )

    return order
