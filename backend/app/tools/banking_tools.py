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
        
        # STUBBED: Mock multi-country accounts
        mock_accounts = [
            {
                "account_id": "acc_ca_001",
                "institution": "TD Canada Trust",
                "country": "CA",
                "currency": "CAD",
                "account_type": "checking",
                "account_name": "TD Chequing",
                "last_four": "5678",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "acc_ca_002",
                "institution": "RBC Royal Bank",
                "country": "CA",
                "currency": "CAD",
                "account_type": "business",
                "account_name": "RBC Business Account",
                "last_four": "9012",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "acc_us_001",
                "institution": "Chase Bank",
                "country": "US",
                "currency": "USD",
                "account_type": "checking",
                "account_name": "Chase Total Checking",
                "last_four": "3456",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "acc_us_002",
                "institution": "Bank of America",
                "country": "US",
                "currency": "USD",
                "account_type": "savings",
                "account_name": "BoA Savings",
                "last_four": "7890",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "acc_ke_001",
                "institution": "Kenya Commercial Bank",
                "country": "KE",
                "currency": "KES",
                "account_type": "checking",
                "account_name": "KCB Current Account",
                "last_four": "2345",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "acc_ke_002",
                "institution": "Equity Bank Kenya",
                "country": "KE",
                "currency": "KES",
                "account_type": "business",
                "account_name": "Equity Business",
                "last_four": "6789",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            }
        ]
        
        # Filter by country if specified
        if country_filter:
            mock_accounts = [acc for acc in mock_accounts if acc["country"] == country_filter]
        
        logger.info(f"Listed {len(mock_accounts)} bank accounts for {user_id}")
        
        return ToolResult(
            success=True,
            data={
                "accounts": mock_accounts,
                "total_count": len(mock_accounts),
                "countries": list(set(acc["country"] for acc in mock_accounts))
            },
            message=f"Found {len(mock_accounts)} connected bank accounts"
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
        
        account_id = parameters.get("account_id")  # Specific account
        country = parameters.get("country")  # Filter by country
        
        # STUBBED: Mock balances with multi-currency support
        mock_balances = {
            "acc_ca_001": {
                "account_id": "acc_ca_001",
                "institution": "TD Canada Trust",
                "account_name": "TD Chequing",
                "country": "CA",
                "currency": "CAD",
                "current_balance": 12450.75,
                "available_balance": 12450.75,
                "as_of": datetime.now().isoformat()
            },
            "acc_ca_002": {
                "account_id": "acc_ca_002",
                "institution": "RBC Royal Bank",
                "account_name": "RBC Business Account",
                "country": "CA",
                "currency": "CAD",
                "current_balance": 45230.50,
                "available_balance": 45230.50,
                "as_of": datetime.now().isoformat()
            },
            "acc_us_001": {
                "account_id": "acc_us_001",
                "institution": "Chase Bank",
                "account_name": "Chase Total Checking",
                "country": "US",
                "currency": "USD",
                "current_balance": 8750.25,
                "available_balance": 8750.25,
                "as_of": datetime.now().isoformat()
            },
            "acc_us_002": {
                "account_id": "acc_us_002",
                "institution": "Bank of America",
                "account_name": "BoA Savings",
                "country": "US",
                "currency": "USD",
                "current_balance": 25000.00,
                "available_balance": 25000.00,
                "as_of": datetime.now().isoformat()
            },
            "acc_ke_001": {
                "account_id": "acc_ke_001",
                "institution": "Kenya Commercial Bank",
                "account_name": "KCB Current Account",
                "country": "KE",
                "currency": "KES",
                "current_balance": 1250000.00,
                "available_balance": 1250000.00,
                "as_of": datetime.now().isoformat()
            },
            "acc_ke_002": {
                "account_id": "acc_ke_002",
                "institution": "Equity Bank Kenya",
                "account_name": "Equity Business",
                "country": "KE",
                "currency": "KES",
                "current_balance": 3500000.00,
                "available_balance": 3500000.00,
                "as_of": datetime.now().isoformat()
            }
        }
        
        # Filter results
        if account_id:
            if account_id in mock_balances:
                balances = [mock_balances[account_id]]
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    message="Account not found",
                    error=f"Account '{account_id}' not found"
                )
        else:
            balances = list(mock_balances.values())
            if country:
                balances = [b for b in balances if b["country"] == country]
        
        # Calculate totals by currency
        totals_by_currency = {}
        for bal in balances:
            curr = bal["currency"]
            if curr not in totals_by_currency:
                totals_by_currency[curr] = 0
            totals_by_currency[curr] += bal["current_balance"]
        
        logger.info(f"Balance retrieved for {user_id}: {len(balances)} accounts")
        
        return ToolResult(
            success=True,
            data={
                "balances": balances,
                "totals_by_currency": totals_by_currency,
                "account_count": len(balances)
            },
            message=f"Retrieved balances for {len(balances)} accounts"
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
            description="Get comprehensive daily balance summary across all accounts in Canada, US, and Kenya",
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
        
        # STUBBED: Mock daily summary
        summary = {
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "by_country": {
                "CA": {
                    "currency": "CAD",
                    "total_balance": 57681.25,
                    "accounts": [
                        {"name": "TD Chequing", "balance": 12450.75},
                        {"name": "RBC Business Account", "balance": 45230.50}
                    ],
                    "daily_change": 1250.00,
                    "change_percent": 2.21
                },
                "US": {
                    "currency": "USD",
                    "total_balance": 33750.25,
                    "accounts": [
                        {"name": "Chase Total Checking", "balance": 8750.25},
                        {"name": "BoA Savings", "balance": 25000.00}
                    ],
                    "daily_change": -500.00,
                    "change_percent": -1.46
                },
                "KE": {
                    "currency": "KES",
                    "total_balance": 4750000.00,
                    "accounts": [
                        {"name": "KCB Current Account", "balance": 1250000.00},
                        {"name": "Equity Business", "balance": 3500000.00}
                    ],
                    "daily_change": 150000.00,
                    "change_percent": 3.26
                }
            },
            "usd_equivalent_total": 98500.00,
            "alerts": [
                {"type": "info", "message": "Positive cash flow across all regions"}
            ]
        }
        
        logger.info(f"Daily balance summary generated for {user_id}")
        
        return ToolResult(
            success=True,
            data=summary,
            message=f"Daily balance summary for {date}"
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
        
        account_id = parameters.get("account_id")
        country = parameters.get("country")
        days = parameters.get("days", 7)
        category = parameters.get("category")
        limit = parameters.get("limit", 50)
        
        # STUBBED: Generate realistic mock transactions
        merchants_by_country = {
            "CA": ["Tim Hortons", "Shoppers Drug Mart", "Loblaws", "Canadian Tire", "Rogers", "Bell Canada"],
            "US": ["Amazon", "Starbucks", "Walmart", "Target", "AT&T", "Verizon"],
            "KE": ["Safaricom M-Pesa", "Naivas Supermarket", "Java House", "Nakumatt", "Kenya Power"]
        }
        
        categories = ["food", "shopping", "utilities", "transport", "entertainment", "business", "transfer"]
        
        transactions = []
        countries_to_use = [country] if country else ["CA", "US", "KE"]
        
        for _ in range(min(limit, 50)):
            txn_country = random.choice(countries_to_use)
            txn_currency = {"CA": "CAD", "US": "USD", "KE": "KES"}[txn_country]
            amount_multiplier = {"CA": 1, "US": 1, "KE": 150}[txn_country]
            
            txn = {
                "transaction_id": f"TXN-{random.randint(100000, 999999)}",
                "account_id": f"acc_{txn_country.lower()}_{random.choice(['001', '002'])}",
                "date": (datetime.now() - timedelta(days=random.randint(0, days))).strftime("%Y-%m-%d"),
                "merchant": random.choice(merchants_by_country[txn_country]),
                "amount": round(random.uniform(10, 500) * amount_multiplier, 2),
                "currency": txn_currency,
                "country": txn_country,
                "category": random.choice(categories),
                "type": random.choice(["debit", "credit"]),
                "status": "posted",
                "description": f"Transaction at merchant"
            }
            
            if category and txn["category"] != category:
                continue
                
            transactions.append(txn)
        
        transactions.sort(key=lambda x: x["date"], reverse=True)
        transactions = transactions[:limit]
        
        summary = {
            "total_transactions": len(transactions),
            "total_debits": sum(t["amount"] for t in transactions if t["type"] == "debit"),
            "total_credits": sum(t["amount"] for t in transactions if t["type"] == "credit"),
            "by_category": {}
        }
        
        for txn in transactions:
            cat = txn["category"]
            if cat not in summary["by_category"]:
                summary["by_category"][cat] = {"count": 0, "total": 0}
            summary["by_category"][cat]["count"] += 1
            summary["by_category"][cat]["total"] += txn["amount"]
        
        logger.info(f"Transactions retrieved for {user_id}: {len(transactions)} transactions")
        
        return ToolResult(
            success=True,
            data={
                "transactions": transactions,
                "summary": summary,
                "date_range": {
                    "start": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d")
                }
            },
            message=f"Retrieved {len(transactions)} transactions"
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
        country = parameters.get("country")
        format_type = parameters.get("format", "quickbooks")
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        export_data = {
            "export_id": f"EXP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "format": format_type,
            "country_filter": country or "all",
            "file_info": {
                "filename": f"transactions_{start_date}_to_{end_date}.xlsx",
                "path": f"./exports/transactions_{start_date}_to_{end_date}.xlsx",
                "size_kb": random.randint(50, 200),
                "sheets": ["All Transactions", "By Category", "By Account", "Summary"]
            },
            "statistics": {
                "total_transactions": random.randint(50, 200),
                "total_debits": round(random.uniform(5000, 20000), 2),
                "total_credits": round(random.uniform(2000, 10000), 2),
                "accounts_included": 6 if not country else 2
            },
            "quickbooks_ready": format_type == "quickbooks",
            "columns": [
                "Date", "Account", "Description", "Category", "Debit", "Credit", 
                "Currency", "Country", "Reference"
            ]
        }
        
        logger.info(f"Transaction export generated for {user_id}: {export_data['export_id']}")
        
        return ToolResult(
            success=True,
            data=export_data,
            message=f"Excel export ready: {export_data['file_info']['filename']}"
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
        
        report = {
            "report_id": f"RPT-{week_end.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": week_start.strftime("%Y-%m-%d"),
                "end": week_ending,
                "type": "weekly"
            },
            "summary": {
                "opening_balance_usd_equiv": 95000.00,
                "closing_balance_usd_equiv": 98500.00,
                "net_change_usd_equiv": 3500.00,
                "total_income": 12500.00,
                "total_expenses": 9000.00
            },
            "by_country": {
                "CA": {
                    "currency": "CAD",
                    "opening_balance": 54000.00,
                    "closing_balance": 57681.25,
                    "transactions": 45,
                    "income": 8500.00,
                    "expenses": 4818.75
                },
                "US": {
                    "currency": "USD",
                    "opening_balance": 35000.00,
                    "closing_balance": 33750.25,
                    "transactions": 32,
                    "income": 2000.00,
                    "expenses": 3249.75
                },
                "KE": {
                    "currency": "KES",
                    "opening_balance": 4500000.00,
                    "closing_balance": 4750000.00,
                    "transactions": 28,
                    "income": 500000.00,
                    "expenses": 250000.00
                }
            },
            "expense_categories": {
                "business": 4500.00,
                "utilities": 1200.00,
                "travel": 2000.00,
                "food": 800.00,
                "other": 500.00
            },
            "attachments": [
                {
                    "name": f"transactions_{week_start.strftime('%Y%m%d')}_{week_ending}.xlsx",
                    "type": "excel",
                    "quickbooks_ready": True
                },
                {
                    "name": f"summary_{week_ending}.pdf",
                    "type": "pdf"
                }
            ],
            "notes": "All transactions categorized and ready for QuickBooks import.",
            "email_status": "sent" if send_email else "not_requested"
        }
        
        logger.info(f"Accountant report generated for {user_id}: {report['report_id']}")
        
        return ToolResult(
            success=True,
            data=report,
            message=f"Weekly accountant report generated for week ending {week_ending}"
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
