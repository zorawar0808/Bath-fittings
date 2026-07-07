import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Integer,
    Boolean,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False, default="Employee")  # Admin or Employee
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    assigned_jobs = relationship("Job", back_populates="assigned_employee")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    jobs = relationship("Job", back_populates="customer", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")

class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    subcategory = relationship("Subcategory", back_populates="products")
    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    SKU = Column(String(50), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    dimensions = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    finish = Column(String(50), nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)  # Cached balance from transactions
    reorder_threshold = Column(Float, nullable=False, default=5.0)
    unit = Column(String(20), nullable=False)  # sq ft, pieces, meters, boxes, packets
    attributes = Column(JSONB, nullable=True, default=dict)  # Flexible metadata JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="variants")
    transactions = relationship("InventoryTransaction", back_populates="variant", cascade="all, delete-orphan")
    job_materials = relationship("JobMaterial", back_populates="variant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="variant", cascade="all, delete-orphan")
    supplier_order_items = relationship("SupplierOrderItem", back_populates="variant", cascade="all, delete-orphan")

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)  # signed (+ for stock added, - for removal/damaged/used)
    action_type = Column(String(30), nullable=False)  # added, removed, damaged, job_used, job_returned
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    variant = relationship("Variant", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="Pending")  # Pending, In_Progress, Completed, Cancelled
    start_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    assigned_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="jobs")
    assigned_employee = relationship("User", back_populates="assigned_jobs")
    materials = relationship("JobMaterial", back_populates="job", cascade="all, delete-orphan")

class JobMaterial(Base):
    __tablename__ = "job_materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id", ondelete="CASCADE"), nullable=False)
    quantity_assigned = Column(Float, nullable=False, default=0.0)
    quantity_consumed = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), nullable=False, default="Assigned")  # Assigned, Consumed, Returned

    # Relationships
    job = relationship("Job", back_populates="materials")
    variant = relationship("Variant", back_populates="job_materials")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("SupplierOrder", back_populates="supplier", cascade="all, delete-orphan")

class SupplierOrder(Base):
    __tablename__ = "supplier_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="Pending")  # Pending, Received, Cancelled
    notes = Column(Text, nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="orders")
    items = relationship("SupplierOrderItem", back_populates="supplier_order", cascade="all, delete-orphan")

class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_order_id = Column(UUID(as_uuid=True), ForeignKey("supplier_orders.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id", ondelete="CASCADE"), nullable=False)
    quantity_ordered = Column(Float, nullable=False)

    # Relationships
    supplier_order = relationship("SupplierOrder", back_populates="items")
    variant = relationship("Variant", back_populates="supplier_order_items")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False, default="low_stock")
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    variant = relationship("Variant", back_populates="alerts")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # variant, job, transaction, order, customer
    target_id = Column(UUID(as_uuid=True), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSONB, nullable=True, default=dict)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
