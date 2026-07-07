from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import User
from app.schemas.schemas import UserResponse, UserCreate, Token
from app.api.deps import get_current_user, get_admin_user
from app.services.services import write_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.username)
    
    # Audit log login
    write_audit_log(
        db=db,
        user_id=user.id,
        action="User logged in",
        target_type="user",
        target_id=user.id
    )
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register-employee", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_employee(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pwd,
        role=user_in.role
    )
    db.add(user)
    db.flush()
    
    write_audit_log(
        db=db,
        user_id=admin_user.id,
        action=f"Created user account ({user.role})",
        target_type="user",
        target_id=user.id,
        details={"username": user.username}
    )
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/employees", response_model=List[UserResponse])
def list_employees(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    return db.query(User).all()
