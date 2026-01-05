"""Plaid Service - Banking Integration via Plaid API.

Handles:
- Link token creation for bank authentication
- Access token exchange
- Account balance retrieval
- Transaction history
- Multi-country support (US, Canada, Kenya)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.auth_get_request import AuthGetRequest

from app.config import settings

logger = logging.getLogger(__name__)


class PlaidService:
    """Service for interacting with Plaid API."""

    def __init__(self):
        """Initialize Plaid client."""
        # Map environment string to Plaid environment
        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "development": plaid.Environment.Sandbox,  # Use sandbox for development
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
        logger.info(f"Plaid service initialized in {settings.PLAID_ENV} environment")

    async def create_link_token(
        self,
        user_id: str,
        country_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization.

        Args:
            user_id: Unique user identifier
            country_codes: List of country codes (US, CA, etc.)

        Returns:
            Dictionary with link_token and expiration
        """
        try:
            # Default to all supported countries
            if not country_codes:
                country_codes = ["US", "CA"]

            # Convert country codes
            countries = [CountryCode(code) for code in country_codes]

            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                client_name="Salim AI Assistant",
                products=[Products("auth"), Products("transactions")],
                country_codes=countries,
                language="en",
                redirect_uri=None  # For web, not needed
            )

            response = self.client.link_token_create(request)

            logger.info(f"Link token created for user {user_id}")

            return {
                "link_token": response['link_token'],
                "expiration": response['expiration'],
                "request_id": response.get('request_id')
            }

        except plaid.ApiException as e:
            logger.error(f"Plaid API error creating link token: {e}")
            raise Exception(f"Failed to create link token: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating link token: {e}")
            raise

    async def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        """Exchange public token for access token.

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Dictionary with access_token and item_id
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = self.client.item_public_token_exchange(request)

            logger.info(f"Public token exchanged successfully")

            return {
                "access_token": response['access_token'],
                "item_id": response['item_id'],
                "request_id": response.get('request_id')
            }

        except plaid.ApiException as e:
            logger.error(f"Plaid API error exchanging token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
        except Exception as e:
            logger.error(f"Error exchanging public token: {e}")
            raise

    async def get_accounts(self, access_token: str) -> Dict[str, Any]:
        """Get account information.

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary with accounts information
        """
        try:
            request = AccountsGetRequest(
                access_token=access_token
            )

            response = self.client.accounts_get(request)

            # Format accounts
            accounts = []
            for account in response['accounts']:
                accounts.append({
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "official_name": account.get('official_name'),
                    "type": account['type'],
                    "subtype": account['subtype'],
                    "mask": account.get('mask'),
                    "balance": {
                        "current": account['balances']['current'],
                        "available": account['balances'].get('available'),
                        "limit": account['balances'].get('limit'),
                        "currency": account['balances'].get('iso_currency_code', 'USD')
                    }
                })

            logger.info(f"Retrieved {len(accounts)} accounts")

            return {
                "accounts": accounts,
                "item_id": response['item']['item_id'],
                "institution_id": response['item'].get('institution_id'),
                "request_id": response.get('request_id')
            }

        except plaid.ApiException as e:
            logger.error(f"Plaid API error getting accounts: {e}")
            raise Exception(f"Failed to get accounts: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise

    async def get_auth_data(self, access_token: str) -> Dict[str, Any]:
        """Get auth data including account and routing numbers.

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary with auth information
        """
        try:
            request = AuthGetRequest(
                access_token=access_token
            )

            response = self.client.auth_get(request)

            # Format auth data
            accounts = []
            for account in response['accounts']:
                account_data = {
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "type": account['type'],
                    "subtype": account['subtype'],
                    "mask": account.get('mask')
                }

                # Add routing numbers if available
                if 'numbers' in response:
                    for number_data in response['numbers'].get('ach', []):
                        if number_data['account_id'] == account['account_id']:
                            account_data['routing'] = number_data['routing']
                            account_data['account_number'] = number_data['account']
                            account_data['wire_routing'] = number_data.get('wire_routing')

                accounts.append(account_data)

            logger.info(f"Retrieved auth data for {len(accounts)} accounts")

            return {
                "accounts": accounts,
                "request_id": response.get('request_id')
            }

        except plaid.ApiException as e:
            logger.error(f"Plaid API error getting auth data: {e}")
            raise Exception(f"Failed to get auth data: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting auth data: {e}")
            raise

    async def get_transactions(
        self,
        access_token: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get transaction history.

        Args:
            access_token: Plaid access token
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_ids: Optional list of account IDs to filter

        Returns:
            Dictionary with transactions
        """
        try:
            # Default to last 30 days if not specified
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
                options={
                    "account_ids": account_ids,
                    "count": 500,
                    "offset": 0
                } if account_ids else {"count": 500, "offset": 0}
            )

            response = self.client.transactions_get(request)

            # Format transactions
            transactions = []
            for txn in response['transactions']:
                transactions.append({
                    "transaction_id": txn['transaction_id'],
                    "account_id": txn['account_id'],
                    "date": str(txn['date']),
                    "name": txn['name'],
                    "merchant_name": txn.get('merchant_name'),
                    "amount": txn['amount'],
                    "currency": txn.get('iso_currency_code', 'USD'),
                    "category": txn.get('category', []),
                    "pending": txn['pending'],
                    "payment_channel": txn.get('payment_channel'),
                    "location": {
                        "address": txn.get('location', {}).get('address'),
                        "city": txn.get('location', {}).get('city'),
                        "region": txn.get('location', {}).get('region'),
                        "country": txn.get('location', {}).get('country')
                    } if txn.get('location') else None
                })

            logger.info(f"Retrieved {len(transactions)} transactions")

            return {
                "transactions": transactions,
                "total_transactions": response['total_transactions'],
                "accounts": response['accounts'],
                "request_id": response.get('request_id')
            }

        except plaid.ApiException as e:
            logger.error(f"Plaid API error getting transactions: {e}")
            raise Exception(f"Failed to get transactions: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise


# Global Plaid service instance
plaid_service = PlaidService()
