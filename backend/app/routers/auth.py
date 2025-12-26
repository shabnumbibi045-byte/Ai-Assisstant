"""Authentication Router - User registration, login, and token management."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import (
    UserCreate, UserLogin, UserResponse, Token, 
    UserUpdate, PasswordChange, RefreshToken
)
from app.auth.service import AuthService
from app.auth.dependencies import get_db, get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    - **phone**: Optional phone number
    """
    try:
        user, verification_token = await AuthService.register_user(db, user_data)
        
        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user.email, verification_token)
        
        return UserResponse(
            id=user.id,
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            modules_enabled=["chat", "memory"]
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and get access tokens.
    
    - **email**: Registered email address
    - **password**: User password
    - **remember_me**: Extend token lifetime (optional)
    """
    user = await AuthService.authenticate_user(db, login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    tokens = AuthService.create_tokens(user, login_data.remember_me)
    
    logger.info(f"User logged in: {user.email}")
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    tokens = await AuthService.refresh_tokens(db, token_data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user's information."""
    # Get enabled modules from permissions
    modules_enabled = list(set(
        perm.module for perm in current_user.permissions if perm.granted
    ))
    
    return UserResponse(
        id=current_user.id,
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_active=current_user.last_active,
        modules_enabled=modules_enabled
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    if user_data.preferences:
        current_user.preferences = {
            **(current_user.preferences or {}),
            **user_data.preferences
        }
    
    await db.commit()
    await db.refresh(current_user)
    
    modules_enabled = list(set(
        perm.module for perm in current_user.permissions if perm.granted
    ))
    
    return UserResponse(
        id=current_user.id,
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_active=current_user.last_active,
        modules_enabled=modules_enabled
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password."""
    success = await AuthService.change_password(
        db,
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}


@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with verification token."""
    success = await AuthService.verify_email(db, token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user.
    
    Note: Client should discard tokens. 
    For full token invalidation, implement token blacklist.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}
