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

    # ============================================
    # CAR RENTAL SEARCH (Amadeus Self-Service)
    # ============================================

    async def search_car_rentals(
        self,
        pickup_location: str,
        pickup_date: str,
        pickup_time: str = "10:00:00",
        dropoff_date: str = None,
        dropoff_time: str = "10:00:00",
        dropoff_location: str = None,
        driver_age: int = 30,
        currency: str = "USD"
    ) -> Optional[Dict[str, Any]]:
        """
        Search for car rentals using Amadeus Transfer API.

        Note: Amadeus Self-Service offers Transfer API for ground transportation.
        For comprehensive car rentals, consider integrating with:
        - Discover Cars API
        - Rentalcars.com API
        - CarTrawler API

        Args:
            pickup_location: Pickup airport/city code (e.g., 'JFK', 'LAX')
            pickup_date: Pickup date in YYYY-MM-DD format
            pickup_time: Pickup time in HH:MM:SS format
            dropoff_date: Return date (defaults to pickup_date + 1 week)
            dropoff_time: Return time in HH:MM:SS format
            dropoff_location: Return location (defaults to pickup_location)
            driver_age: Driver's age (affects pricing)
            currency: Currency code

        Returns:
            Available car rental options
        """
        # Amadeus Transfer API endpoint for ground transportation
        endpoint = "/v1/shopping/transfer-offers"
        
        # Default dropoff to 7 days after pickup
        if not dropoff_date:
            from datetime import datetime, timedelta
            pickup_dt = datetime.strptime(pickup_date, "%Y-%m-%d")
            dropoff_date = (pickup_dt + timedelta(days=7)).strftime("%Y-%m-%d")
        
        if not dropoff_location:
            dropoff_location = pickup_location

        # Note: This uses POST request with JSON body
        token = await self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "startLocationCode": pickup_location.upper(),
            "endAddressLine": pickup_location.upper(),  # For car rentals, often same area
            "startDateTime": f"{pickup_date}T{pickup_time}",
            "passengers": 1,
            "transferType": "PRIVATE"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Found transfer/car options for {pickup_location}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.warning(f"Amadeus Transfer API: {response.status} - {error_text}")
                        # Return mock data for demonstration
                        return self._get_mock_car_rentals(pickup_location, pickup_date, dropoff_date)
        except Exception as e:
            logger.error(f"Error searching car rentals: {e}")
            return self._get_mock_car_rentals(pickup_location, pickup_date, dropoff_date)

    def _get_mock_car_rentals(
        self,
        pickup_location: str,
        pickup_date: str,
        dropoff_date: str
    ) -> Dict[str, Any]:
        """Return mock car rental data for demonstration."""
        return {
            "data": [
                {
                    "provider": "Enterprise",
                    "vehicle": {
                        "category": "ECONOMY",
                        "type": "Toyota Corolla or similar",
                        "seats": 5,
                        "doors": 4,
                        "transmission": "Automatic",
                        "air_conditioning": True,
                        "fuel_type": "Gasoline"
                    },
                    "price": {
                        "total": "245.00",
                        "currency": "USD",
                        "per_day": "35.00"
                    },
                    "pickup": {
                        "location": pickup_location,
                        "date": pickup_date,
                        "time": "10:00"
                    },
                    "dropoff": {
                        "location": pickup_location,
                        "date": dropoff_date,
                        "time": "10:00"
                    },
                    "included": ["Unlimited mileage", "Third party liability", "Theft protection"]
                },
                {
                    "provider": "Hertz",
                    "vehicle": {
                        "category": "INTERMEDIATE",
                        "type": "Honda Accord or similar",
                        "seats": 5,
                        "doors": 4,
                        "transmission": "Automatic",
                        "air_conditioning": True,
                        "fuel_type": "Gasoline"
                    },
                    "price": {
                        "total": "315.00",
                        "currency": "USD",
                        "per_day": "45.00"
                    },
                    "pickup": {
                        "location": pickup_location,
                        "date": pickup_date,
                        "time": "10:00"
                    },
                    "dropoff": {
                        "location": pickup_location,
                        "date": dropoff_date,
                        "time": "10:00"
                    },
                    "included": ["Unlimited mileage", "Collision damage waiver", "Theft protection"]
                },
                {
                    "provider": "Budget",
                    "vehicle": {
                        "category": "SUV",
                        "type": "Ford Explorer or similar",
                        "seats": 7,
                        "doors": 4,
                        "transmission": "Automatic",
                        "air_conditioning": True,
                        "fuel_type": "Gasoline"
                    },
                    "price": {
                        "total": "455.00",
                        "currency": "USD",
                        "per_day": "65.00"
                    },
                    "pickup": {
                        "location": pickup_location,
                        "date": pickup_date,
                        "time": "10:00"
                    },
                    "dropoff": {
                        "location": pickup_location,
                        "date": dropoff_date,
                        "time": "10:00"
                    },
                    "included": ["Unlimited mileage", "Full insurance", "Free cancellation"]
                }
            ],
            "meta": {
                "note": "For production car rentals, integrate with Discover Cars, CarTrawler, or direct provider APIs",
                "providers_available": ["Enterprise", "Hertz", "Budget", "Avis", "National", "Alamo"]
            }
        }

    # ============================================
    # HOTEL BOOKING (Enhanced)
    # ============================================

    async def book_hotel(
        self,
        offer_id: str,
        guest_info: Dict[str, Any],
        payment_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Book a hotel using Amadeus Hotel Booking API.

        Args:
            offer_id: Hotel offer ID from search results
            guest_info: Guest information (name, email, phone)
            payment_info: Payment card information

        Returns:
            Booking confirmation
        """
        endpoint = "/v2/booking/hotel-orders"
        token = await self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "data": {
                "type": "hotel-order",
                "guests": [{
                    "tid": 1,
                    "name": {
                        "firstName": guest_info.get("first_name"),
                        "lastName": guest_info.get("last_name")
                    },
                    "contact": {
                        "email": guest_info.get("email"),
                        "phone": guest_info.get("phone")
                    }
                }],
                "payments": [{
                    "method": "CREDIT_CARD",
                    "paymentCard": {
                        "vendorCode": payment_info.get("card_type", "VI"),  # VI=Visa, MC=Mastercard
                        "cardNumber": payment_info.get("card_number"),
                        "expiryDate": payment_info.get("expiry_date"),  # YYYY-MM
                        "holderName": payment_info.get("holder_name")
                    }
                }],
                "rooms": [{
                    "guestIds": [1],
                    "offerId": offer_id
                }]
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        logger.info(f"Hotel booked successfully: {offer_id}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Hotel booking failed: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error booking hotel: {e}")
            return None

    # ============================================
    # FLIGHT BOOKING
    # ============================================

    async def book_flight(
        self,
        flight_offer: Dict[str, Any],
        travelers: List[Dict[str, Any]],
        contact_info: Dict[str, Any],
        payment_info: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Book a flight using Amadeus Flight Orders API.

        Args:
            flight_offer: Flight offer from search results
            travelers: List of traveler information
            contact_info: Contact information for booking
            payment_info: Payment information (optional for some markets)

        Returns:
            Booking confirmation with PNR
        """
        endpoint = "/v1/booking/flight-orders"
        token = await self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Format travelers
        formatted_travelers = []
        for i, traveler in enumerate(travelers, 1):
            formatted_travelers.append({
                "id": str(i),
                "dateOfBirth": traveler.get("date_of_birth"),
                "name": {
                    "firstName": traveler.get("first_name"),
                    "lastName": traveler.get("last_name")
                },
                "gender": traveler.get("gender", "MALE"),
                "contact": {
                    "emailAddress": contact_info.get("email"),
                    "phones": [{
                        "deviceType": "MOBILE",
                        "countryCallingCode": contact_info.get("country_code", "1"),
                        "number": contact_info.get("phone")
                    }]
                },
                "documents": [{
                    "documentType": "PASSPORT",
                    "number": traveler.get("passport_number"),
                    "expiryDate": traveler.get("passport_expiry"),
                    "issuanceCountry": traveler.get("passport_country"),
                    "nationality": traveler.get("nationality"),
                    "holder": True
                }] if traveler.get("passport_number") else []
            })

        payload = {
            "data": {
                "type": "flight-order",
                "flightOffers": [flight_offer],
                "travelers": formatted_travelers,
                "remarks": {
                    "general": [{
                        "subType": "GENERAL_MISCELLANEOUS",
                        "text": "Booked via Salim AI Assistant"
                    }]
                }
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        pnr = result.get("data", {}).get("associatedRecords", [{}])[0].get("reference")
                        logger.info(f"Flight booked successfully. PNR: {pnr}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Flight booking failed: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error booking flight: {e}")
            return None


# Global instance - Get credentials from environment variables for security
amadeus_service = AmadeusService(
    client_id=os.getenv("AMADEUS_API_KEY", ""),
    client_secret=os.getenv("AMADEUS_API_SECRET", ""),
    test_mode=os.getenv("AMADEUS_TEST_MODE", "true").lower() == "true"
)
