"""Configuration Management - Environment variables and settings."""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    APP_NAME: str = "Salim AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS Settings - Allow frontend origins
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default port
        "https://frontend-rho-six-34.vercel.app",  # Vercel deployment
        "https://*.vercel.app",  # All Vercel deployments
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database (SQLite for local dev, MySQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./salim_ai.db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # Set True if Redis is available
    
    # Qdrant (Vector DB)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "user_memories"
    QDRANT_VECTOR_SIZE: int = 1536  # OpenAI text-embedding-3-small
    QDRANT_ENABLED: bool = False  # Set True if Qdrant is available
    
    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Default LLM Settings
    DEFAULT_LLM_PROVIDER: str = "openai"  # openai, anthropic, gemini
    DEFAULT_CHAT_MODEL: str = "gpt-4-turbo-preview"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Memory Settings
    SHORT_TERM_MAX_MESSAGES: int = 50
    SHORT_TERM_TTL_HOURS: int = 24
    VECTOR_SEARCH_TOP_K: int = 5
    VECTOR_SCORE_THRESHOLD: float = 0.7
    
    # RAG Settings
    RAG_CHUNK_SIZE: int = 400
    RAG_CHUNK_OVERLAP: int = 80
    RAG_MIN_CHUNK_SIZE: int = 50
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # ===========================================
    # BANKING CONFIGURATION (Multi-Country)
    # ===========================================
    # Plaid API (Primary banking aggregator - supports US, Canada)
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"  # sandbox, development, production
    
    # Plaid Investments (Brokerage Integration - Schwab, Fidelity, etc.)
    PLAID_INVESTMENTS_ENABLED: bool = True
    
    # Lean Technologies (UAE/Middle East banking aggregator)
    # Covers: FAB Bank, RAK Bank, ENBD, ADCB, and more UAE/Saudi banks
    # Apply at: https://www.leantech.me/
    LEAN_APP_TOKEN: Optional[str] = None
    LEAN_APP_SECRET: Optional[str] = None
    LEAN_ENV: str = "sandbox"  # sandbox, production
    
    # Mono (Africa banking aggregator - Kenya, Nigeria, etc.)
    # Covers: I&M Bank, Equity Bank, KCB, and more African banks
    # Apply at: https://mono.co/
    MONO_SECRET_KEY: Optional[str] = None
    MONO_PUBLIC_KEY: Optional[str] = None
    MONO_WEBHOOK_SECRET: Optional[str] = None
    
    # Supported countries for banking
    BANKING_COUNTRIES: List[str] = ["CA", "US", "KE", "AE"]  # Canada, US, Kenya, UAE
    
    # Export Settings
    EXPORT_DIR: str = "./exports"
    EXCEL_TEMPLATE_DIR: str = "./templates"
    
    # Banking refresh schedule (cron format)
    DAILY_BALANCE_CHECK_HOUR: int = 6  # 6 AM daily check
    WEEKLY_TRANSACTION_EXPORT_DAY: int = 0  # Monday = 0
    
    # ===========================================
    # STOCK TRADING CONFIGURATION
    # ===========================================
    # Alpaca (Stock trading API)
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # paper trading
    
    # Charles Schwab Developer API (read-only portfolio access)
    # Apply at: https://developer.schwab.com/
    SCHWAB_CLIENT_ID: Optional[str] = None
    SCHWAB_CLIENT_SECRET: Optional[str] = None
    SCHWAB_REFRESH_TOKEN: Optional[str] = None
    SCHWAB_ACCOUNT_ID: Optional[str] = None
    
    # Interactive Brokers Client Portal API
    # Docs: https://www.interactivebrokers.com/api/doc.html
    IB_ACCOUNT_ID: Optional[str] = None
    IB_API_PORT: int = 7497
    IB_GATEWAY_HOST: str = "localhost"
    IB_CLIENT_ID: int = 1
    
    # Stock data providers
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    
    # ===========================================
    # TRAVEL CONFIGURATION
    # ===========================================
    # Amadeus API (Flights, Hotels)
    AMADEUS_API_KEY: Optional[str] = None
    AMADEUS_API_SECRET: Optional[str] = None
    AMADEUS_ENV: str = "test"  # test, production
    AMADEUS_TEST_MODE: bool = True  # Use test environment
    
    # Skyscanner API
    SKYSCANNER_API_KEY: Optional[str] = None
    
    # Priceline Partner API (VIP Platinum member features)
    PRICELINE_API_KEY: Optional[str] = None
    PRICELINE_MEMBER_ID: Optional[str] = None
    PRICELINE_MEMBERSHIP_TIER: str = "platinum"
    
    # Expedia Affiliate API
    EXPEDIA_API_KEY: Optional[str] = None
    EXPEDIA_SHARED_SECRET: Optional[str] = None
    
    # Car Rental APIs
    ENTERPRISE_API_KEY: Optional[str] = None
    HERTZ_API_KEY: Optional[str] = None
    
    # Travel monitoring settings
    TRAVEL_PRICE_CHECK_INTERVAL_MINUTES: int = 30
    TRAVEL_ALERT_PRICE_DROP_PERCENT: float = 5.0  # Alert if price drops 5%+
    
    # ===========================================
    # RESEARCH CONFIGURATION
    # ===========================================
    # Legal research APIs
    CANLII_API_KEY: Optional[str] = None  # Canadian legal research
    COURTLISTENER_API_TOKEN: Optional[str] = None  # US legal research (CourtListener API)
    WESTLAW_API_KEY: Optional[str] = None
    
    # General research
    SERPAPI_API_KEY: Optional[str] = None  # Google search API
    TAVILY_API_KEY: Optional[str] = None  # AI research API
    
    # Document storage
    DOCUMENTS_DIR: str = "./documents"
    MAX_DOCUMENT_SIZE_MB: int = 50
    
    # ===========================================
    # VOICE CONFIGURATION
    # ===========================================
    # OpenAI Realtime API (Recommended - handles both STT and TTS)
    # Single multimodal stream with low-latency, barge-in support
    # No separate STT service needed - processes audio directly
    OPENAI_REALTIME_ENABLED: bool = True
    OPENAI_REALTIME_MODEL: str = "gpt-4o-realtime-preview-2024-12-17"
    OPENAI_REALTIME_VOICE: str = "alloy"  # alloy, echo, shimmer, ash, ballad, coral, sage, verse
    
    # ElevenLabs (Alternative TTS - premium voice quality)
    # Pricing: https://elevenlabs.io/pricing
    # - Free: 10,000 chars/month
    # - Starter ($5/mo): 30,000 chars/month  
    # - Creator ($22/mo): 100,000 chars/month
    # - Pro ($99/mo): 500,000 chars/month
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    ELEVENLABS_MODEL_ID: str = "eleven_turbo_v2_5"
    
    # Speech-to-Text (Fallback when not using Realtime API)
    WHISPER_MODEL: str = "whisper-1"  # OpenAI Whisper
    DEEPGRAM_API_KEY: Optional[str] = None
    
    # Legacy TTS Voice ID
    TTS_VOICE_ID: str = "default"
    
    # ===========================================
    # NOTIFICATION SETTINGS
    # ===========================================
    # Email notifications
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    NOTIFICATION_EMAIL: Optional[str] = None
    
    # Accountant email for weekly reports
    ACCOUNTANT_EMAIL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
