"""OpenAI Realtime Voice Service - Unified STT/TTS with low-latency streaming.

OpenAI Realtime API Features:
- Single multimodal stream (audio in, audio out)
- Ultra-low latency (~300ms response time)
- Barge-in support (interrupt the AI while it's speaking)
- No separate STT service needed - processes audio directly
- Natural conversation flow with turn detection
- Function calling support during conversation

Pricing (as of 2024):
- Audio input: $0.06 / minute
- Audio output: $0.24 / minute
- Text tokens: Same as GPT-4o pricing

Alternative: ElevenLabs (premium voice quality)
- Free: 10,000 chars/month
- Starter ($5/mo): 30,000 chars/month
- Creator ($22/mo): 100,000 chars/month
- Pro ($99/mo): 500,000 chars/month
"""

import logging
import json
import asyncio
import base64
from typing import Dict, Any, Optional, List, AsyncGenerator, Callable
from datetime import datetime
from enum import Enum
import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class VoiceProvider(str, Enum):
    """Voice service providers."""
    OPENAI_REALTIME = "openai_realtime"
    ELEVENLABS = "elevenlabs"
    WHISPER = "whisper"  # STT only


class OpenAIRealtimeVoice(str, Enum):
    """Available voices for OpenAI Realtime API."""
    ALLOY = "alloy"       # Neutral, balanced
    ECHO = "echo"         # Warm, conversational
    SHIMMER = "shimmer"   # Clear, expressive
    ASH = "ash"           # Confident, professional
    BALLAD = "ballad"     # Melodic, soothing
    CORAL = "coral"       # Warm, friendly
    SAGE = "sage"         # Wise, measured
    VERSE = "verse"       # Dynamic, engaging


class RealtimeVoiceService:
    """Service for OpenAI Realtime API voice interactions.
    
    The Realtime API uses WebSocket connections for bidirectional audio streaming.
    It handles both speech-to-text and text-to-speech in a single connection.
    """

    def __init__(self):
        """Initialize Realtime Voice service."""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_REALTIME_MODEL
        self.voice = settings.OPENAI_REALTIME_VOICE
        self.ws_url = "wss://api.openai.com/v1/realtime"
        self.enabled = settings.OPENAI_REALTIME_ENABLED and bool(self.api_key)
        
        # ElevenLabs fallback
        self.elevenlabs_key = settings.ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = settings.ELEVENLABS_VOICE_ID
        self.elevenlabs_model = settings.ELEVENLABS_MODEL_ID
        
        logger.info(f"Realtime Voice service initialized - OpenAI Realtime: {self.enabled}")

    async def create_session(
        self,
        tools: Optional[List[Dict]] = None,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Realtime API session configuration.
        
        Args:
            tools: List of function tools the AI can call
            instructions: System instructions for the conversation
            
        Returns:
            Session configuration for WebSocket connection
        """
        session_config = {
            "model": self.model,
            "voice": self.voice,
            "modalities": ["text", "audio"],
            "instructions": instructions or self._get_default_instructions(),
            "input_audio_format": "pcm16",  # 16-bit PCM at 24kHz
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"  # Transcribe user speech
            },
            "turn_detection": {
                "type": "server_vad",  # Voice Activity Detection
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
        
        if tools:
            session_config["tools"] = tools
            
        return {
            "type": "session.update",
            "session": session_config
        }

    def _get_default_instructions(self) -> str:
        """Get default system instructions for voice interactions."""
        return """You are Salim AI, a helpful personal assistant with access to banking, 
travel booking, stock portfolio, and research tools. 

When speaking:
- Be concise and natural
- Confirm important actions before executing
- For financial amounts, speak clearly (e.g., "one thousand two hundred fifty dollars")
- If you need to use a tool, briefly explain what you're doing

You can help with:
- Checking bank balances and transactions
- Searching and booking flights, hotels, and car rentals
- Viewing stock portfolio and market quotes
- Conducting research on various topics
"""

    async def connect_websocket(
        self,
        on_audio: Callable[[bytes], None],
        on_transcript: Callable[[str, str], None],
        on_function_call: Callable[[str, Dict], None],
        tools: Optional[List[Dict]] = None
    ) -> 'RealtimeSession':
        """Create a WebSocket connection to OpenAI Realtime API.
        
        Args:
            on_audio: Callback for audio output (bytes)
            on_transcript: Callback for transcripts (role, text)
            on_function_call: Callback for function calls (name, arguments)
            tools: Available function tools
            
        Returns:
            RealtimeSession object for managing the connection
        """
        session = RealtimeSession(
            api_key=self.api_key,
            model=self.model,
            voice=self.voice,
            on_audio=on_audio,
            on_transcript=on_transcript,
            on_function_call=on_function_call,
            tools=tools
        )
        await session.connect()
        return session

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Transcribe audio using Whisper (fallback for non-realtime use).
        
        Args:
            audio_data: Audio bytes (supports wav, mp3, m4a, webm)
            language: Language code
            
        Returns:
            Transcription result
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured")

        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        # Create form data
        form = aiohttp.FormData()
        form.add_field('file', audio_data, filename='audio.webm', content_type='audio/webm')
        form.add_field('model', 'whisper-1')
        form.add_field('language', language)
        form.add_field('response_format', 'verbose_json')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=form) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Transcribed {data.get('duration', 0):.1f}s of audio")
                        return {
                            "text": data.get("text", ""),
                            "language": data.get("language", language),
                            "duration": data.get("duration", 0),
                            "segments": data.get("segments", [])
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Whisper API error: {response.status} - {error_text}")
                        raise Exception(f"Transcription failed: {error_text}")
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    async def text_to_speech_openai(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """Convert text to speech using OpenAI TTS.
        
        Args:
            text: Text to convert
            voice: Voice ID (alloy, echo, shimmer, etc.)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "tts-1",  # or "tts-1-hd" for higher quality
            "input": text,
            "voice": voice or self.voice,
            "speed": speed,
            "response_format": "mp3"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"Generated TTS for {len(text)} characters")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"TTS API error: {response.status} - {error_text}")
                        raise Exception(f"TTS failed: {error_text}")
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise

    async def text_to_speech_elevenlabs(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> bytes:
        """Convert text to speech using ElevenLabs (premium quality).
        
        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID
            stability: Voice stability (0-1)
            similarity_boost: Voice clarity (0-1)
            
        Returns:
            Audio bytes (MP3 format)
        """
        if not self.elevenlabs_key:
            raise Exception("ElevenLabs API key not configured")

        voice = voice_id or self.elevenlabs_voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self.elevenlabs_model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        logger.info(f"ElevenLabs TTS generated for {len(text)} characters")
                        return audio_data
                    else:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                        raise Exception(f"ElevenLabs TTS failed: {error_text}")
        except Exception as e:
            logger.error(f"Error with ElevenLabs TTS: {e}")
            raise

    async def get_elevenlabs_voices(self) -> List[Dict[str, Any]]:
        """Get available ElevenLabs voices.
        
        Returns:
            List of available voices
        """
        if not self.elevenlabs_key:
            return []

        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": self.elevenlabs_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        voices = []
                        for voice in data.get("voices", []):
                            voices.append({
                                "voice_id": voice.get("voice_id"),
                                "name": voice.get("name"),
                                "category": voice.get("category"),
                                "description": voice.get("description"),
                                "preview_url": voice.get("preview_url"),
                                "labels": voice.get("labels", {})
                            })
                        return voices
                    else:
                        logger.error(f"Failed to fetch ElevenLabs voices")
                        return []
        except Exception as e:
            logger.error(f"Error fetching ElevenLabs voices: {e}")
            return []


class RealtimeSession:
    """Manages a single OpenAI Realtime API WebSocket session.
    
    This class handles the bidirectional audio streaming for voice conversations.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        voice: str,
        on_audio: Callable[[bytes], None],
        on_transcript: Callable[[str, str], None],
        on_function_call: Callable[[str, Dict], None],
        tools: Optional[List[Dict]] = None
    ):
        """Initialize Realtime session.
        
        Args:
            api_key: OpenAI API key
            model: Model ID (e.g., gpt-4o-realtime-preview)
            voice: Voice ID
            on_audio: Callback for audio output
            on_transcript: Callback for transcripts
            on_function_call: Callback for function calls
            tools: Available function tools
        """
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.on_audio = on_audio
        self.on_transcript = on_transcript
        self.on_function_call = on_function_call
        self.tools = tools or []
        self.ws = None
        self._receive_task = None
        self._connected = False

    async def connect(self):
        """Establish WebSocket connection."""
        url = f"wss://api.openai.com/v1/realtime?model={self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }

        try:
            self._session = aiohttp.ClientSession()
            self.ws = await self._session.ws_connect(url, headers=headers)
            self._connected = True
            
            # Configure session
            await self._configure_session()
            
            # Start receiving messages
            self._receive_task = asyncio.create_task(self._receive_loop())
            
            logger.info("Realtime WebSocket connected")
        except Exception as e:
            logger.error(f"Failed to connect Realtime WebSocket: {e}")
            raise

    async def _configure_session(self):
        """Send session configuration."""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": self.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                }
            }
        }
        
        if self.tools:
            config["session"]["tools"] = self.tools
            
        await self.send_event(config)

    async def _receive_loop(self):
        """Process incoming WebSocket messages."""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    event = json.loads(msg.data)
                    await self._handle_event(event)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {msg.data}")
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
        finally:
            self._connected = False

    async def _handle_event(self, event: Dict[str, Any]):
        """Handle incoming Realtime API events."""
        event_type = event.get("type", "")
        
        if event_type == "response.audio.delta":
            # Audio output chunk
            audio_b64 = event.get("delta", "")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                self.on_audio(audio_bytes)
                
        elif event_type == "response.audio_transcript.delta":
            # AI response transcript
            text = event.get("delta", "")
            if text:
                self.on_transcript("assistant", text)
                
        elif event_type == "conversation.item.input_audio_transcription.completed":
            # User speech transcript
            text = event.get("transcript", "")
            if text:
                self.on_transcript("user", text)
                
        elif event_type == "response.function_call_arguments.done":
            # Function call completed
            name = event.get("name", "")
            args_str = event.get("arguments", "{}")
            try:
                args = json.loads(args_str)
            except:
                args = {}
            self.on_function_call(name, args)
            
        elif event_type == "error":
            error = event.get("error", {})
            logger.error(f"Realtime API error: {error.get('message', 'Unknown error')}")

    async def send_event(self, event: Dict[str, Any]):
        """Send an event to the Realtime API.
        
        Args:
            event: Event dictionary
        """
        if self.ws and self._connected:
            await self.ws.send_json(event)

    async def send_audio(self, audio_data: bytes):
        """Send audio input to the session.
        
        Args:
            audio_data: PCM16 audio bytes at 24kHz
        """
        audio_b64 = base64.b64encode(audio_data).decode()
        await self.send_event({
            "type": "input_audio_buffer.append",
            "audio": audio_b64
        })

    async def commit_audio(self):
        """Commit the audio buffer and trigger response."""
        await self.send_event({
            "type": "input_audio_buffer.commit"
        })
        await self.send_event({
            "type": "response.create"
        })

    async def send_text(self, text: str):
        """Send text input and get response.
        
        Args:
            text: Text message
        """
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": text
                }]
            }
        })
        await self.send_event({
            "type": "response.create"
        })

    async def send_function_result(self, call_id: str, result: str):
        """Send function call result back to the conversation.
        
        Args:
            call_id: Function call ID
            result: Result string
        """
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": result
            }
        })
        await self.send_event({
            "type": "response.create"
        })

    async def interrupt(self):
        """Interrupt the current response (barge-in)."""
        await self.send_event({
            "type": "response.cancel"
        })

    async def disconnect(self):
        """Close the WebSocket connection."""
        self._connected = False
        if self._receive_task:
            self._receive_task.cancel()
        if self.ws:
            await self.ws.close()
        if hasattr(self, '_session'):
            await self._session.close()
        logger.info("Realtime WebSocket disconnected")


# Global instance
realtime_voice_service = RealtimeVoiceService()
