import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../store/authStore';
import api from '../../services/api';
import {
  HiArrowLeft,
  HiArrowRight,
  HiCheck,
  HiClock,
  HiLocationMarker,
  HiUser,
  HiMail,
  HiPhone,
  HiIdentification,
  HiCalendar,
  HiShieldCheck,
  HiTicket,
  HiPrinter,
  HiDownload,
} from 'react-icons/hi';
import { FaPlane, FaSuitcase, FaBarcode } from 'react-icons/fa';

// Steps for the booking flow
const STEPS = [
  { id: 1, name: 'Review Flight', icon: FaPlane },
  { id: 2, name: 'Passenger Info', icon: HiUser },
  { id: 3, name: 'Confirmation', icon: HiCheck },
];

const FlightBooking = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { token, user } = useAuthStore();
  const [currentStep, setCurrentStep] = useState(1);
  const [isBooking, setIsBooking] = useState(false);
  const [bookingConfirmation, setBookingConfirmation] = useState(null);

  // Get flight data from navigation state
  const flight = location.state?.flight;
  const searchParams = location.state?.searchParams;

  // Passenger form
  const [passenger, setPassenger] = useState({
    firstName: user?.full_name?.split(' ')[0] || '',
    lastName: user?.full_name?.split(' ').slice(1).join(' ') || '',
    email: user?.email || '',
    phone: '',
    dateOfBirth: '',
    passportNumber: '',
    nationality: '',
    gender: '',
  });

  // Redirect if no flight data
  useEffect(() => {
    if (!flight) {
      toast.error('No flight selected. Redirecting to search...');
      navigate('/travel');
    }
  }, [flight, navigate]);

  if (!flight) return null;

  const formatDuration = (duration) => {
    if (!duration) return 'N/A';
    const match = duration.match(/PT(\d+H)?(\d+M)?/);
    if (!match) return duration;
    const hours = match[1] ? match[1].replace('H', 'h ') : '';
    const minutes = match[2] ? match[2].replace('M', 'm') : '';
    return hours + minutes;
  };

  const formatTime = (datetime) => {
    if (!datetime) return 'N/A';
    const date = new Date(datetime);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (datetime) => {
    if (!datetime) return 'N/A';
    const date = new Date(datetime);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  };

  const handlePassengerChange = (field, value) => {
    setPassenger(prev => ({ ...prev, [field]: value }));
  };

  const validatePassenger = () => {
    if (!passenger.firstName.trim()) { toast.error('First name is required'); return false; }
    if (!passenger.lastName.trim()) { toast.error('Last name is required'); return false; }
    if (!passenger.email.trim()) { toast.error('Email is required'); return false; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(passenger.email)) { toast.error('Invalid email address'); return false; }
    return true;
  };

  const handleNextStep = () => {
    if (currentStep === 2 && !validatePassenger()) return;
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };

  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleConfirmBooking = async () => {
    if (!validatePassenger()) return;

    setIsBooking(true);
    try {
      const response = await api.post('/travel/book', {
        flight: flight,
        passenger: passenger,
        user_id: user?.user_id || user?.id,
      });

      const data = response.data;

      if (data.success) {
        setBookingConfirmation(data);
        setCurrentStep(3);
        toast.success('Flight booked successfully!');
      } else {
        toast.error(data.message || 'Booking failed. Please try again.');
      }
    } catch (error) {
      console.error('Booking error:', error);
      toast.error('Booking service temporarily unavailable.');
    }
    setIsBooking(false);
  };

  // ==========================================
  // STEP 1: Flight Review (Ticket Style)
  // ==========================================
  const renderFlightReview = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* Ticket Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-2xl">
        {/* Ticket Header */}
        <div className="bg-gradient-to-r from-primary-600 to-secondary-600 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FaPlane className="w-6 h-6 text-white" />
              <div>
                <h3 className="text-lg font-bold text-white">{flight.airline}</h3>
                <p className="text-sm text-white/80">{flight.flight_number}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="px-3 py-1 bg-white/20 rounded-full text-xs text-white font-medium">
                {flight.cabin_class || 'Economy'}
              </div>
            </div>
          </div>
        </div>

        {/* Ticket Body */}
        <div className="p-6">
          {/* Route */}
          <div className="flex items-center justify-between mb-8">
            {/* Departure */}
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{flight.origin}</p>
              <p className="text-sm text-slate-400 mt-1">{formatTime(flight.departure)}</p>
              <p className="text-xs text-slate-500">{formatDate(flight.departure)}</p>
            </div>

            {/* Flight Path */}
            <div className="flex-1 mx-6">
              <div className="flex flex-col items-center">
                <p className="text-xs text-slate-400 mb-2">{formatDuration(flight.duration)}</p>
                <div className="w-full relative flex items-center">
                  <div className="w-3 h-3 rounded-full bg-primary-500 border-2 border-primary-400"></div>
                  <div className="flex-1 h-0.5 bg-gradient-to-r from-primary-500 via-slate-500 to-secondary-500 mx-1 relative">
                    <FaPlane className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white text-sm" />
                  </div>
                  <div className="w-3 h-3 rounded-full bg-secondary-500 border-2 border-secondary-400"></div>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  {flight.stops === 0 ? 'Direct Flight' : `${flight.stops} Stop${flight.stops > 1 ? 's' : ''}`}
                </p>
              </div>
            </div>

            {/* Arrival */}
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{flight.destination}</p>
              <p className="text-sm text-slate-400 mt-1">{formatTime(flight.arrival)}</p>
              <p className="text-xs text-slate-500">{formatDate(flight.arrival)}</p>
            </div>
          </div>

          {/* Dashed Separator */}
          <div className="border-t-2 border-dashed border-slate-700 my-6 relative">
            <div className="absolute -left-8 -top-4 w-8 h-8 rounded-full bg-slate-900"></div>
            <div className="absolute -right-8 -top-4 w-8 h-8 rounded-full bg-slate-900"></div>
          </div>

          {/* Flight Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Airline</p>
              <p className="text-sm font-medium text-white mt-1">{flight.airline}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Flight</p>
              <p className="text-sm font-medium text-white mt-1">{flight.flight_number}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Class</p>
              <p className="text-sm font-medium text-white mt-1">{flight.cabin_class || 'Economy'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Seats Left</p>
              <p className="text-sm font-medium text-amber-400 mt-1">{flight.bookable_seats} available</p>
            </div>
          </div>
        </div>

        {/* Ticket Footer - Price */}
        <div className="bg-slate-800/50 border-t border-slate-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wide">Total Price</p>
              <p className="text-xs text-slate-400">per passenger</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-emerald-400">${flight.price?.toFixed(2)}</p>
              <p className="text-xs text-slate-400">{flight.currency || 'USD'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-slate-800/50 flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
            <FaSuitcase className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-white">Baggage</p>
            <p className="text-xs text-slate-400 mt-1">Checked bag included in fare. Carry-on allowed.</p>
          </div>
        </div>
        <div className="card bg-slate-800/50 flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
            <HiShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-white">Flexible Booking</p>
            <p className="text-xs text-slate-400 mt-1">Free cancellation within 24 hours of booking.</p>
          </div>
        </div>
        <div className="card bg-slate-800/50 flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
            <HiTicket className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-white">E-Ticket</p>
            <p className="text-xs text-slate-400 mt-1">Digital ticket sent to your email after booking.</p>
          </div>
        </div>
      </div>
    </motion.div>
  );

  // ==========================================
  // STEP 2: Passenger Details
  // ==========================================
  const renderPassengerDetails = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* Flight Summary Bar */}
      <div className="card bg-slate-800/50 border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <FaPlane className="w-5 h-5 text-primary-400" />
            <div>
              <p className="text-sm font-medium text-white">
                {flight.airline} • {flight.flight_number}
              </p>
              <p className="text-xs text-slate-400">
                {flight.origin} → {flight.destination} • {formatDate(flight.departure)}
              </p>
            </div>
          </div>
          <p className="text-lg font-bold text-emerald-400">${flight.price?.toFixed(2)}</p>
        </div>
      </div>

      {/* Passenger Form */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <HiUser className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Passenger Details</h3>
            <p className="text-sm text-slate-400">Enter traveler information as shown on ID</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* First Name */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiUser className="w-4 h-4" /> First Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={passenger.firstName}
              onChange={(e) => handlePassengerChange('firstName', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="Enter first name"
            />
          </div>

          {/* Last Name */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiUser className="w-4 h-4" /> Last Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={passenger.lastName}
              onChange={(e) => handlePassengerChange('lastName', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="Enter last name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiMail className="w-4 h-4" /> Email <span className="text-red-400">*</span>
            </label>
            <input
              type="email"
              value={passenger.email}
              onChange={(e) => handlePassengerChange('email', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="your@email.com"
            />
          </div>

          {/* Phone */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiPhone className="w-4 h-4" /> Phone
            </label>
            <input
              type="tel"
              value={passenger.phone}
              onChange={(e) => handlePassengerChange('phone', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="+1 234 567 8900"
            />
          </div>

          {/* Date of Birth */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiCalendar className="w-4 h-4" /> Date of Birth
            </label>
            <input
              type="date"
              value={passenger.dateOfBirth}
              onChange={(e) => handlePassengerChange('dateOfBirth', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Gender */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiUser className="w-4 h-4" /> Gender
            </label>
            <select
              value={passenger.gender}
              onChange={(e) => handlePassengerChange('gender', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Passport Number */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiIdentification className="w-4 h-4" /> Passport Number
            </label>
            <input
              type="text"
              value={passenger.passportNumber}
              onChange={(e) => handlePassengerChange('passportNumber', e.target.value.toUpperCase())}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all uppercase"
              placeholder="AB1234567"
            />
          </div>

          {/* Nationality */}
          <div>
            <label className="flex items-center gap-1.5 text-sm text-slate-400 mb-2">
              <HiLocationMarker className="w-4 h-4" /> Nationality
            </label>
            <input
              type="text"
              value={passenger.nationality}
              onChange={(e) => handlePassengerChange('nationality', e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              placeholder="e.g., Canadian"
            />
          </div>
        </div>
      </div>

      {/* Terms Notice */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
        <p className="text-sm text-amber-400">
          <strong>Important:</strong> Ensure all details match your travel document exactly. Name changes after booking may incur fees.
        </p>
      </div>
    </motion.div>
  );

  // ==========================================
  // STEP 3: Booking Confirmation
  // ==========================================
  const renderConfirmation = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      {/* Success Banner */}
      <div className="text-center py-6">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
          className="w-20 h-20 mx-auto rounded-full bg-emerald-500/20 flex items-center justify-center mb-4"
        >
          <HiCheck className="w-10 h-10 text-emerald-400" />
        </motion.div>
        <h2 className="text-2xl font-bold text-white mb-2">Booking Confirmed!</h2>
        <p className="text-slate-400">Your flight has been booked successfully</p>
      </div>

      {/* Boarding Pass Style Ticket */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-2xl max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FaPlane className="w-4 h-4 text-white" />
              <span className="text-sm font-bold text-white">BOARDING PASS</span>
            </div>
            <span className="text-xs text-white/80">{flight.cabin_class || 'ECONOMY'}</span>
          </div>
        </div>

        <div className="p-6">
          {/* Passenger & Booking Info */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs text-slate-500 uppercase">Passenger</p>
              <p className="text-lg font-bold text-white">
                {passenger.firstName.toUpperCase()} {passenger.lastName.toUpperCase()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 uppercase">Confirmation</p>
              <p className="text-lg font-bold text-emerald-400 font-mono">
                {bookingConfirmation?.confirmation_number || 'PENDING'}
              </p>
            </div>
          </div>

          {/* Route */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-3xl font-bold text-white">{flight.origin}</p>
              <p className="text-sm text-slate-400">{formatTime(flight.departure)}</p>
              <p className="text-xs text-slate-500">{formatDate(flight.departure)}</p>
            </div>
            <div className="flex-1 mx-4 flex flex-col items-center">
              <FaPlane className="text-primary-400 mb-1" />
              <div className="w-full h-0.5 bg-gradient-to-r from-primary-500 to-secondary-500"></div>
              <p className="text-xs text-slate-400 mt-1">{formatDuration(flight.duration)}</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">{flight.destination}</p>
              <p className="text-sm text-slate-400">{formatTime(flight.arrival)}</p>
              <p className="text-xs text-slate-500">{formatDate(flight.arrival)}</p>
            </div>
          </div>

          {/* Dashed line */}
          <div className="border-t-2 border-dashed border-slate-700 my-5 relative">
            <div className="absolute -left-8 -top-4 w-8 h-8 rounded-full bg-slate-900"></div>
            <div className="absolute -right-8 -top-4 w-8 h-8 rounded-full bg-slate-900"></div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div>
              <p className="text-xs text-slate-500 uppercase">Flight</p>
              <p className="text-sm font-semibold text-white">{flight.flight_number}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase">Airline</p>
              <p className="text-sm font-semibold text-white">{flight.airline}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase">Status</p>
              <p className="text-sm font-semibold text-emerald-400">Confirmed</p>
            </div>
          </div>

          {/* Barcode */}
          <div className="flex items-center justify-center py-4 bg-white rounded-lg">
            <div className="text-center">
              <div className="flex items-center justify-center gap-0.5 mb-1">
                {Array.from({ length: 40 }).map((_, i) => (
                  <div
                    key={i}
                    className="bg-black"
                    style={{
                      width: Math.random() > 0.5 ? '2px' : '1px',
                      height: '40px',
                    }}
                  />
                ))}
              </div>
              <p className="text-xs text-gray-600 font-mono">
                {bookingConfirmation?.booking_id || 'PROCESSING'}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-800/50 border-t border-slate-700 px-6 py-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">Total Paid</p>
            <p className="text-xl font-bold text-emerald-400">${flight.price?.toFixed(2)} {flight.currency || 'USD'}</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto">
        <button
          onClick={() => window.print()}
          className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <HiPrinter className="w-4 h-4" />
          Print Ticket
        </button>
        <button
          onClick={() => navigate('/travel')}
          className="flex-1 px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <FaPlane className="w-4 h-4" />
          Search More Flights
        </button>
      </div>

      {/* Email Notice */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 text-center max-w-lg mx-auto">
        <p className="text-sm text-blue-400">
          <HiMail className="inline w-4 h-4 mr-1" />
          A confirmation email with your e-ticket has been sent to <strong>{passenger.email}</strong>
        </p>
      </div>
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => currentStep === 3 ? navigate('/travel') : navigate(-1)}
          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
        >
          <HiArrowLeft className="w-5 h-5 text-slate-400" />
        </button>
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Book Flight</h1>
          <p className="text-slate-400">
            {flight.origin} → {flight.destination} • {flight.airline}
          </p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="card bg-slate-800/50">
        <div className="flex items-center justify-between max-w-lg mx-auto">
          {STEPS.map((step, index) => {
            const StepIcon = step.icon;
            const isActive = currentStep === step.id;
            const isCompleted = currentStep > step.id;
            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center gap-2">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                      isCompleted
                        ? 'bg-emerald-500 text-white'
                        : isActive
                        ? 'bg-primary-500 text-white ring-4 ring-primary-500/30'
                        : 'bg-slate-700 text-slate-400'
                    }`}
                  >
                    {isCompleted ? (
                      <HiCheck className="w-5 h-5" />
                    ) : (
                      <StepIcon className="w-5 h-5" />
                    )}
                  </div>
                  <span className={`text-xs font-medium ${isActive ? 'text-white' : 'text-slate-500'}`}>
                    {step.name}
                  </span>
                </div>
                {index < STEPS.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-2 transition-colors ${
                      currentStep > step.id ? 'bg-emerald-500' : 'bg-slate-700'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      {currentStep === 1 && renderFlightReview()}
      {currentStep === 2 && renderPassengerDetails()}
      {currentStep === 3 && renderConfirmation()}

      {/* Navigation Buttons (Steps 1 & 2 only) */}
      {currentStep < 3 && (
        <div className="flex items-center justify-between">
          <button
            onClick={currentStep === 1 ? () => navigate('/travel') : handlePrevStep}
            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <HiArrowLeft className="w-4 h-4" />
            {currentStep === 1 ? 'Back to Search' : 'Previous'}
          </button>

          {currentStep === 1 ? (
            <button
              onClick={handleNextStep}
              className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              Continue to Passenger Info
              <HiArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleConfirmBooking}
              disabled={isBooking}
              className="px-8 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-500/50 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              {isBooking ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <HiShieldCheck className="w-5 h-5" />
                  Confirm & Book — ${flight.price?.toFixed(2)}
                </>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default FlightBooking;
