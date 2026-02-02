"""Brokerage Service - Investment Account Integration via Plaid & Direct APIs.

Supports:
- Plaid Investments (aggregated access to Schwab, Fidelity, Vanguard, etc.)
- Charles Schwab Developer API (direct integration)
- Interactive Brokers Client Portal API

This provides read-only portfolio access for tracking investments.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import base64

from app.config import settings

logger = logging.getLogger(__name__)


class BrokerageProvider(str, Enum):
    """Supported brokerage providers."""
    PLAID = "plaid"            # Aggregated - supports many brokerages
    SCHWAB = "schwab"          # Charles Schwab direct API
    IBKR = "interactive_brokers"  # Interactive Brokers


class BrokerageService:
    """Unified service for brokerage account access."""

    def __init__(self):
        """Initialize brokerage services."""
        self.plaid_investments = PlaidInvestmentsService() if settings.PLAID_CLIENT_ID else None
        self.schwab_service = SchwabService() if settings.SCHWAB_CLIENT_ID else None
        self.ibkr_service = IBKRService() if settings.IB_ACCOUNT_ID else None
        
        providers = []
        if self.plaid_investments:
            providers.append("Plaid Investments")
        if self.schwab_service:
            providers.append("Schwab")
        if self.ibkr_service:
            providers.append("IBKR")
            
        logger.info(f"Brokerage service initialized with: {', '.join(providers) or 'None'}")

    async def get_all_holdings(self, user_id: str) -> Dict[str, Any]:
        """Get holdings from all connected brokerage accounts.
        
        Args:
            user_id: User identifier
            
        Returns:
            Combined holdings from all providers
        """
        all_holdings = []
        errors = []
        
        # In production, you would fetch user's stored access tokens
        # and call each provider they've connected
        
        return {
            "holdings": all_holdings,
            "errors": errors,
            "providers_checked": ["plaid", "schwab", "ibkr"]
        }


# ============================================
# PLAID INVESTMENTS SERVICE
# ============================================

class PlaidInvestmentsService:
    """Service for Plaid Investments API.
    
    Plaid Investments provides aggregated access to brokerage accounts from:
    - Charles Schwab
    - Fidelity
    - Vanguard
    - E*TRADE
    - TD Ameritrade
    - Robinhood
    - And 100+ more brokerages
    
    Documentation: https://plaid.com/docs/investments/
    """

    def __init__(self):
        """Initialize Plaid Investments service."""
        import plaid
        from plaid.api import plaid_api
        
        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "development": plaid.Environment.Sandbox,
            "production": plaid.Environment.Production
        }

        configuration = plaid.Configuration(
            host=env_map.get(settings.PLAID_ENV, plaid.Environment.Sandbox),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )

        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        logger.info(f"Plaid Investments service initialized in {settings.PLAID_ENV} environment")

    async def create_link_token(self, user_id: str) -> Dict[str, Any]:
        """Create a link token for Plaid Link with investments product.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Link token for initializing Plaid Link
        """
        from plaid.model.products import Products
        from plaid.model.country_code import CountryCode
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="Salim AI Assistant",
                products=[Products("investments")],  # Request investments access
                country_codes=[CountryCode("US")],
                language="en"
            )

            response = self.client.link_token_create(request)
            
            expiration = response['expiration']
            if hasattr(expiration, 'isoformat'):
                expiration = expiration.isoformat()

            logger.info(f"Plaid Investments link token created for user {user_id}")
            return {
                "link_token": response['link_token'],
                "expiration": expiration,
                "provider": "plaid_investments"
            }

        except Exception as e:
            logger.error(f"Error creating Plaid Investments link token: {e}")
            raise

    async def get_holdings(self, access_token: str) -> Dict[str, Any]:
        """Get investment holdings.
        
        Args:
            access_token: Plaid access token
            
        Returns:
            Investment holdings with current values
        """
        from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
        
        try:
            request = InvestmentsHoldingsGetRequest(access_token=access_token)
            response = self.client.investments_holdings_get(request)

            # Format holdings
            holdings = []
            securities_map = {s['security_id']: s for s in response.get('securities', [])}
            
            for holding in response.get('holdings', []):
                security = securities_map.get(holding['security_id'], {})
                holdings.append({
                    "security_id": holding['security_id'],
                    "account_id": holding['account_id'],
                    "symbol": security.get('ticker_symbol'),
                    "name": security.get('name'),
                    "quantity": holding['quantity'],
                    "cost_basis": holding.get('cost_basis'),
                    "current_value": holding['institution_value'],
                    "current_price": holding['institution_price'],
                    "currency": holding.get('iso_currency_code', 'USD'),
                    "type": security.get('type'),  # equity, etf, mutual fund, etc.
                    "close_price": security.get('close_price'),
                    "close_price_as_of": str(security.get('close_price_as_of')) if security.get('close_price_as_of') else None
                })

            # Format accounts
            accounts = []
            for account in response.get('accounts', []):
                accounts.append({
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "type": str(account['type']) if account['type'] else None,
                    "subtype": str(account['subtype']) if account['subtype'] else None,
                    "mask": account.get('mask'),
                    "balance": {
                        "current": account['balances']['current'],
                        "available": account['balances'].get('available')
                    }
                })

            logger.info(f"Retrieved {len(holdings)} holdings from Plaid Investments")
            return {
                "holdings": holdings,
                "accounts": accounts,
                "provider": "plaid_investments"
            }

        except Exception as e:
            logger.error(f"Error getting Plaid Investments holdings: {e}")
            raise

    async def get_transactions(
        self,
        access_token: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get investment transactions (buys, sells, dividends, etc.).
        
        Args:
            access_token: Plaid access token
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Investment transactions
        """
        from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
        
        try:
            # Default to last 30 days
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            request = InvestmentsTransactionsGetRequest(
                access_token=access_token,
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
            )

            response = self.client.investments_transactions_get(request)
            
            # Format transactions
            transactions = []
            securities_map = {s['security_id']: s for s in response.get('securities', [])}
            
            for txn in response.get('investment_transactions', []):
                security = securities_map.get(txn.get('security_id'), {})
                transactions.append({
                    "transaction_id": txn['investment_transaction_id'],
                    "account_id": txn['account_id'],
                    "date": str(txn['date']),
                    "name": txn['name'],
                    "type": txn['type'],  # buy, sell, dividend, transfer, etc.
                    "subtype": txn.get('subtype'),
                    "symbol": security.get('ticker_symbol'),
                    "security_name": security.get('name'),
                    "quantity": txn.get('quantity'),
                    "price": txn.get('price'),
                    "amount": txn['amount'],
                    "fees": txn.get('fees'),
                    "currency": txn.get('iso_currency_code', 'USD')
                })

            logger.info(f"Retrieved {len(transactions)} investment transactions")
            return {
                "transactions": transactions,
                "total_transactions": response['total_investment_transactions'],
                "provider": "plaid_investments"
            }

        except Exception as e:
            logger.error(f"Error getting investment transactions: {e}")
            raise


# ============================================
# CHARLES SCHWAB SERVICE
# ============================================

class SchwabService:
    """Service for Charles Schwab Developer API.
    
    Provides direct integration with Schwab accounts for:
    - Account balances
    - Holdings/positions
    - Transaction history
    - Real-time quotes
    
    Documentation: https://developer.schwab.com/
    
    Setup:
    1. Register at https://developer.schwab.com/
    2. Create an app and get Client ID & Secret
    3. User authorizes via OAuth2 flow
    4. Store refresh token for ongoing access
    """

    def __init__(self):
        """Initialize Schwab service."""
        self.client_id = settings.SCHWAB_CLIENT_ID
        self.client_secret = settings.SCHWAB_CLIENT_SECRET
        self.refresh_token = settings.SCHWAB_REFRESH_TOKEN
        self.account_id = settings.SCHWAB_ACCOUNT_ID
        self.base_url = "https://api.schwabapi.com"
        self.access_token = None
        self.token_expires_at = None
        logger.info("Schwab service initialized")

    async def _get_access_token(self) -> str:
        """Get OAuth2 access token using refresh token."""
        # Return cached token if still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        if not self.refresh_token:
            raise Exception("Schwab refresh token not configured")

        url = "https://api.schwabapi.com/v1/oauth/token"
        
        # Basic auth with client credentials
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data["access_token"]
                        # New refresh token may be returned
                        if "refresh_token" in token_data:
                            self.refresh_token = token_data["refresh_token"]
                            # TODO: Persist new refresh token to database
                        expires_in = token_data.get("expires_in", 1800)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("Schwab access token refreshed")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Schwab token refresh failed: {response.status} - {error_text}")
                        raise Exception("Failed to refresh Schwab access token")
        except Exception as e:
            logger.error(f"Error refreshing Schwab token: {e}")
            raise

    async def get_accounts(self) -> Dict[str, Any]:
        """Get all linked Schwab accounts."""
        token = await self._get_access_token()
        url = f"{self.base_url}/trader/v1/accounts"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        accounts = []
                        for account in data:
                            acc = account.get("securitiesAccount", {})
                            accounts.append({
                                "account_id": acc.get("accountId"),
                                "type": acc.get("type"),
                                "balance": {
                                    "liquidation_value": acc.get("currentBalances", {}).get("liquidationValue"),
                                    "cash_balance": acc.get("currentBalances", {}).get("cashBalance"),
                                    "buying_power": acc.get("currentBalances", {}).get("buyingPower")
                                }
                            })
                        logger.info(f"Retrieved {len(accounts)} Schwab accounts")
                        return {"accounts": accounts, "provider": "schwab"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Schwab API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get Schwab accounts: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Schwab accounts: {e}")
            raise

    async def get_positions(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get portfolio positions/holdings.
        
        Args:
            account_id: Schwab account ID (uses default if not provided)
            
        Returns:
            Current positions with market values
        """
        token = await self._get_access_token()
        acct = account_id or self.account_id
        url = f"{self.base_url}/trader/v1/accounts/{acct}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"fields": "positions"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        positions = []
                        for pos in data.get("securitiesAccount", {}).get("positions", []):
                            positions.append({
                                "symbol": pos.get("instrument", {}).get("symbol"),
                                "name": pos.get("instrument", {}).get("description"),
                                "type": pos.get("instrument", {}).get("assetType"),
                                "quantity": pos.get("longQuantity", 0) - pos.get("shortQuantity", 0),
                                "average_cost": pos.get("averagePrice"),
                                "current_price": pos.get("marketValue") / pos.get("longQuantity", 1) if pos.get("longQuantity") else 0,
                                "market_value": pos.get("marketValue"),
                                "day_gain_loss": pos.get("currentDayProfitLoss"),
                                "day_gain_loss_percent": pos.get("currentDayProfitLossPercentage"),
                                "total_gain_loss": pos.get("longQuantity", 0) * (pos.get("marketValue", 0) / pos.get("longQuantity", 1) - pos.get("averagePrice", 0)) if pos.get("longQuantity") else 0
                            })
                        logger.info(f"Retrieved {len(positions)} Schwab positions")
                        return {"positions": positions, "provider": "schwab"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Schwab API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get positions: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Schwab positions: {e}")
            raise

    async def get_transactions(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get transaction history.
        
        Args:
            account_id: Schwab account ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Transaction history
        """
        token = await self._get_access_token()
        acct = account_id or self.account_id
        url = f"{self.base_url}/trader/v1/accounts/{acct}/transactions"
        headers = {"Authorization": f"Bearer {token}"}
        
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = []
                        for txn in data:
                            transactions.append({
                                "transaction_id": txn.get("transactionId"),
                                "date": txn.get("transactionDate"),
                                "type": txn.get("type"),
                                "description": txn.get("description"),
                                "symbol": txn.get("transactionItem", {}).get("instrument", {}).get("symbol"),
                                "quantity": txn.get("transactionItem", {}).get("amount"),
                                "price": txn.get("transactionItem", {}).get("price"),
                                "net_amount": txn.get("netAmount"),
                                "fees": txn.get("fees", {}).get("commission", 0)
                            })
                        logger.info(f"Retrieved {len(transactions)} Schwab transactions")
                        return {"transactions": transactions, "provider": "schwab"}
                    else:
                        error_text = await response.text()
                        logger.error(f"Schwab API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get transactions: {error_text}")
        except Exception as e:
            logger.error(f"Error getting Schwab transactions: {e}")
            raise


# ============================================
# INTERACTIVE BROKERS SERVICE
# ============================================

class IBKRService:
    """Service for Interactive Brokers Client Portal API.
    
    Documentation: https://www.interactivebrokers.com/api/doc.html
    
    Note: Requires IB Gateway or TWS running locally.
    The Client Portal API connects to the running gateway.
    
    Setup:
    1. Download IB Gateway from https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
    2. Configure gateway with your IBKR credentials
    3. Enable API access in gateway settings
    4. Gateway runs on localhost:5000 by default
    """

    def __init__(self):
        """Initialize IBKR service."""
        self.account_id = settings.IB_ACCOUNT_ID
        self.base_url = f"https://{settings.IB_GATEWAY_HOST}:5000/v1/api"
        # Note: In production, handle SSL verification properly
        logger.info(f"IBKR service initialized for account {self.account_id}")

    async def get_accounts(self) -> Dict[str, Any]:
        """Get IBKR account information."""
        url = f"{self.base_url}/portfolio/accounts"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        accounts = await response.json()
                        logger.info(f"Retrieved {len(accounts)} IBKR accounts")
                        return {"accounts": accounts, "provider": "ibkr"}
                    else:
                        error_text = await response.text()
                        logger.error(f"IBKR API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get IBKR accounts: {error_text}")
        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to IB Gateway. Ensure it's running.")
            raise Exception("IB Gateway not running. Please start IB Gateway or TWS.")
        except Exception as e:
            logger.error(f"Error getting IBKR accounts: {e}")
            raise

    async def get_positions(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get portfolio positions.
        
        Args:
            account_id: IBKR account ID
            
        Returns:
            Current positions
        """
        acct = account_id or self.account_id
        url = f"{self.base_url}/portfolio/{acct}/positions/0"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        positions = []
                        for pos in data:
                            positions.append({
                                "contract_id": pos.get("conid"),
                                "symbol": pos.get("contractDesc"),
                                "position": pos.get("position"),
                                "market_price": pos.get("mktPrice"),
                                "market_value": pos.get("mktValue"),
                                "average_cost": pos.get("avgCost"),
                                "unrealized_pnl": pos.get("unrealizedPnl"),
                                "realized_pnl": pos.get("realizedPnl"),
                                "currency": pos.get("currency")
                            })
                        logger.info(f"Retrieved {len(positions)} IBKR positions")
                        return {"positions": positions, "provider": "ibkr"}
                    else:
                        error_text = await response.text()
                        logger.error(f"IBKR API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get positions: {error_text}")
        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to IB Gateway")
            raise Exception("IB Gateway not running")
        except Exception as e:
            logger.error(f"Error getting IBKR positions: {e}")
            raise

    async def get_account_summary(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get account summary with balances and buying power.
        
        Args:
            account_id: IBKR account ID
            
        Returns:
            Account summary
        """
        acct = account_id or self.account_id
        url = f"{self.base_url}/portfolio/{acct}/summary"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        summary = {
                            "account_id": acct,
                            "net_liquidation": data.get("netliquidation", {}).get("amount"),
                            "total_cash": data.get("totalcashvalue", {}).get("amount"),
                            "buying_power": data.get("buyingpower", {}).get("amount"),
                            "gross_position_value": data.get("grosspositionvalue", {}).get("amount"),
                            "available_funds": data.get("availablefunds", {}).get("amount"),
                            "currency": data.get("netliquidation", {}).get("currency", "USD")
                        }
                        logger.info("Retrieved IBKR account summary")
                        return {"summary": summary, "provider": "ibkr"}
                    else:
                        error_text = await response.text()
                        logger.error(f"IBKR API error: {response.status} - {error_text}")
                        raise Exception(f"Failed to get account summary: {error_text}")
        except aiohttp.ClientConnectorError:
            logger.error("Cannot connect to IB Gateway")
            raise Exception("IB Gateway not running")
        except Exception as e:
            logger.error(f"Error getting IBKR summary: {e}")
            raise


# Global instance
brokerage_service = BrokerageService()
