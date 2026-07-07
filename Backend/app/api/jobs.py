from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.models.models import Job, JobMaterial, User, Variant, Customer
from app.schemas.schemas import (
    JobCreate, JobUpdate, JobResponse,
    JobMaterialResponse, JobMaterialCreate
)
from app.api.deps import get_current_user
from app.services.services import (
    assign_material_to_job,
    return_material_from_job,
    consume_material_for_job,
    write_audit_log
)

router = APIRouter(prefix="/jobs", tags=["Job Management"])

@router.get("", response_model=List[JobResponse])
def get_jobs(
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Job).join(Customer)
    if status:
        query = query.filter(Job.status == status)
    if customer_id:
        query = query.filter(Job.customer_id == customer_id)
        
    jobs = query.all()
    
    response = []
    for j in jobs:
        res = JobResponse.model_validate(j)
        res.customer_name = j.customer.name
        res.assigned_employee_name = j.assigned_employee.username if j.assigned_employee else None
        
        # Map materials with SKUs and unit prices for frontend usage
        materials_res = []
        for m in j.materials:
            m_res = JobMaterialResponse.model_validate(m)
            m_res.sku = m.variant.SKU
            m_res.price = m.variant.price
            materials_res.append(m_res)
            
        res.materials = materials_res
        response.append(res)
        
    return response

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Create base job
    job = Job(
        customer_id=job_in.customer_id,
        name=job_in.name,
        status="Pending",
        start_date=job_in.start_date,
        deadline=job_in.deadline,
        assigned_employee_id=job_in.assigned_employee_id,
        notes=job_in.notes
    )
    db.add(job)
    db.flush()
    
    # 2. Assign materials if present
    for material in job_in.materials:
        assign_material_to_job(
            db=db,
            job_id=job.id,
            variant_id=material.variant_id,
            quantity=material.quantity_assigned,
            user_id=current_user.id,
            notes="Initial job assignment"
        )
        
    write_audit_log(db, current_user.id, "Created job project", "job", job.id, {"name": job.name})
    db.commit()
    db.refresh(job)
    
    # Format response
    res = JobResponse.model_validate(job)
    res.customer_name = job.customer.name
    res.assigned_employee_name = job.assigned_employee.username if job.assigned_employee else None
    
    materials_res = []
    for m in job.materials:
        m_res = JobMaterialResponse.model_validate(m)
        m_res.sku = m.variant.SKU
        m_res.price = m.variant.price
        materials_res.append(m_res)
    res.materials = materials_res
    
    return res

@router.get("/{id}", response_model=JobResponse)
def get_job(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    res = JobResponse.model_validate(job)
    res.customer_name = job.customer.name
    res.assigned_employee_name = job.assigned_employee.username if job.assigned_employee else None
    
    materials_res = []
    for m in job.materials:
        m_res = JobMaterialResponse.model_validate(m)
        m_res.sku = m.variant.SKU
        m_res.price = m.variant.price
        materials_res.append(m_res)
    res.materials = materials_res
    
    return res

@router.put("/{id}", response_model=JobResponse)
def update_job(
    id: UUID,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    update_data = job_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(job, field, val)
        
    db.add(job)
    write_audit_log(
        db,
        current_user.id,
        "Updated job project status",
        "job",
        job.id,
        {"status": job.status, "updated_fields": list(update_data.keys())}
    )
    db.commit()
    db.refresh(job)
    
    res = JobResponse.model_validate(job)
    res.customer_name = job.customer.name
    res.assigned_employee_name = job.assigned_employee.username if job.assigned_employee else None
    
    materials_res = []
    for m in job.materials:
        m_res = JobMaterialResponse.model_validate(m)
        m_res.sku = m.variant.SKU
        m_res.price = m.variant.price
        materials_res.append(m_res)
    res.materials = materials_res
    
    return res

@router.post("/{id}/assign-material", response_model=JobMaterialResponse)
def assign_material(
    id: UUID,
    mat_in: JobMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mat = assign_material_to_job(
        db=db,
        job_id=id,
        variant_id=mat_in.variant_id,
        quantity=mat_in.quantity_assigned,
        user_id=current_user.id
    )
    db.commit()
    db.refresh(mat)
    
    res = JobMaterialResponse.model_validate(mat)
    res.sku = mat.variant.SKU
    res.price = mat.variant.price
    return res

@router.post("/{id}/consume-material", response_model=JobMaterialResponse)
def consume_material(
    id: UUID,
    variant_id: UUID = Query(...),
    quantity: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mat = consume_material_for_job(
        db=db,
        job_id=id,
        variant_id=variant_id,
        quantity=quantity,
        user_id=current_user.id
    )
    db.commit()
    db.refresh(mat)
    
    res = JobMaterialResponse.model_validate(mat)
    res.sku = mat.variant.SKU
    res.price = mat.variant.price
    return res

@router.post("/{id}/return-material", response_model=JobMaterialResponse)
def return_material(
    id: UUID,
    variant_id: UUID = Query(...),
    quantity: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mat = return_material_from_job(
        db=db,
        job_id=id,
        variant_id=variant_id,
        quantity=quantity,
        user_id=current_user.id
    )
    db.commit()
    db.refresh(mat)
    
    res = JobMaterialResponse.model_validate(mat)
    res.sku = mat.variant.SKU
    res.price = mat.variant.price
    return res
