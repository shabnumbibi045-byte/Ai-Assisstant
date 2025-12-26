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
        
        # STUBBED: Mock flight search results from multiple providers
        airlines = ["Air Canada", "United Airlines", "Delta", "American Airlines", "British Airways", "Emirates", "Kenya Airways"]
        
        results = []
        
        # FareCompare results
        for i in range(3):
            base_price = random.randint(400, 1500)
            results.append({
                "provider": "FareCompare",
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(['AC', 'UA', 'DL', 'AA', 'BA'])}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure": f"{departure_date}T{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival": f"{departure_date}T{random.randint(10, 23):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                "stops": random.randint(0, 2),
                "cabin_class": cabin_class,
                "price": base_price,
                "currency": "USD",
                "total_price": base_price * passengers,
                "baggage": "1 carry-on, 1 checked",
                "refundable": random.choice([True, False]),
                "booking_link": "https://farecompare.com/book/..."
            })
        
        # Expedia results
        for i in range(3):
            base_price = random.randint(380, 1400)
            results.append({
                "provider": "Expedia",
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(['AC', 'UA', 'DL', 'AA', 'BA'])}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure": f"{departure_date}T{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival": f"{departure_date}T{random.randint(10, 23):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                "stops": random.randint(0, 2),
                "cabin_class": cabin_class,
                "price": base_price,
                "currency": "USD",
                "total_price": base_price * passengers,
                "baggage": "1 carry-on included",
                "refundable": random.choice([True, False]),
                "booking_link": "https://expedia.com/book/..."
            })
        
        # Priceline VIP Platinum results (with member discount)
        for i in range(3):
            base_price = random.randint(350, 1300)  # Better rates for VIP
            vip_discount = int(base_price * 0.08)  # 8% VIP discount
            results.append({
                "provider": "Priceline",
                "provider_tier": "VIP Platinum",
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(['AC', 'UA', 'DL', 'AA', 'BA'])}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure": f"{departure_date}T{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival": f"{departure_date}T{random.randint(10, 23):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                "stops": random.randint(0, 2),
                "cabin_class": cabin_class,
                "original_price": base_price,
                "vip_discount": vip_discount,
                "price": base_price - vip_discount,
                "currency": "USD",
                "total_price": (base_price - vip_discount) * passengers,
                "baggage": "1 carry-on, 1 checked (VIP benefit)",
                "vip_benefits": ["Priority boarding", "Free seat selection", "Flexible cancellation"],
                "refundable": True,
                "booking_link": "https://priceline.com/vip/book/..."
            })
        
        # Direct airline results
        for i in range(2):
            airline = random.choice(airlines)
            base_price = random.randint(420, 1600)
            results.append({
                "provider": "Direct Airline",
                "airline": airline,
                "flight_number": f"{airline[:2].upper()}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure": f"{departure_date}T{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "arrival": f"{departure_date}T{random.randint(10, 23):02d}:{random.choice(['00', '15', '30', '45'])}:00",
                "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                "stops": random.randint(0, 1),
                "cabin_class": cabin_class,
                "price": base_price,
                "currency": "USD",
                "total_price": base_price * passengers,
                "baggage": "2 checked bags",
                "miles_earned": random.randint(2000, 8000),
                "refundable": random.choice([True, False]),
                "booking_link": f"https://{airline.lower().replace(' ', '')}.com/book/..."
            })
        
        # Sort by price
        results.sort(key=lambda x: x["price"])
        
        # Find best deal
        best_deal = results[0]
        
        logger.info(f"Flight search completed for {user_id}: {origin} -> {destination}, {len(results)} results")
        
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
                    "max": results[-1]["price"]
                },
                "searched_at": datetime.now().isoformat()
            },
            message=f"Found {len(results)} flights. Best price: ${best_deal['price']} on {best_deal['provider']}"
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
    """Search hotels across multiple providers."""
    
    def __init__(self):
        super().__init__(
            name="search_hotels",
            description="Search for hotels across Expedia, Priceline (VIP), and other providers",
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
        nights = (check_out_dt - check_in_dt).days
        
        # STUBBED: Mock hotel results
        hotel_chains = ["Marriott", "Hilton", "Hyatt", "Sheraton", "Holiday Inn", "Best Western", "Four Seasons", "Ritz-Carlton"]
        
        results = []
        
        # Expedia results
        for i in range(4):
            nightly_rate = random.randint(100, 500)
            results.append({
                "provider": "Expedia",
                "hotel_name": f"{random.choice(hotel_chains)} {location}",
                "star_rating": random.randint(3, 5),
                "location": location,
                "address": f"{random.randint(100, 999)} {random.choice(['Main', 'Park', 'Ocean', 'Lake'])} Street",
                "nightly_rate": nightly_rate,
                "total_price": nightly_rate * nights,
                "currency": "USD",
                "room_type": random.choice(["Standard King", "Double Queen", "Suite", "Deluxe King"]),
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Parking"],
                "rating": round(random.uniform(7.5, 9.5), 1),
                "reviews": random.randint(500, 5000),
                "free_cancellation": random.choice([True, False]),
                "breakfast_included": random.choice([True, False]),
                "booking_link": "https://expedia.com/hotel/..."
            })
        
        # Priceline VIP results
        for i in range(4):
            nightly_rate = random.randint(90, 450)  # Better VIP rates
            vip_discount = int(nightly_rate * 0.10)  # 10% VIP discount
            results.append({
                "provider": "Priceline",
                "provider_tier": "VIP Platinum",
                "hotel_name": f"{random.choice(hotel_chains)} {location}",
                "star_rating": random.randint(3, 5),
                "location": location,
                "address": f"{random.randint(100, 999)} {random.choice(['Main', 'Park', 'Ocean', 'Lake'])} Avenue",
                "original_nightly_rate": nightly_rate,
                "vip_discount_per_night": vip_discount,
                "nightly_rate": nightly_rate - vip_discount,
                "total_price": (nightly_rate - vip_discount) * nights,
                "currency": "USD",
                "room_type": random.choice(["Standard King", "Double Queen", "Suite", "Deluxe King"]),
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Parking"],
                "rating": round(random.uniform(7.5, 9.5), 1),
                "reviews": random.randint(500, 5000),
                "vip_benefits": ["Room upgrade when available", "Late checkout", "VIP welcome"],
                "free_cancellation": True,
                "breakfast_included": random.choice([True, False]),
                "booking_link": "https://priceline.com/vip/hotel/..."
            })
        
        # Sort by price
        results.sort(key=lambda x: x["total_price"])
        
        best_deal = results[0]
        
        logger.info(f"Hotel search completed for {user_id}: {location}, {len(results)} results")
        
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
                "searched_at": datetime.now().isoformat()
            },
            message=f"Found {len(results)} hotels. Best price: ${best_deal['nightly_rate']}/night at {best_deal['hotel_name']}"
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
    """Search car rentals across providers."""
    
    def __init__(self):
        super().__init__(
            name="search_car_rentals",
            description="Search for car rentals from Enterprise, Hertz, and other providers",
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
        days = (return_dt - pickup_dt).days
        
        # STUBBED: Mock car rental results
        providers = ["Enterprise", "Hertz", "Avis", "Budget", "National", "Alamo"]
        car_types = ["Economy", "Compact", "Midsize", "Full-size", "SUV", "Premium", "Luxury"]
        
        results = []
        
        for provider in providers[:4]:
            for ct in (car_types if not car_type else [car_type]):
                daily_rate = random.randint(30, 150)
                results.append({
                    "provider": provider,
                    "car_type": ct,
                    "car_model": random.choice(["Toyota Corolla", "Honda Civic", "Ford Escape", "Jeep Cherokee", "BMW 3 Series"]),
                    "pickup_location": pickup_location,
                    "daily_rate": daily_rate,
                    "total_price": daily_rate * days,
                    "currency": "USD",
                    "features": ["Automatic", "A/C", "Bluetooth", "GPS"],
                    "mileage": "Unlimited",
                    "insurance_included": random.choice([True, False]),
                    "free_cancellation": random.choice([True, False]),
                    "booking_link": f"https://{provider.lower()}.com/book/..."
                })
        
        # Sort by price
        results.sort(key=lambda x: x["total_price"])
        
        best_deal = results[0]
        
        logger.info(f"Car rental search completed for {user_id}: {pickup_location}, {len(results)} results")
        
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
                "searched_at": datetime.now().isoformat()
            },
            message=f"Found {len(results)} car rentals. Best price: ${best_deal['daily_rate']}/day from {best_deal['provider']}"
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
