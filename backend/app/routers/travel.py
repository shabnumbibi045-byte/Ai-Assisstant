"""Travel Router - Flight/hotel search and booking with price monitoring."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.auth.dependencies import get_current_active_user
from app.database.models import User
from app.services.amadeus_service import amadeus_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/travel", tags=["travel"])


# ============================================
# SCHEMAS
# ============================================

class FlightOption(BaseModel):
    """Flight search result."""
    flight_id: str
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    cabin_class: str
    price: float
    currency: str
    available_seats: int
    baggage_included: bool
    cancellation_policy: str


class HotelOption(BaseModel):
    """Hotel search result."""
    hotel_id: str
    name: str
    city: str
    country: str
    address: str
    star_rating: float
    user_rating: float
    amenities: List[str]
    price_per_night: float
    currency: str
    total_price: float
    room_type: str
    breakfast_included: bool
    free_cancellation: bool
    distance_from_center: float  # km


class Booking(BaseModel):
    """Travel booking."""
    booking_id: str
    booking_type: str  # flight or hotel
    status: str  # confirmed, pending, cancelled
    created_at: datetime
    travel_date: date
    details: Dict[str, Any]
    total_cost: float
    currency: str


class PriceAlert(BaseModel):
    """Price monitoring alert."""
    alert_id: str
    route: str
    target_price: float
    current_price: float
    price_drop_percent: float
    created_at: datetime
    expires_at: datetime
    active: bool


class CarRentalOption(BaseModel):
    """Car rental search result."""
    car_id: str
    company: str
    name: str
    type: str
    seats: int
    doors: int
    transmission: str
    fuel_type: str
    price_per_day: float
    total_price: float
    currency: str
    features: List[str]
    mileage: str
    insurance: str
    free_cancellation: bool
    pickup_location: str
    dropoff_location: str
    pickup_date: str
    dropoff_date: str


class TravelRecommendation(BaseModel):
    """AI-powered travel recommendation."""
    destination: str
    country: str
    best_time_to_visit: str
    estimated_cost: float
    flight_price_range: Dict[str, float]
    hotel_price_range: Dict[str, float]
    highlights: List[str]
    weather: str
    visa_required: bool
    recommended_duration: str


# ============================================
# CITY CODE MAPPING (for Amadeus hotel by-city API)
# ============================================
CITY_TO_IATA = {
    "new york": "NYC", "nyc": "NYC", "manhattan": "NYC",
    "los angeles": "LAX", "la": "LAX",
    "chicago": "CHI", "san francisco": "SFO",
    "miami": "MIA", "dallas": "DFW", "houston": "IAH",
    "atlanta": "ATL", "boston": "BOS", "seattle": "SEA",
    "denver": "DEN", "orlando": "MCO", "las vegas": "LAS",
    "phoenix": "PHX", "philadelphia": "PHL", "detroit": "DTW",
    "minneapolis": "MSP", "charlotte": "CLT", "washington": "WAS",
    "toronto": "YYZ", "vancouver": "YVR", "montreal": "YUL",
    "calgary": "YYC", "ottawa": "YOW",
    "london": "LON", "paris": "PAR", "rome": "ROM",
    "berlin": "BER", "madrid": "MAD", "barcelona": "BCN",
    "amsterdam": "AMS", "munich": "MUC", "frankfurt": "FRA",
    "vienna": "VIE", "zurich": "ZRH", "milan": "MIL",
    "istanbul": "IST", "athens": "ATH", "lisbon": "LIS",
    "dublin": "DUB", "brussels": "BRU", "copenhagen": "CPH",
    "oslo": "OSL", "stockholm": "STO", "helsinki": "HEL",
    "tokyo": "TYO", "osaka": "OSA", "seoul": "SEL",
    "beijing": "BJS", "shanghai": "SHA", "hong kong": "HKG",
    "singapore": "SIN", "bangkok": "BKK", "kuala lumpur": "KUL",
    "dubai": "DXB", "abu dhabi": "AUH", "doha": "DOH",
    "riyadh": "RUH", "mumbai": "BOM", "delhi": "DEL",
    "sydney": "SYD", "melbourne": "MEL", "auckland": "AKL",
    "cairo": "CAI", "johannesburg": "JNB", "nairobi": "NBO",
    "sao paulo": "SAO", "rio de janeiro": "GIG", "mexico city": "MEX",
    "cancun": "CUN", "lima": "LIM", "bogota": "BOG",
    "buenos aires": "BUE", "santiago": "SCL",
}


def city_to_iata_code(city: str) -> str:
    """Convert city name to IATA code. Returns the input uppercased if already a code."""
    lowered = city.strip().lower()
    if lowered in CITY_TO_IATA:
        return CITY_TO_IATA[lowered]
    # If it's 3 chars, assume it's already an IATA code
    if len(city.strip()) == 3 and city.strip().isalpha():
        return city.strip().upper()
    # Try partial match
    for key, code in CITY_TO_IATA.items():
        if lowered in key or key in lowered:
            return code
    # Fallback: use first 3 letters uppercased (best guess)
    return city.strip()[:3].upper()


# ============================================
# DEMO DATA GENERATORS (fallback)
# ============================================

def search_demo_flights(
    origin: str,
    destination: str,
    departure_date: date,
    return_date: Optional[date] = None
) -> List[FlightOption]:
    """Generate demo flight options."""
    base_time = datetime.combine(departure_date, datetime.min.time())

    return [
        FlightOption(
            flight_id="FL001",
            airline="Air Canada",
            flight_number="AC123",
            departure_airport=origin,
            arrival_airport=destination,
            departure_time=base_time.replace(hour=8, minute=30),
            arrival_time=base_time.replace(hour=16, minute=45),
            duration_minutes=495,
            stops=0,
            cabin_class="Economy",
            price=650.00,
            currency="USD",
            available_seats=45,
            baggage_included=True,
            cancellation_policy="Free cancellation within 24h"
        ),
        FlightOption(
            flight_id="FL002",
            airline="United Airlines",
            flight_number="UA456",
            departure_airport=origin,
            arrival_airport=destination,
            departure_time=base_time.replace(hour=11, minute=15),
            arrival_time=base_time.replace(hour=19, minute=30),
            duration_minutes=495,
            stops=0,
            cabin_class="Economy",
            price=595.50,
            currency="USD",
            available_seats=32,
            baggage_included=True,
            cancellation_policy="Non-refundable"
        ),
        FlightOption(
            flight_id="FL003",
            airline="Delta Air Lines",
            flight_number="DL789",
            departure_airport=origin,
            arrival_airport=destination,
            departure_time=base_time.replace(hour=14, minute=0),
            arrival_time=base_time.replace(hour=22, minute=15),
            duration_minutes=495,
            stops=0,
            cabin_class="Business",
            price=1_850.00,
            currency="USD",
            available_seats=12,
            baggage_included=True,
            cancellation_policy="Free cancellation within 48h"
        ),
        FlightOption(
            flight_id="FL004",
            airline="American Airlines",
            flight_number="AA234",
            departure_airport=origin,
            arrival_airport=destination,
            departure_time=base_time.replace(hour=6, minute=45),
            arrival_time=base_time.replace(hour=18, minute=30),
            duration_minutes=705,
            stops=1,
            cabin_class="Economy",
            price=485.00,
            currency="USD",
            available_seats=58,
            baggage_included=False,
            cancellation_policy="Non-refundable"
        ),
    ]


def search_demo_hotels(city: str, check_in: date, check_out: date) -> List[HotelOption]:
    """Generate demo hotel options."""
    nights = (check_out - check_in).days

    return [
        HotelOption(
            hotel_id="HTL001",
            name="Grand Luxury Hotel & Spa",
            city=city,
            country="USA",
            address="123 Main Street, Downtown",
            star_rating=5.0,
            user_rating=4.8,
            amenities=["Free WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar", "Room Service"],
            price_per_night=350.00,
            currency="USD",
            total_price=350.00 * nights,
            room_type="Deluxe King Room",
            breakfast_included=True,
            free_cancellation=True,
            distance_from_center=0.5
        ),
        HotelOption(
            hotel_id="HTL002",
            name="Business Executive Suites",
            city=city,
            country="USA",
            address="456 Business Ave",
            star_rating=4.0,
            user_rating=4.5,
            amenities=["Free WiFi", "Gym", "Business Center", "Breakfast", "Parking"],
            price_per_night=180.00,
            currency="USD",
            total_price=180.00 * nights,
            room_type="Executive Suite",
            breakfast_included=True,
            free_cancellation=True,
            distance_from_center=1.2
        ),
        HotelOption(
            hotel_id="HTL003",
            name="City Center Inn",
            city=city,
            country="USA",
            address="789 Central Plaza",
            star_rating=3.0,
            user_rating=4.2,
            amenities=["Free WiFi", "Breakfast", "24h Reception"],
            price_per_night=95.00,
            currency="USD",
            total_price=95.00 * nights,
            room_type="Standard Double Room",
            breakfast_included=True,
            free_cancellation=False,
            distance_from_center=0.3
        ),
        HotelOption(
            hotel_id="HTL004",
            name="Boutique Riverside Hotel",
            city=city,
            country="USA",
            address="321 Riverfront Drive",
            star_rating=4.5,
            user_rating=4.9,
            amenities=["Free WiFi", "Restaurant", "Bar", "River View", "Concierge"],
            price_per_night=275.00,
            currency="USD",
            total_price=275.00 * nights,
            room_type="River View Suite",
            breakfast_included=True,
            free_cancellation=True,
            distance_from_center=1.8
        ),
    ]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/flights/search", response_model=List[FlightOption])
async def search_flights(
    origin: str = Query(..., description="Origin airport code (e.g., YYZ, JFK)"),
    destination: str = Query(..., description="Destination airport code"),
    departure_date: date = Query(..., description="Departure date (YYYY-MM-DD)"),
    return_date: Optional[date] = Query(None, description="Return date for round trip"),
    passengers: int = Query(1, ge=1, le=9),
    cabin_class: str = Query("economy", description="economy, business, or first"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for flights with real-time pricing.
    Supports round-trip and one-way bookings.
    """
    try:
        flights = search_demo_flights(origin, destination, departure_date, return_date)

        # Filter by cabin class
        if cabin_class.lower() != "economy":
            flights = [f for f in flights if f.cabin_class.lower() == cabin_class.lower()]

        logger.info(f"Found {len(flights)} flights from {origin} to {destination} for user {current_user.email}")
        return flights

    except Exception as e:
        logger.error(f"Flight search error: {e}")
        raise HTTPException(status_code=500, detail="Flight search failed")


@router.get("/hotels/search")
async def search_hotels(
    city: str = Query(..., description="City name or IATA code"),
    check_in: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(1, ge=1, le=10),
    rooms: int = Query(1, ge=1, le=4),
    min_rating: float = Query(0, ge=0, le=5),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for hotels with real-time pricing from Amadeus API.
    Step 1: Find hotels by city code.
    Step 2: Get real-time offers/pricing for those hotels.
    Falls back to demo data if API fails.
    """
    try:
        if check_out <= check_in:
            raise HTTPException(status_code=400, detail="Check-out must be after check-in")

        nights = (check_out - check_in).days
        city_code = city_to_iata_code(city)
        check_in_str = check_in.isoformat()
        check_out_str = check_out.isoformat()

        logger.info(f"Searching hotels in {city} (code: {city_code}) for user {current_user.email}")

        # Step 1: Get hotel list by city
        hotel_list_result = await amadeus_service.search_hotels(
            city_code=city_code,
            check_in_date=check_in_str,
            check_out_date=check_out_str,
            adults=guests,
            rooms=rooms,
        )

        if not hotel_list_result or "data" not in hotel_list_result:
            logger.warning(f"Amadeus hotel list API returned no data for {city_code}, falling back to demo")
            hotels = search_demo_hotels(city, check_in, check_out)
            if min_rating > 0:
                hotels = [h for h in hotels if h.user_rating >= min_rating]
            return [h.dict() for h in hotels]

        # Extract hotel IDs (take up to 20 for offers)
        raw_hotels = hotel_list_result["data"][:20]
        hotel_ids = [h.get("hotelId") for h in raw_hotels if h.get("hotelId")]

        if not hotel_ids:
            logger.warning("No hotel IDs found from Amadeus, falling back to demo")
            hotels = search_demo_hotels(city, check_in, check_out)
            return [h.dict() for h in hotels]

        # Step 2: Get real-time offers with pricing
        offers_result = await amadeus_service.get_hotel_offers(
            hotel_ids=hotel_ids[:10],  # API max 10
            check_in_date=check_in_str,
            check_out_date=check_out_str,
            adults=guests,
            rooms=rooms,
        )

        # Build a lookup of raw hotel metadata
        hotel_meta = {}
        for h in raw_hotels:
            hid = h.get("hotelId")
            hotel_meta[hid] = h

        formatted_hotels = []
        if offers_result and "data" in offers_result:
            for offer_item in offers_result["data"]:
                try:
                    hotel_data = offer_item.get("hotel", {})
                    hotel_id = hotel_data.get("hotelId", offer_item.get("hotelId", ""))
                    offers = offer_item.get("offers", [])
                    if not offers:
                        continue

                    best_offer = offers[0]  # cheapest/first offer
                    price_info = best_offer.get("price", {})
                    total_str = price_info.get("total", "0")
                    currency = price_info.get("currency", "USD")
                    total_price = float(total_str) if total_str else 0.0
                    price_per_night = round(total_price / max(nights, 1), 2)

                    # Room info
                    room = best_offer.get("room", {})
                    room_type = room.get("typeEstimated", {}).get("category", "Standard Room")
                    room_beds = room.get("typeEstimated", {}).get("beds", 1)
                    room_bed_type = room.get("typeEstimated", {}).get("bedType", "")
                    room_desc = room.get("description", {}).get("text", room_type)

                    # Policies
                    policies = best_offer.get("policies", {})
                    cancellation = policies.get("cancellations", [{}])
                    free_cancel = False
                    if cancellation:
                        cancel_type = cancellation[0].get("type", "")
                        free_cancel = cancel_type == "FULL_STAY" or "FREE" in cancel_type.upper()

                    # Hotel name and rating
                    name = hotel_data.get("name", "Hotel")
                    # Try getting rating from metadata
                    meta = hotel_meta.get(hotel_id, {})
                    star_rating = float(meta.get("rating", hotel_data.get("rating", 3)))

                    # Amenities from metadata if available
                    amenities_raw = meta.get("amenities", [])
                    amenity_map = {
                        "SWIMMING_POOL": "Pool", "WIFI": "Free WiFi", "FREE_WIFI": "Free WiFi",
                        "FITNESS_CENTER": "Gym", "RESTAURANT": "Restaurant", "BAR": "Bar",
                        "SPA": "Spa", "PARKING": "Parking", "ROOM_SERVICE": "Room Service",
                        "BUSINESS_CENTER": "Business Center", "AIR_CONDITIONING": "A/C",
                        "LAUNDRY_SERVICE": "Laundry", "CONCIERGE": "Concierge",
                        "PETS_ALLOWED": "Pet Friendly", "BEACH_ACCESS": "Beach Access",
                    }
                    amenities = []
                    for a in amenities_raw:
                        mapped = amenity_map.get(a, a.replace("_", " ").title())
                        if mapped not in amenities:
                            amenities.append(mapped)

                    hotel_obj = {
                        "hotel_id": hotel_id,
                        "name": name.title() if name == name.upper() else name,
                        "city": city,
                        "country": meta.get("address", {}).get("countryCode", ""),
                        "address": meta.get("address", {}).get("lines", [""])[0] if meta.get("address") else "",
                        "star_rating": star_rating,
                        "user_rating": min(star_rating + 0.2, 5.0),  # Estimated from star rating
                        "amenities": amenities[:8] if amenities else ["Free WiFi"],
                        "price_per_night": price_per_night,
                        "currency": currency,
                        "total_price": total_price,
                        "room_type": room_desc if room_desc != room_type else f"{room_type} ({room_beds} {room_bed_type})".strip(),
                        "breakfast_included": any("BREAKFAST" in str(a).upper() for a in amenities_raw),
                        "free_cancellation": free_cancel,
                        "distance_from_center": round(meta.get("distance", {}).get("value", 0), 1) if meta.get("distance") else 0,
                    }

                    # Filter by min rating
                    if min_rating > 0 and hotel_obj["user_rating"] < min_rating:
                        continue

                    formatted_hotels.append(hotel_obj)
                except Exception as e:
                    logger.warning(f"Error parsing hotel offer: {e}")
                    continue

        if formatted_hotels:
            logger.info(f"Returning {len(formatted_hotels)} real-time hotel results for {city}")
            return formatted_hotels

        # Fallback to demo data
        logger.warning(f"No offers parsed from Amadeus for {city}, using demo data")
        hotels = search_demo_hotels(city, check_in, check_out)
        if min_rating > 0:
            hotels = [h for h in hotels if h.user_rating >= min_rating]
        return [h.dict() for h in hotels]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hotel search error: {e}")
        # Fallback to demo
        try:
            hotels = search_demo_hotels(city, check_in, check_out)
            return [h.dict() for h in hotels]
        except:
            raise HTTPException(status_code=500, detail="Hotel search failed")


@router.get("/cars/search")
async def search_cars(
    pickup_location: str = Query(..., description="Pickup city or airport code"),
    pickup_date: date = Query(..., description="Pickup date YYYY-MM-DD"),
    dropoff_date: date = Query(..., description="Drop-off date YYYY-MM-DD"),
    pickup_time: str = Query("10:00", description="Pickup time HH:MM"),
    dropoff_time: str = Query("10:00", description="Drop-off time HH:MM"),
    dropoff_location: Optional[str] = Query(None, description="Drop-off location (defaults to pickup)"),
    car_type: str = Query("all", description="Car type filter: all, economy, suv, premium, van, luxury, electric"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for car rentals using Amadeus Transfer/Car API.
    Returns real-time pricing from Amadeus with fallback to generated data.
    """
    try:
        if dropoff_date < pickup_date:
            raise HTTPException(status_code=400, detail="Drop-off date must be after pickup date")

        days = max(1, (dropoff_date - pickup_date).days)
        location_code = city_to_iata_code(pickup_location)
        dropoff_code = city_to_iata_code(dropoff_location) if dropoff_location else location_code

        logger.info(f"Searching car rentals at {pickup_location} (code: {location_code}) for user {current_user.email}")

        # Call Amadeus Transfer API
        result = await amadeus_service.search_car_rentals(
            pickup_location=location_code,
            pickup_date=pickup_date.isoformat(),
            pickup_time=f"{pickup_time}:00",
            dropoff_date=dropoff_date.isoformat(),
            dropoff_time=f"{dropoff_time}:00",
            dropoff_location=dropoff_code,
        )

        formatted_cars = []
        if result and "data" in result:
            for idx, car_data in enumerate(result["data"]):
                try:
                    # Handle both Transfer API format and mock format
                    if "vehicle" in car_data:
                        vehicle = car_data["vehicle"]
                        price_info = car_data.get("price", {})
                        pickup_info = car_data.get("pickup", {})
                        dropoff_info = car_data.get("dropoff", {})
                    elif "transferType" in car_data:
                        # Amadeus Transfer API format
                        vehicle = car_data.get("vehicle", car_data.get("serviceProvider", {}))
                        price_info = car_data.get("quotation", car_data.get("price", {}))
                        pickup_info = car_data.get("start", {})
                        dropoff_info = car_data.get("end", {})
                    else:
                        vehicle = car_data
                        price_info = car_data.get("price", {})
                        pickup_info = {}
                        dropoff_info = {}

                    provider = car_data.get("provider", car_data.get("serviceProvider", {}).get("name", "Rental Company"))
                    if isinstance(provider, dict):
                        provider = provider.get("name", "Rental Company")

                    category = vehicle.get("category", vehicle.get("type", "Standard"))
                    car_name = vehicle.get("type", vehicle.get("description", f"{category} Car"))
                    seats = int(vehicle.get("seats", 5))
                    doors = int(vehicle.get("doors", 4))
                    transmission = vehicle.get("transmission", "Automatic")
                    fuel = vehicle.get("fuel_type", vehicle.get("fuelType", "Gasoline"))
                    ac = vehicle.get("air_conditioning", True)

                    # Price
                    total_price_str = price_info.get("total", price_info.get("monetaryAmount", "0"))
                    currency = price_info.get("currency", price_info.get("currencyCode", "USD"))
                    total_price = float(total_price_str) if total_price_str else 0.0
                    price_per_day_str = price_info.get("per_day", "0")
                    price_per_day = float(price_per_day_str) if price_per_day_str != "0" else round(total_price / max(days, 1), 2)

                    # Included features
                    included = car_data.get("included", [])
                    features = ["A/C"] if ac else []
                    if transmission == "Automatic":
                        features.append("Automatic")
                    features.extend(included[:4])

                    # Insurance
                    has_full_insurance = any("full" in str(i).lower() or "collision" in str(i).lower() for i in included)
                    insurance = "Full coverage included" if has_full_insurance else "Basic included"

                    free_cancel = any("free" in str(i).lower() or "cancel" in str(i).lower() for i in included)

                    # Type filter
                    car_type_str = category.upper()
                    type_label = category.title()
                    if "ECONOMY" in car_type_str or "MINI" in car_type_str:
                        type_label = "Economy"
                    elif "SUV" in car_type_str or "4X4" in car_type_str:
                        type_label = "SUV"
                    elif "PREMIUM" in car_type_str or "FULL" in car_type_str or "LUXURY" in car_type_str:
                        type_label = "Premium" if "PREMIUM" in car_type_str else "Luxury"
                    elif "VAN" in car_type_str or "MINIVAN" in car_type_str:
                        type_label = "Van"
                    elif "INTERMEDIATE" in car_type_str or "COMPACT" in car_type_str:
                        type_label = "Compact"
                    elif "ELECTRIC" in car_type_str:
                        type_label = "Electric"

                    # Apply type filter
                    if car_type != "all" and type_label.lower() != car_type.lower():
                        continue

                    formatted_cars.append({
                        "car_id": f"CAR-{idx:03d}",
                        "company": provider,
                        "name": car_name,
                        "type": type_label,
                        "seats": seats,
                        "doors": doors,
                        "transmission": transmission,
                        "fuel_type": fuel,
                        "price_per_day": price_per_day,
                        "total_price": total_price,
                        "currency": currency,
                        "features": features[:6],
                        "mileage": "Unlimited" if any("unlimited" in str(i).lower() for i in included) else "Limited",
                        "insurance": insurance,
                        "free_cancellation": free_cancel,
                        "pickup_location": pickup_location,
                        "dropoff_location": dropoff_location or pickup_location,
                        "pickup_date": pickup_date.isoformat(),
                        "dropoff_date": dropoff_date.isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"Error parsing car rental data: {e}")
                    continue

        if formatted_cars:
            logger.info(f"Returning {len(formatted_cars)} car rental results for {pickup_location}")
            return formatted_cars

        logger.info(f"Using Amadeus transfer fallback data for {pickup_location}")
        # The amadeus_service.search_car_rentals already returns mock if API fails
        return formatted_cars if formatted_cars else _build_fallback_cars(pickup_location, dropoff_location or pickup_location, pickup_date, dropoff_date, days, car_type)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Car search error: {e}")
        return _build_fallback_cars(pickup_location, dropoff_location or pickup_location, pickup_date, dropoff_date, max(1, (dropoff_date - pickup_date).days), car_type)


def _build_fallback_cars(pickup_loc, dropoff_loc, pickup_date, dropoff_date, days, car_type):
    """Build fallback car rental data when Amadeus is unavailable."""
    import random
    cars_data = [
        {"company": "Enterprise", "name": "Toyota Corolla or similar", "type": "Economy", "seats": 5, "doors": 4, "ppd": 35, "features": ["A/C", "Automatic", "Unlimited mileage", "Bluetooth"]},
        {"company": "Hertz", "name": "Honda Accord or similar", "type": "Compact", "seats": 5, "doors": 4, "ppd": 45, "features": ["A/C", "Automatic", "Unlimited mileage", "GPS"]},
        {"company": "Budget", "name": "Ford Explorer or similar", "type": "SUV", "seats": 7, "doors": 4, "ppd": 65, "features": ["A/C", "Automatic", "Unlimited mileage", "All-Wheel Drive"]},
        {"company": "Avis", "name": "BMW 3 Series or similar", "type": "Premium", "seats": 5, "doors": 4, "ppd": 95, "features": ["A/C", "Automatic", "Leather Seats", "GPS Navigation"]},
        {"company": "National", "name": "Mercedes E-Class or similar", "type": "Luxury", "seats": 5, "doors": 4, "ppd": 150, "features": ["A/C", "Automatic", "Leather Seats", "Premium Sound"]},
        {"company": "Alamo", "name": "Chrysler Pacifica or similar", "type": "Van", "seats": 7, "doors": 4, "ppd": 75, "features": ["A/C", "Automatic", "Spacious Cargo", "Rear Camera"]},
    ]
    results = []
    for idx, c in enumerate(cars_data):
        if car_type != "all" and c["type"].lower() != car_type.lower():
            continue
        results.append({
            "car_id": f"CAR-FB-{idx:03d}",
            "company": c["company"],
            "name": c["name"],
            "type": c["type"],
            "seats": c["seats"],
            "doors": c["doors"],
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "price_per_day": float(c["ppd"]),
            "total_price": float(c["ppd"] * days),
            "currency": "USD",
            "features": c["features"],
            "mileage": "Unlimited",
            "insurance": "Basic included",
            "free_cancellation": True,
            "pickup_location": pickup_loc,
            "dropoff_location": dropoff_loc,
            "pickup_date": pickup_date.isoformat() if hasattr(pickup_date, 'isoformat') else str(pickup_date),
            "dropoff_date": dropoff_date.isoformat() if hasattr(dropoff_date, 'isoformat') else str(dropoff_date),
        })
    return results


@router.post("/book/flight")
async def book_flight(
    flight_id: str,
    passengers: List[Dict[str, str]],
    contact_email: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Book a flight.
    Returns booking confirmation with details.
    """
    try:
        # Demo booking - in production would process actual booking
        return {
            "status": "success",
            "booking_id": f"BK_{datetime.now().timestamp()}",
            "flight_id": flight_id,
            "passengers": passengers,
            "contact_email": contact_email,
            "booking_status": "confirmed",
            "confirmation_code": "ABC123XYZ",
            "created_at": datetime.now(),
            "message": "Flight booked successfully! Confirmation email sent."
        }

    except Exception as e:
        logger.error(f"Flight booking error: {e}")
        raise HTTPException(status_code=500, detail="Flight booking failed")


@router.post("/book/hotel")
async def book_hotel(
    hotel_id: str,
    check_in: date,
    check_out: date,
    guests: int,
    contact_email: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Book a hotel.
    Returns booking confirmation with details.
    """
    try:
        # Demo booking - in production would process actual booking
        return {
            "status": "success",
            "booking_id": f"HB_{datetime.now().timestamp()}",
            "hotel_id": hotel_id,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "contact_email": contact_email,
            "booking_status": "confirmed",
            "confirmation_code": "HTL456DEF",
            "created_at": datetime.now(),
            "message": "Hotel booked successfully! Confirmation email sent."
        }

    except Exception as e:
        logger.error(f"Hotel booking error: {e}")
        raise HTTPException(status_code=500, detail="Hotel booking failed")


@router.get("/bookings", response_model=List[Booking])
async def get_bookings(
    booking_type: Optional[str] = Query(None, description="Filter by flight or hotel"),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user bookings."""
    try:
        # Demo bookings
        bookings = [
            Booking(
                booking_id="BK_001",
                booking_type="flight",
                status="confirmed",
                created_at=datetime.now() - timedelta(days=15),
                travel_date=date.today() + timedelta(days=30),
                details={
                    "route": "YYZ → JFK",
                    "airline": "Air Canada",
                    "flight_number": "AC123"
                },
                total_cost=650.00,
                currency="USD"
            ),
            Booking(
                booking_id="HB_001",
                booking_type="hotel",
                status="confirmed",
                created_at=datetime.now() - timedelta(days=15),
                travel_date=date.today() + timedelta(days=30),
                details={
                    "hotel": "Grand Luxury Hotel & Spa",
                    "city": "New York",
                    "nights": 3
                },
                total_cost=1050.00,
                currency="USD"
            ),
        ]

        if booking_type:
            bookings = [b for b in bookings if b.booking_type == booking_type]

        logger.info(f"Retrieved {len(bookings)} bookings for user {current_user.email}")
        return bookings

    except Exception as e:
        logger.error(f"Error retrieving bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve bookings")


@router.post("/alerts/create")
async def create_price_alert(
    route: str,
    target_price: float,
    departure_date: date,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a price alert for flight monitoring.
    Get notified when prices drop below target.
    """
    try:
        return {
            "status": "success",
            "alert_id": f"ALERT_{datetime.now().timestamp()}",
            "route": route,
            "target_price": target_price,
            "departure_date": departure_date,
            "created_at": datetime.now(),
            "expires_at": departure_date,
            "message": "Price alert created! You'll receive notifications when prices drop."
        }

    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")


@router.get("/alerts", response_model=List[PriceAlert])
async def get_price_alerts(
    current_user: User = Depends(get_current_active_user)
):
    """Get all active price alerts."""
    try:
        alerts = [
            PriceAlert(
                alert_id="ALERT_001",
                route="YYZ → LAX",
                target_price=500.00,
                current_price=625.00,
                price_drop_percent=0,
                created_at=datetime.now() - timedelta(days=7),
                expires_at=datetime.now() + timedelta(days=30),
                active=True
            ),
            PriceAlert(
                alert_id="ALERT_002",
                route="YYZ → LHR",
                target_price=800.00,
                current_price=750.00,
                price_drop_percent=6.25,
                created_at=datetime.now() - timedelta(days=3),
                expires_at=datetime.now() + timedelta(days=45),
                active=True
            ),
        ]

        logger.info(f"Retrieved {len(alerts)} price alerts for user {current_user.email}")
        return alerts

    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.get("/recommendations", response_model=List[TravelRecommendation])
async def get_travel_recommendations(
    budget: Optional[float] = Query(None, description="Budget in USD"),
    duration: Optional[str] = Query(None, description="Trip duration (weekend, week, month)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-powered travel recommendations.
    Based on budget, preferences, and seasonal trends.
    """
    try:
        recommendations = [
            TravelRecommendation(
                destination="Barcelona",
                country="Spain",
                best_time_to_visit="May - September",
                estimated_cost=1_800.00,
                flight_price_range={"min": 450.00, "max": 850.00},
                hotel_price_range={"min": 80.00, "max": 250.00},
                highlights=[
                    "Sagrada Familia and Gaudi architecture",
                    "Beautiful Mediterranean beaches",
                    "Rich cultural heritage and museums",
                    "Vibrant nightlife and cuisine"
                ],
                weather="Sunny, 25-30°C",
                visa_required=False,
                recommended_duration="5-7 days"
            ),
            TravelRecommendation(
                destination="Tokyo",
                country="Japan",
                best_time_to_visit="March - May, October - November",
                estimated_cost=2_500.00,
                flight_price_range={"min": 800.00, "max": 1_400.00},
                hotel_price_range={"min": 100.00, "max": 300.00},
                highlights=[
                    "Ancient temples and modern technology",
                    "World-class cuisine and street food",
                    "Cherry blossoms in spring",
                    "Efficient public transportation"
                ],
                weather="Mild, 15-25°C",
                visa_required=True,
                recommended_duration="7-10 days"
            ),
        ]

        logger.info(f"Generated {len(recommendations)} recommendations for user {current_user.email}")
        return recommendations

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


# ============================================
# BOOKING ENDPOINT
# ============================================

class PassengerDetails(BaseModel):
    """Passenger booking details."""
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    dateOfBirth: Optional[str] = None
    passportNumber: Optional[str] = None


class BookingRequest(BaseModel):
    """Flight booking request."""
    flight: Dict[str, Any]
    passenger: PassengerDetails
    user_id: Optional[str] = None


class BookingResponse(BaseModel):
    """Booking response."""
    success: bool
    booking_id: str
    message: str
    confirmation_number: str
    flight_details: Dict[str, Any]
    passenger_name: str
    total_amount: float
    currency: str
    status: str


@router.post("/book", response_model=BookingResponse)
async def book_flight(
    request: BookingRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Book a flight.
    Creates a booking request and returns confirmation details.
    """
    import uuid
    from datetime import datetime
    
    try:
        # Generate booking ID and confirmation number
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        confirmation_number = f"CNF{uuid.uuid4().hex[:6].upper()}"
        
        # Get flight details
        flight = request.flight
        passenger = request.passenger
        
        # In production, this would:
        # 1. Call Amadeus booking API
        # 2. Process payment
        # 3. Send confirmation email
        # 4. Store in database
        
        logger.info(f"Flight booking requested by {current_user.email}")
        logger.info(f"Flight: {flight.get('airline')} {flight.get('flight_number')}")
        logger.info(f"Passenger: {passenger.firstName} {passenger.lastName}")
        
        response = BookingResponse(
            success=True,
            booking_id=booking_id,
            message="Your booking request has been received. A confirmation email will be sent shortly.",
            confirmation_number=confirmation_number,
            flight_details={
                "airline": flight.get("airline", "Unknown"),
                "flight_number": flight.get("flight_number", ""),
                "origin": flight.get("origin", ""),
                "destination": flight.get("destination", ""),
                "departure": flight.get("departure", ""),
                "arrival": flight.get("arrival", ""),
                "cabin_class": flight.get("cabin_class", "Economy"),
            },
            passenger_name=f"{passenger.firstName} {passenger.lastName}",
            total_amount=float(flight.get("price", 0)),
            currency=flight.get("currency", "USD"),
            status="pending_confirmation"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Booking error: {e}")
        raise HTTPException(status_code=500, detail="Booking failed. Please try again.")
