import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiSearch,
  HiCalendar,
  HiLocationMarker,
  HiUsers,
  HiCurrencyDollar,
  HiStar,
  HiHeart,
  HiBell,
  HiTrendingUp,
  HiTrendingDown,
  HiArrowRight,
  HiSwitchHorizontal,
  HiOfficeBuilding,
} from 'react-icons/hi';
import { FaPlane, FaHotel, FaCar, FaUmbrellaBeach } from 'react-icons/fa';

const Travel = () => {
  const [activeTab, setActiveTab] = useState('flights');
  const [searchType, setSearchType] = useState('roundtrip');
  const [isSearching, setIsSearching] = useState(false);

  // Flight search form state
  const [flightSearch, setFlightSearch] = useState({
    from: '',
    to: '',
    departDate: '',
    returnDate: '',
    passengers: 1,
    class: 'economy',
  });

  // Hotel search form state
  const [hotelSearch, setHotelSearch] = useState({
    destination: '',
    checkIn: '',
    checkOut: '',
    guests: 2,
    rooms: 1,
  });

  // Mock saved searches
  const savedSearches = [
    { from: 'Toronto (YYZ)', to: 'New York (JFK)', date: 'Feb 15-20', price: '$245' },
    { from: 'Toronto (YYZ)', to: 'London (LHR)', date: 'Mar 1-10', price: '$680' },
    { from: 'Nairobi (NBO)', to: 'Dubai (DXB)', date: 'Apr 5-12', price: '$420' },
  ];

  // Mock price alerts
  const priceAlerts = [
    { route: 'YYZ → LAX', alertPrice: 300, currentPrice: 285, trend: 'down', change: -15 },
    { route: 'YYZ → MIA', alertPrice: 250, currentPrice: 268, trend: 'up', change: 8 },
    { route: 'NBO → LHR', alertPrice: 600, currentPrice: 545, trend: 'down', change: -55 },
  ];

  // Mock hotel recommendations
  const hotelRecommendations = [
    {
      name: 'The Ritz-Carlton, Toronto',
      location: 'Toronto, Canada',
      rating: 4.9,
      price: 450,
      image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400',
      amenities: ['Spa', 'Pool', 'Restaurant'],
    },
    {
      name: 'Serena Hotel Nairobi',
      location: 'Nairobi, Kenya',
      rating: 4.7,
      price: 280,
      image: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400',
      amenities: ['Garden', 'Pool', 'Safari Tours'],
    },
    {
      name: 'The Plaza Hotel',
      location: 'New York, USA',
      rating: 4.8,
      price: 595,
      image: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400',
      amenities: ['Spa', 'Concierge', 'Fine Dining'],
    },
  ];

  const handleSearch = async () => {
    setIsSearching(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    toast.success('Search results ready!');
    setIsSearching(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Travel</h1>
          <p className="text-slate-400">Search flights, hotels, and track price alerts</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-ghost flex items-center gap-2 border border-slate-700">
            <HiHeart className="w-5 h-5" />
            Saved
          </button>
          <button className="btn-primary flex items-center gap-2">
            <HiBell className="w-5 h-5" />
            Price Alerts
          </button>
        </div>
      </div>

      {/* Travel Type Tabs */}
      <div className="flex gap-4 overflow-x-auto pb-2">
        {[
          { id: 'flights', label: 'Flights', icon: FaPlane },
          { id: 'hotels', label: 'Hotels', icon: FaHotel },
          { id: 'cars', label: 'Car Rentals', icon: FaCar },
          { id: 'packages', label: 'Packages', icon: FaUmbrellaBeach },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg shadow-primary-500/25'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            <span className="font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Search Card */}
      {activeTab === 'flights' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80"
        >
          {/* Trip Type */}
          <div className="flex gap-4 mb-6">
            {['roundtrip', 'oneway', 'multicity'].map((type) => (
              <label key={type} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="tripType"
                  checked={searchType === type}
                  onChange={() => setSearchType(type)}
                  className="w-4 h-4 text-primary-500 bg-slate-700 border-slate-600 focus:ring-primary-500"
                />
                <span className="text-slate-300 capitalize">{type.replace('trip', ' Trip').replace('city', '-City')}</span>
              </label>
            ))}
          </div>

          {/* Search Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="lg:col-span-2 flex gap-4 items-center">
              <div className="flex-1 relative">
                <label className="text-xs text-slate-400 mb-1 block">From</label>
                <div className="relative">
                  <HiLocationMarker className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={flightSearch.from}
                    onChange={(e) => setFlightSearch({ ...flightSearch, from: e.target.value })}
                    placeholder="City or Airport"
                    className="input pl-10"
                  />
                </div>
              </div>
              <button className="mt-6 p-2 rounded-full bg-slate-700 hover:bg-slate-600 transition-colors">
                <HiSwitchHorizontal className="w-5 h-5 text-slate-300" />
              </button>
              <div className="flex-1 relative">
                <label className="text-xs text-slate-400 mb-1 block">To</label>
                <div className="relative">
                  <HiLocationMarker className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={flightSearch.to}
                    onChange={(e) => setFlightSearch({ ...flightSearch, to: e.target.value })}
                    placeholder="City or Airport"
                    className="input pl-10"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Depart</label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={flightSearch.departDate}
                  onChange={(e) => setFlightSearch({ ...flightSearch, departDate: e.target.value })}
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Return</label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={flightSearch.returnDate}
                  onChange={(e) => setFlightSearch({ ...flightSearch, returnDate: e.target.value })}
                  className="input pl-10"
                  disabled={searchType === 'oneway'}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Passengers</label>
              <div className="relative">
                <HiUsers className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <select
                  value={flightSearch.passengers}
                  onChange={(e) => setFlightSearch({ ...flightSearch, passengers: e.target.value })}
                  className="input pl-10"
                >
                  {[1, 2, 3, 4, 5, 6].map(n => (
                    <option key={n} value={n}>{n} Passenger{n > 1 ? 's' : ''}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Class</label>
              <select
                value={flightSearch.class}
                onChange={(e) => setFlightSearch({ ...flightSearch, class: e.target.value })}
                className="input"
              >
                <option value="economy">Economy</option>
                <option value="premium">Premium Economy</option>
                <option value="business">Business</option>
                <option value="first">First Class</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="btn-primary w-full flex items-center justify-center gap-2 py-3"
          >
            {isSearching ? (
              <>
                <span className="spinner-small" />
                Searching...
              </>
            ) : (
              <>
                <HiSearch className="w-5 h-5" />
                Search Flights
              </>
            )}
          </button>
        </motion.div>
      )}

      {activeTab === 'hotels' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="lg:col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Destination</label>
              <div className="relative">
                <HiOfficeBuilding className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={hotelSearch.destination}
                  onChange={(e) => setHotelSearch({ ...hotelSearch, destination: e.target.value })}
                  placeholder="City, hotel, or landmark"
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Check-in</label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={hotelSearch.checkIn}
                  onChange={(e) => setHotelSearch({ ...hotelSearch, checkIn: e.target.value })}
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 mb-1 block">Check-out</label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={hotelSearch.checkOut}
                  onChange={(e) => setHotelSearch({ ...hotelSearch, checkOut: e.target.value })}
                  className="input pl-10"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Guests</label>
              <div className="relative">
                <HiUsers className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <select
                  value={hotelSearch.guests}
                  onChange={(e) => setHotelSearch({ ...hotelSearch, guests: e.target.value })}
                  className="input pl-10"
                >
                  {[1, 2, 3, 4, 5, 6].map(n => (
                    <option key={n} value={n}>{n} Guest{n > 1 ? 's' : ''}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Rooms</label>
              <select
                value={hotelSearch.rooms}
                onChange={(e) => setHotelSearch({ ...hotelSearch, rooms: e.target.value })}
                className="input"
              >
                {[1, 2, 3, 4].map(n => (
                  <option key={n} value={n}>{n} Room{n > 1 ? 's' : ''}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="btn-primary w-full flex items-center justify-center gap-2 py-3"
          >
            {isSearching ? (
              <>
                <span className="spinner-small" />
                Searching...
              </>
            ) : (
              <>
                <HiSearch className="w-5 h-5" />
                Search Hotels
              </>
            )}
          </button>
        </motion.div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <HiTrendingDown className="w-5 h-5 text-emerald-400" />
            </div>
            <span className="text-slate-400">Savings this month</span>
          </div>
          <p className="text-2xl font-bold text-white">$847</p>
          <p className="text-sm text-emerald-400 mt-1">From price alerts</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiBell className="w-5 h-5 text-primary-400" />
            </div>
            <span className="text-slate-400">Active Alerts</span>
          </div>
          <p className="text-2xl font-bold text-white">{priceAlerts.length}</p>
          <p className="text-sm text-slate-400 mt-1">Routes being tracked</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-secondary-500/20 flex items-center justify-center">
              <HiHeart className="w-5 h-5 text-secondary-400" />
            </div>
            <span className="text-slate-400">Saved Searches</span>
          </div>
          <p className="text-2xl font-bold text-white">{savedSearches.length}</p>
          <p className="text-sm text-slate-400 mt-1">Quick access</p>
        </motion.div>
      </div>

      {/* Price Alerts */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Price Alerts</h3>
          <button className="text-sm text-primary-400 hover:text-primary-300">Manage Alerts</button>
        </div>
        <div className="space-y-3">
          {priceAlerts.map((alert, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center justify-between p-4 rounded-xl ${
                alert.currentPrice <= alert.alertPrice
                  ? 'bg-emerald-500/10 border border-emerald-500/30'
                  : 'bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  alert.trend === 'down' ? 'bg-emerald-500/20' : 'bg-red-500/20'
                }`}>
                  <FaPlane className={`w-5 h-5 ${alert.trend === 'down' ? 'text-emerald-400' : 'text-red-400'}`} />
                </div>
                <div>
                  <p className="font-semibold text-white">{alert.route}</p>
                  <p className="text-sm text-slate-400">Alert at ${alert.alertPrice}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-white">${alert.currentPrice}</p>
                <p className={`text-sm flex items-center gap-1 ${
                  alert.trend === 'down' ? 'text-emerald-400' : 'text-red-400'
                }`}>
                  {alert.trend === 'down' ? <HiTrendingDown className="w-4 h-4" /> : <HiTrendingUp className="w-4 h-4" />}
                  {alert.change > 0 ? '+' : ''}{alert.change}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Hotel Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Recommended Hotels</h3>
          <button className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1">
            View All <HiArrowRight className="w-4 h-4" />
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {hotelRecommendations.map((hotel, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card overflow-hidden cursor-pointer hover:border-primary-500/50 p-0"
            >
              <div className="h-40 bg-gradient-to-br from-primary-500/20 to-secondary-500/20 flex items-center justify-center">
                <FaHotel className="w-12 h-12 text-slate-600" />
              </div>
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex items-center gap-1 text-amber-400">
                    <HiStar className="w-4 h-4" />
                    <span className="text-sm font-medium">{hotel.rating}</span>
                  </div>
                  <span className="text-sm text-slate-400">{hotel.location}</span>
                </div>
                <h4 className="font-semibold text-white mb-2">{hotel.name}</h4>
                <div className="flex flex-wrap gap-2 mb-3">
                  {hotel.amenities.map((amenity, i) => (
                    <span key={i} className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded">
                      {amenity}
                    </span>
                  ))}
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-lg font-bold text-white">
                    ${hotel.price}<span className="text-sm text-slate-400 font-normal">/night</span>
                  </p>
                  <button className="btn-primary text-sm py-1.5 px-3">Book</button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Travel;
