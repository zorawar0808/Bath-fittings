from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# JWT Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = "Employee"  # Admin or Employee

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Customer schemas
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

class CustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: Optional[str]
    email: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Category schemas
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# Subcategory schemas
class SubcategoryCreate(BaseModel):
    category_id: UUID
    name: str
    description: Optional[str] = None

class SubcategoryResponse(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# Product schemas
class ProductCreate(BaseModel):
    subcategory_id: UUID
    name: str
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: UUID
    subcategory_id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# Variant schemas
class VariantCreate(BaseModel):
    product_id: UUID
    SKU: str
    price: float
    dimensions: Optional[str] = None
    color: Optional[str] = None
    finish: Optional[str] = None
    quantity: float = 0.0
    reorder_threshold: float = 5.0
    unit: str  # sq ft, pieces, meters, boxes, packets
    attributes: Optional[Dict[str, Any]] = None

class VariantUpdate(BaseModel):
    price: Optional[float] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    finish: Optional[str] = None
    reorder_threshold: Optional[float] = None
    unit: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class VariantResponse(BaseModel):
    id: UUID
    product_id: UUID
    SKU: str
    price: float
    dimensions: Optional[str]
    color: Optional[str]
    finish: Optional[str]
    quantity: float
    reorder_threshold: float
    unit: str
    attributes: Optional[Dict[str, Any]]
    created_at: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True

# Inventory transaction schemas
class TransactionCreate(BaseModel):
    variant_id: UUID
    quantity: float  # signed
    action_type: str  # added, removed, damaged, job_used, job_returned
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: UUID
    variant_id: UUID
    quantity: float
    action_type: str
    timestamp: datetime
    user_id: Optional[UUID]
    notes: Optional[str]
    username: Optional[str] = None
    sku: Optional[str] = None

    class Config:
        from_attributes = True

# Job schemas
class JobMaterialCreate(BaseModel):
    variant_id: UUID
    quantity_assigned: float

class JobMaterialResponse(BaseModel):
    id: UUID
    job_id: UUID
    variant_id: UUID
    quantity_assigned: float
    quantity_consumed: float
    status: str
    sku: Optional[str] = None
    price: Optional[float] = None

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    customer_id: UUID
    name: str
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    assigned_employee_id: Optional[UUID] = None
    notes: Optional[str] = None
    materials: List[JobMaterialCreate] = []

class JobUpdate(BaseModel):
    status: Optional[str] = None  # Pending, In_Progress, Completed, Cancelled
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    assigned_employee_id: Optional[UUID] = None
    notes: Optional[str] = None

class JobResponse(BaseModel):
    id: UUID
    customer_id: UUID
    name: str
    status: str
    start_date: Optional[datetime]
    deadline: Optional[datetime]
    assigned_employee_id: Optional[UUID]
    notes: Optional[str]
    customer_name: Optional[str] = None
    assigned_employee_name: Optional[str] = None
    materials: List[JobMaterialResponse] = []

    class Config:
        from_attributes = True

# Supplier schemas
class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierResponse(BaseModel):
    id: UUID
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SupplierOrderItemCreate(BaseModel):
    variant_id: UUID
    quantity_ordered: float

class SupplierOrderCreate(BaseModel):
    supplier_id: UUID
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[SupplierOrderItemCreate]

class SupplierOrderItemResponse(BaseModel):
    id: UUID
    variant_id: UUID
    quantity_ordered: float
    sku: Optional[str] = None

    class Config:
        from_attributes = True

class SupplierOrderResponse(BaseModel):
    id: UUID
    supplier_id: UUID
    order_date: datetime
    expected_delivery: Optional[datetime]
    status: str
    notes: Optional[str]
    supplier_name: Optional[str] = None
    items: List[SupplierOrderItemResponse] = []

    class Config:
        from_attributes = True

# Alert schema
class AlertResponse(BaseModel):
    id: UUID
    variant_id: UUID
    alert_type: str
    message: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    sku: Optional[str] = None

    class Config:
        from_attributes = True

# AuditLog schema
class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    target_type: str
    target_id: Optional[UUID]
    timestamp: datetime
    details: Optional[Dict[str, Any]]
    username: Optional[str] = None

    class Config:
        from_attributes = True
