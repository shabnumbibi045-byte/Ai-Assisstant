"""Plaid API Router - Banking Integration Endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.plaid_service import plaid_service
from app.auth.dependencies import get_current_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plaid", tags=["plaid"])


# Request/Response Models
class LinkTokenRequest(BaseModel):
    """Request model for creating link token."""
    country_codes: Optional[List[str]] = Field(default=["US", "CA"], description="Country codes")


class LinkTokenResponse(BaseModel):
    """Response model for link token."""
    link_token: str
    expiration: str
    request_id: Optional[str] = None


class ExchangeTokenRequest(BaseModel):
    """Request model for exchanging public token."""
    public_token: str = Field(..., description="Public token from Plaid Link")


class ExchangeTokenResponse(BaseModel):
    """Response model for token exchange."""
    access_token: str
    item_id: str
    request_id: Optional[str] = None


class GetAccountsRequest(BaseModel):
    """Request model for getting accounts."""
    access_token: str = Field(..., description="Plaid access token")


class GetTransactionsRequest(BaseModel):
    """Request model for getting transactions."""
    access_token: str = Field(..., description="Plaid access token")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    account_ids: Optional[List[str]] = Field(None, description="Filter by account IDs")


# Endpoints
@router.post("/create_link_token", response_model=LinkTokenResponse)
async def create_link_token(
    request: LinkTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a link token for Plaid Link initialization.

    This endpoint creates a link token that is used to initialize Plaid Link
    in the frontend. The link token is required to start the bank connection flow.
    """
    try:
        result = await plaid_service.create_link_token(
            user_id=str(current_user.id),
            country_codes=request.country_codes
        )

        return LinkTokenResponse(**result)

    except Exception as e:
        logger.error(f"Error creating link token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exchange_public_token", response_model=ExchangeTokenResponse)
async def exchange_public_token(
    request: ExchangeTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """Exchange public token for access token.

    After the user successfully connects their bank account through Plaid Link,
    you receive a public token. This endpoint exchanges that public token for
    an access token that can be used to fetch account data.

    IMPORTANT: Store the access_token securely - it's needed for all future requests.
    """
    try:
        result = await plaid_service.exchange_public_token(request.public_token)

        # TODO: Store access_token in database associated with user
        logger.info(f"Access token obtained for user {current_user.id}")

        return ExchangeTokenResponse(**result)

    except Exception as e:
        logger.error(f"Error exchanging public token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts")
async def get_accounts(
    request: GetAccountsRequest,
    current_user: User = Depends(get_current_user)
):
    """Get account information and balances.

    Retrieves all accounts associated with the access token, including:
    - Account names and types
    - Current balances
    - Available balances
    - Account masks (last 4 digits)
    """
    try:
        result = await plaid_service.get_accounts(request.access_token)
        return result

    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth")
async def get_auth_data(
    request: GetAccountsRequest,
    current_user: User = Depends(get_current_user)
):
    """Get account and routing numbers for ACH transfers.

    Retrieves authentication data including:
    - Account numbers
    - Routing numbers
    - Wire routing numbers

    This endpoint requires the 'auth' product to be enabled for your Plaid account.
    """
    try:
        result = await plaid_service.get_auth_data(request.access_token)
        return result

    except Exception as e:
        logger.error(f"Error getting auth data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions")
async def get_transactions(
    request: GetTransactionsRequest,
    current_user: User = Depends(get_current_user)
):
    """Get transaction history.

    Retrieves transactions for the specified date range. By default, returns
    transactions from the last 30 days.

    You can filter by specific account IDs to get transactions for only certain accounts.
    """
    try:
        result = await plaid_service.get_transactions(
            access_token=request.access_token,
            start_date=request.start_date,
            end_date=request.end_date,
            account_ids=request.account_ids
        )
        return result

    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def plaid_health():
    """Health check for Plaid integration."""
    return {
        "status": "healthy",
        "service": "plaid",
        "environment": "sandbox"  # From settings
    }
