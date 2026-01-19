import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../store/authStore';
import {
  HiSearch,
  HiCalendar,
  HiLocationMarker,
  HiUsers,
  HiArrowRight,
  HiRefresh,
  HiArrowNarrowRight,
} from 'react-icons/hi';
import { FaPlane } from 'react-icons/fa';

// API base URL from environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const Travel = () => {
  const { token, user } = useAuthStore();
  const [searchType, setSearchType] = useState('oneway');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  // Flight search form state
  const [flightSearch, setFlightSearch] = useState({
    from: '',
    to: '',
    departDate: '',
    returnDate: '',
    passengers: 1,
    class: 'economy',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFlightSearch(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const searchFlights = async () => {
    // Validate inputs
    if (!flightSearch.from || !flightSearch.to || !flightSearch.departDate) {
      toast.error('Please fill in origin, destination, and departure date');
      return;
    }

    if (!token) {
      toast.error('Please log in to search flights');
      return;
    }

    setIsSearching(true);
    setSearchResults(null);

    try {
      // Call backend API to search flights
      const response = await fetch(`${API_BASE_URL}/tools/invoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.user_id || user?.id || 'unknown',
          tool_name: 'search_flights',
          parameters: {
            origin: flightSearch.from.toUpperCase(),
            destination: flightSearch.to.toUpperCase(),
            departure_date: flightSearch.departDate,
            return_date: searchType === 'roundtrip' ? flightSearch.returnDate : null,
            passengers: parseInt(flightSearch.passengers),
            cabin_class: flightSearch.class
          }
        })
      });

      const data = await response.json();

      if (data.success && data.data) {
        setSearchResults(data.data);
        toast.success(`Found ${data.data.total_results} real-time flights!`);
      } else {
        toast.error(data.message || 'No flights found. Try different dates or airports.');
      }
    } catch (error) {
      toast.error('Failed to search flights. Please try again.');
    }

    setIsSearching(false);
  };

  const formatDuration = (duration) => {
    // Convert ISO 8601 duration (PT5H31M) to readable format
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
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Travel</h1>
          <p className="text-slate-400">Search real-time flights powered by Amadeus API</p>
          <div className="flex items-center gap-2 mt-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-emerald-400">Real-time data from Amadeus Travel API</span>
          </div>
        </div>
      </div>

      {/* Search Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-gradient-to-br from-primary-600/20 to-secondary-600/20 border-primary-500/30"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <FaPlane className="w-6 h-6 text-primary-400" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Flight Search</h2>
            <p className="text-sm text-slate-400">Find the best flights at the best prices</p>
          </div>
        </div>

        {/* Search Type Toggle */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setSearchType('oneway')}
            className={`px-4 py-2 rounded-lg transition-all ${
              searchType === 'oneway'
                ? 'bg-primary-500 text-white'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
            }`}
          >
            One-way
          </button>
          <button
            onClick={() => setSearchType('roundtrip')}
            className={`px-4 py-2 rounded-lg transition-all ${
              searchType === 'roundtrip'
                ? 'bg-primary-500 text-white'
                : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Round-trip
          </button>
        </div>

        {/* Search Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* From */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              <HiLocationMarker className="inline w-4 h-4 mr-1" />
              From (Airport Code)
            </label>
            <input
              type="text"
              name="from"
              value={flightSearch.from}
              onChange={handleInputChange}
              placeholder="JFK, LAX, LHR..."
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 uppercase"
              maxLength={3}
            />
          </div>

          {/* To */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              <HiLocationMarker className="inline w-4 h-4 mr-1" />
              To (Airport Code)
            </label>
            <input
              type="text"
              name="to"
              value={flightSearch.to}
              onChange={handleInputChange}
              placeholder="JFK, LAX, LHR..."
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 uppercase"
              maxLength={3}
            />
          </div>

          {/* Depart Date */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              <HiCalendar className="inline w-4 h-4 mr-1" />
              Departure Date
            </label>
            <input
              type="date"
              name="departDate"
              value={flightSearch.departDate}
              onChange={handleInputChange}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          {/* Return Date */}
          {searchType === 'roundtrip' && (
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiCalendar className="inline w-4 h-4 mr-1" />
                Return Date
              </label>
              <input
                type="date"
                name="returnDate"
                value={flightSearch.returnDate}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                min={flightSearch.departDate || new Date().toISOString().split('T')[0]}
              />
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Passengers */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              <HiUsers className="inline w-4 h-4 mr-1" />
              Passengers
            </label>
            <select
              name="passengers"
              value={flightSearch.passengers}
              onChange={handleInputChange}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
            >
              {[1, 2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num} {num === 1 ? 'Passenger' : 'Passengers'}</option>
              ))}
            </select>
          </div>

          {/* Class */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              <FaPlane className="inline w-4 h-4 mr-1" />
              Class
            </label>
            <select
              name="class"
              value={flightSearch.class}
              onChange={handleInputChange}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>

          {/* Search Button */}
          <div className="flex items-end">
            <button
              onClick={searchFlights}
              disabled={isSearching}
              className="w-full px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSearching ? (
                <>
                  <HiRefresh className="w-5 h-5 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <HiSearch className="w-5 h-5" />
                  Search Flights
                </>
              )}
            </button>
          </div>
        </div>

        {/* Helper Text */}
        <div className="text-xs text-slate-500">
          💡 <strong>Common airport codes:</strong> JFK (New York), LAX (Los Angeles), LHR (London), CDG (Paris), DXB (Dubai), SYD (Sydney), NRT (Tokyo)
        </div>
      </motion.div>

      {/* Search Results */}
      {searchResults && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Results Header */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">
                  {searchResults.total_results} Flights Found
                </h3>
                <p className="text-sm text-slate-400">
                  {searchResults.search_params.origin} → {searchResults.search_params.destination} • {formatDate(searchResults.search_params.departure_date)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-400">Price Range</p>
                <p className="text-lg font-semibold text-white">
                  ${searchResults.price_range.min.toFixed(2)} - ${searchResults.price_range.max.toFixed(2)} {searchResults.price_range.currency}
                </p>
              </div>
            </div>
          </div>

          {/* Best Deal Card */}
          {searchResults.best_deal && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card bg-gradient-to-br from-emerald-600/20 to-teal-600/20 border-emerald-500/30"
            >
              <div className="flex items-center gap-2 mb-4">
                <div className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-full">
                  BEST DEAL
                </div>
                <span className="text-xs text-slate-400">Lowest price available</span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Flight Info */}
                <div className="lg:col-span-2">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="text-xl font-bold text-white">{searchResults.best_deal.airline}</h4>
                      <p className="text-sm text-slate-400">{searchResults.best_deal.flight_number}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-emerald-400">${searchResults.best_deal.price.toFixed(2)}</p>
                      <p className="text-xs text-slate-400">{searchResults.best_deal.currency}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div>
                      <p className="text-2xl font-bold text-white">{formatTime(searchResults.best_deal.departure)}</p>
                      <p className="text-sm text-slate-400">{searchResults.best_deal.origin}</p>
                      <p className="text-xs text-slate-500">{formatDate(searchResults.best_deal.departure)}</p>
                    </div>

                    <div className="flex-1 flex flex-col items-center">
                      <p className="text-xs text-slate-400 mb-1">{formatDuration(searchResults.best_deal.duration)}</p>
                      <div className="w-full relative">
                        <div className="h-0.5 bg-slate-600"></div>
                        <FaPlane className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary-400" />
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        {searchResults.best_deal.stops === 0 ? 'Direct' : `${searchResults.best_deal.stops} stop${searchResults.best_deal.stops > 1 ? 's' : ''}`}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-2xl font-bold text-white">{formatTime(searchResults.best_deal.arrival)}</p>
                      <p className="text-sm text-slate-400">{searchResults.best_deal.destination}</p>
                      <p className="text-xs text-slate-500">{formatDate(searchResults.best_deal.arrival)}</p>
                    </div>
                  </div>

                  <div className="flex gap-4 mt-4 text-xs text-slate-400">
                    <div>
                      <span className="text-slate-500">Class:</span> {searchResults.best_deal.cabin_class}
                    </div>
                    <div>
                      <span className="text-slate-500">Seats:</span> {searchResults.best_deal.bookable_seats} available
                    </div>
                    <div>
                      <span className="text-slate-500">Source:</span> {searchResults.best_deal.data_source}
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <div className="flex items-center justify-center">
                  <button className="w-full px-6 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-all flex items-center justify-center gap-2">
                    <span className="font-semibold">Select Flight</span>
                    <HiArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Other Flights */}
          <div className="grid grid-cols-1 gap-4">
            {searchResults.results && searchResults.results.slice(1, 10).map((flight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card hover:border-primary-500/30 transition-all"
              >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  {/* Flight Info */}
                  <div className="lg:col-span-2">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="text-lg font-bold text-white">{flight.airline}</h4>
                        <p className="text-sm text-slate-400">{flight.flight_number}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-white">${flight.price.toFixed(2)}</p>
                        <p className="text-xs text-slate-400">{flight.currency}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div>
                        <p className="text-xl font-bold text-white">{formatTime(flight.departure)}</p>
                        <p className="text-sm text-slate-400">{flight.origin}</p>
                      </div>

                      <div className="flex-1 flex flex-col items-center">
                        <p className="text-xs text-slate-400 mb-1">{formatDuration(flight.duration)}</p>
                        <div className="w-full relative">
                          <div className="h-0.5 bg-slate-600"></div>
                          <HiArrowNarrowRight className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-slate-500" />
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          {flight.stops === 0 ? 'Direct' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="text-xl font-bold text-white">{formatTime(flight.arrival)}</p>
                        <p className="text-sm text-slate-400">{flight.destination}</p>
                      </div>
                    </div>

                    <div className="flex gap-4 mt-3 text-xs text-slate-400">
                      <div>
                        <span className="text-slate-500">Seats:</span> {flight.bookable_seats} available
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <div className="flex items-center justify-center">
                    <button className="w-full px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-all flex items-center justify-center gap-2">
                      <span>Select</span>
                      <HiArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!searchResults && !isSearching && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card text-center py-12"
        >
          <FaPlane className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Ready to Search</h3>
          <p className="text-slate-400 mb-4">
            Enter your travel details above and click "Search Flights" to find real-time flight options
          </p>
          <p className="text-xs text-slate-500">
            💡 All flight data is fetched in real-time from Amadeus Travel API
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default Travel;
