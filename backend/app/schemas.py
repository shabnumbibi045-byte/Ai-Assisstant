"""Pydantic Schemas for API requests/responses.

Comprehensive schemas for:
- Banking (multi-country: Canada, US, Kenya)
- Stock trading
- Travel booking
- Research
- Voice commands
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class BankCountry(str, Enum):
    CANADA = "CA"
    USA = "US"
    KENYA = "KE"


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    BUSINESS = "business"


class TravelProvider(str, Enum):
    FARECOMPARE = "farecompare"
    EXPEDIA = "expedia"
    PRICELINE = "priceline"
    SKYSCANNER = "skyscanner"
    DIRECT = "direct"


class ResearchType(str, Enum):
    LEGAL_CANADA = "legal_canada"
    LEGAL_US = "legal_us"
    BUSINESS = "business"
    MARKET = "market"
    GENERAL = "general"


# ============================================
# CHAT SCHEMAS
# ============================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    module: Optional[str] = None  # banking, stocks, travel, research
    use_rag: bool = False
    use_tools: bool = True


class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    tool_calls: Optional[List[Dict]] = []
    sources: Optional[List[Dict]] = []
    session_id: str


# ============================================
# BANKING SCHEMAS
# ============================================

class BankAccountInfo(BaseModel):
    account_id: str
    institution: str
    country: BankCountry
    currency: str
    account_type: AccountType
    account_name: str
    last_four: str
    status: str


class BankBalance(BaseModel):
    account_id: str
    institution: str
    account_name: str
    country: BankCountry
    currency: str
    current_balance: float
    available_balance: float
    as_of: datetime


class BankTransaction(BaseModel):
    transaction_id: str
    account_id: str
    date: str
    merchant: str
    amount: float
    currency: str
    country: BankCountry
    category: str
    type: str  # debit, credit
    status: str


class GetBalanceRequest(BaseModel):
    user_id: str
    account_id: Optional[str] = None
    country: Optional[BankCountry] = None


class GetTransactionsRequest(BaseModel):
    user_id: str
    account_id: Optional[str] = None
    country: Optional[BankCountry] = None
    days: int = 7
    category: Optional[str] = None
    limit: int = 50


class ExportTransactionsRequest(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    country: Optional[BankCountry] = None
    format: str = "quickbooks"


class AccountantReportRequest(BaseModel):
    user_id: str
    week_ending: Optional[str] = None
    send_email: bool = False
    include_stocks: bool = False


# ============================================
# STOCK SCHEMAS
# ============================================

class StockHolding(BaseModel):
    symbol: str
    name: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    gain_loss: float
    gain_loss_percent: float
    account: str
    currency: str = "USD"


class StockTransaction(BaseModel):
    transaction_id: str
    date: str
    symbol: str
    type: str  # buy, sell, dividend
    quantity: int
    price: float
    amount: float
    fees: float
    account: str
    currency: str


class PortfolioSummary(BaseModel):
    total_value: float
    total_cost_basis: float
    total_gain_loss: float
    total_gain_loss_percent: float
    day_change: float
    day_change_percent: float
    holdings: List[StockHolding]


class GetPortfolioRequest(BaseModel):
    user_id: str
    account_id: Optional[str] = None


class GetStockQuoteRequest(BaseModel):
    symbol: str


class ExportPortfolioRequest(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    include_transactions: bool = True


# ============================================
# TRAVEL SCHEMAS
# ============================================

class FlightResult(BaseModel):
    provider: str
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration: str
    stops: int
    cabin_class: str
    price: float
    currency: str
    refundable: bool
    booking_link: str
    vip_discount: Optional[float] = None
    vip_benefits: Optional[List[str]] = None


class HotelResult(BaseModel):
    provider: str
    hotel_name: str
    star_rating: int
    location: str
    nightly_rate: float
    total_price: float
    currency: str
    room_type: str
    amenities: List[str]
    rating: float
    free_cancellation: bool
    vip_discount: Optional[float] = None


class CarRentalResult(BaseModel):
    provider: str
    car_type: str
    car_model: str
    daily_rate: float
    total_price: float
    currency: str
    features: List[str]
    mileage: str


class SearchFlightsRequest(BaseModel):
    user_id: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    cabin_class: str = "economy"
    providers: Optional[List[str]] = None


class SearchHotelsRequest(BaseModel):
    user_id: str
    location: str
    check_in: str
    check_out: str
    guests: int = 1
    rooms: int = 1
    star_rating: Optional[int] = None


class SearchCarRentalsRequest(BaseModel):
    user_id: str
    pickup_location: str
    pickup_date: str
    return_date: str
    car_type: Optional[str] = None


class SetPriceAlertRequest(BaseModel):
    user_id: str
    origin: str
    destination: str
    departure_date: str
    target_price: Optional[float] = None
    check_interval_minutes: int = 30


class CreateTripPlanRequest(BaseModel):
    user_id: str
    destination: str
    start_date: str
    end_date: str
    trip_name: Optional[str] = None
    include_car: bool = False


# ============================================
# RESEARCH SCHEMAS
# ============================================

class LegalSearchResult(BaseModel):
    type: str  # case, statute, regulation
    title: str
    citation: str
    court: Optional[str] = None
    date: Optional[str] = None
    jurisdiction: str
    summary: str
    relevance_score: float
    url: str


class ResearchProject(BaseModel):
    project_id: str
    name: str
    type: ResearchType
    description: str
    status: str
    document_count: int
    created_at: datetime
    updated_at: datetime


class ResearchDocument(BaseModel):
    document_id: str
    project_id: str
    name: str
    type: str
    folder: str
    size_kb: int
    version: int
    created_at: datetime
    updated_at: datetime


class SearchLegalRequest(BaseModel):
    user_id: str
    query: str
    jurisdiction: str = "federal"
    doc_type: Optional[str] = None
    country: str = "canada"  # canada, us


class CreateProjectRequest(BaseModel):
    user_id: str
    project_name: str
    project_type: ResearchType = ResearchType.GENERAL
    description: Optional[str] = None


class SaveDocumentRequest(BaseModel):
    user_id: str
    project_id: str
    document_name: str
    document_type: str = "other"
    content: Optional[str] = None
    folder: str = "drafts"


class ConductResearchRequest(BaseModel):
    user_id: str
    topic: str
    research_type: str = "general"
    depth: str = "standard"


class GenerateReportRequest(BaseModel):
    user_id: str
    project_id: str
    report_type: str = "summary"
    format: str = "pdf"


# ============================================
# VOICE SCHEMAS
# ============================================

class VoiceCommandRequest(BaseModel):
    user_id: str
    audio_url: Optional[str] = None
    text: Optional[str] = None


class VoiceCommandResponse(BaseModel):
    command_id: str
    transcription: Optional[str] = None
    intent: str
    intent_type: str
    parameters: Dict[str, Any]
    response_text: str
    audio_response_url: Optional[str] = None


# ============================================
# MEMORY SCHEMAS
# ============================================

class AddMemoryRequest(BaseModel):
    user_id: str
    key: str
    value: str
    category: str = "general"
    confidence: int = 100


class GetMemoryRequest(BaseModel):
    user_id: str
    category: Optional[str] = None


# ============================================
# RAG SCHEMAS
# ============================================

class RAGUploadRequest(BaseModel):
    user_id: str
    filename: str


class RAGQueryRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = 5


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    chunks_used: int


# ============================================
# TOOL SCHEMAS
# ============================================

class ToolInvokeRequest(BaseModel):
    user_id: str
    tool_name: str
    parameters: Dict[str, Any]


class ToolInvokeResponse(BaseModel):
    success: bool
    data: Any
    message: str
    error: Optional[str] = None
    requires_confirmation: bool = False


# ============================================
# SETUP SCHEMAS
# ============================================

class UserProfileRequest(BaseModel):
    user_id: str
    email: str
    full_name: str
    preferences: Optional[Dict] = {}


class ModuleSetupRequest(BaseModel):
    user_id: str
    modules: List[str]  # ["banking", "travel", "research", "stocks"]
    permissions: Dict[str, Dict[str, bool]]


class UserPreferences(BaseModel):
    user_id: str
    default_currency: str = "USD"
    default_language: str = "en"
    banking_countries: List[BankCountry] = [BankCountry.CANADA, BankCountry.USA, BankCountry.KENYA]
    priceline_vip_tier: str = "platinum"
    accountant_email: Optional[str] = None
    notification_preferences: Dict[str, bool] = {
        "email": True,
        "push": True,
        "price_alerts": True
    }
