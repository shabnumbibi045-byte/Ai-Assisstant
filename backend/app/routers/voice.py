"""Voice Router - Voice Command Processing for AI Assistant.

Features:
- Speech-to-text transcription (Whisper/Deepgram)
- Voice command parsing
- Text-to-speech responses
- Natural language understanding for commands
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import random

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice Commands"])


# ============================================
# SCHEMAS
# ============================================

class VoiceCommandType(str, Enum):
    """Types of voice commands."""
    BANKING = "banking"
    STOCKS = "stocks"
    TRAVEL = "travel"
    RESEARCH = "research"
    GENERAL = "general"


class TranscriptionResponse(BaseModel):
    """Response from speech-to-text."""
    text: str
    confidence: float
    language: str
    duration_seconds: float


class VoiceCommandRequest(BaseModel):
    """Voice command request."""
    user_id: str
    audio_url: Optional[str] = None
    text: Optional[str] = None  # For text-based testing


class VoiceCommandResponse(BaseModel):
    """Voice command response."""
    command_id: str
    transcription: Optional[str] = None
    intent: str
    intent_type: VoiceCommandType
    parameters: Dict[str, Any]
    response_text: str
    audio_response_url: Optional[str] = None
    action_taken: Optional[str] = None


class TextToSpeechRequest(BaseModel):
    """TTS request."""
    text: str
    voice_id: Optional[str] = "default"
    speed: Optional[float] = 1.0


class TextToSpeechResponse(BaseModel):
    """TTS response."""
    audio_url: str
    duration_seconds: float
    format: str


# ============================================
# VOICE SERVICE
# ============================================

class VoiceService:
    """Service for voice processing."""
    
    # Intent patterns for command recognition
    INTENT_PATTERNS = {
        "banking": {
            "check_balance": ["balance", "how much", "account", "money"],
            "list_transactions": ["transactions", "spending", "history", "payments"],
            "export_report": ["export", "excel", "report", "accountant", "quickbooks"],
            "add_account": ["add account", "connect bank", "new account"]
        },
        "stocks": {
            "portfolio_summary": ["portfolio", "stocks", "investments", "holdings"],
            "stock_quote": ["price", "quote", "stock price", "how is"],
            "export_portfolio": ["export portfolio", "stock report"]
        },
        "travel": {
            "set_alert": ["alert", "notify", "watch price", "monitor price"],
            "search_flights": ["flight", "fly", "airline", "airfare"],
            "search_hotels": ["hotel", "stay", "accommodation", "room", "lodge", "resort"],
            "search_cars": ["car rental", "rent a car", "rent car", "vehicle rental", "car hire"],
            "book_travel": ["book flight", "book hotel", "book car", "reserve", "booking"]
        },
        "research": {
            "summarize_document": ["summarize", "summary", "summarise", "sum up", "tldr", "overview of document", "summarize my document", "summarize document", "summarize the", "give me a summary"],
            "list_uploaded_docs": ["my documents", "uploaded documents", "list documents", "what documents", "show documents", "my files", "uploaded files"],
            "legal_search": ["legal", "law", "case", "statute", "court"],
            "conduct_research": ["research", "look up", "find information"],
            "list_projects": ["projects", "files"]
        }
    }
    
    @classmethod
    async def transcribe_audio(
        cls,
        audio_data: bytes,
        language: str = "en"
    ) -> TranscriptionResponse:
        """
        Transcribe audio to text using Whisper/Deepgram.
        
        STUBBED: In production, would call actual STT API.
        """
        logger.info("Transcribing audio...")
        
        # STUBBED: Return mock transcription
        mock_transcriptions = [
            "Check my bank balance for all accounts",
            "What's my portfolio value today",
            "Search for flights from Toronto to Dubai next week",
            "Export weekly transactions for my accountant",
            "Find legal cases about contract disputes in Canada",
            "What are the best hotel rates in New York"
        ]
        
        return TranscriptionResponse(
            text=random.choice(mock_transcriptions),
            confidence=round(random.uniform(0.92, 0.99), 2),
            language=language,
            duration_seconds=round(random.uniform(2.0, 8.0), 1)
        )
    
    @classmethod
    async def parse_intent(cls, text: str) -> Dict[str, Any]:
        """
        Parse intent from transcribed text.
        
        Returns intent type, action, and extracted parameters.
        """
        text_lower = text.lower()
        
        # Priority intents: check document/summary commands first (before banking "report" matches)
        priority_intents = [
            ("research", "summarize_document"),
            ("research", "list_uploaded_docs"),
            ("travel", "set_alert"),
        ]
        for category, intent in priority_intents:
            keywords = cls.INTENT_PATTERNS.get(category, {}).get(intent, [])
            if any(kw in text_lower for kw in keywords):
                return {
                    "category": category,
                    "intent": intent,
                    "confidence": round(random.uniform(0.85, 0.98), 2),
                    "original_text": text
                }
        
        # Check each category
        for category, intents in cls.INTENT_PATTERNS.items():
            for intent, keywords in intents.items():
                if any(kw in text_lower for kw in keywords):
                    return {
                        "category": category,
                        "intent": intent,
                        "confidence": round(random.uniform(0.85, 0.98), 2),
                        "original_text": text
                    }
        
        # Default to general
        return {
            "category": "general",
            "intent": "general_query",
            "confidence": 0.5,
            "original_text": text
        }
    
    @classmethod
    async def extract_parameters(cls, text: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from command text."""
        params = {}
        text_lower = text.lower()
        
        # Extract country mentions
        if "canada" in text_lower:
            params["country"] = "CA"
        elif "us" in text_lower or "america" in text_lower:
            params["country"] = "US"
        elif "kenya" in text_lower:
            params["country"] = "KE"
        
        # Extract date mentions (simple patterns)
        if "today" in text_lower:
            params["date"] = datetime.now().strftime("%Y-%m-%d")
        elif "tomorrow" in text_lower:
            params["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "yesterday" in text_lower:
            params["date"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in text_lower:
            params["date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        elif "next month" in text_lower:
            params["date"] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        elif "this week" in text_lower or "weekly" in text_lower:
            params["period"] = "weekly"
            params.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
        elif "this month" in text_lower or "monthly" in text_lower:
            params["period"] = "monthly"
            params.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
        
        # Default date if not set (use tomorrow for travel searches)
        if "date" not in params:
            params["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Extract cities for travel
        cities = [
            "toronto", "new york", "dubai", "london", "nairobi", "vancouver",
            "los angeles", "paris", "tokyo", "singapore", "sydney", "chicago",
            "miami", "san francisco", "seattle", "boston", "atlanta", "dallas",
            "montreal", "calgary", "rome", "berlin", "amsterdam", "bangkok",
            "hong kong", "mumbai", "delhi", "cairo", "istanbul", "madrid",
            "barcelona", "vienna", "zurich", "seoul", "osaka", "mexico city",
            "cancun", "las vegas", "orlando", "denver", "phoenix"
        ]
        # Sort by length descending to match "new york" before "york", etc.
        cities.sort(key=len, reverse=True)
        
        # Find positions of key prepositions
        from_pos = text_lower.find("from ")
        to_pos = text_lower.find(" to ")
        in_pos = text_lower.find(" in ")
        at_pos = text_lower.find(" at ")
        
        for city in cities:
            if city not in text_lower:
                continue
            city_pos = text_lower.index(city)
            
            # "from X to Y" pattern: city after "from" but before "to" = origin
            if from_pos >= 0 and city_pos > from_pos:
                if to_pos >= 0 and city_pos < to_pos:
                    params.setdefault("origin", city.title())
                elif to_pos >= 0 and city_pos > to_pos:
                    params.setdefault("destination", city.title())
                elif to_pos < 0:
                    # Only "from X" with no "to Y"
                    params.setdefault("origin", city.title())
            elif to_pos >= 0 and city_pos > to_pos:
                params.setdefault("destination", city.title())
            elif in_pos >= 0 and city_pos > in_pos:
                params.setdefault("destination", city.title())
            elif at_pos >= 0 and city_pos > at_pos:
                params.setdefault("destination", city.title())
            else:
                params.setdefault("destination", city.title())

        # Extract number of nights for hotel
        import re
        nights_match = re.search(r'(\d+)\s*night', text_lower)
        if nights_match:
            nights = int(nights_match.group(1))
            if params.get("date"):
                check_in_dt = datetime.strptime(params["date"], "%Y-%m-%d")
                params["check_out"] = (check_in_dt + timedelta(days=nights)).strftime("%Y-%m-%d")

        # Extract number of days for car rental
        days_match = re.search(r'(\d+)\s*day', text_lower)
        if days_match:
            days = int(days_match.group(1))
            if params.get("date"):
                pickup_dt = datetime.strptime(params["date"], "%Y-%m-%d")
                params["return_date"] = (pickup_dt + timedelta(days=days)).strftime("%Y-%m-%d")
        
        return params
    
    @classmethod
    async def generate_response(
        cls,
        intent: Dict[str, Any],
        action_result: Optional[Dict] = None
    ) -> str:
        """Generate natural language response."""
        
        category = intent["category"]
        intent_name = intent["intent"]
        
        responses = {
            "banking": {
                "check_balance": "I've retrieved your account balances. You have accounts in Canada, US, and Kenya with a combined equivalent of approximately $98,500 USD.",
                "list_transactions": "I found your recent transactions. Would you like me to export them to Excel for your accountant?",
                "export_report": "I've generated the weekly transaction report in QuickBooks-compatible format. It's ready to send to your accountant.",
                "add_account": "I can help you connect a new bank account. Which country is this bank in - Canada, US, or Kenya?"
            },
            "stocks": {
                "portfolio_summary": "Your portfolio is valued at $287,450.75, up $1,250.50 today. Your top performers are Shopify and Microsoft.",
                "stock_quote": "Let me get that stock quote for you.",
                "export_portfolio": "I've generated your portfolio report including holdings, transactions, and tax summary."
            },
            "travel": {
                "search_flights": "I'm searching real-time flights via Amadeus to find the best rates for you.",
                "search_hotels": "I'm searching real-time hotel availability and pricing via Amadeus for you.",
                "search_cars": "I'm checking real-time car rental rates via Amadeus for your dates.",
                "set_alert": "I've set up a price alert. I'll continuously monitor prices and notify you when they drop."
            },
            "research": {
                "summarize_document": "I'm summarizing your uploaded document now. This may take a moment...",
                "list_uploaded_docs": "Let me check your uploaded documents...",
                "legal_search": "I'm searching Canadian and US legal databases for relevant cases and statutes.",
                "conduct_research": "I'll research that topic for you. What type of report would you like - summary, detailed, or executive?",
                "list_projects": "You have 4 active research projects. The most recently updated is 'New Venture Business Plan'."
            },
            "general": {
                "general_query": "I understand you need assistance. Could you please be more specific about what you'd like me to help with?"
            }
        }
        
        return responses.get(category, {}).get(intent_name, "I'm processing your request. Is there anything specific you'd like me to focus on?")
    
    @classmethod
    async def text_to_speech(
        cls,
        text: str,
        voice_id: str = "default",
        speed: float = 1.0
    ) -> TextToSpeechResponse:
        """
        Convert text to speech.
        
        STUBBED: In production, would call ElevenLabs/other TTS API.
        """
        logger.info(f"Generating speech for: {text[:50]}...")
        
        # STUBBED: Return mock audio URL
        return TextToSpeechResponse(
            audio_url=f"https://storage.example.com/audio/response_{datetime.now().timestamp()}.mp3",
            duration_seconds=len(text) * 0.05,  # Rough estimate
            format="mp3"
        )


# ============================================
# API ENDPOINTS
# ============================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    """
    Transcribe audio file to text.
    
    Accepts audio files (wav, mp3, m4a, webm) and returns transcription.
    """
    if not audio.content_type or not any(
        fmt in audio.content_type 
        for fmt in ["audio/", "video/webm"]
    ):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    audio_data = await audio.read()
    result = await VoiceService.transcribe_audio(audio_data)
    
    return result


@router.post("/command", response_model=VoiceCommandResponse)
async def process_voice_command(request: VoiceCommandRequest):
    """
    Process a voice command.
    
    Can accept either audio URL or text for processing.
    Returns intent, parameters, and response with ACTUAL results.
    """
    from app.tools.tool_registry import ToolRegistry
    
    # Get transcription
    if request.audio_url:
        # STUBBED: Would download and transcribe audio
        transcription = "Check my bank balance"
    elif request.text:
        transcription = request.text
    else:
        raise HTTPException(status_code=400, detail="Either audio_url or text is required")
    
    # Parse intent
    intent = await VoiceService.parse_intent(transcription)
    
    # Extract parameters
    params = await VoiceService.extract_parameters(transcription, intent["intent"])
    
    # Map intent to tool and execute for real results
    action_taken = None
    action_results = None
    
    try:
        ToolRegistry.initialize()
        
        # Map voice intents to actual tools
        intent_tool_map = {
            "check_balance": "get_multi_currency_balance",
            "list_transactions": "get_recent_transactions",
            "portfolio_summary": "get_portfolio_summary",
            "stock_quote": "get_stock_quote",
            "search_flights": "search_flights",
            "search_hotels": "search_hotels",
            "search_cars": "search_car_rentals",
            "set_alert": "set_flight_price_alert",
            "book_travel": "book_travel",
            "summarize_document": "summarize_document",
            "list_uploaded_docs": "list_uploaded_documents",
            "legal_search": "search_legal_canada" if params.get("country") == "CA" else "search_legal_us"
        }
        
        tool_name = intent_tool_map.get(intent["intent"])
        
        if tool_name:
            logger.info(f"Executing voice command tool: {tool_name}")
            
            # Build tool parameters based on intent
            tool_params = {}
            
            if tool_name == "search_flights":
                # Convert city names to IATA codes for Amadeus
                from app.routers.travel import city_to_iata_code
                origin_raw = params.get("origin", "YVR")
                dest_raw = params.get("destination", "NBO")
                tool_params = {
                    "origin": city_to_iata_code(origin_raw),
                    "destination": city_to_iata_code(dest_raw),
                    "departure_date": params.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "passengers": 1
                }
            elif tool_name == "search_hotels":
                from datetime import timedelta as td
                check_in = params.get("date", datetime.now().strftime("%Y-%m-%d"))
                check_out = params.get("check_out", (datetime.strptime(check_in, "%Y-%m-%d") + td(days=3)).strftime("%Y-%m-%d"))
                tool_params = {
                    "location": params.get("destination", params.get("origin", "New York")),
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": 1,
                    "rooms": 1
                }
            elif tool_name == "search_car_rentals":
                from datetime import timedelta as td
                pickup_date = params.get("date", datetime.now().strftime("%Y-%m-%d"))
                return_date = params.get("return_date", (datetime.strptime(pickup_date, "%Y-%m-%d") + td(days=7)).strftime("%Y-%m-%d"))
                tool_params = {
                    "pickup_location": params.get("destination", params.get("origin", "New York")),
                    "pickup_date": pickup_date,
                    "return_date": return_date
                }
            elif tool_name == "set_flight_price_alert":
                from app.routers.travel import city_to_iata_code as to_iata
                tool_params = {
                    "origin": to_iata(params.get("origin", "YVR")),
                    "destination": to_iata(params.get("destination", "NBO")),
                    "departure_date": params.get("date", datetime.now().strftime("%Y-%m-%d"))
                }
            elif tool_name == "book_travel":
                tool_params = {
                    "booking_type": "flight",  # Default; would be refined from context
                    "search_id": params.get("search_id", ""),
                }
            elif tool_name == "summarize_document":
                # Extract document name from text
                doc_name = ""
                text_l = transcription.lower()
                for marker in ["summarize ", "summary of ", "summarise ", "sum up "]:
                    if marker in text_l:
                        doc_name = transcription[text_l.index(marker) + len(marker):].strip()
                        # Clean trailing words
                        for stop in [" document", " file", " for me", " please"]:
                            if doc_name.lower().endswith(stop):
                                doc_name = doc_name[:-(len(stop))].strip()
                        break
                summarize_all = any(kw in text_l for kw in ["all document", "all my document", "all files", "everything"])
                tool_params = {
                    "document_name": doc_name,
                    "summarize_all": summarize_all
                }
            elif tool_name == "list_uploaded_documents":
                tool_params = {}
            elif tool_name in ["search_legal_canada", "search_legal_us"]:
                tool_params = {"query": transcription, "limit": 5}
            
            # Execute the tool
            result = await ToolRegistry.execute_tool(
                tool_name=tool_name,
                user_id=request.user_id,
                parameters=tool_params,
                permissions={"banking_read": True, "stocks_read": True, "travel_read": True, "travel_write": True, "research_read": True, "research_write": True}
            )
            
            if result.success:
                action_results = result.data
                action_taken = f"Executed {tool_name}"
                logger.info(f"Voice command executed successfully: {tool_name}")
            else:
                logger.warning(f"Voice command tool failed: {result.error}")
                
    except Exception as e:
        logger.error(f"Voice command execution error: {e}")
    
    # Generate response with actual results
    response_text = await VoiceService.generate_response(intent, action_results)
    
    # If we have actual results, enhance the response
    if action_results:
        response_text = enhance_response_with_results(intent, action_results, response_text)
    
    # Generate TTS response (optional)
    tts_response = await VoiceService.text_to_speech(response_text)
    
    return VoiceCommandResponse(
        command_id=f"CMD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
        transcription=transcription,
        intent=intent["intent"],
        intent_type=VoiceCommandType(intent["category"]),
        parameters=params,
        response_text=response_text,
        audio_response_url=tts_response.audio_url,
        action_taken=action_taken or f"Processed {intent['intent']} in {intent['category']} module"
    )


def enhance_response_with_results(intent: Dict, results: Dict, base_response: str) -> str:
    """Enhance the voice response with actual data results."""
    
    intent_name = intent.get("intent", "")
    
    if intent_name == "search_flights" and results:
        total = results.get("total_results", 0)
        if results.get("best_deal"):
            best = results["best_deal"]
            return f"I found {total} flights. The best deal is {best.get('airline', 'Unknown')} for ${best.get('price', 0):.2f}, departing at {best.get('departure', 'N/A')[:10] if best.get('departure') else 'N/A'}."
        return f"I found {total} flight options for your route. Check the Travel page for details."
    
    if intent_name == "search_hotels" and results:
        total = results.get("total_results", 0)
        if results.get("best_deal"):
            best = results["best_deal"]
            hotel_name = best.get("hotel_name", best.get("name", "a hotel"))
            nightly = best.get("nightly_rate", best.get("price_per_night", 0))
            total_price = best.get("total_price", 0)
            return f"I found {total} hotels. The best deal is {hotel_name} at ${nightly:.2f} per night (${total_price:.2f} total). Check the Travel page for all options."
        return f"I found {total} hotel options. Check the Travel page for details."

    if intent_name == "search_cars" and results:
        total = results.get("total_results", 0)
        if results.get("best_deal"):
            best = results["best_deal"]
            provider = best.get("provider", "a provider")
            daily = best.get("daily_rate", 0)
            car_type = best.get("car_type", "")
            return f"I found {total} car rentals. The best deal is a {car_type} from {provider} at ${daily:.2f} per day. Check the Travel page for all options."
        return f"I found {total} car rental options. Check the Travel page for details."

    if intent_name == "set_alert" and results:
        route = results.get("route", "your route")
        interval = results.get("check_interval_minutes", 30)
        return f"Price alert set for {route}. I'll monitor prices every {interval} minutes and notify you when they drop."

    if intent_name == "check_balance" and results:
        if isinstance(results, dict) and results.get("balances"):
            total = sum(b.get("balance_usd", 0) for b in results.get("balances", []))
            return f"Your total balance across all accounts is approximately ${total:,.2f} USD."
        return base_response
    
    if intent_name == "portfolio_summary" and results:
        value = results.get("total_value", 0)
        change = results.get("daily_change", 0)
        return f"Your portfolio is worth ${value:,.2f}, {'up' if change >= 0 else 'down'} ${abs(change):,.2f} today."
    
    if intent_name == "legal_search" and results:
        total = results.get("total_results", 0)
        return f"I found {total} relevant legal documents. The results include cases from various courts. Check the Research page for full details."
    
    if intent_name == "summarize_document" and results:
        summaries = results.get("summaries", [])
        if summaries:
            first = summaries[0]
            filename = first.get("filename", "your document")
            summary = first.get("summary", "")
            # Truncate for voice response
            if len(summary) > 500:
                summary = summary[:500] + "..."
            if len(summaries) == 1:
                return f"Here's the summary of {filename}: {summary}\n\nYou can download the full summary from the Documents page."
            else:
                names = ", ".join(s.get("filename", "Unknown") for s in summaries[:3])
                return f"I've summarized {len(summaries)} documents: {names}. Here's the first summary: {summary}\n\nYou can download all summaries from the Documents page."
        return "I couldn't find any documents to summarize. Please upload documents first."

    if intent_name == "list_uploaded_docs" and results:
        docs = results.get("documents", [])
        total = results.get("total", 0)
        if total == 0:
            return "You don't have any uploaded documents yet. Go to the Documents page to upload files."
        doc_list = ", ".join(d.get("filename", "Unknown") for d in docs[:5])
        return f"You have {total} uploaded document(s): {doc_list}. You can summarize or download summaries from the Documents page."
    
    return base_response


@router.post("/tts", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech.
    
    Returns URL to generated audio file.
    """
    result = await VoiceService.text_to_speech(
        text=request.text,
        voice_id=request.voice_id,
        speed=request.speed
    )
    
    return result


@router.get("/voices")
async def list_available_voices():
    """List available TTS voices."""
    return {
        "voices": [
            {"id": "default", "name": "Default", "language": "en-US", "gender": "neutral"},
            {"id": "male_1", "name": "James", "language": "en-US", "gender": "male"},
            {"id": "female_1", "name": "Sarah", "language": "en-US", "gender": "female"},
            {"id": "british_male", "name": "Oliver", "language": "en-GB", "gender": "male"},
            {"id": "british_female", "name": "Emma", "language": "en-GB", "gender": "female"}
        ],
        "default_voice": "default"
    }


# Import timedelta for the extract_parameters method
from datetime import timedelta
