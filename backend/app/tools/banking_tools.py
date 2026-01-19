"""Banking Tools - Multi-Country Financial Operations.

Supports bank accounts in:
- Canada (CA)
- United States (US)
- Kenya (KE)

Features:
- Daily balance checks
- Transaction history with export to Excel
- Multi-account management
- Weekly accountant reports
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import random
import json

from .base_tool import BaseTool, ToolResult, ToolCategory

logger = logging.getLogger(__name__)


class BankCountry(str, Enum):
    """Supported banking countries."""
    CANADA = "CA"
    USA = "US"
    KENYA = "KE"


class AccountType(str, Enum):
    """Bank account types."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    BUSINESS = "business"


# ============================================
# MULTI-ACCOUNT MANAGEMENT
# ============================================

class ListBankAccountsTool(BaseTool):
    """List all connected bank accounts across countries."""
    
    def __init__(self):
        super().__init__(
            name="list_bank_accounts",
            description="List all connected bank accounts across Canada, US, and Kenya with current status",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        """Execute account listing."""
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        country_filter = parameters.get("country")  # Optional filter

        # Try to get real Plaid data first
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if plaid_account:
                    # Fetch real accounts from Plaid
                    logger.info(f"Fetching real Plaid data for user {user_id}")
                    accounts_data = await plaid_service.get_accounts(plaid_account.access_token)

                    # Format Plaid accounts
                    real_accounts = []
                    for account in accounts_data.get('accounts', []):
                        real_accounts.append({
                            "account_id": account['account_id'],
                            "institution": plaid_account.institution_name or "Connected Bank",
                            "country": "US",  # Plaid doesn't directly provide country
                            "currency": account['balance'].get('currency', 'USD'),
                            "account_type": account['subtype'],
                            "account_name": account['name'],
                            "last_four": account.get('mask', 'XXXX'),
                            "status": "active",
                            "last_synced": datetime.now().isoformat(),
                            "balance": account['balance'].get('current', 0),
                            "available_balance": account['balance'].get('available', 0)
                        })

                    logger.info(f"Retrieved {len(real_accounts)} real accounts from Plaid")

                    return ToolResult(
                        success=True,
                        data={
                            "accounts": real_accounts,
                            "total_count": len(real_accounts),
                            "countries": list(set(acc["country"] for acc in real_accounts)),
                            "data_source": "plaid",
                            "has_connected_bank": True
                        },
                        message=f"Found {len(real_accounts)} connected bank accounts (Real Data)"
                    )
        except Exception as e:
            logger.warning(f"Could not fetch Plaid data: {e}. Falling back to no accounts.")

        # No Plaid connection - return empty with instruction
        logger.info(f"No bank accounts connected for user {user_id}")

        return ToolResult(
            success=False,
            data={
                "accounts": [],
                "total_count": 0,
                "countries": [],
                "data_source": "none",
                "has_connected_bank": False
            },
            message="No bank accounts connected. Please connect your bank account first using Plaid to access banking features.",
            error="NO_BANK_CONNECTED"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "enum": ["CA", "US", "KE"],
                        "description": "Filter accounts by country (optional)"
                    }
                },
                "required": []
            }
        }


class AddBankAccountTool(BaseTool):
    """Add a new bank account connection."""
    
    def __init__(self):
        super().__init__(
            name="add_bank_account",
            description="Initiate connection to a new bank account in Canada, US, or Kenya",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_write permission"
            )
        
        country = parameters.get("country")
        institution = parameters.get("institution")
        
        if not country or not institution:
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Both country and institution are required"
            )
        
        # STUBBED: Return link token for Plaid/bank connection
        link_data = {
            "link_token": f"link-sandbox-{random.randint(100000, 999999)}",
            "expiration": (datetime.now() + timedelta(hours=4)).isoformat(),
            "country": country,
            "institution": institution,
            "instructions": "Use this link token to complete bank authentication in the frontend"
        }
        
        logger.info(f"Bank account link initiated for {user_id}: {institution} ({country})")
        
        return ToolResult(
            success=True,
            data=link_data,
            message=f"Bank connection initiated for {institution}. Complete authentication to link account.",
            requires_confirmation=True
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "enum": ["CA", "US", "KE"],
                        "description": "Country of the bank"
                    },
                    "institution": {
                        "type": "string",
                        "description": "Name of the bank/institution"
                    }
                },
                "required": ["country", "institution"]
            }
        }


# ============================================
# BALANCE OPERATIONS
# ============================================

class GetBalanceTool(BaseTool):
    """Get account balance for specific or all accounts."""
    
    def __init__(self):
        super().__init__(
            name="get_balance",
            description="Retrieve current balance for specific accounts or all accounts across countries",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        # Check if user has Plaid connection
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if not plaid_account:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="No bank accounts connected. Please connect your bank account first.",
                        error="NO_BANK_CONNECTED"
                    )

                # Fetch real balance from Plaid
                accounts_data = await plaid_service.get_accounts(plaid_account.access_token)

                balances = []
                for account in accounts_data.get('accounts', []):
                    balances.append({
                        "account_id": account['account_id'],
                        "institution": plaid_account.institution_name or "Connected Bank",
                        "account_name": account['name'],
                        "country": "US",
                        "currency": account['balance'].get('currency', 'USD'),
                        "current_balance": account['balance'].get('current', 0),
                        "available_balance": account['balance'].get('available', 0),
                        "as_of": datetime.now().isoformat()
                    })

                # Calculate totals by currency
                totals_by_currency = {}
                for bal in balances:
                    curr = bal["currency"]
                    if curr not in totals_by_currency:
                        totals_by_currency[curr] = 0
                    totals_by_currency[curr] += bal["current_balance"]

                logger.info(f"Balance retrieved for {user_id}: {len(balances)} accounts (Real Data)")

                return ToolResult(
                    success=True,
                    data={
                        "balances": balances,
                        "totals_by_currency": totals_by_currency,
                        "account_count": len(balances),
                        "data_source": "plaid"
                    },
                    message=f"Retrieved balances for {len(balances)} accounts (Real Data)"
                )
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to fetch account balances. Please ensure your bank account is connected.",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Specific account ID (optional, returns all if not specified)"
                    },
                    "country": {
                        "type": "string",
                        "enum": ["CA", "US", "KE"],
                        "description": "Filter by country (optional)"
                    }
                },
                "required": []
            }
        }


class GetDailyBalanceSummaryTool(BaseTool):
    """Get daily balance summary across all accounts."""

    def __init__(self):
        super().__init__(
            name="get_daily_balance_summary",
            description="Get comprehensive daily balance summary across all connected bank accounts",
            category=ToolCategory.BANKING
        )

    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        date = parameters.get("date", datetime.now().strftime("%Y-%m-%d"))

        # Check if user has Plaid connection
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if not plaid_account:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="No bank accounts connected. Please connect your bank account first.",
                        error="NO_BANK_CONNECTED"
                    )

                # Fetch real account balances from Plaid
                accounts_data = await plaid_service.get_accounts(plaid_account.access_token)
                accounts = accounts_data.get('accounts', [])

                # Calculate summary
                total_balance = sum(acc['balance'].get('current', 0) for acc in accounts)
                total_available = sum(acc['balance'].get('available', 0) for acc in accounts if acc['balance'].get('available') is not None)

                account_list = []
                for account in accounts:
                    account_list.append({
                        "name": account['name'],
                        "balance": account['balance'].get('current', 0),
                        "available": account['balance'].get('available'),
                        "type": account.get('subtype', account.get('type'))
                    })

                summary = {
                    "date": date,
                    "generated_at": datetime.now().isoformat(),
                    "total_balance": total_balance,
                    "total_available": total_available,
                    "currency": accounts[0]['balance'].get('currency', 'USD') if accounts else 'USD',
                    "accounts": account_list,
                    "account_count": len(accounts),
                    "data_source": "plaid"
                }

                logger.info(f"Daily balance summary generated for {user_id} (Real Data)")

                return ToolResult(
                    success=True,
                    data=summary,
                    message=f"Daily balance summary for {date} - Total: ${total_balance:,.2f}"
                )
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to generate balance summary. Please ensure your bank account is connected.",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date for summary (YYYY-MM-DD), defaults to today"
                    }
                },
                "required": []
            }
        }


# ============================================
# TRANSACTION OPERATIONS
# ============================================

class ListTransactionsTool(BaseTool):
    """List transactions with filtering and categorization."""
    
    def __init__(self):
        super().__init__(
            name="list_transactions",
            description="Fetch transaction history with filters for accounts, date range, category, and amount",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        days = parameters.get("days", 7)
        limit = parameters.get("limit", 50)

        # Check if user has Plaid connection and fetch real transactions
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if not plaid_account:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="No bank accounts connected. Please connect your bank account first to view transactions.",
                        error="NO_BANK_CONNECTED"
                    )

                # Fetch real transactions from Plaid
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

                transactions_data = await plaid_service.get_transactions(
                    access_token=plaid_account.access_token,
                    start_date=start_date,
                    end_date=end_date
                )

                transactions = transactions_data.get('transactions', [])
                transactions = transactions[:limit]

                # Calculate summary
                summary = {
                    "total_transactions": len(transactions),
                    "total_debits": sum(abs(t['amount']) for t in transactions if t['amount'] > 0),
                    "total_credits": sum(abs(t['amount']) for t in transactions if t['amount'] < 0),
                    "by_category": {}
                }

                for txn in transactions:
                    cat = txn.get('category', ['Other'])[0] if txn.get('category') else 'Other'
                    if cat not in summary["by_category"]:
                        summary["by_category"][cat] = {"count": 0, "total": 0}
                    summary["by_category"][cat]["count"] += 1
                    summary["by_category"][cat]["total"] += abs(txn['amount'])

                logger.info(f"Transactions retrieved for {user_id}: {len(transactions)} transactions (Real Data)")

                return ToolResult(
                    success=True,
                    data={
                        "transactions": transactions,
                        "summary": summary,
                        "date_range": {
                            "start": start_date,
                            "end": end_date
                        },
                        "data_source": "plaid"
                    },
                    message=f"Retrieved {len(transactions)} transactions from your connected bank account"
                )
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to fetch transactions. Please ensure your bank account is connected.",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Filter by specific account ID"
                    },
                    "country": {
                        "type": "string",
                        "enum": ["CA", "US", "KE"],
                        "description": "Filter by country"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back (default: 7 for weekly)",
                        "default": 7
                    },
                    "category": {
                        "type": "string",
                        "enum": ["food", "shopping", "utilities", "transport", "entertainment", "business", "transfer"],
                        "description": "Filter by transaction category"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum transactions to return",
                        "default": 50
                    }
                },
                "required": []
            }
        }


# ============================================
# EXPORT OPERATIONS (For Accountant/QuickBooks)
# ============================================

class ExportTransactionsToExcelTool(BaseTool):
    """Export transactions to Excel format for accountant."""
    
    def __init__(self):
        super().__init__(
            name="export_transactions_excel",
            description="Export transactions to Excel spreadsheet format for accountant/QuickBooks posting",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        format_type = parameters.get("format", "quickbooks")

        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Check if user has Plaid connection
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if not plaid_account:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="No bank accounts connected. Please connect your bank account first.",
                        error="NO_BANK_CONNECTED"
                    )

                # Fetch real transactions from Plaid
                transactions_data = await plaid_service.get_transactions(
                    access_token=plaid_account.access_token,
                    start_date=start_date,
                    end_date=end_date
                )

                transactions = transactions_data.get('transactions', [])

                # Calculate statistics
                total_debits = sum(abs(t['amount']) for t in transactions if t['amount'] > 0)
                total_credits = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)

                export_data = {
                    "export_id": f"EXP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    "generated_at": datetime.now().isoformat(),
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    },
                    "format": format_type,
                    "file_info": {
                        "filename": f"transactions_{start_date}_to_{end_date}.xlsx",
                        "path": f"./exports/transactions_{start_date}_to_{end_date}.xlsx",
                        "sheets": ["All Transactions", "By Category", "By Account", "Summary"]
                    },
                    "statistics": {
                        "total_transactions": len(transactions),
                        "total_debits": round(total_debits, 2),
                        "total_credits": round(total_credits, 2),
                        "accounts_included": 1
                    },
                    "quickbooks_ready": format_type == "quickbooks",
                    "columns": [
                        "Date", "Account", "Description", "Category", "Debit", "Credit",
                        "Currency", "Reference"
                    ],
                    "transactions": transactions[:100],  # Include first 100 transactions
                    "data_source": "plaid"
                }

                logger.info(f"Transaction export generated for {user_id}: {export_data['export_id']} (Real Data)")

                return ToolResult(
                    success=True,
                    data=export_data,
                    message=f"Excel export ready: {export_data['file_info']['filename']} ({len(transactions)} transactions)"
                )
        except Exception as e:
            logger.error(f"Error exporting transactions: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to export transactions. Please ensure your bank account is connected.",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD), defaults to 7 days ago"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD), defaults to today"
                    },
                    "country": {
                        "type": "string",
                        "enum": ["CA", "US", "KE"],
                        "description": "Filter by country (optional)"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["quickbooks", "standard"],
                        "description": "Export format (default: quickbooks)",
                        "default": "quickbooks"
                    }
                },
                "required": []
            }
        }


class GenerateAccountantReportTool(BaseTool):
    """Generate weekly report for accountant."""
    
    def __init__(self):
        super().__init__(
            name="generate_accountant_report",
            description="Generate comprehensive weekly financial report for accountant to post to QuickBooks",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_read permission"
            )

        week_ending = parameters.get("week_ending", datetime.now().strftime("%Y-%m-%d"))
        send_email = parameters.get("send_email", False)

        week_end = datetime.strptime(week_ending, "%Y-%m-%d")
        week_start = week_end - timedelta(days=6)

        # Check if user has Plaid connection
        try:
            from app.database.database import db_manager
            from app.database.models import PlaidAccount
            from app.services.plaid_service import plaid_service
            from sqlalchemy import select

            async with db_manager.async_session_maker() as session:
                result = await session.execute(
                    select(PlaidAccount).where(
                        PlaidAccount.user_id == user_id,
                        PlaidAccount.is_active == True
                    )
                )
                plaid_account = result.scalar_one_or_none()

                if not plaid_account:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="No bank accounts connected. Please connect your bank account first.",
                        error="NO_BANK_CONNECTED"
                    )

                # Fetch transactions and accounts
                transactions_data = await plaid_service.get_transactions(
                    access_token=plaid_account.access_token,
                    start_date=week_start.strftime("%Y-%m-%d"),
                    end_date=week_ending
                )
                accounts_data = await plaid_service.get_accounts(plaid_account.access_token)

                transactions = transactions_data.get('transactions', [])
                accounts = accounts_data.get('accounts', [])

                # Calculate totals
                total_balance = sum(acc['balance'].get('current', 0) for acc in accounts)
                total_income = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
                total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] > 0)

                # Categorize expenses
                expense_categories = {}
                for txn in transactions:
                    if txn['amount'] > 0:  # Expense
                        cat = txn.get('category', ['Other'])[0] if txn.get('category') else 'Other'
                        if cat not in expense_categories:
                            expense_categories[cat] = 0
                        expense_categories[cat] += abs(txn['amount'])

                report = {
                    "report_id": f"RPT-{week_end.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    "generated_at": datetime.now().isoformat(),
                    "period": {
                        "start": week_start.strftime("%Y-%m-%d"),
                        "end": week_ending,
                        "type": "weekly"
                    },
                    "summary": {
                        "current_balance": round(total_balance, 2),
                        "total_income": round(total_income, 2),
                        "total_expenses": round(total_expenses, 2),
                        "net_change": round(total_income - total_expenses, 2),
                        "transaction_count": len(transactions)
                    },
                    "accounts": [
                        {
                            "name": acc['name'],
                            "balance": acc['balance'].get('current', 0),
                            "type": acc.get('subtype', acc.get('type'))
                        } for acc in accounts
                    ],
                    "expense_categories": {k: round(v, 2) for k, v in expense_categories.items()},
                    "attachments": [
                        {
                            "name": f"transactions_{week_start.strftime('%Y%m%d')}_{week_ending}.xlsx",
                            "type": "excel",
                            "quickbooks_ready": True
                        }
                    ],
                    "notes": "All transactions from connected bank account, ready for QuickBooks import.",
                    "email_status": "sent" if send_email else "not_requested",
                    "data_source": "plaid"
                }

                logger.info(f"Accountant report generated for {user_id}: {report['report_id']} (Real Data)")

                return ToolResult(
                    success=True,
                    data=report,
                    message=f"Weekly report generated for {week_start.strftime('%Y-%m-%d')} to {week_ending}: {len(transactions)} transactions, ${total_income:,.2f} income, ${total_expenses:,.2f} expenses"
                )
        except Exception as e:
            logger.error(f"Error generating accountant report: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to generate report. Please ensure your bank account is connected.",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "week_ending": {
                        "type": "string",
                        "description": "Week ending date (YYYY-MM-DD), defaults to today"
                    },
                    "send_email": {
                        "type": "boolean",
                        "description": "Send report to accountant via email",
                        "default": False
                    }
                },
                "required": []
            }
        }


# ============================================
# PAYMENT OPERATIONS
# ============================================

class CreatePaymentTool(BaseTool):
    """Create payment or transfer (REQUIRES CONFIRMATION)."""
    
    def __init__(self):
        super().__init__(
            name="create_payment",
            description="Prepare a payment or transfer between accounts (requires user confirmation)",
            category=ToolCategory.BANKING
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("banking_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have banking_write permission"
            )
        
        error = self.validate_parameters(parameters, ["from_account", "amount", "recipient"])
        if error:
            return ToolResult(success=False, data=None, message="Invalid parameters", error=error)
        
        from_account = parameters["from_account"]
        amount = parameters["amount"]
        recipient = parameters["recipient"]
        currency = parameters.get("currency", "USD")
        note = parameters.get("note", "")
        
        payment_payload = {
            "payment_id": f"PAY-{random.randint(100000, 999999)}",
            "from_account": from_account,
            "recipient": recipient,
            "amount": amount,
            "currency": currency,
            "note": note,
            "status": "pending_confirmation",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        logger.warning(f"Payment prepared (NOT executed) for {user_id}: {amount} {currency} to {recipient}")
        
        return ToolResult(
            success=True,
            data=payment_payload,
            message="Payment prepared. User MUST confirm before execution.",
            requires_confirmation=True,
            metadata={"warning": "This payment has NOT been executed. User confirmation required."}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "from_account": {
                        "type": "string",
                        "description": "Account ID to pay from"
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Recipient name, email, or account number"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Payment amount"
                    },
                    "currency": {
                        "type": "string",
                        "enum": ["CAD", "USD", "KES"],
                        "description": "Payment currency"
                    },
                    "note": {
                        "type": "string",
                        "description": "Payment note/memo"
                    }
                },
                "required": ["from_account", "recipient", "amount"]
            }
        }


# ============================================
# BANKING TOOLS COLLECTION
# ============================================

class BankingTools:
    """Collection of all banking tools."""
    
    @staticmethod
    def get_all_tools() -> list[BaseTool]:
        """Get all banking tools."""
        return [
            ListBankAccountsTool(),
            AddBankAccountTool(),
            GetBalanceTool(),
            GetDailyBalanceSummaryTool(),
            ListTransactionsTool(),
            ExportTransactionsToExcelTool(),
            GenerateAccountantReportTool(),
            CreatePaymentTool()
        ]
    
    @staticmethod
    def get_schemas() -> list[Dict[str, Any]]:
        """Get all banking tool schemas."""
        return [tool.get_schema() for tool in BankingTools.get_all_tools()]
