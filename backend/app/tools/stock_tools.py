"""Stock Trading Tools - Portfolio Management and Monitoring.

Features:
- Multi-brokerage portfolio tracking
- Real-time stock quotes
- Transaction history
- Performance reporting
- Excel export for accountant

DISCLAIMER: This is for informational purposes only. Not financial advice.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import random

from .base_tool import BaseTool, ToolResult, ToolCategory

logger = logging.getLogger(__name__)


class BrokerageType(str, Enum):
    """Supported brokerage platforms."""
    ALPACA = "alpaca"
    INTERACTIVE_BROKERS = "ib"
    TD_AMERITRADE = "tda"
    QUESTRADE = "questrade"  # Canadian
    GENERIC = "generic"


# ============================================
# ACCOUNT MANAGEMENT
# ============================================

class ListTradingAccountsTool(BaseTool):
    """List all connected trading accounts."""
    
    def __init__(self):
        super().__init__(
            name="list_trading_accounts",
            description="List all connected stock trading/brokerage accounts with status",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        # STUBBED: Mock trading accounts
        accounts = [
            {
                "account_id": "tda_001",
                "brokerage": "TD Ameritrade",
                "account_type": "individual",
                "account_name": "TD Individual Trading",
                "country": "US",
                "currency": "USD",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "qt_001",
                "brokerage": "Questrade",
                "account_type": "tfsa",
                "account_name": "Questrade TFSA",
                "country": "CA",
                "currency": "CAD",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            },
            {
                "account_id": "ib_001",
                "brokerage": "Interactive Brokers",
                "account_type": "margin",
                "account_name": "IB Margin Account",
                "country": "US",
                "currency": "USD",
                "status": "active",
                "last_synced": datetime.now().isoformat()
            }
        ]
        
        logger.info(f"Listed {len(accounts)} trading accounts for {user_id}")
        
        return ToolResult(
            success=True,
            data={
                "accounts": accounts,
                "total_count": len(accounts)
            },
            message=f"Found {len(accounts)} trading accounts",
            metadata={"disclaimer": "For informational purposes only. Not financial advice."}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }


class AddTradingAccountTool(BaseTool):
    """Add a new trading account connection."""
    
    def __init__(self):
        super().__init__(
            name="add_trading_account",
            description="Connect a new brokerage/trading account for portfolio tracking",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_write permission"
            )
        
        brokerage = parameters.get("brokerage")
        account_type = parameters.get("account_type", "individual")
        
        if not brokerage:
            return ToolResult(
                success=False,
                data=None,
                message="Missing brokerage",
                error="Brokerage name is required"
            )
        
        # STUBBED: Return connection instructions
        connection_data = {
            "connection_id": f"conn-{random.randint(100000, 999999)}",
            "brokerage": brokerage,
            "account_type": account_type,
            "oauth_url": f"https://oauth.{brokerage.lower().replace(' ', '')}.com/authorize",
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "instructions": f"Complete OAuth authentication with {brokerage} to link your account"
        }
        
        logger.info(f"Trading account connection initiated for {user_id}: {brokerage}")
        
        return ToolResult(
            success=True,
            data=connection_data,
            message=f"Connection initiated for {brokerage}. Complete authentication to link account.",
            requires_confirmation=True
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "brokerage": {
                        "type": "string",
                        "enum": ["TD Ameritrade", "Questrade", "Interactive Brokers", "Alpaca", "Robinhood"],
                        "description": "Brokerage platform name"
                    },
                    "account_type": {
                        "type": "string",
                        "enum": ["individual", "margin", "tfsa", "rrsp", "ira", "roth_ira"],
                        "description": "Type of trading account"
                    }
                },
                "required": ["brokerage"]
            }
        }


# ============================================
# PORTFOLIO OPERATIONS
# ============================================

class GetPortfolioSummaryTool(BaseTool):
    """Get comprehensive portfolio summary."""
    
    def __init__(self):
        super().__init__(
            name="get_portfolio_summary",
            description="Get portfolio holdings, current values, and performance across all trading accounts",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        account_id = parameters.get("account_id")  # Optional filter
        
        # STUBBED: Mock portfolio data
        portfolio = {
            "as_of": datetime.now().isoformat(),
            "total_value": 287450.75,
            "total_cost_basis": 245000.00,
            "total_gain_loss": 42450.75,
            "total_gain_loss_percent": 17.33,
            "day_change": 1250.50,
            "day_change_percent": 0.44,
            "holdings": [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "quantity": 150,
                    "avg_cost": 145.00,
                    "current_price": 178.50,
                    "market_value": 26775.00,
                    "gain_loss": 5025.00,
                    "gain_loss_percent": 23.10,
                    "day_change": 2.30,
                    "day_change_percent": 1.30,
                    "account": "TD Ameritrade"
                },
                {
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation",
                    "quantity": 100,
                    "avg_cost": 280.00,
                    "current_price": 378.25,
                    "market_value": 37825.00,
                    "gain_loss": 9825.00,
                    "gain_loss_percent": 35.09,
                    "day_change": -1.50,
                    "day_change_percent": -0.40,
                    "account": "TD Ameritrade"
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "quantity": 50,
                    "avg_cost": 125.00,
                    "current_price": 141.80,
                    "market_value": 7090.00,
                    "gain_loss": 840.00,
                    "gain_loss_percent": 13.44,
                    "day_change": 0.80,
                    "day_change_percent": 0.57,
                    "account": "Interactive Brokers"
                },
                {
                    "symbol": "SHOP.TO",
                    "name": "Shopify Inc.",
                    "quantity": 75,
                    "avg_cost": 85.00,
                    "current_price": 102.50,
                    "market_value": 7687.50,
                    "gain_loss": 1312.50,
                    "gain_loss_percent": 20.59,
                    "day_change": 1.25,
                    "day_change_percent": 1.23,
                    "account": "Questrade",
                    "currency": "CAD"
                },
                {
                    "symbol": "TD.TO",
                    "name": "Toronto-Dominion Bank",
                    "quantity": 200,
                    "avg_cost": 78.50,
                    "current_price": 82.30,
                    "market_value": 16460.00,
                    "gain_loss": 760.00,
                    "gain_loss_percent": 4.84,
                    "day_change": -0.45,
                    "day_change_percent": -0.54,
                    "account": "Questrade",
                    "currency": "CAD"
                }
            ],
            "by_account": {
                "TD Ameritrade": {
                    "value": 150000.00,
                    "gain_loss": 25000.00,
                    "currency": "USD"
                },
                "Interactive Brokers": {
                    "value": 85000.00,
                    "gain_loss": 12000.00,
                    "currency": "USD"
                },
                "Questrade": {
                    "value": 52450.75,
                    "gain_loss": 5450.75,
                    "currency": "CAD"
                }
            },
            "sector_allocation": {
                "Technology": 65.5,
                "Financials": 15.2,
                "Healthcare": 10.3,
                "Consumer": 9.0
            }
        }
        
        logger.info(f"Portfolio summary retrieved for {user_id}")
        
        return ToolResult(
            success=True,
            data=portfolio,
            message="Portfolio summary retrieved",
            metadata={"disclaimer": "For informational purposes only. Not financial advice."}
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
                        "description": "Filter by specific account ID (optional)"
                    }
                },
                "required": []
            }
        }


class GetDailyPortfolioSummaryTool(BaseTool):
    """Get daily portfolio performance summary."""
    
    def __init__(self):
        super().__init__(
            name="get_daily_portfolio_summary",
            description="Get comprehensive daily portfolio summary with balances and performance metrics",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        date = parameters.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # STUBBED: Mock daily summary
        summary = {
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "market_status": "open" if datetime.now().hour >= 9 and datetime.now().hour < 16 else "closed",
            "total_portfolio_value": 287450.75,
            "previous_close_value": 286200.25,
            "day_change": 1250.50,
            "day_change_percent": 0.44,
            "cash_balance": 15420.00,
            "buying_power": 45000.00,
            "by_account": {
                "TD Ameritrade": {
                    "value": 150000.00,
                    "day_change": 750.00,
                    "day_change_percent": 0.50
                },
                "Interactive Brokers": {
                    "value": 85000.00,
                    "day_change": 350.00,
                    "day_change_percent": 0.41
                },
                "Questrade": {
                    "value": 52450.75,
                    "day_change": 150.50,
                    "day_change_percent": 0.29
                }
            },
            "top_gainers": [
                {"symbol": "AAPL", "change_percent": 1.30},
                {"symbol": "SHOP.TO", "change_percent": 1.23}
            ],
            "top_losers": [
                {"symbol": "TD.TO", "change_percent": -0.54},
                {"symbol": "MSFT", "change_percent": -0.40}
            ],
            "alerts": [
                {"type": "info", "message": "Market performing above average today"}
            ]
        }
        
        logger.info(f"Daily portfolio summary generated for {user_id}")
        
        return ToolResult(
            success=True,
            data=summary,
            message=f"Daily portfolio summary for {date}",
            metadata={"disclaimer": "For informational purposes only. Not financial advice."}
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
# STOCK QUOTES AND DATA
# ============================================

class GetStockQuoteTool(BaseTool):
    """Get real-time stock quote."""
    
    def __init__(self):
        super().__init__(
            name="get_stock_quote",
            description="Get real-time stock quote with price, volume, and key metrics",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        symbol = parameters.get("symbol")
        if not symbol:
            return ToolResult(
                success=False,
                data=None,
                message="Missing symbol",
                error="Stock symbol is required"
            )
        
        # STUBBED: Mock quote data
        mock_quotes = {
            "AAPL": {"price": 178.50, "change": 2.30, "volume": 45_000_000},
            "MSFT": {"price": 378.25, "change": -1.50, "volume": 22_000_000},
            "GOOGL": {"price": 141.80, "change": 0.80, "volume": 18_000_000},
            "AMZN": {"price": 185.50, "change": 1.20, "volume": 35_000_000},
            "TSLA": {"price": 248.75, "change": -3.50, "volume": 85_000_000}
        }
        
        base_data = mock_quotes.get(symbol.upper(), {"price": 100.00, "change": 0.50, "volume": 1_000_000})
        
        quote = {
            "symbol": symbol.upper(),
            "price": base_data["price"],
            "change": base_data["change"],
            "change_percent": round(base_data["change"] / base_data["price"] * 100, 2),
            "volume": base_data["volume"],
            "avg_volume": int(base_data["volume"] * 0.9),
            "high": round(base_data["price"] * 1.02, 2),
            "low": round(base_data["price"] * 0.98, 2),
            "open": round(base_data["price"] - base_data["change"], 2),
            "previous_close": round(base_data["price"] - base_data["change"], 2),
            "market_cap": f"{random.randint(100, 3000)}B",
            "pe_ratio": round(random.uniform(15, 35), 2),
            "52_week_high": round(base_data["price"] * 1.25, 2),
            "52_week_low": round(base_data["price"] * 0.75, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Quote retrieved for {symbol}")
        
        return ToolResult(
            success=True,
            data=quote,
            message=f"{symbol.upper()} quote retrieved",
            metadata={"disclaimer": "Quotes may be delayed. Not financial advice."}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                    }
                },
                "required": ["symbol"]
            }
        }


# ============================================
# TRANSACTION HISTORY
# ============================================

class ListStockTransactionsTool(BaseTool):
    """List stock trading transactions."""
    
    def __init__(self):
        super().__init__(
            name="list_stock_transactions",
            description="Fetch stock trading transaction history with filters",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        account_id = parameters.get("account_id")
        days = parameters.get("days", 30)
        transaction_type = parameters.get("type")  # buy, sell, dividend
        limit = parameters.get("limit", 50)
        
        # STUBBED: Mock transactions
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SHOP.TO", "TD.TO"]
        transaction_types = ["buy", "sell", "dividend"]
        accounts = ["TD Ameritrade", "Interactive Brokers", "Questrade"]
        
        transactions = []
        for i in range(min(limit, 50)):
            txn_type = random.choice(transaction_types) if not transaction_type else transaction_type
            symbol = random.choice(symbols)
            
            txn = {
                "transaction_id": f"STK-{random.randint(100000, 999999)}",
                "date": (datetime.now() - timedelta(days=random.randint(0, days))).strftime("%Y-%m-%d"),
                "time": f"{random.randint(9, 15)}:{random.randint(0, 59):02d}:00",
                "symbol": symbol,
                "type": txn_type,
                "quantity": random.randint(1, 100) if txn_type != "dividend" else 0,
                "price": round(random.uniform(50, 400), 2) if txn_type != "dividend" else 0,
                "amount": round(random.uniform(500, 10000), 2),
                "fees": round(random.uniform(0, 10), 2),
                "account": random.choice(accounts),
                "status": "executed",
                "currency": "CAD" if ".TO" in symbol else "USD"
            }
            transactions.append(txn)
        
        transactions.sort(key=lambda x: x["date"], reverse=True)
        
        # Calculate summary
        summary = {
            "total_transactions": len(transactions),
            "total_buys": sum(1 for t in transactions if t["type"] == "buy"),
            "total_sells": sum(1 for t in transactions if t["type"] == "sell"),
            "total_dividends": sum(1 for t in transactions if t["type"] == "dividend"),
            "total_buy_amount": sum(t["amount"] for t in transactions if t["type"] == "buy"),
            "total_sell_amount": sum(t["amount"] for t in transactions if t["type"] == "sell"),
            "total_dividend_amount": sum(t["amount"] for t in transactions if t["type"] == "dividend"),
            "total_fees": sum(t["fees"] for t in transactions)
        }
        
        logger.info(f"Stock transactions retrieved for {user_id}: {len(transactions)} transactions")
        
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
            message=f"Retrieved {len(transactions)} stock transactions",
            metadata={"disclaimer": "For informational purposes only. Not financial advice."}
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
                        "description": "Filter by specific account"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Days to look back (default: 30)",
                        "default": 30
                    },
                    "type": {
                        "type": "string",
                        "enum": ["buy", "sell", "dividend"],
                        "description": "Filter by transaction type"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max transactions to return",
                        "default": 50
                    }
                },
                "required": []
            }
        }


# ============================================
# EXPORT OPERATIONS
# ============================================

class ExportPortfolioToExcelTool(BaseTool):
    """Export portfolio data to Excel."""
    
    def __init__(self):
        super().__init__(
            name="export_portfolio_excel",
            description="Export portfolio holdings and transactions to Excel for accountant/tax reporting",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        include_transactions = parameters.get("include_transactions", True)
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        export_data = {
            "export_id": f"STK-EXP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "file_info": {
                "filename": f"portfolio_{start_date}_to_{end_date}.xlsx",
                "path": f"./exports/portfolio_{start_date}_to_{end_date}.xlsx",
                "size_kb": random.randint(80, 300),
                "sheets": [
                    "Portfolio Summary",
                    "Holdings Detail",
                    "Transactions" if include_transactions else None,
                    "Performance",
                    "Tax Summary"
                ]
            },
            "statistics": {
                "total_holdings": 15,
                "total_transactions": random.randint(20, 100) if include_transactions else 0,
                "realized_gains": round(random.uniform(5000, 25000), 2),
                "unrealized_gains": round(random.uniform(10000, 50000), 2),
                "total_dividends": round(random.uniform(1000, 5000), 2)
            },
            "columns": {
                "holdings": ["Symbol", "Name", "Quantity", "Cost Basis", "Market Value", "Gain/Loss", "Account"],
                "transactions": ["Date", "Symbol", "Type", "Quantity", "Price", "Amount", "Fees", "Account"]
            }
        }
        
        # Remove None sheets
        export_data["file_info"]["sheets"] = [s for s in export_data["file_info"]["sheets"] if s]
        
        logger.info(f"Portfolio export generated for {user_id}: {export_data['export_id']}")
        
        return ToolResult(
            success=True,
            data=export_data,
            message=f"Portfolio export ready: {export_data['file_info']['filename']}",
            metadata={"disclaimer": "For informational purposes only. Consult tax professional."}
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
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "include_transactions": {
                        "type": "boolean",
                        "description": "Include transaction history",
                        "default": True
                    }
                },
                "required": []
            }
        }


class GenerateStockReportTool(BaseTool):
    """Generate comprehensive stock portfolio report."""
    
    def __init__(self):
        super().__init__(
            name="generate_stock_report",
            description="Generate detailed portfolio report with performance analysis for accountant",
            category=ToolCategory.STOCKS
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("stocks_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have stocks_read permission"
            )
        
        period = parameters.get("period", "monthly")  # weekly, monthly, quarterly, ytd
        send_email = parameters.get("send_email", False)
        
        # Determine date range based on period
        end_date = datetime.now()
        if period == "weekly":
            start_date = end_date - timedelta(days=7)
        elif period == "monthly":
            start_date = end_date - timedelta(days=30)
        elif period == "quarterly":
            start_date = end_date - timedelta(days=90)
        else:  # ytd
            start_date = datetime(end_date.year, 1, 1)
        
        report = {
            "report_id": f"STK-RPT-{end_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "type": period,
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "portfolio_summary": {
                "starting_value": 275000.00,
                "ending_value": 287450.75,
                "net_deposits": 5000.00,
                "net_performance": 7450.75,
                "performance_percent": 2.71,
                "total_dividends": 850.25,
                "total_fees": 125.50
            },
            "by_account": {
                "TD Ameritrade": {
                    "starting_value": 145000.00,
                    "ending_value": 150000.00,
                    "performance": 5000.00,
                    "performance_percent": 3.45
                },
                "Interactive Brokers": {
                    "starting_value": 82000.00,
                    "ending_value": 85000.00,
                    "performance": 3000.00,
                    "performance_percent": 3.66
                },
                "Questrade": {
                    "starting_value": 48000.00,
                    "ending_value": 52450.75,
                    "performance": 4450.75,
                    "performance_percent": 9.27
                }
            },
            "top_performers": [
                {"symbol": "SHOP.TO", "return_percent": 12.5},
                {"symbol": "MSFT", "return_percent": 8.2},
                {"symbol": "AAPL", "return_percent": 5.8}
            ],
            "worst_performers": [
                {"symbol": "TSLA", "return_percent": -3.2},
                {"symbol": "TD.TO", "return_percent": -1.5}
            ],
            "tax_relevant": {
                "realized_gains": 3500.00,
                "realized_losses": 750.00,
                "dividends_received": 850.25,
                "foreign_dividends": 650.00,
                "withholding_tax_paid": 97.50
            },
            "attachments": [
                {"name": f"portfolio_report_{period}_{end_date.strftime('%Y%m%d')}.xlsx", "type": "excel"},
                {"name": f"portfolio_report_{period}_{end_date.strftime('%Y%m%d')}.pdf", "type": "pdf"}
            ],
            "email_status": "sent" if send_email else "not_requested"
        }
        
        logger.info(f"Stock report generated for {user_id}: {report['report_id']}")
        
        return ToolResult(
            success=True,
            data=report,
            message=f"{period.capitalize()} portfolio report generated",
            metadata={"disclaimer": "For informational purposes only. Not financial advice."}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "enum": ["weekly", "monthly", "quarterly", "ytd"],
                        "description": "Report period",
                        "default": "monthly"
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
# STOCK TOOLS COLLECTION
# ============================================

class StockTools:
    """Collection of all stock trading tools."""
    
    @staticmethod
    def get_all_tools() -> list[BaseTool]:
        """Get all stock tools."""
        return [
            ListTradingAccountsTool(),
            AddTradingAccountTool(),
            GetPortfolioSummaryTool(),
            GetDailyPortfolioSummaryTool(),
            GetStockQuoteTool(),
            ListStockTransactionsTool(),
            ExportPortfolioToExcelTool(),
            GenerateStockReportTool()
        ]
    
    @staticmethod
    def get_schemas() -> list[Dict[str, Any]]:
        """Get all stock tool schemas."""
        return [tool.get_schema() for tool in StockTools.get_all_tools()]
