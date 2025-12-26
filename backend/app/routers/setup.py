"""Setup Router - User profile and module setup endpoints."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.schemas import UserProfileRequest, ModuleSetupRequest, UserPreferences, BankCountry
from app.auth.dependencies import get_current_user, get_current_verified_user
from app.database.database import get_db_session
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/setup", tags=["setup"])


# ============================================
# ADDITIONAL SCHEMAS
# ============================================

class ModulePermission(BaseModel):
    """Permission settings for a module."""
    enabled: bool = True
    read: bool = True
    write: bool = True
    execute: bool = True
    admin: bool = False


class UserModulesResponse(BaseModel):
    """Response with user's enabled modules."""
    user_id: str
    modules: List[str]
    permissions: Dict[str, Dict[str, bool]]
    updated_at: datetime


class UserProfileResponse(BaseModel):
    """User profile response."""
    user_id: str
    email: str
    full_name: str
    is_verified: bool
    preferences: Dict[str, Any]
    modules_enabled: List[str]
    created_at: datetime
    updated_at: datetime


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences."""
    default_currency: Optional[str] = None
    default_language: Optional[str] = None
    banking_countries: Optional[List[BankCountry]] = None
    priceline_vip_tier: Optional[str] = None
    accountant_email: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None


# ============================================
# DEFAULT VALUES
# ============================================

DEFAULT_MODULES = ["chat", "memory"]
ALL_MODULES = ["chat", "memory", "banking", "stocks", "travel", "research", "voice", "rag"]

DEFAULT_PREFERENCES = {
    "default_currency": "USD",
    "default_language": "en",
    "banking_countries": ["CA", "US", "KE"],
    "priceline_vip_tier": "standard",
    "accountant_email": None,
    "notification_preferences": {
        "email": True,
        "push": True,
        "price_alerts": True
    }
}

DEFAULT_MODULE_PERMISSIONS = {
    "read": True,
    "write": True,
    "execute": True,
    "admin": False
}


# ============================================
# PROFILE ENDPOINTS
# ============================================

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's profile."""
    try:
        preferences = current_user.preferences or DEFAULT_PREFERENCES.copy()
        modules = preferences.get("modules_enabled", DEFAULT_MODULES)
        
        return UserProfileResponse(
            user_id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.name,
            is_verified=current_user.is_verified,
            preferences=preferences,
            modules_enabled=modules,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update user profile."""
    try:
        # Update user fields
        current_user.name = request.full_name
        
        # Update preferences
        existing_prefs = current_user.preferences or DEFAULT_PREFERENCES.copy()
        if request.preferences:
            existing_prefs.update(request.preferences)
        current_user.preferences = existing_prefs
        current_user.updated_at = datetime.utcnow()
        
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
        modules = existing_prefs.get("modules_enabled", DEFAULT_MODULES)
        
        return UserProfileResponse(
            user_id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.name,
            is_verified=current_user.is_verified,
            preferences=existing_prefs,
            modules_enabled=modules,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update user preferences."""
    try:
        preferences = current_user.preferences or DEFAULT_PREFERENCES.copy()
        
        # Update only provided fields
        update_data = request.model_dump(exclude_none=True)
        
        # Handle banking_countries enum conversion
        if "banking_countries" in update_data:
            update_data["banking_countries"] = [
                c.value if hasattr(c, 'value') else c 
                for c in update_data["banking_countries"]
            ]
        
        preferences.update(update_data)
        current_user.preferences = preferences
        current_user.updated_at = datetime.utcnow()
        
        db.add(current_user)
        await db.commit()
        
        return {
            "status": "success",
            "message": "Preferences updated",
            "preferences": preferences
        }
    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MODULE ENDPOINTS
# ============================================

@router.get("/modules", response_model=UserModulesResponse)
async def get_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's enabled modules and permissions."""
    try:
        preferences = current_user.preferences or {}
        modules = preferences.get("modules_enabled", DEFAULT_MODULES)
        permissions = preferences.get("module_permissions", {})
        
        return UserModulesResponse(
            user_id=str(current_user.id),
            modules=modules,
            permissions=permissions,
            updated_at=current_user.updated_at
        )
    except Exception as e:
        logger.error(f"Get modules error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules", response_model=UserModulesResponse)
async def setup_modules(
    request: ModuleSetupRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Setup user modules and permissions."""
    try:
        # Validate modules
        invalid_modules = [m for m in request.modules if m not in ALL_MODULES]
        if invalid_modules:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid modules: {invalid_modules}. Valid modules: {ALL_MODULES}"
            )
        
        # Ensure base modules are always enabled
        enabled_modules = list(set(request.modules + DEFAULT_MODULES))
        
        # Update preferences
        preferences = current_user.preferences or DEFAULT_PREFERENCES.copy()
        preferences["modules_enabled"] = enabled_modules
        preferences["module_permissions"] = request.permissions
        
        current_user.preferences = preferences
        current_user.updated_at = datetime.utcnow()
        
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"Modules configured for user {current_user.id}: {enabled_modules}")
        
        return UserModulesResponse(
            user_id=str(current_user.id),
            modules=enabled_modules,
            permissions=request.permissions,
            updated_at=current_user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Module setup error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{module_name}/enable")
async def enable_module(
    module_name: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Enable a specific module for the user."""
    try:
        if module_name not in ALL_MODULES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid module: {module_name}. Valid modules: {ALL_MODULES}"
            )
        
        preferences = current_user.preferences or DEFAULT_PREFERENCES.copy()
        modules = preferences.get("modules_enabled", DEFAULT_MODULES.copy())
        
        if module_name not in modules:
            modules.append(module_name)
            preferences["modules_enabled"] = modules
            
            # Set default permissions
            module_perms = preferences.get("module_permissions", {})
            module_perms[module_name] = DEFAULT_MODULE_PERMISSIONS.copy()
            preferences["module_permissions"] = module_perms
            
            current_user.preferences = preferences
            current_user.updated_at = datetime.utcnow()
            
            db.add(current_user)
            await db.commit()
        
        return {
            "status": "success",
            "message": f"Module '{module_name}' enabled",
            "modules_enabled": modules
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable module error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/{module_name}/disable")
async def disable_module(
    module_name: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Disable a specific module for the user."""
    try:
        if module_name in DEFAULT_MODULES:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot disable core module: {module_name}"
            )
        
        preferences = current_user.preferences or DEFAULT_PREFERENCES.copy()
        modules = preferences.get("modules_enabled", DEFAULT_MODULES.copy())
        
        if module_name in modules:
            modules.remove(module_name)
            preferences["modules_enabled"] = modules
            
            current_user.preferences = preferences
            current_user.updated_at = datetime.utcnow()
            
            db.add(current_user)
            await db.commit()
        
        return {
            "status": "success",
            "message": f"Module '{module_name}' disabled",
            "modules_enabled": modules
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable module error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/available")
async def list_available_modules():
    """List all available modules."""
    return {
        "modules": [
            {
                "name": "chat",
                "description": "Core chat functionality with LLM",
                "required": True
            },
            {
                "name": "memory",
                "description": "Memory management for conversations and facts",
                "required": True
            },
            {
                "name": "banking",
                "description": "Banking operations for Canada, US, and Kenya",
                "required": False
            },
            {
                "name": "stocks",
                "description": "Stock portfolio management and trading",
                "required": False
            },
            {
                "name": "travel",
                "description": "Travel booking with multiple providers",
                "required": False
            },
            {
                "name": "research",
                "description": "Legal and business research tools",
                "required": False
            },
            {
                "name": "voice",
                "description": "Voice command processing",
                "required": False
            },
            {
                "name": "rag",
                "description": "Document upload and retrieval-augmented generation",
                "required": False
            }
        ]
    }
