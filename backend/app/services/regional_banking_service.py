"""Regional Banking Service - Multi-Country Banking Integration.

Supports:
- Lean Technologies (UAE/Middle East) - FAB Bank, RAK Bank, ENBD, ADCB
- Mono (Africa) - I&M Bank (Kenya), Equity Bank, KCB, GTBank (Nigeria)

These are Plaid-equivalent aggregators for regions where Plaid doesn't operate.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.config import settings

logger = logging.getLogger(__name__)


class BankingRegion(str, Enum):
    """Supported banking regions."""
    NORTH_AMERICA = "north_america"  # Plaid - US, Canada
    MIDDLE_EAST = "middle_east"      # Lean - UAE, Saudi Arabia
    AFRICA = "africa"                 # Mono - Kenya, Nigeria, Ghana


class RegionalBankingService:
    """Unified service for regional banking aggregators."""

    def __init__(self):
        """Initialize regional banking services."""
        self.lean_service = LeanService() if settings.LEAN_APP_TOKEN else None
        self.mono_service = MonoService() if settings.MONO_SECRET_KEY else None
        
        logger.info(f"Regional banking initialized - Lean: {bool(self.lean_service)}, Mono: {bool(self.mono_service)}")

    def get_provider_for_country(self, country_code: str) -> str:
        """Get the appropriate banking provider for a country.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
            
        Returns:
            Provider name: 'plaid', 'lean', or 'mono'
        """
        country_providers = {
            # North America - Plaid
            "US": "plaid",
            "CA": "plaid",
            # Middle East - Lean Technologies
            "AE": "lean",  # UAE
            "SA": "lean",  # Saudi Arabia
            "BH": "lean",  # Bahrain
            "KW": "lean",  # Kuwait
            "OM": "lean",  # Oman
            "QA": "lean",  # Qatar
            # Africa - Mono
            "KE": "mono",  # Kenya
            "NG": "mono",  # Nigeria
            "GH": "mono",  # Ghana
            "ZA": "mono",  # South Africa
        }
        return country_providers.get(country_code.upper(), "unsupported")

    async def create_link_token(
        self,
        user_id: str,
        country_code: str
    ) -> Dict[str, Any]:
        """Create a link token for the appropriate regional provider.
        
        Args:
            user_id: Unique user identifier
            country_code: Target country code
            
        Returns:
            Link token and provider information
        """
        provider = self.get_provider_for_country(country_code)
        
        if provider == "plaid":
            # Handled by existing PlaidService
            return {"provider": "plaid", "message": "Use PlaidService for US/Canada"}
        elif provider == "lean":
            if not self.lean_service:
                raise Exception("Lean Technologies not configured for UAE/Middle East banking")
            return await self.lean_service.create_link_token(user_id)
        elif provider == "mono":
            if not self.mono_service:
                raise Exception("Mono not configured for African banking")
            return await self.mono_service.create_widget_token(user_id)
        else:
            raise Exception(f"Banking not supported for country: {country_code}")


# ============================================
# LEAN TECHNOLOGIES SERVICE (UAE/Middle East)
# ============================================

class LeanService:
    """Service for Lean Technologies API - UAE/Middle East banking.
    
    Documentation: https://docs.leantech.me/
    
    Supported Banks:
    - FAB (First Abu Dhabi Bank)
    - RAK Bank
    - ENBD (Emirates NBD)
    - ADCB (Abu Dhabi Commercial Bank)
    - Mashreq Bank
    - CBD (Commercial Bank of Dubai)
    - And more across GCC region
    """

    def __init__(self):
        """Initialize Lean service."""
        self.app_token = settings.LEAN_APP_TOKEN
        self.app_secret = settings.LEAN_APP_SECRET
        self.base_url = "https://sandbox.leantech.me" if settings.LEAN_ENV == "sandbox" else "https://api.leantech.me"
        logger.info(f"Lean service initialized in {settings.LEAN_ENV} environment")

    async def create_link_token(self, user_id: str) -> Dict[str, Any]:
        """Create a Lean Link initialization token.
        
        This token is used to initialize the Lean Link widget for bank connection.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary with link_token for widget initialization
        """
        url = f"{self.base_url}/customers/v1/"
        headers = {
            "Content-Type": "application/json",
            "lean-app-token": self.app_token
        }
        payload = {
            "app_user_id": user_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200 or response.status == 201:
                        data = await response.json()
                        logger.info(f"Lean customer created for user {user_id}")
                        return {
                            "provider": "lean",
                            "customer_id": data.get("customer_id"),
                            "app_token": self.app_token,  # Used for widget initialization
                            "environment": settings.LEAN_ENV
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Lean API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to create Lean link token: {error_text}")
        except Exception as e:
            logger.error(f"Error creating Lean link token: {e}")
            raise

    async def exchange_token(self, entity_id: str) -> Dict[str, Any]:
        """Exchange entity ID for access credentials after user connects bank.
        
        Args:
            entity_id: Entity ID from Lean Link callback
            
        Returns:
            Access credentials for the connected bank
        """
        # Entity ID is returned from Lean Link widget after successful connection
        logger.info(f"Lean entity connected: {entity_id}")
        return {
            "provider": "lean",
            "entity_id": entity_id,
            "status": "connected"
        }

    async def get_accounts(self, entity_id: str) -> Dict[str, Any]:
        """Get accounts for a connected entity.
        
        Args:
            entity_id: Lean entity ID
            
        Returns:
            List of connected bank accounts
        """
        url = f"{self.base_url}/data/v1/accounts"
        headers = {
            "Content-Type": "application/json",
            "lean-app-token": self.app_token
        }
        params = {"entity_id": entity_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        accounts = []
                        for account in data.get("accounts", []):
                            accounts.append({
                                "account_id": account.get("id"),
                                "name": account.get("name"),
                                "type": account.get("type"),
                                "balance": {
                                    "current": account.get("balance", {}).get("amount"),
                                    "currency": account.get("balance", {}).get("currency", "AED")
                                },
                                "bank_name": account.get("institution", {}).get("name"),
                                "mask": account.get("account_number", "")[-4:]
                            })
                        
                        logger.info(f"Retrieved {len(accounts)} accounts from Lean")
                        return {"accounts": accounts, "provider": "lean"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Lean API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get accounts: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Lean accounts: {e}")
            raise

    async def get_transactions(
        self,
        entity_id: str,
        account_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get transactions for an account.
        
        Args:
            entity_id: Lean entity ID
            account_id: Account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of transactions
        """
        url = f"{self.base_url}/data/v1/transactions"
        headers = {
            "Content-Type": "application/json",
            "lean-app-token": self.app_token
        }
        
        # Default to last 30 days
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
        params = {
            "entity_id": entity_id,
            "account_id": account_id,
            "from_date": start_date,
            "to_date": end_date
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = []
                        for txn in data.get("transactions", []):
                            transactions.append({
                                "transaction_id": txn.get("id"),
                                "account_id": account_id,
                                "date": txn.get("timestamp", "")[:10],
                                "name": txn.get("description"),
                                "amount": txn.get("amount", {}).get("amount"),
                                "currency": txn.get("amount", {}).get("currency", "AED"),
                                "type": txn.get("type"),
                                "category": [txn.get("category")] if txn.get("category") else []
                            })
                        
                        logger.info(f"Retrieved {len(transactions)} transactions from Lean")
                        return {"transactions": transactions, "provider": "lean"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Lean API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get transactions: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Lean transactions: {e}")
            raise


# ============================================
# MONO SERVICE (Africa)
# ============================================

class MonoService:
    """Service for Mono API - African banking aggregator.
    
    Documentation: https://docs.mono.co/
    
    Supported Banks (Kenya):
    - I&M Bank
    - Equity Bank
    - KCB (Kenya Commercial Bank)
    - Co-operative Bank
    - Standard Chartered Kenya
    - Absa Bank Kenya
    
    Supported Banks (Nigeria):
    - GTBank
    - Access Bank
    - First Bank
    - UBA
    - Zenith Bank
    - And 100+ more
    """

    def __init__(self):
        """Initialize Mono service."""
        self.secret_key = settings.MONO_SECRET_KEY
        self.public_key = settings.MONO_PUBLIC_KEY
        self.base_url = "https://api.withmono.com"
        logger.info("Mono service initialized for African banking")

    async def create_widget_token(self, user_id: str) -> Dict[str, Any]:
        """Create a Mono Connect widget session token.
        
        This token initializes the Mono Connect widget for bank linking.
        
        Args:
            user_id: Unique user identifier (for reference tracking)
            
        Returns:
            Public key and session info for widget initialization
        """
        # Mono uses client-side widget with public key
        logger.info(f"Creating Mono widget session for user {user_id}")
        return {
            "provider": "mono",
            "public_key": self.public_key,
            "reference": user_id,
            "environment": "live" if self.secret_key and not self.secret_key.startswith("test_") else "test"
        }

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for account ID.
        
        Called after user successfully connects their bank via Mono Connect widget.
        
        Args:
            code: Authorization code from Mono Connect callback
            
        Returns:
            Account ID and status
        """
        url = f"{self.base_url}/account/auth"
        headers = {
            "Content-Type": "application/json",
            "mono-sec-key": self.secret_key
        }
        payload = {"code": code}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Mono account linked successfully")
                        return {
                            "provider": "mono",
                            "account_id": data.get("id"),
                            "status": "connected"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Mono API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to exchange Mono code: {error_text}")
        except Exception as e:
            logger.error(f"Error exchanging Mono code: {e}")
            raise

    async def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """Get account information.
        
        Args:
            account_id: Mono account ID
            
        Returns:
            Account details including balance
        """
        url = f"{self.base_url}/accounts/{account_id}"
        headers = {
            "Content-Type": "application/json",
            "mono-sec-key": self.secret_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        account = data.get("account", {})
                        
                        formatted_account = {
                            "account_id": account_id,
                            "name": account.get("name"),
                            "type": account.get("type"),
                            "account_number": account.get("accountNumber"),
                            "mask": account.get("accountNumber", "")[-4:],
                            "balance": {
                                "current": account.get("balance", 0) / 100,  # Mono returns in smallest currency unit
                                "currency": account.get("currency", "KES")
                            },
                            "bank_name": account.get("institution", {}).get("name"),
                            "bvn": account.get("bvn")  # Bank Verification Number (Nigeria)
                        }
                        
                        logger.info(f"Retrieved account details from Mono")
                        return {"account": formatted_account, "provider": "mono"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Mono API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get account: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Mono account: {e}")
            raise

    async def get_transactions(
        self,
        account_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        paginate: bool = False
    ) -> Dict[str, Any]:
        """Get transaction history.
        
        Args:
            account_id: Mono account ID
            start_date: Start date (YYYY-MM-DD or DD-MM-YYYY)
            end_date: End date (YYYY-MM-DD or DD-MM-YYYY)
            paginate: Whether to use pagination
            
        Returns:
            List of transactions
        """
        url = f"{self.base_url}/accounts/{account_id}/transactions"
        headers = {
            "Content-Type": "application/json",
            "mono-sec-key": self.secret_key
        }
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
        if paginate:
            params["paginate"] = "true"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = []
                        
                        for txn in data.get("data", []):
                            transactions.append({
                                "transaction_id": txn.get("_id"),
                                "account_id": account_id,
                                "date": txn.get("date"),
                                "name": txn.get("narration"),
                                "amount": txn.get("amount", 0) / 100,  # Convert from smallest unit
                                "currency": txn.get("currency", "KES"),
                                "type": txn.get("type"),  # debit or credit
                                "category": [txn.get("category")] if txn.get("category") else [],
                                "balance_after": txn.get("balance", 0) / 100
                            })
                        
                        logger.info(f"Retrieved {len(transactions)} transactions from Mono")
                        return {
                            "transactions": transactions,
                            "provider": "mono",
                            "paging": data.get("paging") if paginate else None
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Mono API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get transactions: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Mono transactions: {e}")
            raise

    async def get_identity(self, account_id: str) -> Dict[str, Any]:
        """Get account holder identity information.
        
        Args:
            account_id: Mono account ID
            
        Returns:
            Identity information
        """
        url = f"{self.base_url}/accounts/{account_id}/identity"
        headers = {
            "Content-Type": "application/json",
            "mono-sec-key": self.secret_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("Retrieved identity from Mono")
                        return {"identity": data, "provider": "mono"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Mono API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get identity: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Mono identity: {e}")
            raise


# Global instance
regional_banking_service = RegionalBankingService()
