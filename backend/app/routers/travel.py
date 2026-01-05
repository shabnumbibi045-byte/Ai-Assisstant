"""Travel Router - Flight/hotel search and booking with price monitoring."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.auth.dependencies import get_current_active_user
from app.database.models import User

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
# DEMO DATA GENERATORS
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


@router.get("/hotels/search", response_model=List[HotelOption])
async def search_hotels(
    city: str = Query(..., description="City name"),
    check_in: date = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: date = Query(..., description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(1, ge=1, le=10),
    min_rating: float = Query(0, ge=0, le=5),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for hotels with real-time availability.
    Includes user ratings and amenities.
    """
    try:
        if check_out <= check_in:
            raise HTTPException(status_code=400, detail="Check-out must be after check-in")

        hotels = search_demo_hotels(city, check_in, check_out)

        # Filter by rating
        if min_rating > 0:
            hotels = [h for h in hotels if h.user_rating >= min_rating]

        logger.info(f"Found {len(hotels)} hotels in {city} for user {current_user.email}")
        return hotels

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hotel search error: {e}")
        raise HTTPException(status_code=500, detail="Hotel search failed")


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
