"""Amadeus Travel API Service - Real-time flight, hotel, and car rental data.

API Documentation: https://developers.amadeus.com/self-service
"""

import logging
import aiohttp
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class AmadeusService:
    """Service for interacting with Amadeus Travel API."""

    def __init__(self, client_id: str, client_secret: str, test_mode: bool = True):
        """
        Initialize Amadeus service.

        Args:
            client_id: Amadeus API client ID
            client_secret: Amadeus API client secret
            test_mode: Use test environment (True) or production (False)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.test_mode = test_mode
        self.base_url = "https://test.api.amadeus.com" if test_mode else "https://api.amadeus.com"
        self.access_token = None
        self.token_expires_at = None

    async def _get_access_token(self) -> str:
        """
        Get OAuth2 access token from Amadeus.
        Caches token until expiration.

        Returns:
            Access token string
        """
        # Return cached token if still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Request new token
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data["access_token"]
                        expires_in = token_data.get("expires_in", 1799)
                        # Set expiration 1 minute before actual expiry
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("Amadeus access token obtained successfully")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get Amadeus token: {response.status} - {error_text}")
                        raise Exception(f"Amadeus authentication failed: {response.status}")
        except Exception as e:
            logger.error(f"Error getting Amadeus access token: {e}")
            raise

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to Amadeus API.

        Args:
            endpoint: API endpoint (e.g., '/v2/shopping/flight-offers')
            params: Query parameters

        Returns:
            API response data
        """
        token = await self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Amadeus API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error making Amadeus request: {e}")
            return None

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        travel_class: str = "ECONOMY",
        max_results: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Search for flights using Amadeus Flight Offers Search API.

        Args:
            origin: Origin airport code (e.g., 'JFK', 'LAX')
            destination: Destination airport code
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date for round-trip (optional)
            adults: Number of adult passengers (1-9)
            children: Number of child passengers (0-9)
            travel_class: Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
            max_results: Maximum number of results (1-250)

        Returns:
            Flight search results with pricing and itineraries
        """
        endpoint = "/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": travel_class,
            "max": max_results,
            "currencyCode": "USD"
        }

        if return_date:
            params["returnDate"] = return_date

        if children > 0:
            params["children"] = children

        logger.info(f"Searching flights: {origin} → {destination} on {departure_date}")
        result = await self._make_request(endpoint, params)

        if result and "data" in result:
            logger.info(f"Found {len(result['data'])} flight offers")
            return result
        else:
            logger.warning(f"No flights found for {origin} → {destination}")
            return None

    async def search_hotels(
        self,
        city_code: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        rooms: int = 1,
        radius: int = 5,
        radius_unit: str = "KM",
        max_results: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Search for hotels using Amadeus Hotel List API.

        Args:
            city_code: City/Airport IATA code (e.g., 'NYC', 'LON')
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            adults: Number of adult guests
            rooms: Number of rooms
            radius: Search radius
            radius_unit: Unit for radius (KM or MILE)
            max_results: Maximum number of results

        Returns:
            Hotel search results with pricing and details
        """
        endpoint = "/v1/reference-data/locations/hotels/by-city"
        params = {
            "cityCode": city_code.upper(),
            "radius": radius,
            "radiusUnit": radius_unit,
            "hotelSource": "ALL"
        }

        logger.info(f"Searching hotels in {city_code}")
        result = await self._make_request(endpoint, params)

        if result and "data" in result:
            logger.info(f"Found {len(result['data'])} hotels in {city_code}")
            return result
        else:
            logger.warning(f"No hotels found in {city_code}")
            return None

    async def get_hotel_offers(
        self,
        hotel_ids: List[str],
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        rooms: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Get hotel offers with pricing for specific hotels.

        Args:
            hotel_ids: List of Amadeus hotel IDs
            check_in_date: Check-in date in YYYY-MM-DD format
            check_out_date: Check-out date in YYYY-MM-DD format
            adults: Number of adult guests
            rooms: Number of rooms

        Returns:
            Hotel offers with real-time pricing
        """
        endpoint = "/v3/shopping/hotel-offers"
        params = {
            "hotelIds": ",".join(hotel_ids[:10]),  # Max 10 hotels at once
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "roomQuantity": rooms,
            "currency": "USD"
        }

        logger.info(f"Getting offers for {len(hotel_ids)} hotels")
        result = await self._make_request(endpoint, params)

        if result and "data" in result:
            logger.info(f"Retrieved {len(result['data'])} hotel offers with pricing")
            return result
        else:
            logger.warning(f"No hotel offers found")
            return None

    async def search_airport(self, keyword: str, max_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Search for airports by keyword.

        Args:
            keyword: Search keyword (city name, airport name, code)
            max_results: Maximum number of results

        Returns:
            List of matching airports with codes
        """
        endpoint = "/v1/reference-data/locations"
        params = {
            "keyword": keyword,
            "subType": "AIRPORT,CITY",
            "page[limit]": max_results
        }

        logger.info(f"Searching airports for keyword: {keyword}")
        result = await self._make_request(endpoint, params)

        if result and "data" in result:
            logger.info(f"Found {len(result['data'])} locations for '{keyword}'")
            return result
        else:
            logger.warning(f"No airports found for '{keyword}'")
            return None

    async def get_flight_status(
        self,
        flight_number: str,
        flight_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get real-time flight status.

        Args:
            flight_number: Flight number (e.g., 'AA100')
            flight_date: Flight date in YYYY-MM-DD format

        Returns:
            Flight status information
        """
        # Extract carrier code and flight number
        carrier_code = ''.join([c for c in flight_number if c.isalpha()])
        number = ''.join([c for c in flight_number if c.isdigit()])

        endpoint = "/v2/schedule/flights"
        params = {
            "carrierCode": carrier_code,
            "flightNumber": number,
            "scheduledDepartureDate": flight_date
        }

        logger.info(f"Getting flight status for {flight_number} on {flight_date}")
        result = await self._make_request(endpoint, params)

        if result and "data" in result:
            logger.info(f"Flight status retrieved for {flight_number}")
            return result
        else:
            logger.warning(f"Flight status not found for {flight_number}")
            return None


# Global instance - Get credentials from environment variables for security
amadeus_service = AmadeusService(
    client_id=os.getenv("AMADEUS_API_KEY", ""),
    client_secret=os.getenv("AMADEUS_API_SECRET", ""),
    test_mode=os.getenv("AMADEUS_TEST_MODE", "true").lower() == "true"
)
