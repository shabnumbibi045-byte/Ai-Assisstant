"""Stocks Router - Portfolio management and market analysis for demo."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.auth.dependencies import get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stocks", tags=["stocks"])


# ============================================
# SCHEMAS
# ============================================

class StockHolding(BaseModel):
    """Stock holding in portfolio."""
    symbol: str
    company_name: str
    quantity: float
    average_cost: float
    current_price: float
    market_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    day_change: float
    day_change_percent: float
    sector: str
    exchange: str


class StockQuote(BaseModel):
    """Real-time stock quote."""
    symbol: str
    company_name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    high_52week: float
    low_52week: float
    last_updated: datetime


class PortfolioSummary(BaseModel):
    """Portfolio summary."""
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    day_change: float
    day_change_percent: float
    holdings_count: int
    top_performers: List[StockHolding]
    worst_performers: List[StockHolding]
    sector_allocation: Dict[str, float]


class MarketNews(BaseModel):
    """Market news article."""
    title: str
    summary: str
    source: str
    published_at: datetime
    url: str
    sentiment: str  # positive, negative, neutral
    related_symbols: List[str]


class StockAnalysis(BaseModel):
    """AI-powered stock analysis."""
    symbol: str
    recommendation: str  # buy, sell, hold
    confidence: float  # 0-100
    target_price: float
    analysis: str
    key_metrics: Dict[str, Any]
    risks: List[str]
    opportunities: List[str]


# ============================================
# DEMO DATA GENERATORS
# ============================================

def get_demo_holdings(user_id: int) -> List[StockHolding]:
    """Generate demo stock holdings."""
    return [
        StockHolding(
            symbol="AAPL",
            company_name="Apple Inc.",
            quantity=150,
            average_cost=145.50,
            current_price=178.25,
            market_value=26_737.50,
            total_gain_loss=4_912.50,
            total_gain_loss_percent=22.52,
            day_change=2.45,
            day_change_percent=1.39,
            sector="Technology",
            exchange="NASDAQ"
        ),
        StockHolding(
            symbol="MSFT",
            company_name="Microsoft Corporation",
            quantity=100,
            average_cost=320.00,
            current_price=368.50,
            market_value=36_850.00,
            total_gain_loss=4_850.00,
            total_gain_loss_percent=15.16,
            day_change=5.20,
            day_change_percent=1.43,
            sector="Technology",
            exchange="NASDAQ"
        ),
        StockHolding(
            symbol="GOOGL",
            company_name="Alphabet Inc.",
            quantity=80,
            average_cost=125.00,
            current_price=140.75,
            market_value=11_260.00,
            total_gain_loss=1_260.00,
            total_gain_loss_percent=12.60,
            day_change=-0.85,
            day_change_percent=-0.60,
            sector="Technology",
            exchange="NASDAQ"
        ),
        StockHolding(
            symbol="TSLA",
            company_name="Tesla, Inc.",
            quantity=50,
            average_cost=215.00,
            current_price=242.80,
            market_value=12_140.00,
            total_gain_loss=1_390.00,
            total_gain_loss_percent=12.93,
            day_change=8.50,
            day_change_percent=3.63,
            sector="Automotive",
            exchange="NASDAQ"
        ),
        StockHolding(
            symbol="JPM",
            company_name="JPMorgan Chase & Co.",
            quantity=200,
            average_cost=140.00,
            current_price=152.30,
            market_value=30_460.00,
            total_gain_loss=2_460.00,
            total_gain_loss_percent=8.79,
            day_change=1.20,
            day_change_percent=0.79,
            sector="Financial",
            exchange="NYSE"
        ),
        StockHolding(
            symbol="NVDA",
            company_name="NVIDIA Corporation",
            quantity=60,
            average_cost=420.00,
            current_price=495.20,
            market_value=29_712.00,
            total_gain_loss=4_512.00,
            total_gain_loss_percent=17.90,
            day_change=12.50,
            day_change_percent=2.59,
            sector="Technology",
            exchange="NASDAQ"
        ),
    ]


def get_demo_market_news() -> List[MarketNews]:
    """Generate demo market news."""
    return [
        MarketNews(
            title="Tech Stocks Rally as AI Sector Shows Strong Growth",
            summary="Major technology stocks surged today driven by optimism around AI developments and strong earnings reports from leading companies.",
            source="Financial Times",
            published_at=datetime.now() - timedelta(hours=2),
            url="https://example.com/news/1",
            sentiment="positive",
            related_symbols=["AAPL", "MSFT", "NVDA", "GOOGL"]
        ),
        MarketNews(
            title="Federal Reserve Maintains Interest Rates",
            summary="The Federal Reserve announced it will keep interest rates unchanged, citing stable inflation and economic growth.",
            source="Bloomberg",
            published_at=datetime.now() - timedelta(hours=5),
            url="https://example.com/news/2",
            sentiment="neutral",
            related_symbols=["JPM", "BAC", "GS"]
        ),
        MarketNews(
            title="Tesla Announces Record Deliveries for Q4",
            summary="Tesla reported record vehicle deliveries exceeding analyst expectations, pushing stock prices higher in after-hours trading.",
            source="Reuters",
            published_at=datetime.now() - timedelta(hours=8),
            url="https://example.com/news/3",
            sentiment="positive",
            related_symbols=["TSLA"]
        ),
    ]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive portfolio summary with analytics.
    Perfect for dashboard display.
    """
    try:
        holdings = get_demo_holdings(current_user.id)

        # Calculate totals
        total_value = sum(h.market_value for h in holdings)
        total_gain_loss = sum(h.total_gain_loss for h in holdings)
        total_gain_loss_percent = (total_gain_loss / (total_value - total_gain_loss)) * 100
        day_change = sum(h.day_change * h.quantity for h in holdings)
        day_change_percent = (day_change / total_value) * 100

        # Sort for top/worst performers
        sorted_holdings = sorted(holdings, key=lambda x: x.total_gain_loss_percent, reverse=True)

        # Sector allocation
        sector_allocation = {}
        for holding in holdings:
            sector_allocation[holding.sector] = sector_allocation.get(holding.sector, 0) + holding.market_value

        summary = PortfolioSummary(
            total_value=total_value,
            total_gain_loss=total_gain_loss,
            total_gain_loss_percent=total_gain_loss_percent,
            day_change=day_change,
            day_change_percent=day_change_percent,
            holdings_count=len(holdings),
            top_performers=sorted_holdings[:3],
            worst_performers=sorted_holdings[-3:],
            sector_allocation=sector_allocation
        )

        logger.info(f"Retrieved portfolio for user {current_user.email}")
        return summary

    except Exception as e:
        logger.error(f"Error retrieving portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio")


@router.get("/holdings", response_model=List[StockHolding])
async def get_holdings(
    current_user: User = Depends(get_current_active_user)
):
    """Get all stock holdings in portfolio."""
    try:
        holdings = get_demo_holdings(current_user.id)
        logger.info(f"Retrieved {len(holdings)} holdings for user {current_user.email}")
        return holdings
    except Exception as e:
        logger.error(f"Error retrieving holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve holdings")


@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get real-time stock quote from Alpha Vantage.
    Supports all major US stock exchanges.
    """
    try:
        from app.services.alpha_vantage_service import alpha_vantage_service

        symbol = symbol.upper()
        logger.info(f"Fetching real-time quote for {symbol} from Alpha Vantage")

        # Fetch real-time quote data
        quote_data = await alpha_vantage_service.get_quote(symbol)

        if not quote_data:
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found or API error")

        # Fetch company overview for additional data (PE ratio, market cap, etc.)
        overview_data = await alpha_vantage_service.get_company_overview(symbol)

        # Build quote response
        quote = StockQuote(
            symbol=symbol,
            company_name=overview_data.get("name", symbol) if overview_data else symbol,
            price=quote_data["price"],
            change=quote_data["change"],
            change_percent=quote_data["change_percent"],
            volume=quote_data["volume"],
            market_cap=float(overview_data.get("market_cap", 0)) if overview_data and overview_data.get("market_cap") else 0,
            pe_ratio=float(overview_data.get("pe_ratio", 0)) if overview_data and overview_data.get("pe_ratio") else None,
            dividend_yield=float(overview_data.get("dividend_yield", 0)) if overview_data and overview_data.get("dividend_yield") else None,
            high_52week=float(overview_data.get("52_week_high", 0)) if overview_data and overview_data.get("52_week_high") else quote_data["high"],
            low_52week=float(overview_data.get("52_week_low", 0)) if overview_data and overview_data.get("52_week_low") else quote_data["low"],
            last_updated=datetime.now()
        )

        logger.info(f"Retrieved real-time quote for {symbol}: ${quote.price}")
        return quote

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quote: {str(e)}")


@router.get("/news", response_model=List[MarketNews])
async def get_market_news(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols to filter by"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get latest market news with AI sentiment analysis.
    Can filter by specific stock symbols.
    """
    try:
        news = get_demo_market_news()

        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            news = [n for n in news if any(sym in n.related_symbols for sym in symbol_list)]

        logger.info(f"Retrieved {len(news)} news articles for user {current_user.email}")
        return news[:limit]

    except Exception as e:
        logger.error(f"Error retrieving news: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve news")


@router.get("/analysis/{symbol}", response_model=StockAnalysis)
async def get_stock_analysis(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-powered stock analysis with recommendations.
    Uses advanced ML models for predictions.
    """
    try:
        symbol = symbol.upper()

        # Demo analysis - in production would use real AI/ML models
        analysis = StockAnalysis(
            symbol=symbol,
            recommendation="buy",
            confidence=78.5,
            target_price=195.00 if symbol == "AAPL" else 400.00,
            analysis=(
                f"{symbol} shows strong fundamentals with consistent revenue growth and "
                "expanding profit margins. The company's innovation in AI and cloud services "
                "positions it well for long-term growth. Recent market trends and technical "
                "indicators suggest continued upward momentum."
            ),
            key_metrics={
                "revenue_growth": "12.3%",
                "profit_margin": "25.8%",
                "debt_to_equity": "1.45",
                "return_on_equity": "45.2%",
                "price_to_earnings": "28.5"
            },
            risks=[
                "Market volatility and macroeconomic uncertainty",
                "Regulatory challenges in international markets",
                "Competition from emerging tech companies"
            ],
            opportunities=[
                "Expansion into AI and machine learning services",
                "Growing demand for cloud infrastructure",
                "Strategic partnerships and acquisitions"
            ]
        )

        logger.info(f"Generated analysis for {symbol}")
        return analysis

    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analysis")


@router.post("/trade")
async def execute_trade(
    symbol: str,
    action: str,  # buy or sell
    quantity: float,
    order_type: str = "market",  # market or limit
    limit_price: Optional[float] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute a stock trade.
    Supports market and limit orders.
    """
    try:
        if action not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Action must be 'buy' or 'sell'")

        if order_type == "limit" and not limit_price:
            raise HTTPException(status_code=400, detail="Limit price required for limit orders")

        # Demo response - in production would execute actual trade
        return {
            "status": "success",
            "order_id": f"order_{datetime.now().timestamp()}",
            "symbol": symbol.upper(),
            "action": action,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
            "executed_at": datetime.now(),
            "message": f"{action.capitalize()} order for {quantity} shares of {symbol.upper()} placed successfully."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed")


@router.get("/watchlist")
async def get_watchlist(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's stock watchlist."""
    return {
        "watchlist": [
            {"symbol": "AMZN", "company_name": "Amazon.com Inc.", "added_at": datetime.now() - timedelta(days=5)},
            {"symbol": "META", "company_name": "Meta Platforms Inc.", "added_at": datetime.now() - timedelta(days=12)},
            {"symbol": "NFLX", "company_name": "Netflix Inc.", "added_at": datetime.now() - timedelta(days=20)},
        ]
    }
