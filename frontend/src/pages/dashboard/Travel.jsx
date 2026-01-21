import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
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
  HiChevronDown,
  HiX,
} from 'react-icons/hi';
import { FaPlane } from 'react-icons/fa';

// API base URL from environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Comprehensive list of major airports worldwide
const AIRPORTS = [
  // North America - USA
  { code: 'JFK', city: 'New York', name: 'John F. Kennedy International', country: 'USA' },
  { code: 'LGA', city: 'New York', name: 'LaGuardia', country: 'USA' },
  { code: 'EWR', city: 'Newark', name: 'Newark Liberty International', country: 'USA' },
  { code: 'LAX', city: 'Los Angeles', name: 'Los Angeles International', country: 'USA' },
  { code: 'SFO', city: 'San Francisco', name: 'San Francisco International', country: 'USA' },
  { code: 'ORD', city: 'Chicago', name: "O'Hare International", country: 'USA' },
  { code: 'MDW', city: 'Chicago', name: 'Midway International', country: 'USA' },
  { code: 'ATL', city: 'Atlanta', name: 'Hartsfield-Jackson Atlanta International', country: 'USA' },
  { code: 'DFW', city: 'Dallas', name: 'Dallas/Fort Worth International', country: 'USA' },
  { code: 'DEN', city: 'Denver', name: 'Denver International', country: 'USA' },
  { code: 'SEA', city: 'Seattle', name: 'Seattle-Tacoma International', country: 'USA' },
  { code: 'MIA', city: 'Miami', name: 'Miami International', country: 'USA' },
  { code: 'BOS', city: 'Boston', name: 'Logan International', country: 'USA' },
  { code: 'PHX', city: 'Phoenix', name: 'Phoenix Sky Harbor International', country: 'USA' },
  { code: 'IAH', city: 'Houston', name: 'George Bush Intercontinental', country: 'USA' },
  { code: 'LAS', city: 'Las Vegas', name: 'Harry Reid International', country: 'USA' },
  { code: 'MCO', city: 'Orlando', name: 'Orlando International', country: 'USA' },
  { code: 'MSP', city: 'Minneapolis', name: 'Minneapolis-Saint Paul International', country: 'USA' },
  { code: 'DTW', city: 'Detroit', name: 'Detroit Metropolitan', country: 'USA' },
  { code: 'PHL', city: 'Philadelphia', name: 'Philadelphia International', country: 'USA' },
  { code: 'CLT', city: 'Charlotte', name: 'Charlotte Douglas International', country: 'USA' },
  { code: 'SAN', city: 'San Diego', name: 'San Diego International', country: 'USA' },
  { code: 'TPA', city: 'Tampa', name: 'Tampa International', country: 'USA' },
  { code: 'PDX', city: 'Portland', name: 'Portland International', country: 'USA' },
  { code: 'SLC', city: 'Salt Lake City', name: 'Salt Lake City International', country: 'USA' },
  { code: 'DCA', city: 'Washington D.C.', name: 'Ronald Reagan National', country: 'USA' },
  { code: 'IAD', city: 'Washington D.C.', name: 'Dulles International', country: 'USA' },
  { code: 'BWI', city: 'Baltimore', name: 'Baltimore/Washington International', country: 'USA' },
  { code: 'HNL', city: 'Honolulu', name: 'Daniel K. Inouye International', country: 'USA' },
  { code: 'ANC', city: 'Anchorage', name: 'Ted Stevens Anchorage International', country: 'USA' },

  // North America - Canada
  { code: 'YYZ', city: 'Toronto', name: 'Toronto Pearson International', country: 'Canada' },
  { code: 'YVR', city: 'Vancouver', name: 'Vancouver International', country: 'Canada' },
  { code: 'YUL', city: 'Montreal', name: 'Montreal-Trudeau International', country: 'Canada' },
  { code: 'YYC', city: 'Calgary', name: 'Calgary International', country: 'Canada' },
  { code: 'YEG', city: 'Edmonton', name: 'Edmonton International', country: 'Canada' },
  { code: 'YOW', city: 'Ottawa', name: 'Ottawa Macdonald-Cartier International', country: 'Canada' },
  { code: 'YWG', city: 'Winnipeg', name: 'Winnipeg James Armstrong Richardson International', country: 'Canada' },
  { code: 'YHZ', city: 'Halifax', name: 'Halifax Stanfield International', country: 'Canada' },

  // Mexico & Caribbean
  { code: 'MEX', city: 'Mexico City', name: 'Benito Juarez International', country: 'Mexico' },
  { code: 'CUN', city: 'Cancun', name: 'Cancun International', country: 'Mexico' },
  { code: 'GDL', city: 'Guadalajara', name: 'Guadalajara International', country: 'Mexico' },
  { code: 'SJD', city: 'Los Cabos', name: 'Los Cabos International', country: 'Mexico' },
  { code: 'PVR', city: 'Puerto Vallarta', name: 'Gustavo Diaz Ordaz International', country: 'Mexico' },
  { code: 'MBJ', city: 'Montego Bay', name: 'Sangster International', country: 'Jamaica' },
  { code: 'NAS', city: 'Nassau', name: 'Lynden Pindling International', country: 'Bahamas' },
  { code: 'SJU', city: 'San Juan', name: 'Luis Munoz Marin International', country: 'Puerto Rico' },

  // Europe - UK & Ireland
  { code: 'LHR', city: 'London', name: 'Heathrow', country: 'UK' },
  { code: 'LGW', city: 'London', name: 'Gatwick', country: 'UK' },
  { code: 'STN', city: 'London', name: 'Stansted', country: 'UK' },
  { code: 'LTN', city: 'London', name: 'Luton', country: 'UK' },
  { code: 'MAN', city: 'Manchester', name: 'Manchester', country: 'UK' },
  { code: 'EDI', city: 'Edinburgh', name: 'Edinburgh', country: 'UK' },
  { code: 'BHX', city: 'Birmingham', name: 'Birmingham', country: 'UK' },
  { code: 'GLA', city: 'Glasgow', name: 'Glasgow', country: 'UK' },
  { code: 'DUB', city: 'Dublin', name: 'Dublin', country: 'Ireland' },
  { code: 'SNN', city: 'Shannon', name: 'Shannon', country: 'Ireland' },

  // Europe - Western
  { code: 'CDG', city: 'Paris', name: 'Charles de Gaulle', country: 'France' },
  { code: 'ORY', city: 'Paris', name: 'Orly', country: 'France' },
  { code: 'NCE', city: 'Nice', name: 'Nice Cote d\'Azur', country: 'France' },
  { code: 'LYS', city: 'Lyon', name: 'Lyon-Saint Exupery', country: 'France' },
  { code: 'AMS', city: 'Amsterdam', name: 'Schiphol', country: 'Netherlands' },
  { code: 'BRU', city: 'Brussels', name: 'Brussels', country: 'Belgium' },
  { code: 'FRA', city: 'Frankfurt', name: 'Frankfurt', country: 'Germany' },
  { code: 'MUC', city: 'Munich', name: 'Munich', country: 'Germany' },
  { code: 'BER', city: 'Berlin', name: 'Berlin Brandenburg', country: 'Germany' },
  { code: 'DUS', city: 'Dusseldorf', name: 'Dusseldorf', country: 'Germany' },
  { code: 'HAM', city: 'Hamburg', name: 'Hamburg', country: 'Germany' },
  { code: 'ZRH', city: 'Zurich', name: 'Zurich', country: 'Switzerland' },
  { code: 'GVA', city: 'Geneva', name: 'Geneva', country: 'Switzerland' },
  { code: 'VIE', city: 'Vienna', name: 'Vienna International', country: 'Austria' },

  // Europe - Southern
  { code: 'FCO', city: 'Rome', name: 'Leonardo da Vinci-Fiumicino', country: 'Italy' },
  { code: 'MXP', city: 'Milan', name: 'Malpensa', country: 'Italy' },
  { code: 'VCE', city: 'Venice', name: 'Marco Polo', country: 'Italy' },
  { code: 'NAP', city: 'Naples', name: 'Naples International', country: 'Italy' },
  { code: 'MAD', city: 'Madrid', name: 'Adolfo Suarez Madrid-Barajas', country: 'Spain' },
  { code: 'BCN', city: 'Barcelona', name: 'Barcelona-El Prat', country: 'Spain' },
  { code: 'AGP', city: 'Malaga', name: 'Malaga-Costa del Sol', country: 'Spain' },
  { code: 'PMI', city: 'Palma', name: 'Palma de Mallorca', country: 'Spain' },
  { code: 'LIS', city: 'Lisbon', name: 'Humberto Delgado', country: 'Portugal' },
  { code: 'OPO', city: 'Porto', name: 'Francisco Sa Carneiro', country: 'Portugal' },
  { code: 'ATH', city: 'Athens', name: 'Athens International', country: 'Greece' },

  // Europe - Nordic
  { code: 'CPH', city: 'Copenhagen', name: 'Copenhagen', country: 'Denmark' },
  { code: 'ARN', city: 'Stockholm', name: 'Arlanda', country: 'Sweden' },
  { code: 'OSL', city: 'Oslo', name: 'Gardermoen', country: 'Norway' },
  { code: 'HEL', city: 'Helsinki', name: 'Helsinki-Vantaa', country: 'Finland' },
  { code: 'KEF', city: 'Reykjavik', name: 'Keflavik International', country: 'Iceland' },

  // Europe - Eastern
  { code: 'PRG', city: 'Prague', name: 'Vaclav Havel', country: 'Czech Republic' },
  { code: 'WAW', city: 'Warsaw', name: 'Warsaw Chopin', country: 'Poland' },
  { code: 'BUD', city: 'Budapest', name: 'Budapest Ferenc Liszt', country: 'Hungary' },
  { code: 'OTP', city: 'Bucharest', name: 'Henri Coanda International', country: 'Romania' },
  { code: 'SOF', city: 'Sofia', name: 'Sofia', country: 'Bulgaria' },

  // Middle East
  { code: 'DXB', city: 'Dubai', name: 'Dubai International', country: 'UAE' },
  { code: 'AUH', city: 'Abu Dhabi', name: 'Abu Dhabi International', country: 'UAE' },
  { code: 'DOH', city: 'Doha', name: 'Hamad International', country: 'Qatar' },
  { code: 'IST', city: 'Istanbul', name: 'Istanbul', country: 'Turkey' },
  { code: 'SAW', city: 'Istanbul', name: 'Sabiha Gokcen', country: 'Turkey' },
  { code: 'TLV', city: 'Tel Aviv', name: 'Ben Gurion', country: 'Israel' },
  { code: 'AMM', city: 'Amman', name: 'Queen Alia International', country: 'Jordan' },
  { code: 'CAI', city: 'Cairo', name: 'Cairo International', country: 'Egypt' },
  { code: 'RUH', city: 'Riyadh', name: 'King Khalid International', country: 'Saudi Arabia' },
  { code: 'JED', city: 'Jeddah', name: 'King Abdulaziz International', country: 'Saudi Arabia' },
  { code: 'BAH', city: 'Manama', name: 'Bahrain International', country: 'Bahrain' },
  { code: 'KWI', city: 'Kuwait City', name: 'Kuwait International', country: 'Kuwait' },
  { code: 'MCT', city: 'Muscat', name: 'Muscat International', country: 'Oman' },

  // Asia - East
  { code: 'NRT', city: 'Tokyo', name: 'Narita International', country: 'Japan' },
  { code: 'HND', city: 'Tokyo', name: 'Haneda', country: 'Japan' },
  { code: 'KIX', city: 'Osaka', name: 'Kansai International', country: 'Japan' },
  { code: 'ICN', city: 'Seoul', name: 'Incheon International', country: 'South Korea' },
  { code: 'GMP', city: 'Seoul', name: 'Gimpo International', country: 'South Korea' },
  { code: 'PEK', city: 'Beijing', name: 'Beijing Capital', country: 'China' },
  { code: 'PKX', city: 'Beijing', name: 'Beijing Daxing', country: 'China' },
  { code: 'PVG', city: 'Shanghai', name: 'Pudong International', country: 'China' },
  { code: 'SHA', city: 'Shanghai', name: 'Hongqiao International', country: 'China' },
  { code: 'CAN', city: 'Guangzhou', name: 'Baiyun International', country: 'China' },
  { code: 'SZX', city: 'Shenzhen', name: 'Bao\'an International', country: 'China' },
  { code: 'HKG', city: 'Hong Kong', name: 'Hong Kong International', country: 'Hong Kong' },
  { code: 'TPE', city: 'Taipei', name: 'Taiwan Taoyuan International', country: 'Taiwan' },

  // Asia - Southeast
  { code: 'SIN', city: 'Singapore', name: 'Changi', country: 'Singapore' },
  { code: 'BKK', city: 'Bangkok', name: 'Suvarnabhumi', country: 'Thailand' },
  { code: 'DMK', city: 'Bangkok', name: 'Don Mueang', country: 'Thailand' },
  { code: 'KUL', city: 'Kuala Lumpur', name: 'Kuala Lumpur International', country: 'Malaysia' },
  { code: 'CGK', city: 'Jakarta', name: 'Soekarno-Hatta International', country: 'Indonesia' },
  { code: 'DPS', city: 'Bali', name: 'Ngurah Rai International', country: 'Indonesia' },
  { code: 'MNL', city: 'Manila', name: 'Ninoy Aquino International', country: 'Philippines' },
  { code: 'SGN', city: 'Ho Chi Minh City', name: 'Tan Son Nhat', country: 'Vietnam' },
  { code: 'HAN', city: 'Hanoi', name: 'Noi Bai International', country: 'Vietnam' },

  // Asia - South
  { code: 'DEL', city: 'New Delhi', name: 'Indira Gandhi International', country: 'India' },
  { code: 'BOM', city: 'Mumbai', name: 'Chhatrapati Shivaji Maharaj International', country: 'India' },
  { code: 'BLR', city: 'Bangalore', name: 'Kempegowda International', country: 'India' },
  { code: 'MAA', city: 'Chennai', name: 'Chennai International', country: 'India' },
  { code: 'HYD', city: 'Hyderabad', name: 'Rajiv Gandhi International', country: 'India' },
  { code: 'CCU', city: 'Kolkata', name: 'Netaji Subhas Chandra Bose International', country: 'India' },
  { code: 'CMB', city: 'Colombo', name: 'Bandaranaike International', country: 'Sri Lanka' },
  { code: 'DAC', city: 'Dhaka', name: 'Hazrat Shahjalal International', country: 'Bangladesh' },
  { code: 'KTM', city: 'Kathmandu', name: 'Tribhuvan International', country: 'Nepal' },
  { code: 'ISB', city: 'Islamabad', name: 'Islamabad International', country: 'Pakistan' },
  { code: 'KHI', city: 'Karachi', name: 'Jinnah International', country: 'Pakistan' },
  { code: 'MLE', city: 'Male', name: 'Velana International', country: 'Maldives' },

  // Africa
  { code: 'JNB', city: 'Johannesburg', name: 'O.R. Tambo International', country: 'South Africa' },
  { code: 'CPT', city: 'Cape Town', name: 'Cape Town International', country: 'South Africa' },
  { code: 'NBO', city: 'Nairobi', name: 'Jomo Kenyatta International', country: 'Kenya' },
  { code: 'MBA', city: 'Mombasa', name: 'Moi International', country: 'Kenya' },
  { code: 'ADD', city: 'Addis Ababa', name: 'Bole International', country: 'Ethiopia' },
  { code: 'LOS', city: 'Lagos', name: 'Murtala Muhammed International', country: 'Nigeria' },
  { code: 'ABV', city: 'Abuja', name: 'Nnamdi Azikiwe International', country: 'Nigeria' },
  { code: 'ACC', city: 'Accra', name: 'Kotoka International', country: 'Ghana' },
  { code: 'CMN', city: 'Casablanca', name: 'Mohammed V International', country: 'Morocco' },
  { code: 'RAK', city: 'Marrakech', name: 'Marrakech Menara', country: 'Morocco' },
  { code: 'TUN', city: 'Tunis', name: 'Tunis-Carthage International', country: 'Tunisia' },
  { code: 'ALG', city: 'Algiers', name: 'Houari Boumediene', country: 'Algeria' },
  { code: 'DAR', city: 'Dar es Salaam', name: 'Julius Nyerere International', country: 'Tanzania' },
  { code: 'EBB', city: 'Entebbe', name: 'Entebbe International', country: 'Uganda' },
  { code: 'MRU', city: 'Mauritius', name: 'Sir Seewoosagur Ramgoolam International', country: 'Mauritius' },

  // Oceania
  { code: 'SYD', city: 'Sydney', name: 'Sydney Kingsford Smith', country: 'Australia' },
  { code: 'MEL', city: 'Melbourne', name: 'Melbourne', country: 'Australia' },
  { code: 'BNE', city: 'Brisbane', name: 'Brisbane', country: 'Australia' },
  { code: 'PER', city: 'Perth', name: 'Perth', country: 'Australia' },
  { code: 'ADL', city: 'Adelaide', name: 'Adelaide', country: 'Australia' },
  { code: 'AKL', city: 'Auckland', name: 'Auckland', country: 'New Zealand' },
  { code: 'WLG', city: 'Wellington', name: 'Wellington', country: 'New Zealand' },
  { code: 'CHC', city: 'Christchurch', name: 'Christchurch', country: 'New Zealand' },
  { code: 'NAN', city: 'Nadi', name: 'Nadi International', country: 'Fiji' },

  // South America
  { code: 'GRU', city: 'Sao Paulo', name: 'Guarulhos International', country: 'Brazil' },
  { code: 'GIG', city: 'Rio de Janeiro', name: 'Galeao International', country: 'Brazil' },
  { code: 'BSB', city: 'Brasilia', name: 'Brasilia International', country: 'Brazil' },
  { code: 'EZE', city: 'Buenos Aires', name: 'Ministro Pistarini', country: 'Argentina' },
  { code: 'SCL', city: 'Santiago', name: 'Arturo Merino Benitez', country: 'Chile' },
  { code: 'LIM', city: 'Lima', name: 'Jorge Chavez International', country: 'Peru' },
  { code: 'BOG', city: 'Bogota', name: 'El Dorado International', country: 'Colombia' },
  { code: 'MDE', city: 'Medellin', name: 'Jose Maria Cordova International', country: 'Colombia' },
  { code: 'UIO', city: 'Quito', name: 'Mariscal Sucre International', country: 'Ecuador' },
  { code: 'CCS', city: 'Caracas', name: 'Simon Bolivar International', country: 'Venezuela' },
  { code: 'MVD', city: 'Montevideo', name: 'Carrasco International', country: 'Uruguay' },
  { code: 'ASU', city: 'Asuncion', name: 'Silvio Pettirossi International', country: 'Paraguay' },
  { code: 'VVI', city: 'Santa Cruz', name: 'Viru Viru International', country: 'Bolivia' },
];

// Airport Autocomplete Component
const AirportAutocomplete = ({
  value,
  onChange,
  placeholder,
  label,
  icon: Icon,
  excludeCode = null
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredAirports, setFilteredAirports] = useState([]);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 });
  const wrapperRef = useRef(null);
  const buttonRef = useRef(null);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Get selected airport details
  const selectedAirport = AIRPORTS.find(a => a.code === value);

  // Filter airports based on search term
  useEffect(() => {
    if (searchTerm.length === 0) {
      // Show popular airports when no search term
      const popularCodes = ['JFK', 'LAX', 'LHR', 'CDG', 'DXB', 'SIN', 'SYD', 'NRT', 'HKG', 'FRA'];
      setFilteredAirports(AIRPORTS.filter(a => popularCodes.includes(a.code) && a.code !== excludeCode));
    } else {
      const term = searchTerm.toLowerCase();
      const filtered = AIRPORTS.filter(airport => {
        if (airport.code === excludeCode) return false;
        return (
          airport.code.toLowerCase().includes(term) ||
          airport.city.toLowerCase().includes(term) ||
          airport.name.toLowerCase().includes(term) ||
          airport.country.toLowerCase().includes(term)
        );
      }).slice(0, 10);
      setFilteredAirports(filtered);
    }
  }, [searchTerm, excludeCode]);

  // Calculate dropdown position when opened
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      // For position: fixed, use rect values directly (relative to viewport)
      setDropdownPosition({
        top: rect.bottom + 4,
        left: rect.left,
        width: rect.width
      });
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (airport) => {
    onChange(airport.code);
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange('');
    setSearchTerm('');
  };

  // Dropdown rendered via Portal
  const dropdownContent = isOpen ? createPortal(
    <div
      ref={dropdownRef}
      style={{
        position: 'fixed',
        top: dropdownPosition.top,
        left: dropdownPosition.left,
        width: dropdownPosition.width,
        zIndex: 99999,
      }}
      className="bg-[#1e293b] border border-gray-500 rounded-lg shadow-2xl max-h-80 overflow-hidden"
    >
      {/* Search Input */}
      <div className="p-3 border-b border-gray-600 bg-[#1e293b]">
        <div className="relative">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by city, airport, or code..."
            className="w-full pl-10 pr-4 py-2.5 bg-[#334155] border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 text-sm"
            autoFocus
          />
        </div>
      </div>

      {/* Results */}
      <div className="overflow-y-auto max-h-60">
        {filteredAirports.length > 0 ? (
          <>
            {searchTerm.length === 0 && (
              <div className="px-4 py-2 text-xs text-gray-300 bg-[#334155] font-medium uppercase tracking-wide">
                Popular Airports
              </div>
            )}
            {filteredAirports.map((airport) => (
              <div
                key={airport.code}
                onClick={() => handleSelect(airport)}
                className={`px-4 py-3 cursor-pointer transition-colors hover:bg-[#475569] ${
                  value === airport.code ? 'bg-purple-900/50' : 'bg-[#1e293b]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="font-bold text-purple-400 w-14 text-base">{airport.code}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium">{airport.city} - {airport.name}</p>
                    <p className="text-sm text-gray-300">{airport.country}</p>
                  </div>
                </div>
              </div>
            ))}
          </>
        ) : (
          <div className="px-4 py-8 text-center bg-[#1e293b]">
            <FaPlane className="w-8 h-8 mx-auto mb-2 text-gray-500" />
            <p className="text-gray-300">No airports found</p>
            <p className="text-xs mt-1 text-gray-400">Try a different search term</p>
          </div>
        )}
      </div>
    </div>,
    document.body
  ) : null;

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-sm text-slate-400 mb-2">
        {Icon && <Icon className="inline w-4 h-4 mr-1" />}
        {label}
      </label>

      <div className="relative">
        <div
          ref={buttonRef}
          onClick={() => setIsOpen(true)}
          className={`w-full px-4 py-3 bg-slate-700/50 border rounded-lg cursor-pointer transition-all flex items-center justify-between ${
            isOpen ? 'border-primary-500 ring-1 ring-primary-500/50' : 'border-slate-600 hover:border-slate-500'
          }`}
        >
          {selectedAirport ? (
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <span className="font-bold text-primary-400 text-lg">{selectedAirport.code}</span>
              <div className="truncate">
                <span className="text-white">{selectedAirport.city}</span>
                <span className="text-slate-500 text-sm ml-1">({selectedAirport.country})</span>
              </div>
            </div>
          ) : (
            <span className="text-slate-500">{placeholder}</span>
          )}

          <div className="flex items-center gap-2">
            {value && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleClear();
                }}
                className="p-1 hover:bg-slate-600 rounded transition-colors"
              >
                <HiX className="w-4 h-4 text-slate-400" />
              </button>
            )}
            <HiChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </div>
        </div>

        {/* Dropdown rendered via Portal */}
        {dropdownContent}
      </div>
    </div>
  );
};

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

  const handleAirportChange = (field, value) => {
    setFlightSearch(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const searchFlights = async () => {
    // Validate inputs
    if (!flightSearch.from || !flightSearch.to || !flightSearch.departDate) {
      toast.error('Please fill in origin, destination, and departure date');
      return;
    }

    if (flightSearch.from === flightSearch.to) {
      toast.error('Origin and destination cannot be the same');
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
          {/* From - Airport Dropdown */}
          <AirportAutocomplete
            value={flightSearch.from}
            onChange={(value) => handleAirportChange('from', value)}
            placeholder="Select departure airport"
            label="From"
            icon={HiLocationMarker}
            excludeCode={flightSearch.to}
          />

          {/* To - Airport Dropdown */}
          <AirportAutocomplete
            value={flightSearch.to}
            onChange={(value) => handleAirportChange('to', value)}
            placeholder="Select destination airport"
            label="To"
            icon={HiLocationMarker}
            excludeCode={flightSearch.from}
          />

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
          Select airports from the dropdown or search by city name, airport name, or code. Over 180 airports worldwide available.
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
            Select your departure and destination airports above and click "Search Flights" to find real-time flight options
          </p>
          <p className="text-xs text-slate-500">
            All flight data is fetched in real-time from Amadeus Travel API
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default Travel;
