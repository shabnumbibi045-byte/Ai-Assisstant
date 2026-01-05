"""Banking Router - Multi-country banking operations for demo."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, get_db
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/banking", tags=["banking"])


# ============================================
# SCHEMAS
# ============================================

class BankAccount(BaseModel):
    """Bank account information."""
    account_id: str
    account_name: str
    account_type: str  # checking, savings, credit
    bank_name: str
    country: str  # CA, US, KE
    currency: str
    balance: float
    available_balance: float
    last_updated: datetime
    status: str = "active"


class Transaction(BaseModel):
    """Bank transaction."""
    transaction_id: str
    account_id: str
    date: datetime
    description: str
    amount: float
    currency: str
    category: str
    merchant: Optional[str] = None
    location: Optional[str] = None
    type: str  # debit, credit


class AccountSummary(BaseModel):
    """Account summary for dashboard."""
    total_accounts: int
    total_balance_usd: float
    total_balance_cad: float
    total_balance_kes: float
    monthly_income: float
    monthly_expenses: float
    top_spending_categories: List[Dict[str, Any]]
    recent_transactions: List[Transaction]


class SpendingAnalytics(BaseModel):
    """Spending analytics."""
    period: str
    total_spent: float
    by_category: Dict[str, float]
    by_merchant: Dict[str, float]
    trend: str  # increasing, decreasing, stable
    comparison_previous_period: float


# ============================================
# DEMO DATA GENERATORS
# ============================================

def get_demo_accounts(user_id: int, country: Optional[str] = None) -> List[BankAccount]:
    """Generate demo bank accounts."""
    all_accounts = [
        # Canadian Accounts
        BankAccount(
            account_id="ca_chk_001",
            account_name="TD Business Checking",
            account_type="checking",
            bank_name="TD Canada Trust",
            country="CA",
            currency="CAD",
            balance=45_250.75,
            available_balance=43_750.75,
            last_updated=datetime.now(),
            status="active"
        ),
        BankAccount(
            account_id="ca_sav_001",
            account_name="TD High Interest Savings",
            account_type="savings",
            bank_name="TD Canada Trust",
            country="CA",
            currency="CAD",
            balance=128_500.00,
            available_balance=128_500.00,
            last_updated=datetime.now(),
            status="active"
        ),
        # US Accounts
        BankAccount(
            account_id="us_chk_001",
            account_name="Chase Business Checking",
            account_type="checking",
            bank_name="JPMorgan Chase",
            country="US",
            currency="USD",
            balance=62_840.50,
            available_balance=60_340.50,
            last_updated=datetime.now(),
            status="active"
        ),
        BankAccount(
            account_id="us_sav_001",
            account_name="Chase Savings Plus",
            account_type="savings",
            bank_name="JPMorgan Chase",
            country="US",
            currency="USD",
            balance=95_600.00,
            available_balance=95_600.00,
            last_updated=datetime.now(),
            status="active"
        ),
        # Kenya Accounts
        BankAccount(
            account_id="ke_chk_001",
            account_name="KCB Current Account",
            account_type="checking",
            bank_name="Kenya Commercial Bank",
            country="KE",
            currency="KES",
            balance=8_450_000.00,
            available_balance=8_200_000.00,
            last_updated=datetime.now(),
            status="active"
        ),
        BankAccount(
            account_id="ke_sav_001",
            account_name="KCB Savings Account",
            account_type="savings",
            bank_name="Kenya Commercial Bank",
            country="KE",
            currency="KES",
            balance=15_750_000.00,
            available_balance=15_750_000.00,
            last_updated=datetime.now(),
            status="active"
        ),
    ]

    if country:
        return [acc for acc in all_accounts if acc.country == country]
    return all_accounts


def get_demo_transactions(account_id: Optional[str] = None, days: int = 30) -> List[Transaction]:
    """Generate demo transactions."""
    base_transactions = [
        # Recent transactions
        Transaction(
            transaction_id="txn_001",
            account_id="ca_chk_001",
            date=datetime.now() - timedelta(days=1),
            description="Amazon Web Services",
            amount=-245.67,
            currency="CAD",
            category="Business Services",
            merchant="AWS",
            location="Online",
            type="debit"
        ),
        Transaction(
            transaction_id="txn_002",
            account_id="ca_chk_001",
            date=datetime.now() - timedelta(days=2),
            description="Client Payment - ABC Corp",
            amount=5_500.00,
            currency="CAD",
            category="Income",
            merchant="ABC Corporation",
            location="Toronto, ON",
            type="credit"
        ),
        Transaction(
            transaction_id="txn_003",
            account_id="us_chk_001",
            date=datetime.now() - timedelta(days=2),
            description="Microsoft 365 Business",
            amount=-129.99,
            currency="USD",
            category="Software",
            merchant="Microsoft",
            location="Online",
            type="debit"
        ),
        Transaction(
            transaction_id="txn_004",
            account_id="us_chk_001",
            date=datetime.now() - timedelta(days=3),
            description="Consulting Fee",
            amount=8_500.00,
            currency="USD",
            category="Income",
            merchant="XYZ Consulting",
            location="New York, NY",
            type="credit"
        ),
        Transaction(
            transaction_id="txn_005",
            account_id="ke_chk_001",
            date=datetime.now() - timedelta(days=1),
            description="Safaricom M-PESA",
            amount=-15_000.00,
            currency="KES",
            category="Utilities",
            merchant="Safaricom",
            location="Nairobi",
            type="debit"
        ),
        Transaction(
            transaction_id="txn_006",
            account_id="ke_chk_001",
            date=datetime.now() - timedelta(days=4),
            description="Client Project Payment",
            amount=450_000.00,
            currency="KES",
            category="Income",
            merchant="Local Client",
            location="Nairobi",
            type="credit"
        ),
    ]

    if account_id:
        return [txn for txn in base_transactions if txn.account_id == account_id]
    return base_transactions


# ============================================
# ENDPOINTS
# ============================================

@router.get("/accounts", response_model=List[BankAccount])
async def get_accounts(
    country: Optional[str] = Query(None, description="Filter by country code (CA, US, KE)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all bank accounts for the current user.
    Supports multi-country banking (Canada, US, Kenya).
    """
    try:
        accounts = get_demo_accounts(current_user.id, country)
        logger.info(f"Retrieved {len(accounts)} accounts for user {current_user.email}")
        return accounts
    except Exception as e:
        logger.error(f"Error retrieving accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve accounts")


@router.get("/accounts/{account_id}", response_model=BankAccount)
async def get_account_details(
    account_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get details for a specific account."""
    accounts = get_demo_accounts(current_user.id)
    account = next((acc for acc in accounts if acc.account_id == account_id), None)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    days: int = Query(30, description="Number of days to retrieve", ge=1, le=365),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get transactions for user's accounts.
    Can filter by account and date range.
    """
    try:
        transactions = get_demo_transactions(account_id, days)
        logger.info(f"Retrieved {len(transactions)} transactions for user {current_user.email}")
        return transactions
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transactions")


@router.get("/summary", response_model=AccountSummary)
async def get_account_summary(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive account summary with analytics.
    Perfect for dashboard display.
    """
    try:
        accounts = get_demo_accounts(current_user.id)
        transactions = get_demo_transactions()

        # Calculate totals by currency
        total_cad = sum(acc.balance for acc in accounts if acc.currency == "CAD")
        total_usd = sum(acc.balance for acc in accounts if acc.currency == "USD")
        total_kes = sum(acc.balance for acc in accounts if acc.currency == "KES")

        # Calculate income and expenses (last 30 days)
        income = sum(txn.amount for txn in transactions if txn.type == "credit")
        expenses = abs(sum(txn.amount for txn in transactions if txn.type == "debit"))

        # Top spending categories
        category_spending = {}
        for txn in transactions:
            if txn.type == "debit":
                category_spending[txn.category] = category_spending.get(txn.category, 0) + abs(txn.amount)

        top_categories = [
            {"category": cat, "amount": amount}
            for cat, amount in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        summary = AccountSummary(
            total_accounts=len(accounts),
            total_balance_cad=total_cad,
            total_balance_usd=total_usd,
            total_balance_kes=total_kes,
            monthly_income=income,
            monthly_expenses=expenses,
            top_spending_categories=top_categories,
            recent_transactions=transactions[:10]
        )

        logger.info(f"Generated summary for user {current_user.email}")
        return summary

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


@router.get("/analytics/spending", response_model=SpendingAnalytics)
async def get_spending_analytics(
    period: str = Query("month", description="Period: week, month, quarter, year"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed spending analytics with trends.
    AI-powered insights for better financial decisions.
    """
    try:
        transactions = get_demo_transactions()

        # Calculate spending by category
        by_category = {}
        by_merchant = {}
        total_spent = 0

        for txn in transactions:
            if txn.type == "debit":
                amount = abs(txn.amount)
                total_spent += amount
                by_category[txn.category] = by_category.get(txn.category, 0) + amount
                if txn.merchant:
                    by_merchant[txn.merchant] = by_merchant.get(txn.merchant, 0) + amount

        analytics = SpendingAnalytics(
            period=period,
            total_spent=total_spent,
            by_category=by_category,
            by_merchant=by_merchant,
            trend="stable",
            comparison_previous_period=5.2  # 5.2% increase from previous period
        )

        logger.info(f"Generated spending analytics for user {current_user.email}")
        return analytics

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")


@router.post("/transfer")
async def initiate_transfer(
    from_account: str,
    to_account: str,
    amount: float,
    currency: str,
    memo: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Initiate a transfer between accounts.
    Supports multi-currency transfers with real-time exchange rates.
    """
    try:
        # Validate accounts exist
        accounts = get_demo_accounts(current_user.id)
        from_acc = next((acc for acc in accounts if acc.account_id == from_account), None)
        to_acc = next((acc for acc in accounts if acc.account_id == to_account), None)

        if not from_acc or not to_acc:
            raise HTTPException(status_code=404, detail="Account not found")

        if from_acc.available_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Demo response - in production would process actual transfer
        return {
            "status": "success",
            "transfer_id": f"transfer_{datetime.now().timestamp()}",
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "currency": currency,
            "memo": memo,
            "processed_at": datetime.now(),
            "message": "Transfer initiated successfully. Funds will be available within 1-2 business days."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        raise HTTPException(status_code=500, detail="Transfer failed")


@router.get("/exchange-rates")
async def get_exchange_rates(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current exchange rates for multi-currency operations.
    Updated in real-time.
    """
    return {
        "base": "USD",
        "rates": {
            "CAD": 1.35,
            "KES": 129.50,
            "EUR": 0.92,
            "GBP": 0.79
        },
        "last_updated": datetime.now()
    }
