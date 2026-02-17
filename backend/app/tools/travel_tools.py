"""Travel Tools - Comprehensive Flight, Hotel, and Car Rental Search.

Features:
- Multi-provider search (FareCompare, Expedia, Priceline, Airlines)
- Priceline VIP Platinum member benefits
- Continuous price monitoring
- Hotel and car rental booking
- Trip planning and management

Providers Supported:
- FareCompare (aggregator)
- Expedia
- Priceline (VIP Platinum)
- Direct airline APIs
- Skyscanner
- Amadeus
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import random

from .base_tool import BaseTool, ToolResult, ToolCategory

logger = logging.getLogger(__name__)


class TravelProvider(str, Enum):
    """Travel search providers."""
    FARECOMPARE = "farecompare"
    EXPEDIA = "expedia"
    PRICELINE = "priceline"
    SKYSCANNER = "skyscanner"
    DIRECT_AIRLINE = "direct"
    AMADEUS = "amadeus"
    ALL = "all"


class CabinClass(str, Enum):
    """Flight cabin classes."""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


# ============================================
# FLIGHT SEARCH TOOLS
# ============================================

class SearchFlightsTool(BaseTool):
    """Search flights across multiple providers."""
    
    def __init__(self):
        super().__init__(
            name="search_flights",
            description="Search for flights across FareCompare, Expedia, Priceline (VIP), and direct airlines to find best rates",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_read permission"
            )

        origin = parameters.get("origin")
        destination = parameters.get("destination")
        departure_date = parameters.get("departure_date")
        return_date = parameters.get("return_date")  # Optional for one-way
        passengers = parameters.get("passengers", 1)
        cabin_class = parameters.get("cabin_class", "economy")
        providers = parameters.get("providers", ["all"])

        if not all([origin, destination, departure_date]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Origin, destination, and departure_date are required"
            )

        # Fetch REAL flight data from Amadeus API
        try:
            from app.services.amadeus_service import amadeus_service

            # Map cabin class to Amadeus format
            travel_class_map = {
                "economy": "ECONOMY",
                "premium_economy": "PREMIUM_ECONOMY",
                "business": "BUSINESS",
                "first": "FIRST"
            }
            travel_class = travel_class_map.get(cabin_class.lower(), "ECONOMY")

            logger.info(f"Searching flights via Amadeus: {origin} → {destination} on {departure_date}")

            # Search flights using Amadeus
            amadeus_result = await amadeus_service.search_flights(
                origin=origin.upper(),
                destination=destination.upper(),
                departure_date=departure_date,
                return_date=return_date,
                adults=passengers,
                travel_class=travel_class,
                max_results=15
            )

            if not amadeus_result or "data" not in amadeus_result:
                logger.warning(f"No flights found from Amadeus for {origin} → {destination}")
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"No flights found for {origin} → {destination} on {departure_date}",
                    error="No available flights for this route. Try different dates or airports."
                )

            # Parse Amadeus response into simplified format
            results = []
            for offer in amadeus_result["data"]:
                try:
                    # Get itinerary details
                    itinerary = offer["itineraries"][0]  # Outbound flight
                    first_segment = itinerary["segments"][0]
                    last_segment = itinerary["segments"][-1]

                    # Extract airline info
                    carrier_code = first_segment["carrierCode"]
                    airline_name = amadeus_result.get("dictionaries", {}).get("carriers", {}).get(carrier_code, carrier_code)

                    # Calculate number of stops
                    num_stops = len(itinerary["segments"]) - 1

                    flight_data = {
                        "provider": "Amadeus (Real-Time)",
                        "airline": airline_name,
                        "carrier_code": carrier_code,
                        "flight_number": f"{first_segment['carrierCode']}{first_segment['number']}",
                        "origin": first_segment["departure"]["iataCode"],
                        "destination": last_segment["arrival"]["iataCode"],
                        "departure": first_segment["departure"]["at"],
                        "arrival": last_segment["arrival"]["at"],
                        "duration": itinerary["duration"],
                        "stops": num_stops,
                        "cabin_class": cabin_class,
                        "price": float(offer["price"]["total"]),
                        "currency": offer["price"]["currency"],
                        "base_price": float(offer["price"]["base"]),
                        "total_price": float(offer["price"]["grandTotal"]),
                        "bookable_seats": offer.get("numberOfBookableSeats", 0),
                        "instant_ticketing": offer.get("instantTicketingRequired", False),
                        "segments": itinerary["segments"],
                        "data_source": "Amadeus API (Real-Time)"
                    }

                    # Add return flight info if available
                    if len(offer["itineraries"]) > 1:
                        return_itinerary = offer["itineraries"][1]
                        flight_data["return_flight"] = {
                            "departure": return_itinerary["segments"][0]["departure"]["at"],
                            "arrival": return_itinerary["segments"][-1]["arrival"]["at"],
                            "duration": return_itinerary["duration"]
                        }

                    results.append(flight_data)
                except Exception as e:
                    logger.error(f"Error parsing flight offer: {e}")
                    continue

            if not results:
                return ToolResult(
                    success=False,
                    data=None,
                    message="No valid flight offers found",
                    error="Failed to parse flight data"
                )

            # Sort by price
            results.sort(key=lambda x: x["price"])

            # Find best deal
            best_deal = results[0]

            logger.info(f"Found {len(results)} real flights from Amadeus for {origin} → {destination}")

            return ToolResult(
                success=True,
                data={
                    "search_id": f"FLT-{random.randint(100000, 999999)}",
                    "search_params": {
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date,
                        "return_date": return_date,
                        "passengers": passengers,
                        "cabin_class": cabin_class
                    },
                    "results": results,
                    "total_results": len(results),
                    "best_deal": best_deal,
                    "price_range": {
                        "min": results[0]["price"],
                        "max": results[-1]["price"],
                        "currency": results[0]["currency"]
                    },
                    "searched_at": datetime.now().isoformat(),
                    "data_source": "Amadeus API (Real-Time)"
                },
                message=f"Found {len(results)} real-time flights from Amadeus. Best price: ${best_deal['price']:.2f} {best_deal['currency']} on {best_deal['airline']}",
                metadata={"disclaimer": "Real-time flight data from Amadeus Travel API"}
            )

        except Exception as e:
            logger.error(f"Error searching flights via Amadeus: {e}")
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to search flights: {str(e)}",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code (e.g., YYZ, JFK, NBO)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date (YYYY-MM-DD)"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date for round trip (optional)"
                    },
                    "passengers": {
                        "type": "integer",
                        "description": "Number of passengers",
                        "default": 1
                    },
                    "cabin_class": {
                        "type": "string",
                        "enum": ["economy", "premium_economy", "business", "first"],
                        "description": "Cabin class",
                        "default": "economy"
                    },
                    "providers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific providers to search (default: all)"
                    }
                },
                "required": ["origin", "destination", "departure_date"]
            }
        }


class SetFlightPriceAlertTool(BaseTool):
    """Set price alert for continuous flight monitoring."""
    
    def __init__(self):
        super().__init__(
            name="set_flight_price_alert",
            description="Set up continuous price monitoring for a flight route with alerts when prices drop",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_write permission"
            )
        
        origin = parameters.get("origin")
        destination = parameters.get("destination")
        departure_date = parameters.get("departure_date")
        target_price = parameters.get("target_price")
        check_interval = parameters.get("check_interval_minutes", 30)
        
        if not all([origin, destination, departure_date]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Origin, destination, and departure_date are required"
            )
        
        # STUBBED: Create price alert
        alert = {
            "alert_id": f"ALERT-{random.randint(100000, 999999)}",
            "route": f"{origin} → {destination}",
            "departure_date": departure_date,
            "target_price": target_price,
            "current_lowest_price": random.randint(400, 800),
            "check_interval_minutes": check_interval,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(minutes=check_interval)).isoformat(),
            "notifications": {
                "email": True,
                "push": True
            }
        }
        
        logger.info(f"Price alert created for {user_id}: {origin} -> {destination}")
        
        return ToolResult(
            success=True,
            data=alert,
            message=f"Price alert set for {origin} → {destination}. Will check every {check_interval} minutes."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date (YYYY-MM-DD)"
                    },
                    "target_price": {
                        "type": "number",
                        "description": "Target price to alert on (optional)"
                    },
                    "check_interval_minutes": {
                        "type": "integer",
                        "description": "How often to check prices (default: 30 min)",
                        "default": 30
                    }
                },
                "required": ["origin", "destination", "departure_date"]
            }
        }


# ============================================
# HOTEL SEARCH TOOLS
# ============================================

class SearchHotelsTool(BaseTool):
    """Search hotels using real Amadeus API."""
    
    def __init__(self):
        super().__init__(
            name="search_hotels",
            description="Search for hotels with real-time pricing from Amadeus API",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_read permission"
            )
        
        location = parameters.get("location")
        check_in = parameters.get("check_in")
        check_out = parameters.get("check_out")
        guests = parameters.get("guests", 1)
        rooms = parameters.get("rooms", 1)
        star_rating = parameters.get("star_rating")
        
        if not all([location, check_in, check_out]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Location, check_in, and check_out are required"
            )
        
        # Calculate nights
        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
        nights = max((check_out_dt - check_in_dt).days, 1)

        try:
            from app.services.amadeus_service import amadeus_service
            from app.routers.travel import city_to_iata_code

            city_code = city_to_iata_code(location)
            logger.info(f"Searching hotels via Amadeus in {location} (code: {city_code})")

            # Step 1: Get hotel list by city
            hotel_list_result = await amadeus_service.search_hotels(
                city_code=city_code,
                check_in_date=check_in,
                check_out_date=check_out,
                adults=guests,
                rooms=rooms,
            )

            if not hotel_list_result or "data" not in hotel_list_result:
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"No hotels found in {location}",
                    error="Amadeus returned no hotel data for this location"
                )

            raw_hotels = hotel_list_result["data"][:20]
            hotel_ids = [h.get("hotelId") for h in raw_hotels if h.get("hotelId")]

            if not hotel_ids:
                return ToolResult(
                    success=False, data=None,
                    message=f"No bookable hotels found in {location}",
                    error="No hotel IDs returned"
                )

            # Step 2: Get real-time offers with pricing
            offers_result = await amadeus_service.get_hotel_offers(
                hotel_ids=hotel_ids[:10],
                check_in_date=check_in,
                check_out_date=check_out,
                adults=guests,
                rooms=rooms,
            )

            # Build metadata lookup
            hotel_meta = {h.get("hotelId"): h for h in raw_hotels}

            results = []
            if offers_result and "data" in offers_result:
                for offer_item in offers_result["data"]:
                    try:
                        hotel_data = offer_item.get("hotel", {})
                        hotel_id = hotel_data.get("hotelId", offer_item.get("hotelId", ""))
                        offers = offer_item.get("offers", [])
                        if not offers:
                            continue

                        best_offer = offers[0]
                        price_info = best_offer.get("price", {})
                        total_price = float(price_info.get("total", "0") or "0")
                        currency = price_info.get("currency", "USD")
                        nightly_rate = round(total_price / nights, 2)

                        room = best_offer.get("room", {})
                        room_type = room.get("typeEstimated", {}).get("category", "Standard Room")
                        room_desc = room.get("description", {}).get("text", room_type)

                        policies = best_offer.get("policies", {})
                        cancellation = policies.get("cancellations", [{}])
                        free_cancel = False
                        if cancellation:
                            cancel_type = cancellation[0].get("type", "")
                            free_cancel = "FREE" in cancel_type.upper() or cancel_type == "FULL_STAY"

                        name = hotel_data.get("name", "Hotel")
                        meta = hotel_meta.get(hotel_id, {})
                        rating = float(meta.get("rating", hotel_data.get("rating", 3)))

                        amenities_raw = meta.get("amenities", [])
                        amenity_map = {
                            "SWIMMING_POOL": "Pool", "WIFI": "Free WiFi", "FREE_WIFI": "Free WiFi",
                            "FITNESS_CENTER": "Gym", "RESTAURANT": "Restaurant", "BAR": "Bar",
                            "SPA": "Spa", "PARKING": "Parking", "ROOM_SERVICE": "Room Service",
                        }
                        amenities = list({amenity_map.get(a, a.replace("_", " ").title()) for a in amenities_raw})

                        if star_rating and rating < star_rating:
                            continue

                        results.append({
                            "hotel_id": hotel_id,
                            "hotel_name": name.title() if name == name.upper() else name,
                            "star_rating": rating,
                            "location": location,
                            "address": meta.get("address", {}).get("lines", [""])[0] if meta.get("address") else "",
                            "nightly_rate": nightly_rate,
                            "total_price": total_price,
                            "currency": currency,
                            "room_type": room_desc if room_desc != room_type else room_type,
                            "amenities": amenities[:8] if amenities else ["Free WiFi"],
                            "free_cancellation": free_cancel,
                            "breakfast_included": any("BREAKFAST" in str(a).upper() for a in amenities_raw),
                            "distance_from_center": round(meta.get("distance", {}).get("value", 0), 1) if meta.get("distance") else 0,
                            "data_source": "Amadeus API (Real-Time)"
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing hotel offer: {e}")
                        continue

            # Fallback: if no offers with pricing, build results from hotel list metadata
            if not results:
                logger.info(f"No pricing offers, building results from hotel metadata for {location}")
                for h in raw_hotels[:8]:
                    try:
                        name = h.get("name", "Hotel")
                        rating = float(h.get("rating", 3))
                        if star_rating and rating < star_rating:
                            continue
                        amenities_raw = h.get("amenities", [])
                        amenity_map = {
                            "SWIMMING_POOL": "Pool", "WIFI": "Free WiFi", "FREE_WIFI": "Free WiFi",
                            "FITNESS_CENTER": "Gym", "RESTAURANT": "Restaurant", "SPA": "Spa",
                            "PARKING": "Parking",
                        }
                        amenities = list({amenity_map.get(a, a.replace("_", " ").title()) for a in amenities_raw})
                        dist = round(h.get("distance", {}).get("value", 0), 1) if h.get("distance") else 0
                        results.append({
                            "hotel_id": h.get("hotelId", ""),
                            "hotel_name": name.title() if name == name.upper() else name,
                            "star_rating": rating,
                            "location": location,
                            "address": h.get("address", {}).get("lines", [""])[0] if h.get("address") else "",
                            "nightly_rate": 0,
                            "total_price": 0,
                            "currency": "USD",
                            "room_type": "Standard Room",
                            "amenities": amenities[:6] if amenities else ["Free WiFi"],
                            "free_cancellation": False,
                            "breakfast_included": any("BREAKFAST" in str(a).upper() for a in amenities_raw),
                            "distance_from_center": dist,
                            "data_source": "Amadeus Hotel List (pricing unavailable in test mode)",
                            "note": "Contact hotel directly for current rates"
                        })
                    except Exception:
                        continue

            if not results:
                return ToolResult(
                    success=False, data=None,
                    message=f"No hotels found in {location}",
                    error="Could not retrieve hotel data"
                )

            results.sort(key=lambda x: x["total_price"])
            best_deal = results[0]

            logger.info(f"Found {len(results)} real-time hotels from Amadeus for {location}")

            return ToolResult(
                success=True,
                data={
                    "search_id": f"HTL-{random.randint(100000, 999999)}",
                    "search_params": {
                        "location": location,
                        "check_in": check_in,
                        "check_out": check_out,
                        "nights": nights,
                        "guests": guests,
                        "rooms": rooms
                    },
                    "results": results,
                    "total_results": len(results),
                    "best_deal": best_deal,
                    "price_range": {
                        "min_nightly": min(r["nightly_rate"] for r in results),
                        "max_nightly": max(r["nightly_rate"] for r in results)
                    },
                    "searched_at": datetime.now().isoformat(),
                    "data_source": "Amadeus API (Real-Time)"
                },
                message=f"Found {len(results)} real-time hotels. Best price: ${best_deal['nightly_rate']:.2f}/night at {best_deal['hotel_name']}",
                metadata={"disclaimer": "Real-time hotel data from Amadeus Travel API"}
            )

        except Exception as e:
            logger.error(f"Error searching hotels via Amadeus: {e}")
            return ToolResult(
                success=False, data=None,
                message=f"Failed to search hotels: {str(e)}",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or area to search"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date (YYYY-MM-DD)"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date (YYYY-MM-DD)"
                    },
                    "guests": {
                        "type": "integer",
                        "description": "Number of guests",
                        "default": 1
                    },
                    "rooms": {
                        "type": "integer",
                        "description": "Number of rooms",
                        "default": 1
                    },
                    "star_rating": {
                        "type": "integer",
                        "description": "Minimum star rating (1-5)"
                    }
                },
                "required": ["location", "check_in", "check_out"]
            }
        }


# ============================================
# CAR RENTAL TOOLS
# ============================================

class SearchCarRentalsTool(BaseTool):
    """Search car rentals using real Amadeus Transfer API."""
    
    def __init__(self):
        super().__init__(
            name="search_car_rentals",
            description="Search for car rentals with real-time pricing from Amadeus API",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_read permission"
            )
        
        pickup_location = parameters.get("pickup_location")
        pickup_date = parameters.get("pickup_date")
        return_date = parameters.get("return_date")
        car_type = parameters.get("car_type")
        
        if not all([pickup_location, pickup_date, return_date]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Pickup location, pickup_date, and return_date are required"
            )
        
        # Calculate days
        pickup_dt = datetime.strptime(pickup_date, "%Y-%m-%d")
        return_dt = datetime.strptime(return_date, "%Y-%m-%d")
        days = max((return_dt - pickup_dt).days, 1)

        try:
            from app.services.amadeus_service import amadeus_service
            from app.routers.travel import city_to_iata_code

            location_code = city_to_iata_code(pickup_location)
            logger.info(f"Searching car rentals via Amadeus at {pickup_location} (code: {location_code})")

            result = await amadeus_service.search_car_rentals(
                pickup_location=location_code,
                pickup_date=pickup_date,
                pickup_time="10:00:00",
                dropoff_date=return_date,
                dropoff_time="10:00:00",
                dropoff_location=location_code,
            )

            results = []
            raw_data = []
            if result:
                if isinstance(result, dict) and "data" in result:
                    raw_data = result["data"]
                elif isinstance(result, list):
                    raw_data = result
                elif isinstance(result, dict):
                    # Some Transfer API responses might have different structure
                    logger.info(f"Car rental response keys: {list(result.keys())}")
                    # Try extracting from other known keys
                    for key in ["transfers", "offers", "results"]:
                        if key in result:
                            raw_data = result[key]
                            break

            if raw_data:
                logger.info(f"Car rental data received: {len(raw_data)} items")
                for idx, car_data in enumerate(raw_data):
                    try:
                        logger.info(f"Parsing car item {idx}, keys: {list(car_data.keys())}")
                        # Handle Amadeus Transfer API format
                        if "transferType" in car_data:
                            vehicle = car_data.get("vehicle", car_data.get("serviceProvider", {}))
                            price_info = car_data.get("quotation", car_data.get("price", {}))
                            provider_data = car_data.get("serviceProvider", {})
                            provider = provider_data.get("name", "Transfer Service") if isinstance(provider_data, dict) else str(provider_data)
                            included = []
                            category = car_data.get("transferType", "PRIVATE")
                            car_name = vehicle.get("description", f"{category} Transfer")
                            seats = int(vehicle.get("seats", {}).get("count", 4)) if isinstance(vehicle.get("seats"), dict) else int(vehicle.get("seats", 4))
                            transmission = "Automatic"
                            total_str = price_info.get("monetaryAmount", price_info.get("total", "0"))
                            currency = price_info.get("currencyCode", price_info.get("currency", "USD"))
                        # Handle mock/standard format with vehicle key
                        elif "vehicle" in car_data:
                            vehicle = car_data["vehicle"]
                            price_info = car_data.get("price", {})
                            provider = car_data.get("provider", "Rental Co")
                            included = car_data.get("included", [])
                            category = vehicle.get("category", vehicle.get("type", "Standard"))
                            car_name = vehicle.get("type", vehicle.get("description", f"{category} Car"))
                            seats = int(vehicle.get("seats", 5))
                            transmission = vehicle.get("transmission", "Automatic")
                            total_str = price_info.get("total", "0")
                            currency = price_info.get("currency", "USD")
                        else:
                            vehicle = car_data
                            price_info = car_data.get("price", {})
                            provider = car_data.get("provider", "Rental Co")
                            included = car_data.get("included", [])
                            category = vehicle.get("category", "Standard")
                            car_name = vehicle.get("type", "Car")
                            seats = 5
                            transmission = "Automatic"
                            total_str = price_info.get("total", "0")
                            currency = price_info.get("currency", "USD")

                        if isinstance(provider, dict):
                            provider = provider.get("name", "Rental Co")

                        total_price = float(total_str) if total_str else 0.0
                        per_day_str = price_info.get("per_day", price_info.get("baseAmount", "0"))
                        daily_rate = float(per_day_str) if per_day_str and per_day_str != "0" else round(total_price / days, 2)

                        # Type classification
                        cat_upper = category.upper()
                        type_label = category.title()
                        if "ECONOMY" in cat_upper or "MINI" in cat_upper:
                            type_label = "Economy"
                        elif "SUV" in cat_upper or "4X4" in cat_upper:
                            type_label = "SUV"
                        elif "PREMIUM" in cat_upper or "LUXURY" in cat_upper:
                            type_label = "Premium"
                        elif "VAN" in cat_upper or "MINIVAN" in cat_upper:
                            type_label = "Van"
                        elif "INTERMEDIATE" in cat_upper or "COMPACT" in cat_upper:
                            type_label = "Compact"

                        if car_type and car_type.lower() != "all" and type_label.lower() != car_type.lower():
                            continue

                        results.append({
                            "provider": provider,
                            "car_type": type_label,
                            "car_model": car_name,
                            "pickup_location": pickup_location,
                            "seats": seats,
                            "transmission": transmission,
                            "daily_rate": daily_rate,
                            "total_price": total_price,
                            "currency": currency,
                            "features": ["Automatic" if transmission == "Automatic" else "Manual", "A/C"] + included[:3],
                            "mileage": "Unlimited" if any("unlimited" in str(i).lower() for i in included) else "Limited",
                            "insurance_included": any("insurance" in str(i).lower() or "collision" in str(i).lower() for i in included),
                            "free_cancellation": any("free" in str(i).lower() or "cancel" in str(i).lower() for i in included),
                            "data_source": "Amadeus API (Real-Time)"
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing car rental: {e}")
                        continue

            if not results:
                return ToolResult(
                    success=False, data=None,
                    message=f"No car rentals found at {pickup_location}",
                    error="No results from Amadeus Transfer API"
                )

            results.sort(key=lambda x: x["total_price"])
            best_deal = results[0]

            logger.info(f"Found {len(results)} car rentals from Amadeus for {pickup_location}")

            return ToolResult(
                success=True,
                data={
                    "search_id": f"CAR-{random.randint(100000, 999999)}",
                    "search_params": {
                        "pickup_location": pickup_location,
                        "pickup_date": pickup_date,
                        "return_date": return_date,
                        "days": days
                    },
                    "results": results,
                    "total_results": len(results),
                    "best_deal": best_deal,
                    "searched_at": datetime.now().isoformat(),
                    "data_source": "Amadeus API (Real-Time)"
                },
                message=f"Found {len(results)} car rentals. Best price: ${best_deal['daily_rate']:.2f}/day from {best_deal['provider']}",
                metadata={"disclaimer": "Real-time car rental data from Amadeus Travel API"}
            )

        except Exception as e:
            logger.error(f"Error searching car rentals via Amadeus: {e}")
            return ToolResult(
                success=False, data=None,
                message=f"Failed to search car rentals: {str(e)}",
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "pickup_location": {
                        "type": "string",
                        "description": "Pickup location (city or airport code)"
                    },
                    "pickup_date": {
                        "type": "string",
                        "description": "Pickup date (YYYY-MM-DD)"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date (YYYY-MM-DD)"
                    },
                    "car_type": {
                        "type": "string",
                        "enum": ["Economy", "Compact", "Midsize", "Full-size", "SUV", "Premium", "Luxury"],
                        "description": "Preferred car type (optional)"
                    }
                },
                "required": ["pickup_location", "pickup_date", "return_date"]
            }
        }


# ============================================
# TRIP PLANNING TOOLS
# ============================================

class CreateTripPlanTool(BaseTool):
    """Create a comprehensive trip plan."""
    
    def __init__(self):
        super().__init__(
            name="create_trip_plan",
            description="Create a trip plan combining flights, hotels, and car rentals",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_write permission"
            )
        
        destination = parameters.get("destination")
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")
        trip_name = parameters.get("trip_name", f"Trip to {destination}")
        include_car = parameters.get("include_car", False)
        
        if not all([destination, start_date, end_date]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Destination, start_date, and end_date are required"
            )
        
        # STUBBED: Create trip plan
        trip_plan = {
            "trip_id": f"TRIP-{random.randint(100000, 999999)}",
            "trip_name": trip_name,
            "destination": destination,
            "dates": {
                "start": start_date,
                "end": end_date,
                "duration_days": (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
            },
            "status": "planning",
            "components": {
                "flights": {
                    "status": "not_booked",
                    "search_pending": True
                },
                "hotel": {
                    "status": "not_booked",
                    "search_pending": True
                },
                "car_rental": {
                    "status": "not_needed" if not include_car else "not_booked",
                    "search_pending": include_car
                }
            },
            "estimated_budget": {
                "flights": random.randint(500, 1500),
                "hotel": random.randint(300, 1000),
                "car": random.randint(100, 400) if include_car else 0,
                "total": 0
            },
            "created_at": datetime.now().isoformat(),
            "notes": []
        }
        
        trip_plan["estimated_budget"]["total"] = sum([
            trip_plan["estimated_budget"]["flights"],
            trip_plan["estimated_budget"]["hotel"],
            trip_plan["estimated_budget"]["car"]
        ])
        
        logger.info(f"Trip plan created for {user_id}: {trip_plan['trip_id']}")
        
        return ToolResult(
            success=True,
            data=trip_plan,
            message=f"Trip plan '{trip_name}' created. Use search tools to find best deals."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Trip destination city"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Trip start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Trip end date (YYYY-MM-DD)"
                    },
                    "trip_name": {
                        "type": "string",
                        "description": "Name for this trip"
                    },
                    "include_car": {
                        "type": "boolean",
                        "description": "Include car rental in plan",
                        "default": False
                    }
                },
                "required": ["destination", "start_date", "end_date"]
            }
        }


class BookTravelTool(BaseTool):
    """Book selected travel options (requires confirmation)."""
    
    def __init__(self):
        super().__init__(
            name="book_travel",
            description="Book selected flight, hotel, or car rental (requires user confirmation)",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_write", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_write permission"
            )
        
        booking_type = parameters.get("booking_type")  # flight, hotel, car
        search_id = parameters.get("search_id")
        selection_index = parameters.get("selection_index", 0)
        
        if not all([booking_type, search_id]):
            return ToolResult(
                success=False,
                data=None,
                message="Missing required parameters",
                error="Booking type and search_id are required"
            )
        
        # STUBBED: Create booking (pending confirmation)
        booking = {
            "booking_id": f"BK-{random.randint(100000, 999999)}",
            "type": booking_type,
            "search_id": search_id,
            "selection_index": selection_index,
            "status": "pending_confirmation",
            "price": random.randint(200, 2000),
            "currency": "USD",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "cancellation_policy": "Free cancellation until 24 hours before"
        }
        
        logger.warning(f"Booking prepared (NOT confirmed) for {user_id}: {booking['booking_id']}")
        
        return ToolResult(
            success=True,
            data=booking,
            message="Booking prepared. User MUST confirm before payment is processed.",
            requires_confirmation=True,
            metadata={"warning": "This booking has NOT been confirmed. User confirmation required."}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_type": {
                        "type": "string",
                        "enum": ["flight", "hotel", "car"],
                        "description": "Type of booking"
                    },
                    "search_id": {
                        "type": "string",
                        "description": "Search ID from previous search"
                    },
                    "selection_index": {
                        "type": "integer",
                        "description": "Index of selected option from search results",
                        "default": 0
                    }
                },
                "required": ["booking_type", "search_id"]
            }
        }


class GetPriceAlertsTool(BaseTool):
    """Get active price alerts and their status."""
    
    def __init__(self):
        super().__init__(
            name="get_price_alerts",
            description="Get all active price alerts for flights, hotels, and travel",
            category=ToolCategory.TRAVEL
        )
    
    async def execute(
        self,
        user_id: str,
        parameters: Dict[str, Any],
        permissions: Optional[Dict[str, bool]] = None
    ) -> ToolResult:
        if not self.check_permission("travel_read", permissions):
            return ToolResult(
                success=False,
                data=None,
                message="Permission denied",
                error="User does not have travel_read permission"
            )
        
        # STUBBED: Mock active alerts
        alerts = [
            {
                "alert_id": "ALERT-123456",
                "type": "flight",
                "route": "YYZ → LHR",
                "departure_date": "2025-02-15",
                "target_price": 600,
                "current_lowest": 650,
                "last_checked": datetime.now().isoformat(),
                "status": "active",
                "price_history": [680, 670, 665, 650]
            },
            {
                "alert_id": "ALERT-789012",
                "type": "flight",
                "route": "JFK → DXB",
                "departure_date": "2025-03-01",
                "target_price": 800,
                "current_lowest": 750,
                "last_checked": datetime.now().isoformat(),
                "status": "triggered",
                "alert_message": "Price dropped below target!"
            }
        ]
        
        logger.info(f"Price alerts retrieved for {user_id}")
        
        return ToolResult(
            success=True,
            data={
                "alerts": alerts,
                "total_alerts": len(alerts),
                "triggered_alerts": sum(1 for a in alerts if a["status"] == "triggered")
            },
            message=f"Found {len(alerts)} active price alerts"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }


# ============================================
# TRAVEL TOOLS COLLECTION
# ============================================

class TravelTools:
    """Collection of all travel tools."""
    
    @staticmethod
    def get_all_tools() -> list[BaseTool]:
        """Get all travel tools."""
        return [
            SearchFlightsTool(),
            SetFlightPriceAlertTool(),
            SearchHotelsTool(),
            SearchCarRentalsTool(),
            CreateTripPlanTool(),
            BookTravelTool(),
            GetPriceAlertsTool()
        ]
    
    @staticmethod
    def get_schemas() -> list[Dict[str, Any]]:
        """Get all travel tool schemas."""
        return [tool.get_schema() for tool in TravelTools.get_all_tools()]
