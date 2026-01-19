"""Alpha Vantage Service - Real-time stock market data integration.

This service fetches real-time stock data from Alpha Vantage API.
API Documentation: https://www.alphavantage.co/documentation/
"""

import logging
import aiohttp
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AlphaVantageService:
    """Service for fetching real-time stock data from Alpha Vantage."""

    def __init__(self, api_key: str):
        """
        Initialize Alpha Vantage service.

        Args:
            api_key: Alpha Vantage API key
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a stock symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Dictionary with stock quote data

        Example Response:
        {
            "symbol": "AAPL",
            "price": 175.43,
            "change": 2.15,
            "change_percent": 1.24,
            "volume": 52847392,
            "latest_trading_day": "2024-01-08",
            "previous_close": 173.28,
            "open": 174.50,
            "high": 176.82,
            "low": 173.91
        }
        """
        try:
            session = await self._get_session()

            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    raise Exception(f"API request failed with status {response.status}")

                data = await response.json()

                # Check for API error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error: {data['Error Message']}")
                    raise Exception(f"Invalid symbol or API error: {data['Error Message']}")

                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    raise Exception("API rate limit reached. Please try again in a minute.")

                # Parse the response
                quote = data.get("Global Quote", {})

                if not quote:
                    logger.warning(f"No data returned for symbol {symbol}")
                    return None

                # Extract and format the data
                return {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0)),
                    "latest_trading_day": quote.get("07. latest trading day", ""),
                    "previous_close": float(quote.get("08. previous close", 0)),
                    "open": float(quote.get("02. open", 0)),
                    "high": float(quote.get("03. high", 0)),
                    "low": float(quote.get("04. low", 0))
                }

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            raise

    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview and fundamental data.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company overview data
        """
        try:
            session = await self._get_session()

            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")

                data = await response.json()

                if "Error Message" in data or not data:
                    logger.warning(f"No overview data for {symbol}")
                    return None

                return {
                    "symbol": symbol,
                    "name": data.get("Name", ""),
                    "description": data.get("Description", ""),
                    "sector": data.get("Sector", ""),
                    "industry": data.get("Industry", ""),
                    "market_cap": data.get("MarketCapitalization", ""),
                    "pe_ratio": data.get("PERatio", ""),
                    "dividend_yield": data.get("DividendYield", ""),
                    "eps": data.get("EPS", ""),
                    "52_week_high": data.get("52WeekHigh", ""),
                    "52_week_low": data.get("52WeekLow", "")
                }

        except Exception as e:
            logger.error(f"Error fetching overview for {symbol}: {e}")
            return None

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to their quote data

        Note: Due to API rate limits (5 calls/minute), this includes delays
        """
        quotes = {}

        for i, symbol in enumerate(symbols):
            try:
                quote = await self.get_quote(symbol)
                if quote:
                    quotes[symbol] = quote
                    logger.info(f"Fetched quote for {symbol}: ${quote['price']}")

                # Add delay to respect rate limits (5 calls per minute = 12 seconds between calls)
                # For demo purposes, using 1 second delay
                if i < len(symbols) - 1:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                quotes[symbol] = None

        return quotes

    async def search_symbols(self, keywords: str) -> List[Dict[str, Any]]:
        """
        Search for stock symbols by keywords.

        Args:
            keywords: Search keywords (e.g., 'Apple', 'Microsoft')

        Returns:
            List of matching symbols with their info
        """
        try:
            session = await self._get_session()

            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords,
                "apikey": self.api_key
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")

                data = await response.json()
                matches = data.get("bestMatches", [])

                results = []
                for match in matches[:10]:  # Limit to top 10
                    results.append({
                        "symbol": match.get("1. symbol", ""),
                        "name": match.get("2. name", ""),
                        "type": match.get("3. type", ""),
                        "region": match.get("4. region", ""),
                        "currency": match.get("8. currency", "")
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []


# Global instance - Get API key from environment variable
alpha_vantage_service = AlphaVantageService(
    api_key=os.getenv("ALPHA_VANTAGE_API_KEY", "")
)
