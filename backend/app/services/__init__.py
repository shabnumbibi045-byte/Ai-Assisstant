"""Services Module - All external API integrations.

Banking:
- PlaidService: US/Canada banking via Plaid
- RegionalBankingService: UAE (Lean) and Africa (Mono) banking
- BrokerageService: Investment accounts (Plaid, Schwab, IBKR)

Travel:
- AmadeusService: Flights, hotels, car rentals

Stock Data:
- AlphaVantageService: Real-time stock quotes

Voice:
- RealtimeVoiceService: OpenAI Realtime API + ElevenLabs TTS

Research:
- CourtlistenerService: US legal research
"""

from .chat_service import ChatService
from .plaid_service import PlaidService, plaid_service
from .regional_banking_service import (
    RegionalBankingService,
    LeanService,
    MonoService,
    regional_banking_service
)
from .brokerage_service import (
    BrokerageService,
    PlaidInvestmentsService,
    SchwabService,
    IBKRService,
    brokerage_service
)
from .amadeus_service import AmadeusService, amadeus_service
from .alpha_vantage_service import AlphaVantageService
from .realtime_voice_service import (
    RealtimeVoiceService,
    RealtimeSession,
    realtime_voice_service
)
from .courtlistener_service import CourtListenerService

__all__ = [
    # Chat
    "ChatService",
    # Banking - North America
    "PlaidService",
    "plaid_service",
    # Banking - Regional (UAE, Africa)
    "RegionalBankingService",
    "LeanService", 
    "MonoService",
    "regional_banking_service",
    # Brokerage
    "BrokerageService",
    "PlaidInvestmentsService",
    "SchwabService",
    "IBKRService",
    "brokerage_service",
    # Travel
    "AmadeusService",
    "amadeus_service",
    # Stocks
    "AlphaVantageService",
    # Voice
    "RealtimeVoiceService",
    "RealtimeSession",
    "realtime_voice_service",
    # Research
    "CourtListenerService",
]
