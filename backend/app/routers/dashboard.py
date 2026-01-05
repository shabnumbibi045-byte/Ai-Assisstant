"""Dashboard Router - Comprehensive analytics and demo statistics."""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import get_current_active_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ============================================
# SCHEMAS
# ============================================

class SystemStatus(BaseModel):
    """System health and status."""
    status: str
    uptime_hours: float
    api_version: str
    total_users: int
    active_sessions: int
    requests_last_hour: int
    avg_response_time_ms: float


class UserStats(BaseModel):
    """User activity statistics."""
    total_api_calls: int
    total_ai_queries: int
    banking_transactions: int
    stock_trades: int
    travel_bookings: int
    research_queries: int
    favorite_feature: str
    account_age_days: int


class FeatureUsage(BaseModel):
    """Feature usage analytics."""
    feature_name: str
    usage_count: int
    last_used: datetime
    avg_rating: float


class DashboardSummary(BaseModel):
    """Complete dashboard summary for demo."""
    user_stats: UserStats
    feature_usage: List[FeatureUsage]
    recent_activity: List[Dict[str, Any]]
    ai_insights: List[str]
    quick_actions: List[Dict[str, str]]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive system status and health metrics.
    Perfect for monitoring and demos.
    """
    return SystemStatus(
        status="healthy",
        uptime_hours=245.5,
        api_version="1.0.0",
        total_users=1_247,
        active_sessions=156,
        requests_last_hour=8_934,
        avg_response_time_ms=125.3
    )


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive dashboard summary.
    Perfect for main dashboard view in demo.
    """
    try:
        summary = DashboardSummary(
            user_stats=UserStats(
                total_api_calls=1_243,
                total_ai_queries=456,
                banking_transactions=89,
                stock_trades=34,
                travel_bookings=12,
                research_queries=67,
                favorite_feature="AI Chat Assistant",
                account_age_days=45
            ),
            feature_usage=[
                FeatureUsage(
                    feature_name="AI Chat",
                    usage_count=456,
                    last_used=datetime.now() - timedelta(hours=2),
                    avg_rating=4.8
                ),
                FeatureUsage(
                    feature_name="Banking Dashboard",
                    usage_count=234,
                    last_used=datetime.now() - timedelta(hours=5),
                    avg_rating=4.9
                ),
                FeatureUsage(
                    feature_name="Stock Portfolio",
                    usage_count=189,
                    last_used=datetime.now() - timedelta(hours=3),
                    avg_rating=4.7
                ),
                FeatureUsage(
                    feature_name="Travel Search",
                    usage_count=145,
                    last_used=datetime.now() - timedelta(days=2),
                    avg_rating=4.6
                ),
                FeatureUsage(
                    feature_name="Legal Research",
                    usage_count=123,
                    last_used=datetime.now() - timedelta(days=1),
                    avg_rating=4.8
                ),
            ],
            recent_activity=[
                {
                    "type": "banking",
                    "action": "Viewed account summary",
                    "timestamp": datetime.now() - timedelta(hours=2),
                    "details": "Checked balances across 6 accounts"
                },
                {
                    "type": "stocks",
                    "action": "Portfolio analysis",
                    "timestamp": datetime.now() - timedelta(hours=3),
                    "details": "AI analyzed portfolio performance"
                },
                {
                    "type": "chat",
                    "action": "AI conversation",
                    "timestamp": datetime.now() - timedelta(hours=5),
                    "details": "Discussed investment strategies"
                },
                {
                    "type": "travel",
                    "action": "Flight search",
                    "timestamp": datetime.now() - timedelta(days=1),
                    "details": "Searched flights to Barcelona"
                },
                {
                    "type": "research",
                    "action": "Legal query",
                    "timestamp": datetime.now() - timedelta(days=1),
                    "details": "Researched corporate governance"
                },
            ],
            ai_insights=[
                "Your portfolio has outperformed the market by 12.3% this quarter",
                "Consider diversifying into emerging markets for better risk-adjusted returns",
                "You have $4,500 in pending transactions across your Canadian accounts",
                "Flight prices to your saved destinations have dropped by an average of 15%",
                "Your monthly expenses are 8% lower than the previous quarter"
            ],
            quick_actions=[
                {
                    "title": "Review Portfolio",
                    "description": "Check today's market performance",
                    "link": "/stocks/portfolio",
                    "icon": "chart"
                },
                {
                    "title": "Transfer Funds",
                    "description": "Move money between accounts",
                    "link": "/banking/transfer",
                    "icon": "exchange"
                },
                {
                    "title": "Book Travel",
                    "description": "Search flights and hotels",
                    "link": "/travel/search",
                    "icon": "plane"
                },
                {
                    "title": "Ask AI",
                    "description": "Get personalized advice",
                    "link": "/chat",
                    "icon": "chat"
                },
            ]
        )

        logger.info(f"Generated dashboard summary for user {current_user.email}")
        return summary

    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        raise


@router.get("/metrics")
async def get_detailed_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed analytics metrics.
    For comprehensive reporting and insights.
    """
    return {
        "performance": {
            "api_latency_p50": 85.2,
            "api_latency_p95": 245.8,
            "api_latency_p99": 456.3,
            "success_rate": 99.7,
            "error_rate": 0.3,
        },
        "user_engagement": {
            "daily_active_users": 842,
            "weekly_active_users": 1_156,
            "monthly_active_users": 1_247,
            "avg_session_duration_min": 12.5,
            "avg_actions_per_session": 8.3,
        },
        "feature_popularity": {
            "ai_chat": 38.2,
            "banking": 24.5,
            "stocks": 18.7,
            "travel": 12.3,
            "research": 6.3,
        },
        "revenue_metrics": {
            "total_transactions": 15_678,
            "transaction_volume_usd": 2_456_789.50,
            "avg_transaction_size": 156.78,
        },
        "ai_performance": {
            "total_queries": 45_678,
            "avg_response_time_ms": 1_234.5,
            "satisfaction_rate": 94.2,
            "queries_by_category": {
                "financial_advice": 35.2,
                "legal_research": 22.1,
                "travel_planning": 18.3,
                "general_queries": 24.4,
            }
        }
    }


@router.get("/capabilities")
async def get_ai_capabilities():
    """
    Get comprehensive list of AI capabilities.
    Perfect for showcasing features in demo.
    """
    return {
        "categories": [
            {
                "name": "Multi-Country Banking",
                "icon": "bank",
                "features": [
                    "Real-time account balances across Canada, US, and Kenya",
                    "Multi-currency support (CAD, USD, KES)",
                    "Transaction categorization and analytics",
                    "Spending insights and budgeting",
                    "Inter-account transfers with exchange rates",
                    "AI-powered financial advice"
                ],
                "demo_endpoint": "/api/v1/banking/summary"
            },
            {
                "name": "Stock Portfolio Management",
                "icon": "trending-up",
                "features": [
                    "Real-time portfolio tracking",
                    "AI-powered stock analysis and recommendations",
                    "Market news with sentiment analysis",
                    "Sector allocation insights",
                    "Performance analytics and benchmarking",
                    "Trade execution (market and limit orders)"
                ],
                "demo_endpoint": "/api/v1/stocks/portfolio"
            },
            {
                "name": "Intelligent Travel Search",
                "icon": "plane",
                "features": [
                    "Flight and hotel search across multiple providers",
                    "Price monitoring and alerts",
                    "AI-powered destination recommendations",
                    "Booking management",
                    "Travel insights and suggestions",
                    "VIP benefits integration"
                ],
                "demo_endpoint": "/api/v1/travel/recommendations"
            },
            {
                "name": "Legal Research (CA & US)",
                "icon": "book",
                "features": [
                    "Case law search with semantic understanding",
                    "Statute and regulation database",
                    "AI-powered legal analysis",
                    "Jurisdiction-specific compliance checks",
                    "Citation tracking and relevance scoring",
                    "Multi-jurisdictional support"
                ],
                "demo_endpoint": "/api/v1/research/search/cases"
            },
            {
                "name": "AI Chat Assistant",
                "icon": "message-circle",
                "features": [
                    "Natural language understanding",
                    "Context-aware responses",
                    "Multi-turn conversations",
                    "Tool integration (33+ tools)",
                    "Memory and personalization",
                    "Voice command support"
                ],
                "demo_endpoint": "/api/v1/chat/"
            }
        ],
        "ai_models": [
            "GPT-4o-mini for chat and analysis",
            "Custom embedding models for semantic search",
            "Sentiment analysis for market news",
            "Financial forecasting models"
        ],
        "integrations": [
            "Plaid for banking connectivity",
            "Real-time stock market data",
            "Travel booking APIs",
            "Legal databases (Canada & US)",
            "Voice recognition and synthesis"
        ]
    }


@router.get("/demo-scenarios")
async def get_demo_scenarios():
    """
    Get suggested demo scenarios to showcase the platform.
    Perfect for client presentations.
    """
    return {
        "scenarios": [
            {
                "title": "Multi-Country Business Owner",
                "description": "Manage finances across Canada, US, and Kenya",
                "steps": [
                    "View consolidated banking dashboard",
                    "Check account balances in multiple currencies",
                    "Analyze spending patterns across countries",
                    "Execute international transfer",
                    "Get AI insights on cash flow optimization"
                ],
                "estimated_duration": "5 minutes"
            },
            {
                "title": "Investment Portfolio Analysis",
                "description": "AI-powered stock analysis and trading",
                "steps": [
                    "Review portfolio performance and allocation",
                    "Get AI analysis for specific stocks",
                    "Check market news with sentiment analysis",
                    "View personalized recommendations",
                    "Execute a demo trade"
                ],
                "estimated_duration": "4 minutes"
            },
            {
                "title": "Business Travel Planning",
                "description": "Search and book travel with price monitoring",
                "steps": [
                    "Search flights with AI recommendations",
                    "Compare hotel options with ratings",
                    "Set up price alerts",
                    "Get destination insights",
                    "Book travel and manage itinerary"
                ],
                "estimated_duration": "6 minutes"
            },
            {
                "title": "Legal Compliance Check",
                "description": "Research corporate obligations and compliance",
                "steps": [
                    "Search relevant case law",
                    "Review applicable statutes",
                    "Get AI legal analysis",
                    "Check compliance requirements",
                    "Generate compliance report"
                ],
                "estimated_duration": "5 minutes"
            },
            {
                "title": "AI-Powered Decision Making",
                "description": "Conversational AI for complex queries",
                "steps": [
                    "Ask complex financial question",
                    "Get data from multiple sources",
                    "Receive AI analysis with citations",
                    "Follow-up questions for clarification",
                    "Get actionable recommendations"
                ],
                "estimated_duration": "3 minutes"
            }
        ]
    }
