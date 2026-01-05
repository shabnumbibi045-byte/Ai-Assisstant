"""Demo Data Service - Provides realistic demo data for client demonstrations."""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


class DemoDataService:
    """Service to provide demo data for all modules."""

    @staticmethod
    def get_demo_bank_accounts() -> List[Dict[str, Any]]:
        """Get demo bank account data."""
        return [
            {
                "account_id": "ca_td_business_001",
                "bank_name": "TD Canada Trust",
                "account_type": "Business Checking",
                "country": "Canada",
                "currency": "CAD",
                "balance": 45234.56,
                "available_balance": 42734.56,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****3456"
            },
            {
                "account_id": "ca_td_savings_001",
                "bank_name": "TD Canada Trust",
                "account_type": "High Interest Savings",
                "country": "Canada",
                "currency": "CAD",
                "balance": 128450.12,
                "available_balance": 128450.12,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****7890"
            },
            {
                "account_id": "us_chase_business_001",
                "bank_name": "JPMorgan Chase",
                "account_type": "Business Checking",
                "country": "USA",
                "currency": "USD",
                "balance": 62145.89,
                "available_balance": 60145.89,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****2341"
            },
            {
                "account_id": "us_chase_savings_001",
                "bank_name": "JPMorgan Chase",
                "account_type": "Savings Plus",
                "country": "USA",
                "currency": "USD",
                "balance": 95320.44,
                "available_balance": 95320.44,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****5678"
            },
            {
                "account_id": "ke_kcb_current_001",
                "bank_name": "Kenya Commercial Bank",
                "account_type": "Current Account",
                "country": "Kenya",
                "currency": "KES",
                "balance": 8423567.00,
                "available_balance": 8200000.00,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****8901"
            },
            {
                "account_id": "ke_kcb_savings_001",
                "bank_name": "Kenya Commercial Bank",
                "account_type": "Savings Account",
                "country": "Kenya",
                "currency": "KES",
                "balance": 15678234.00,
                "available_balance": 15678234.00,
                "last_updated": datetime.now().isoformat(),
                "account_number": "****4567"
            }
        ]

    @staticmethod
    def get_demo_stock_portfolio() -> Dict[str, Any]:
        """Get demo stock portfolio data."""
        holdings = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "quantity": 150,
                "avg_cost": 145.30,
                "current_price": 175.43,
                "market_value": 26314.50,
                "gain_loss": 4519.50,
                "gain_loss_percent": 20.73,
                "sector": "Technology"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "quantity": 100,
                "avg_cost": 320.50,
                "current_price": 378.91,
                "market_value": 37891.00,
                "gain_loss": 5841.00,
                "gain_loss_percent": 18.22,
                "sector": "Technology"
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "quantity": 75,
                "avg_cost": 125.20,
                "current_price": 141.80,
                "market_value": 10635.00,
                "gain_loss": 1245.00,
                "gain_loss_percent": 13.26,
                "sector": "Technology"
            },
            {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "quantity": 50,
                "avg_cost": 240.00,
                "current_price": 248.48,
                "market_value": 12424.00,
                "gain_loss": 424.00,
                "gain_loss_percent": 3.53,
                "sector": "Automotive"
            },
            {
                "symbol": "JPM",
                "name": "JPMorgan Chase & Co.",
                "quantity": 120,
                "avg_cost": 145.75,
                "current_price": 168.25,
                "market_value": 20190.00,
                "gain_loss": 2700.00,
                "gain_loss_percent": 15.44,
                "sector": "Financial"
            },
            {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "quantity": 60,
                "avg_cost": 420.00,
                "current_price": 495.22,
                "market_value": 29713.20,
                "gain_loss": 4513.20,
                "gain_loss_percent": 17.91,
                "sector": "Technology"
            }
        ]

        total_value = sum(h["market_value"] for h in holdings)
        total_cost = sum(h["avg_cost"] * h["quantity"] for h in holdings)
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost) * 100

        return {
            "total_value": total_value,
            "total_cost_basis": total_cost,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "day_change": 1245.67,
            "day_change_percent": 0.89,
            "holdings": holdings,
            "last_updated": datetime.now().isoformat()
        }

    @staticmethod
    def get_demo_transactions(days: int = 7) -> List[Dict[str, Any]]:
        """Get demo transaction data."""
        transactions = []
        categories = [
            ("Office Supplies", "Operating Expenses", -450.00),
            ("Client Lunch", "Marketing", -125.50),
            ("Software Subscription", "Technology", -99.00),
            ("Wire Transfer Received", "Revenue", 5000.00),
            ("Consulting Payment", "Revenue", 2500.00),
            ("Internet Bill", "Utilities", -89.99),
            ("Cloud Services", "Technology", -250.00),
            ("Legal Fees", "Professional Services", -800.00),
            ("Rent Payment", "Operating Expenses", -2500.00),
            ("Client Payment", "Revenue", 3750.00)
        ]

        for i in range(min(days * 2, 20)):
            cat_name, cat_type, amount = random.choice(categories)
            date = datetime.now() - timedelta(days=random.randint(0, days))

            transactions.append({
                "transaction_id": f"tx_{i+1:04d}",
                "date": date.strftime("%Y-%m-%d"),
                "merchant": cat_name,
                "amount": amount,
                "category": cat_type,
                "type": "credit" if amount > 0 else "debit",
                "status": "completed",
                "account": "TD Business Checking"
            })

        return sorted(transactions, key=lambda x: x["date"], reverse=True)

    @staticmethod
    def get_demo_flights() -> List[Dict[str, Any]]:
        """Get demo flight options."""
        return [
            {
                "airline": "Air Canada",
                "flight_number": "AC 001",
                "origin": "YYZ",
                "destination": "NRT",
                "departure": "2025-02-15 18:30",
                "arrival": "2025-02-16 22:45",
                "duration": "13h 15m",
                "stops": 0,
                "cabin_class": "Economy",
                "price": 1245.00,
                "currency": "CAD"
            },
            {
                "airline": "Japan Airlines",
                "flight_number": "JL 002",
                "origin": "YYZ",
                "destination": "NRT",
                "departure": "2025-02-15 14:20",
                "arrival": "2025-02-16 18:35",
                "duration": "13h 15m",
                "stops": 0,
                "cabin_class": "Economy",
                "price": 1189.00,
                "currency": "CAD"
            },
            {
                "airline": "United Airlines",
                "flight_number": "UA 789",
                "origin": "YYZ",
                "destination": "NRT",
                "departure": "2025-02-15 16:45",
                "arrival": "2025-02-16 21:00",
                "duration": "13h 15m",
                "stops": 0,
                "cabin_class": "Business",
                "price": 4299.00,
                "currency": "CAD"
            }
        ]

    @staticmethod
    def get_summary_for_query(query: str) -> str:
        """Get contextual summary based on query."""
        query_lower = query.lower()

        # Banking queries
        if any(word in query_lower for word in ["balance", "account", "bank", "money"]):
            accounts = DemoDataService.get_demo_bank_accounts()
            total_cad = sum(a["balance"] for a in accounts if a["currency"] == "CAD")
            total_usd = sum(a["balance"] for a in accounts if a["currency"] == "USD")
            total_kes = sum(a["balance"] for a in accounts if a["currency"] == "KES")

            return f"""
**Account Summary:**

**Canada (CAD):**
- TD Business Checking: ${accounts[0]['balance']:,.2f}
- TD High Interest Savings: ${accounts[1]['balance']:,.2f}
- **Total CAD:** ${total_cad:,.2f}

**United States (USD):**
- Chase Business Checking: ${accounts[2]['balance']:,.2f}
- Chase Savings Plus: ${accounts[3]['balance']:,.2f}
- **Total USD:** ${total_usd:,.2f}

**Kenya (KES):**
- KCB Current Account: {accounts[4]['balance']:,.0f} KES
- KCB Savings Account: {accounts[5]['balance']:,.0f} KES
- **Total KES:** {total_kes:,.0f} KES

**Combined Total:** ~$375,000 CAD equivalent

All accounts are active and in good standing! 💰
"""

        # Stock queries
        elif any(word in query_lower for word in ["stock", "portfolio", "shares", "invest"]):
            portfolio = DemoDataService.get_demo_stock_portfolio()

            return f"""
**Portfolio Performance:**

**Total Value:** ${portfolio['total_value']:,.2f}
**Total Cost:** ${portfolio['total_cost_basis']:,.2f}
**Total Gain/Loss:** ${portfolio['total_gain_loss']:,.2f} ({portfolio['total_gain_loss_percent']:.2f}%)
**Today's Change:** ${portfolio['day_change']:,.2f} ({portfolio['day_change_percent']:.2f}%)

**Top Holdings:**
1. **MSFT** - Microsoft: ${portfolio['holdings'][1]['market_value']:,.2f} (+18.22%)
2. **NVDA** - NVIDIA: ${portfolio['holdings'][5]['market_value']:,.2f} (+17.91%)
3. **AAPL** - Apple: ${portfolio['holdings'][0]['market_value']:,.2f} (+20.73%)
4. **JPM** - JPMorgan: ${portfolio['holdings'][4]['market_value']:,.2f} (+15.44%)

**Sector Allocation:**
- Technology: 72.5%
- Financial: 14.2%
- Automotive: 8.7%

Your portfolio is performing well with strong tech exposure! 📈
"""

        # Transaction queries
        elif any(word in query_lower for word in ["transaction", "spending", "expense"]):
            transactions = DemoDataService.get_demo_transactions(7)
            total_in = sum(t["amount"] for t in transactions if t["amount"] > 0)
            total_out = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))

            return f"""
**Recent Transactions (Last 7 Days):**

**Revenue:**
- Client Payments: ${total_in:,.2f}

**Expenses:**
- Operating: ${total_out * 0.45:,.2f}
- Technology: ${total_out * 0.25:,.2f}
- Professional Services: ${total_out * 0.20:,.2f}
- Other: ${total_out * 0.10:,.2f}

**Net Cash Flow:** ${total_in - total_out:,.2f}

Last 5 transactions:
{chr(10).join([f"- {t['date']}: {t['merchant']} - ${abs(t['amount']):.2f}" for t in transactions[:5]])}
"""

        # Travel queries
        elif any(word in query_lower for word in ["flight", "travel", "trip", "tokyo"]):
            flights = DemoDataService.get_demo_flights()

            return f"""
**Flight Options to Tokyo:**

**Best Value:**
✈️ Japan Airlines JL 002
- Departure: Feb 15, 2:20 PM
- Arrival: Feb 16, 6:35 PM
- Duration: 13h 15m (Non-stop)
- Price: $1,189 CAD

**Other Options:**
✈️ Air Canada AC 001 - $1,245 CAD
✈️ United Business Class - $4,299 CAD

**Booking Tips:**
- Book 3-4 months in advance for best prices
- Tuesday/Wednesday departures are cheaper
- Consider April/May or September for lower fares
"""

        return ""


# Global instance
demo_data_service = DemoDataService()
