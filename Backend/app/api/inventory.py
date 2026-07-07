from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID
from app.db.session import get_db
from app.models.models import Category, Subcategory, Product, Variant, InventoryTransaction, User
from app.schemas.schemas import (
    CategoryCreate, CategoryResponse,
    SubcategoryCreate, SubcategoryResponse,
    ProductCreate, ProductResponse,
    VariantCreate, VariantUpdate, VariantResponse,
    TransactionResponse, TransactionCreate
)
from app.api.deps import get_current_user, get_admin_user
from app.services.services import create_transaction, record_damaged_stock, write_audit_log

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

# Categories Endpoints
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).all()

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    existing = db.query(Category).filter(Category.name == category_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category = Category(**category_in.model_dump())
    db.add(category)
    db.flush()
    write_audit_log(db, admin_user.id, "Created category", "category", category.id, {"name": category.name})
    db.commit()
    db.refresh(category)
    return category

# Subcategories Endpoints
@router.get("/subcategories", response_model=List[SubcategoryResponse])
def get_subcategories(
    category_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Subcategory)
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    return query.all()

@router.post("/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(
    sub_in: SubcategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    existing = db.query(Subcategory).filter(
        Subcategory.category_id == sub_in.category_id,
        Subcategory.name == sub_in.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subcategory already exists under this category")
    
    subcategory = Subcategory(**sub_in.model_dump())
    db.add(subcategory)
    db.flush()
    write_audit_log(db, admin_user.id, "Created subcategory", "subcategory", subcategory.id, {"name": subcategory.name})
    db.commit()
    db.refresh(subcategory)
    return subcategory

# Products Endpoints
@router.get("/products", response_model=List[ProductResponse])
def get_products(
    subcategory_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)
    return query.all()

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: ProductCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    product = Product(**prod_in.model_dump())
    db.add(product)
    db.flush()
    write_audit_log(db, admin_user.id, "Created product", "product", product.id, {"name": product.name})
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete all transactions for all variants of this product first
    variant_ids = [v.id for v in db.query(Variant).filter(Variant.product_id == id).all()]
    if variant_ids:
        db.query(InventoryTransaction).filter(InventoryTransaction.variant_id.in_(variant_ids)).delete(synchronize_session=False)
        db.query(Variant).filter(Variant.product_id == id).delete(synchronize_session=False)

    write_audit_log(db, admin_user.id, "Deleted product", "product", product.id, {"name": product.name})
    db.delete(product)
    db.commit()

# Variants Endpoints
@router.get("/variants", response_model=List[VariantResponse])
def get_variants(
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    subcategory_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Variant).join(Product)
    
    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)
    elif category_id:
        query = query.join(Subcategory).filter(Subcategory.category_id == category_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Variant.SKU.ilike(search_filter),
                Variant.color.ilike(search_filter),
                Variant.finish.ilike(search_filter),
                Variant.dimensions.ilike(search_filter),
                Product.name.ilike(search_filter)
            )
        )

    variants = query.all()
    
    response = []
    for v in variants:
        res = VariantResponse.model_validate(v)
        res.product_name = v.product.name
        response.append(res)
        
    return response

@router.post("/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    var_in: VariantCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    existing = db.query(Variant).filter(Variant.SKU == var_in.SKU).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
        
    variant = Variant(**var_in.model_dump())
    db.add(variant)
    db.flush()
    
    if var_in.quantity > 0:
        transaction = InventoryTransaction(
            variant_id=variant.id,
            quantity=var_in.quantity,
            action_type="added",
            user_id=admin_user.id,
            notes="Initial quantity at creation"
        )
        db.add(transaction)
        
    write_audit_log(db, admin_user.id, "Created product variant", "variant", variant.id, {"sku": variant.SKU})
    db.commit()
    db.refresh(variant)
    
    res = VariantResponse.model_validate(variant)
    res.product_name = variant.product.name
    return res

@router.put("/variants/{id}", response_model=VariantResponse)
def update_variant(
    id: UUID,
    var_in: VariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    variant = db.query(Variant).filter(Variant.id == id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
        
    update_data = var_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(variant, field, val)
        
    db.add(variant)
    write_audit_log(
        db,
        current_user.id,
        "Updated variant fields",
        "variant",
        variant.id,
        {"sku": variant.SKU, "updated_fields": list(update_data.keys())}
    )
    db.commit()
    db.refresh(variant)
    
    res = VariantResponse.model_validate(variant)
    res.product_name = variant.product.name
    return res

@router.delete("/variants/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    id: UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    variant = db.query(Variant).filter(Variant.id == id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    write_audit_log(db, admin_user.id, "Deleted variant", "variant", variant.id, {"sku": variant.SKU})
    db.query(InventoryTransaction).filter(InventoryTransaction.variant_id == id).delete()
    db.delete(variant)
    db.commit()

# Transaction Endpoints
@router.post("/variants/{id}/transaction", response_model=TransactionResponse)
def add_transaction(
    id: UUID,
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if id != tx_in.variant_id:
        raise HTTPException(status_code=400, detail="Variant ID mismatch")
        
    tx = create_transaction(
        db=db,
        variant_id=tx_in.variant_id,
        quantity=tx_in.quantity,
        action_type=tx_in.action_type,
        user_id=current_user.id,
        notes=tx_in.notes
    )
    db.commit()
    db.refresh(tx)
    
    res = TransactionResponse.model_validate(tx)
    res.username = current_user.username
    res.sku = tx.variant.SKU
    return res

@router.post("/variants/{id}/damaged", response_model=TransactionResponse)
def log_damaged(
    id: UUID,
    quantity: float = Query(..., gt=0),
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = record_damaged_stock(
        db=db,
        variant_id=id,
        quantity=quantity,
        user_id=current_user.id,
        notes=notes
    )
    db.commit()
    db.refresh(tx)
    
    res = TransactionResponse.model_validate(tx)
    res.username = current_user.username
    res.sku = tx.variant.SKU
    return res

@router.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    variant_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(InventoryTransaction).order_by(InventoryTransaction.timestamp.desc())
    if variant_id:
        query = query.filter(InventoryTransaction.variant_id == variant_id)
        
    transactions = query.all()
    
    response = []
    for t in transactions:
        res = TransactionResponse.model_validate(t)
        res.sku = t.variant.SKU
        res.username = t.user.username if t.user else "System"
        response.append(res)
        
    return response