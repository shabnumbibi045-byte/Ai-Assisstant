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

        try:
            from app.services.alpha_vantage_service import alpha_vantage_service

            # Define portfolio holdings with user's positions (quantity and avg cost)
            holdings_config = [
                {"symbol": "AAPL", "name": "Apple Inc.", "quantity": 150, "avg_cost": 145.00, "account": "TD Ameritrade"},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "quantity": 100, "avg_cost": 280.00, "account": "TD Ameritrade"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "quantity": 50, "avg_cost": 125.00, "account": "Interactive Brokers"},
                {"symbol": "NVDA", "name": "NVIDIA Corp.", "quantity": 30, "avg_cost": 450.00, "account": "TD Ameritrade"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "quantity": 40, "avg_cost": 225.00, "account": "Interactive Brokers"},
            ]

            # Fetch real-time prices for all holdings
            logger.info(f"Fetching real-time prices for {len(holdings_config)} holdings")
            holdings = []
            total_value = 0
            total_cost_basis = 0

            for holding_config in holdings_config:
                try:
                    # Fetch real-time quote from Alpha Vantage
                    quote = await alpha_vantage_service.get_quote(holding_config["symbol"])

                    if quote:
                        current_price = quote["price"]
                        quantity = holding_config["quantity"]
                        avg_cost = holding_config["avg_cost"]

                        market_value = current_price * quantity
                        cost_basis = avg_cost * quantity
                        gain_loss = market_value - cost_basis
                        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

                        holdings.append({
                            "symbol": holding_config["symbol"],
                            "name": holding_config["name"],
                            "quantity": quantity,
                            "avg_cost": avg_cost,
                            "current_price": current_price,
                            "market_value": round(market_value, 2),
                            "gain_loss": round(gain_loss, 2),
                            "gain_loss_percent": round(gain_loss_percent, 2),
                            "day_change": quote["change"],
                            "day_change_percent": quote["change_percent"],
                            "account": holding_config["account"],
                            "latest_trading_day": quote["latest_trading_day"],
                            "data_source": "Alpha Vantage (Real-Time)"
                        })

                        total_value += market_value
                        total_cost_basis += cost_basis

                        logger.info(f"Fetched {holding_config['symbol']}: ${current_price} (Real-time)")
                    else:
                        logger.warning(f"Could not fetch quote for {holding_config['symbol']}")
                except Exception as e:
                    logger.error(f"Error fetching quote for {holding_config['symbol']}: {e}")

            total_gain_loss = total_value - total_cost_basis
            total_gain_loss_percent = (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0

            # Calculate day change (sum of all position day changes)
            day_change = sum(h["day_change"] * h["quantity"] for h in holdings)
            day_change_percent = (day_change / total_value * 100) if total_value > 0 else 0

            # Group by account
            by_account = {}
            for holding in holdings:
                account = holding["account"]
                if account not in by_account:
                    by_account[account] = {
                        "value": 0,
                        "gain_loss": 0,
                        "currency": "USD"
                    }
                by_account[account]["value"] += holding["market_value"]
                by_account[account]["gain_loss"] += holding["gain_loss"]

            portfolio = {
                "as_of": datetime.now().isoformat(),
                "total_value": round(total_value, 2),
                "total_cost_basis": round(total_cost_basis, 2),
                "total_gain_loss": round(total_gain_loss, 2),
                "total_gain_loss_percent": round(total_gain_loss_percent, 2),
                "day_change": round(day_change, 2),
                "day_change_percent": round(day_change_percent, 2),
                "holdings": holdings,
                "by_account": by_account,
                "data_source": "Real-time prices from Alpha Vantage API",
                "sector_allocation": {
                    "Technology": 90.0,
                    "Financials": 5.0,
                    "Other": 5.0
                }
            }

            logger.info(f"Portfolio summary retrieved for {user_id} with REAL-TIME data: ${total_value:.2f}")

            return ToolResult(
                success=True,
                data=portfolio,
                message=f"Portfolio summary with real-time prices: ${total_value:.2f}",
                metadata={
                    "disclaimer": "Real-time data from Alpha Vantage. For informational purposes only. Not financial advice.",
                    "data_source": "Alpha Vantage API"
                }
            )
        except Exception as e:
            logger.error(f"Error retrieving portfolio summary: {e}")
            return ToolResult(
                success=False,
                data=None,
                message="Failed to retrieve portfolio summary",
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

        # Fetch REAL-TIME data from Alpha Vantage
        try:
            from app.services.alpha_vantage_service import alpha_vantage_service

            logger.info(f"Fetching real-time quote for {symbol} from Alpha Vantage")
            quote_data = await alpha_vantage_service.get_quote(symbol.upper())

            if not quote_data:
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"Could not fetch data for {symbol}",
                    error="Invalid symbol or API error"
                )

            # Format the quote data
            quote = {
                "symbol": symbol.upper(),
                "price": quote_data["price"],
                "change": quote_data["change"],
                "change_percent": quote_data["change_percent"],
                "volume": quote_data["volume"],
                "high": quote_data["high"],
                "low": quote_data["low"],
                "open": quote_data["open"],
                "previous_close": quote_data["previous_close"],
                "latest_trading_day": quote_data["latest_trading_day"],
                "timestamp": datetime.now().isoformat(),
                "data_source": "Alpha Vantage (Real-Time)"
            }

            logger.info(f"Real-time quote retrieved for {symbol}: ${quote['price']}")

            return ToolResult(
                success=True,
                data=quote,
                message=f"{symbol.upper()} real-time quote retrieved successfully",
                metadata={"disclaimer": "Real-time data from Alpha Vantage. Not financial advice."}
            )

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to fetch quote for {symbol}",
                error=str(e)
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
