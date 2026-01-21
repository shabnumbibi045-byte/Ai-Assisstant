"""Authentication Service - Business logic for user authentication."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database.models import User, UserPermission
from .models import UserCreate, UserLogin, Token, UserResponse
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_verification_token
)
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserCreate
    ) -> Tuple[User, str]:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Tuple of (User, verification_token)
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        verification_token = generate_verification_token()

        user = User(
            user_id=user_id,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            is_active=True,
            is_verified=True,  # Auto-verify all users
            verification_token=verification_token,
            created_at=datetime.utcnow()
        )

        db.add(user)
        await db.flush()  # Flush to get the user.id before creating permissions

        # Add ALL permissions for all modules
        all_modules = ["chat", "memory", "banking", "stocks", "travel", "research", "tools", "rag", "setup"]
        for module in all_modules:
            for perm_type in ["read", "write"]:
                permission = UserPermission(
                    user_id=user.id,
                    module=module,
                    permission_type=perm_type,
                    granted=True,
                    granted_at=datetime.utcnow(),
                    granted_by="system"
                )
                db.add(permission)

        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User registered: {user.email}")
        return user, verification_token
    
    @staticmethod
    async def ensure_all_permissions(db: AsyncSession, user: User):
        """
        Ensure user has all permissions for all modules.
        Automatically grants missing permissions on login.

        Args:
            db: Database session
            user: User object
        """
        all_modules = ["chat", "memory", "banking", "stocks", "travel", "research", "tools", "rag", "setup"]
        all_permission_types = ["read", "write"]

        # Get existing permissions
        stmt = select(UserPermission).where(UserPermission.user_id == user.id)
        result = await db.execute(stmt)
        existing_permissions = result.scalars().all()

        # Create set of existing permission keys
        existing_keys = {
            (perm.module, perm.permission_type)
            for perm in existing_permissions
        }

        # Add missing permissions
        permissions_added = 0
        for module in all_modules:
            for perm_type in all_permission_types:
                if (module, perm_type) not in existing_keys:
                    permission = UserPermission(
                        user_id=user.id,
                        module=module,
                        permission_type=perm_type,
                        granted=True,
                        granted_at=datetime.utcnow(),
                        granted_by="system"
                    )
                    db.add(permission)
                    permissions_added += 1

        if permissions_added > 0:
            await db.commit()
            logger.info(f"Added {permissions_added} missing permissions for user {user.email}")

        # Ensure user is verified and active
        if not user.is_verified or not user.is_active:
            user.is_verified = True
            user.is_active = True
            await db.commit()
            logger.info(f"Auto-verified and activated user {user.email}")

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        login_data: UserLogin
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            login_data: Login credentials

        Returns:
            User if authentication successful, None otherwise
        """
        stmt = select(User).where(User.email == login_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Login failed: user not found - {login_data.email}")
            return None

        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Login failed: invalid password - {login_data.email}")
            return None

        # Auto-grant all permissions and verify user on login
        await AuthService.ensure_all_permissions(db, user)

        # Update last active
        user.last_active = datetime.utcnow()
        await db.commit()

        logger.info(f"User authenticated with full permissions: {user.email}")
        return user
    
    @staticmethod
    def create_tokens(user: User, remember_me: bool = False) -> Token:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: Authenticated user
            remember_me: Whether to extend token lifetime
            
        Returns:
            Token object with access and refresh tokens
        """
        token_data = {
            "sub": user.user_id,
            "email": user.email,
            "name": user.full_name
        }
        
        # Extend expiration if remember_me
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        if remember_me:
            access_expires = timedelta(days=7)
        
        access_token = create_access_token(token_data, access_expires)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_expires.total_seconds())
        )
    
    @staticmethod
    async def refresh_tokens(
        db: AsyncSession,
        refresh_token: str
    ) -> Optional[Token]:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Valid refresh token
            
        Returns:
            New Token object or None if invalid
        """
        payload = verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        
        # Verify user still exists and is active
        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Create new tokens
        return AuthService.create_tokens(user)
    
    @staticmethod
    async def verify_email(
        db: AsyncSession,
        token: str
    ) -> bool:
        """
        Verify user email with token.
        
        Args:
            db: Database session
            token: Verification token
            
        Returns:
            True if verification successful
        """
        stmt = select(User).where(User.verification_token == token)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_verified = True
        user.verification_token = None
        await db.commit()
        
        logger.info(f"Email verified: {user.email}")
        return True
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"Password changed: {user.email}")
        return True
    
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: str
    ) -> Optional[User]:
        """Get user by user_id."""
        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_permissions(
        db: AsyncSession,
        user: User,
        module: str,
        permission_type: str,
        granted: bool
    ) -> None:
        """Update user permission for a module."""
        # Check if permission exists
        for perm in user.permissions:
            if perm.module == module and perm.permission_type == permission_type:
                perm.granted = granted
                perm.granted_at = datetime.utcnow() if granted else None
                await db.commit()
                return
        
        # Create new permission
        permission = UserPermission(
            user_id=user.id,
            module=module,
            permission_type=permission_type,
            granted=granted,
            granted_at=datetime.utcnow() if granted else None
        )
        db.add(permission)
        await db.commit()
