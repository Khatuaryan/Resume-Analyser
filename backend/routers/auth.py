"""
Authentication router for user registration, login, and profile management.
Handles HR and Candidate authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from typing import Optional
import uuid

from database.firebase_adapter import get_collection
from models.user import (
    UserCreate, UserLogin, UserResponse, Token, UserRole,
    HRProfile, CandidateProfile, UserInDB
)
from auth.jwt_handler import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new candidate user only."""
    users_collection = get_collection("users")
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Force all registrations to be candidates
    user_role = "candidate"
    
    # Create user document
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user_doc = {
        "_id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "company": user_data.company,
        "role": user_role,  # Always candidate
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Insert user into database
    result = await users_collection.insert_one(user_doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Return user response (without password)
    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        company=user_data.company,
        role=user_role,
        created_at=user_doc["created_at"],
        updated_at=user_doc["updated_at"],
        is_active=True
    )

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Authenticate user and return access token."""
    users_collection = get_collection("users")
    
    # Special case: admin login
    if login_data.email == "admin@resumeanalyzer.com" and login_data.password == "password123@":
        # Find admin user
        user = await users_collection.find_one({"email": "admin@resumeanalyzer.com"})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin user not found. Please contact system administrator."
            )
        
        # Check if admin is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account is deactivated"
            )
        
        # Create access token for admin
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user["_id"],
                "email": user["email"],
                "role": "hr"
            },
            expires_delta=access_token_expires
        )
        
        # Return token and user info
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user["_id"],
                email=user["email"],
                full_name=user["full_name"],
                phone=user.get("phone"),
                company=user.get("company"),
                role="hr",
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                is_active=user.get("is_active", True)
            )
        )
    
    # Regular user login (candidates only)
    user = await users_collection.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Ensure all non-admin users are candidates
    user_role = "candidate"
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["_id"],
            "email": user["email"],
            "role": user_role
        },
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user.get("phone"),
            company=user.get("company"),
            role=user_role,
            created_at=user["created_at"],
            updated_at=user["updated_at"],
            is_active=user.get("is_active", True)
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile information."""
    users_collection = get_collection("users")
    
    user = await users_collection.find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["_id"],
        email=user["email"],
        full_name=user["full_name"],
        phone=user.get("phone"),
        company=user.get("company"),
        role=user["role"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
        is_active=user.get("is_active", True)
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information."""
    users_collection = get_collection("users")
    
    # Prepare update data
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    # Add allowed fields to update
    allowed_fields = ["full_name", "phone", "company"]
    for field in allowed_fields:
        if field in profile_data:
            update_data[field] = profile_data[field]
    
    # Update user in database
    result = await users_collection.update_one(
        {"_id": current_user.user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    # Return updated user
    updated_user = await users_collection.find_one({"_id": current_user.user_id})
    return UserResponse(
        id=updated_user["_id"],
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        phone=updated_user.get("phone"),
        company=updated_user.get("company"),
        role=updated_user["role"],
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
        is_active=updated_user.get("is_active", True)
    )

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}

@router.get("/verify-token")
async def verify_user_token(current_user: dict = Depends(get_current_user)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }
