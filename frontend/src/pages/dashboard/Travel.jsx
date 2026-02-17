import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../store/authStore';
import api from '../../services/api';
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
  HiStar,
  HiCheck,
  HiClock,
  HiShieldCheck,
} from 'react-icons/hi';
import { FaPlane, FaHotel, FaCar, FaWifi, FaSwimmingPool, FaParking, FaDumbbell, FaCoffee, FaConciergeBell, FaGasPump, FaSnowflake, FaBluetooth, FaSuitcase } from 'react-icons/fa';

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

// Demo hotel data
// Hotel stock images (used since Amadeus doesn't provide images)
const HOTEL_IMAGES = [
  'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400&h=250&fit=crop',
  'https://images.unsplash.com/photo-1625244724120-1fd1d34d00f6?w=400&h=250&fit=crop',
];

// Car stock images by type
const CAR_IMAGES = {
  Economy: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0afe?w=400&h=250&fit=crop',
  Compact: 'https://images.unsplash.com/photo-1590362891991-f776e747a588?w=400&h=250&fit=crop',
  SUV: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=400&h=250&fit=crop',
  Premium: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=400&h=250&fit=crop',
  Luxury: 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&h=250&fit=crop',
  Van: 'https://images.unsplash.com/photo-1559416523-140ddc3d238c?w=400&h=250&fit=crop',
  Electric: 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400&h=250&fit=crop',
  default: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0afe?w=400&h=250&fit=crop',
};

const Travel = () => {
  const navigate = useNavigate();
  const { token, user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('flights');
  const [searchType, setSearchType] = useState('oneway');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  // Hotel search state
  const [hotelSearch, setHotelSearch] = useState({
    city: '',
    checkIn: '',
    checkOut: '',
    guests: 1,
    rooms: 1,
    minRating: 0,
  });
  const [hotelResults, setHotelResults] = useState(null);
  const [isSearchingHotels, setIsSearchingHotels] = useState(false);

  // Car search state
  const [carSearch, setCarSearch] = useState({
    pickupLocation: '',
    dropoffLocation: '',
    pickupDate: '',
    pickupTime: '10:00',
    dropoffDate: '',
    dropoffTime: '10:00',
    carType: 'all',
    driverAge: '25+',
  });
  const [carResults, setCarResults] = useState(null);
  const [isSearchingCars, setIsSearchingCars] = useState(false);

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
      const response = await api.post('/tools/invoke', {
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
      });

      const data = response.data;

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

  // Handle flight selection — navigate to booking page
  const handleSelectFlight = (flight) => {
    navigate('/travel/book', {
      state: {
        flight,
        searchParams: {
          from: flightSearch.from,
          to: flightSearch.to,
          departDate: flightSearch.departDate,
          returnDate: flightSearch.returnDate,
          passengers: flightSearch.passengers,
          class: flightSearch.class,
          searchType,
        },
      },
    });
  };

  // Hotel search handler — calls real backend API which uses Amadeus
  const searchHotels = async () => {
    if (!hotelSearch.city || !hotelSearch.checkIn || !hotelSearch.checkOut) {
      toast.error('Please fill in city, check-in, and check-out dates');
      return;
    }
    if (hotelSearch.checkOut <= hotelSearch.checkIn) {
      toast.error('Check-out must be after check-in date');
      return;
    }
    setIsSearchingHotels(true);
    setHotelResults(null);
    try {
      const response = await api.get('/travel/hotels/search', { params: {
        city: hotelSearch.city,
        check_in: hotelSearch.checkIn,
        check_out: hotelSearch.checkOut,
        guests: hotelSearch.guests,
        rooms: hotelSearch.rooms,
        min_rating: hotelSearch.minRating,
      }});
      const data = response.data;
      const nights = Math.ceil((new Date(hotelSearch.checkOut) - new Date(hotelSearch.checkIn)) / (1000 * 60 * 60 * 24));
      // Map backend response to frontend format
      const hotels = (Array.isArray(data) ? data : []).map((h, idx) => ({
        id: h.hotel_id || `htl-${idx}`,
        name: h.name || 'Hotel',
        image: HOTEL_IMAGES[idx % HOTEL_IMAGES.length],
        starRating: h.star_rating || 3,
        userRating: h.user_rating || h.star_rating || 3,
        reviewCount: Math.floor(Math.random() * 2000) + 100,
        city: h.city || hotelSearch.city,
        address: h.address || '',
        pricePerNight: h.price_per_night || 0,
        totalPrice: h.total_price || 0,
        currency: h.currency || 'USD',
        roomType: h.room_type || 'Standard Room',
        amenities: h.amenities || ['Free WiFi'],
        breakfastIncluded: h.breakfast_included || false,
        freeCancellation: h.free_cancellation || false,
        distanceFromCenter: h.distance_from_center || 0,
      }));
      setHotelResults({ hotels, nights, city: hotelSearch.city });
      if (hotels.length > 0) {
        toast.success(`Found ${hotels.length} hotels in ${hotelSearch.city} (Amadeus API)`);
      } else {
        toast.error('No hotels found. Try a different city or dates.');
      }
    } catch (err) {
      console.error('Hotel search error:', err);
      toast.error('Hotel search failed. Please try again.');
    } finally {
      setIsSearchingHotels(false);
    }
  };

  // Car search handler — calls real backend API which uses Amadeus
  const searchCars = async () => {
    if (!carSearch.pickupLocation || !carSearch.pickupDate || !carSearch.dropoffDate) {
      toast.error('Please fill in pickup location, pickup date, and drop-off date');
      return;
    }
    if (carSearch.dropoffDate < carSearch.pickupDate) {
      toast.error('Drop-off date must be after pickup date');
      return;
    }
    setIsSearchingCars(true);
    setCarResults(null);
    try {
      const carParams = {
        pickup_location: carSearch.pickupLocation,
        pickup_date: carSearch.pickupDate,
        dropoff_date: carSearch.dropoffDate,
        pickup_time: carSearch.pickupTime,
        dropoff_time: carSearch.dropoffTime,
        car_type: carSearch.carType,
      };
      if (carSearch.dropoffLocation) {
        carParams.dropoff_location = carSearch.dropoffLocation;
      }
      const response = await api.get('/travel/cars/search', { params: carParams });
      const data = response.data;
      const days = Math.max(1, Math.ceil((new Date(carSearch.dropoffDate) - new Date(carSearch.pickupDate)) / (1000 * 60 * 60 * 24)));
      // Map backend response to frontend format
      const cars = (Array.isArray(data) ? data : []).map((c, idx) => ({
        id: c.car_id || `car-${idx}`,
        name: c.name || 'Car',
        company: c.company || 'Rental Company',
        image: CAR_IMAGES[c.type] || CAR_IMAGES.default,
        type: c.type || 'Standard',
        seats: c.seats || 5,
        doors: c.doors || 4,
        transmission: c.transmission || 'Automatic',
        fuelType: c.fuel_type || 'Gasoline',
        pricePerDay: c.price_per_day || 0,
        totalPrice: c.total_price || 0,
        currency: c.currency || 'USD',
        features: c.features || ['A/C'],
        mileage: c.mileage || 'Unlimited',
        insurance: c.insurance || 'Basic included',
        freeCancellation: c.free_cancellation || false,
      }));
      setCarResults({ cars, days, location: carSearch.pickupLocation });
      if (cars.length > 0) {
        toast.success(`Found ${cars.length} cars in ${carSearch.pickupLocation} (Amadeus API)`);
      } else {
        toast.error('No cars found. Try a different location or dates.');
      }
    } catch (err) {
      console.error('Car search error:', err);
      toast.error('Car search failed. Please try again.');
    } finally {
      setIsSearchingCars(false);
    }
  };

  // Hotel amenity icon mapper
  const getAmenityIcon = (amenity) => {
    const lower = amenity.toLowerCase();
    if (lower.includes('wifi')) return <FaWifi className="w-3 h-3" />;
    if (lower.includes('pool')) return <FaSwimmingPool className="w-3 h-3" />;
    if (lower.includes('parking') || lower.includes('valet')) return <FaParking className="w-3 h-3" />;
    if (lower.includes('gym')) return <FaDumbbell className="w-3 h-3" />;
    if (lower.includes('breakfast') || lower.includes('coffee')) return <FaCoffee className="w-3 h-3" />;
    if (lower.includes('concierge') || lower.includes('room service')) return <FaConciergeBell className="w-3 h-3" />;
    return <HiCheck className="w-3 h-3" />;
  };

  // ===========================================
  // TAB DEFINITIONS
  // ===========================================
  const tabs = [
    { id: 'flights', label: 'Flights', icon: FaPlane },
    { id: 'hotels', label: 'Hotels', icon: FaHotel },
    { id: 'cars', label: 'Car Rental', icon: FaCar },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Travel</h1>
          <p className="text-slate-400">Search flights, hotels, and car rentals worldwide</p>
          <div className="flex items-center gap-2 mt-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-emerald-400">Real-time data from Amadeus Travel API</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 bg-slate-800/50 p-1.5 rounded-xl border border-slate-700">
        {tabs.map((tab) => {
          const TabIcon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg shadow-primary-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <TabIcon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ============= FLIGHTS TAB ============= */}
      {activeTab === 'flights' && (
      <>
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
                  <button 
                    onClick={() => handleSelectFlight(searchResults.best_deal)}
                    className="w-full px-6 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-all flex items-center justify-center gap-2"
                  >
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
                    <button 
                      onClick={() => handleSelectFlight(flight)}
                      className="w-full px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-all flex items-center justify-center gap-2"
                    >
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
      </>
      )}

      {/* ============= HOTELS TAB ============= */}
      {activeTab === 'hotels' && (
      <>
        {/* Hotel Search Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-amber-600/20 to-orange-600/20 border-amber-500/30"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <FaHotel className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Hotel Search</h2>
              <p className="text-sm text-slate-400">Find the perfect stay at the best prices</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* City */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiLocationMarker className="inline w-4 h-4 mr-1" />
                City / Destination
              </label>
              <input
                type="text"
                value={hotelSearch.city}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, city: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                placeholder="e.g., New York, Paris, Tokyo"
              />
            </div>

            {/* Check-in */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiCalendar className="inline w-4 h-4 mr-1" />
                Check-in
              </label>
              <input
                type="date"
                value={hotelSearch.checkIn}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, checkIn: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-amber-500"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            {/* Check-out */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiCalendar className="inline w-4 h-4 mr-1" />
                Check-out
              </label>
              <input
                type="date"
                value={hotelSearch.checkOut}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, checkOut: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-amber-500"
                min={hotelSearch.checkIn || new Date().toISOString().split('T')[0]}
              />
            </div>

            {/* Guests */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiUsers className="inline w-4 h-4 mr-1" />
                Guests
              </label>
              <select
                value={hotelSearch.guests}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, guests: parseInt(e.target.value) }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-amber-500"
              >
                {[1,2,3,4,5,6].map(n => (
                  <option key={n} value={n}>{n} {n === 1 ? 'Guest' : 'Guests'}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Rooms */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">Rooms</label>
              <select
                value={hotelSearch.rooms}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, rooms: parseInt(e.target.value) }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-amber-500"
              >
                {[1,2,3,4].map(n => (
                  <option key={n} value={n}>{n} {n === 1 ? 'Room' : 'Rooms'}</option>
                ))}
              </select>
            </div>

            {/* Min Rating */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiStar className="inline w-4 h-4 mr-1" />
                Minimum Rating
              </label>
              <select
                value={hotelSearch.minRating}
                onChange={(e) => setHotelSearch(prev => ({ ...prev, minRating: parseFloat(e.target.value) }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-amber-500"
              >
                <option value={0}>Any Rating</option>
                <option value={3}>3+ Stars</option>
                <option value={4}>4+ Stars</option>
                <option value={4.5}>4.5+ Stars</option>
              </select>
            </div>

            {/* Search Button */}
            <div className="flex items-end">
              <button
                onClick={searchHotels}
                disabled={isSearchingHotels}
                className="w-full px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg hover:from-amber-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSearchingHotels ? (
                  <><HiRefresh className="w-5 h-5 animate-spin" /> Searching...</>
                ) : (
                  <><HiSearch className="w-5 h-5" /> Search Hotels</>
                )}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Hotel Results */}
        {hotelResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">{hotelResults.hotels.length} Hotels Found</h3>
                  <p className="text-sm text-slate-400">{hotelResults.city} &bull; {hotelResults.nights} night{hotelResults.nights > 1 ? 's' : ''}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-slate-400">Starting from</p>
                  <p className="text-lg font-semibold text-white">
                    ${Math.min(...hotelResults.hotels.map(h => h.pricePerNight)).toFixed(0)}/night
                  </p>
                </div>
              </div>
            </div>

            {hotelResults.hotels.map((hotel, index) => (
              <motion.div
                key={hotel.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card hover:border-amber-500/30 transition-all overflow-hidden"
              >
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                  {/* Image */}
                  <div className="lg:col-span-1">
                    <div className="w-full h-48 lg:h-full rounded-lg overflow-hidden bg-slate-700">
                      <img
                        src={hotel.image}
                        alt={hotel.name}
                        className="w-full h-full object-cover"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>
                  </div>

                  {/* Info */}
                  <div className="lg:col-span-2">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="text-lg font-bold text-white">{hotel.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex items-center gap-0.5">
                            {Array.from({ length: Math.floor(hotel.starRating) }).map((_, i) => (
                              <HiStar key={i} className="w-4 h-4 text-amber-400" />
                            ))}
                          </div>
                          <span className="text-xs text-slate-400">{hotel.starRating} Star</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 bg-emerald-500/20 px-2 py-1 rounded-lg">
                        <span className="text-sm font-bold text-emerald-400">{hotel.userRating}</span>
                        <span className="text-xs text-slate-400">({hotel.reviewCount})</span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-400 mb-3">
                      <HiLocationMarker className="inline w-4 h-4 mr-1" />
                      {hotel.address}, {hotel.city} &bull; {hotel.distanceFromCenter} km from center
                    </p>

                    <p className="text-sm text-white mb-2">{hotel.roomType}</p>

                    {/* Amenities */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {hotel.amenities.slice(0, 5).map((amenity, i) => (
                        <span key={i} className="flex items-center gap-1 px-2 py-1 bg-slate-700/50 rounded text-xs text-slate-300">
                          {getAmenityIcon(amenity)} {amenity}
                        </span>
                      ))}
                      {hotel.amenities.length > 5 && (
                        <span className="px-2 py-1 bg-slate-700/50 rounded text-xs text-slate-400">+{hotel.amenities.length - 5} more</span>
                      )}
                    </div>

                    {/* Badges */}
                    <div className="flex flex-wrap gap-2">
                      {hotel.breakfastIncluded && (
                        <span className="flex items-center gap-1 text-xs text-emerald-400">
                          <FaCoffee className="w-3 h-3" /> Breakfast included
                        </span>
                      )}
                      {hotel.freeCancellation && (
                        <span className="flex items-center gap-1 text-xs text-emerald-400">
                          <HiShieldCheck className="w-3 h-3" /> Free cancellation
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Price & Book */}
                  <div className="flex flex-col items-end justify-between">
                    <div className="text-right">
                      <p className="text-sm text-slate-400">{hotelResults.nights} night{hotelResults.nights > 1 ? 's' : ''}</p>
                      <p className="text-2xl font-bold text-white">${hotel.totalPrice.toFixed(0)}</p>
                      <p className="text-xs text-slate-400">${hotel.pricePerNight}/night &bull; {hotel.currency}</p>
                    </div>
                    <button
                      onClick={() => toast.success(`Hotel "${hotel.name}" selected! Booking page coming soon.`)}
                      className="w-full mt-4 px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-all flex items-center justify-center gap-2"
                    >
                      <span>Select Room</span>
                      <HiArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Hotel Empty State */}
        {!hotelResults && !isSearchingHotels && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card text-center py-12">
            <FaHotel className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Find Your Perfect Stay</h3>
            <p className="text-slate-400 mb-4">Search for hotels by city, set your dates, and discover the best deals available</p>
            <p className="text-xs text-slate-500">Compare prices, amenities, and ratings across hundreds of properties</p>
          </motion.div>
        )}
      </>
      )}

      {/* ============= CARS TAB ============= */}
      {activeTab === 'cars' && (
      <>
        {/* Car Search Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-cyan-600/20 to-blue-600/20 border-cyan-500/30"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center">
              <FaCar className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Car Rental</h2>
              <p className="text-sm text-slate-400">Rent a car for your trip at the best prices</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Pickup Location */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiLocationMarker className="inline w-4 h-4 mr-1" />
                Pickup Location
              </label>
              <input
                type="text"
                value={carSearch.pickupLocation}
                onChange={(e) => setCarSearch(prev => ({ ...prev, pickupLocation: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                placeholder="City or airport"
              />
            </div>

            {/* Drop-off Location */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiLocationMarker className="inline w-4 h-4 mr-1" />
                Drop-off Location
              </label>
              <input
                type="text"
                value={carSearch.dropoffLocation}
                onChange={(e) => setCarSearch(prev => ({ ...prev, dropoffLocation: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                placeholder="Same as pickup"
              />
            </div>

            {/* Pickup Date */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiCalendar className="inline w-4 h-4 mr-1" />
                Pickup Date
              </label>
              <input
                type="date"
                value={carSearch.pickupDate}
                onChange={(e) => setCarSearch(prev => ({ ...prev, pickupDate: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            {/* Drop-off Date */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiCalendar className="inline w-4 h-4 mr-1" />
                Drop-off Date
              </label>
              <input
                type="date"
                value={carSearch.dropoffDate}
                onChange={(e) => setCarSearch(prev => ({ ...prev, dropoffDate: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                min={carSearch.pickupDate || new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {/* Pickup Time */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiClock className="inline w-4 h-4 mr-1" />
                Pickup Time
              </label>
              <select
                value={carSearch.pickupTime}
                onChange={(e) => setCarSearch(prev => ({ ...prev, pickupTime: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              >
                {Array.from({ length: 24 }, (_, i) => {
                  const h = i.toString().padStart(2, '0');
                  return [<option key={`${h}:00`} value={`${h}:00`}>{h}:00</option>, <option key={`${h}:30`} value={`${h}:30`}>{h}:30</option>];
                })}
              </select>
            </div>

            {/* Drop-off Time */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <HiClock className="inline w-4 h-4 mr-1" />
                Drop-off Time
              </label>
              <select
                value={carSearch.dropoffTime}
                onChange={(e) => setCarSearch(prev => ({ ...prev, dropoffTime: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              >
                {Array.from({ length: 24 }, (_, i) => {
                  const h = i.toString().padStart(2, '0');
                  return [<option key={`${h}:00`} value={`${h}:00`}>{h}:00</option>, <option key={`${h}:30`} value={`${h}:30`}>{h}:30</option>];
                })}
              </select>
            </div>

            {/* Car Type */}
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                <FaCar className="inline w-4 h-4 mr-1" />
                Car Type
              </label>
              <select
                value={carSearch.carType}
                onChange={(e) => setCarSearch(prev => ({ ...prev, carType: e.target.value }))}
                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="all">All Types</option>
                <option value="economy">Economy</option>
                <option value="suv">SUV</option>
                <option value="premium">Premium</option>
                <option value="van">Van / Minivan</option>
                <option value="luxury">Luxury</option>
                <option value="electric">Electric</option>
              </select>
            </div>

            {/* Search Button */}
            <div className="flex items-end">
              <button
                onClick={searchCars}
                disabled={isSearchingCars}
                className="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSearchingCars ? (
                  <><HiRefresh className="w-5 h-5 animate-spin" /> Searching...</>
                ) : (
                  <><HiSearch className="w-5 h-5" /> Search Cars</>
                )}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Car Results */}
        {carResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">{carResults.cars.length} Cars Available</h3>
                  <p className="text-sm text-slate-400">{carResults.location} &bull; {carResults.days} day{carResults.days > 1 ? 's' : ''}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-slate-400">Starting from</p>
                  <p className="text-lg font-semibold text-white">
                    ${Math.min(...carResults.cars.map(c => c.pricePerDay)).toFixed(0)}/day
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {carResults.cars.map((car, index) => (
                <motion.div
                  key={car.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="card hover:border-cyan-500/30 transition-all overflow-hidden"
                >
                  {/* Car Image */}
                  <div className="w-full h-44 rounded-lg overflow-hidden bg-slate-700 mb-4">
                    <img
                      src={car.image}
                      alt={car.name}
                      className="w-full h-full object-cover"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  </div>

                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-lg font-bold text-white">{car.name}</h4>
                      <p className="text-sm text-slate-400">{car.company} &bull; {car.type}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      car.type === 'Electric' ? 'bg-emerald-500/20 text-emerald-400' :
                      car.type === 'Luxury' ? 'bg-purple-500/20 text-purple-400' :
                      car.type === 'Premium' ? 'bg-amber-500/20 text-amber-400' :
                      'bg-slate-700 text-slate-300'
                    }`}>{car.type}</span>
                  </div>

                  {/* Specs */}
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <HiUsers className="w-3.5 h-3.5" /> {car.seats} seats
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <FaGasPump className="w-3 h-3" /> {car.fuelType}
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <HiClock className="w-3.5 h-3.5" /> {car.transmission}
                    </div>
                  </div>

                  {/* Features */}
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {car.features.slice(0, 4).map((feat, i) => (
                      <span key={i} className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{feat}</span>
                    ))}
                    {car.features.length > 4 && (
                      <span className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-400">+{car.features.length - 4}</span>
                    )}
                  </div>

                  {/* Details */}
                  <div className="flex flex-wrap gap-3 mb-4 text-xs">
                    <span className="text-slate-400">Mileage: <span className="text-white">{car.mileage}</span></span>
                    <span className="text-slate-400">Insurance: <span className="text-white">{car.insurance}</span></span>
                  </div>
                  {car.freeCancellation && (
                    <p className="flex items-center gap-1 text-xs text-emerald-400 mb-4">
                      <HiShieldCheck className="w-3.5 h-3.5" /> Free cancellation
                    </p>
                  )}

                  {/* Price & Action */}
                  <div className="border-t border-slate-700 pt-4 flex items-end justify-between">
                    <div>
                      <p className="text-2xl font-bold text-white">${car.totalPrice.toFixed(0)}</p>
                      <p className="text-xs text-slate-400">${car.pricePerDay}/day &bull; {carResults.days} day{carResults.days > 1 ? 's' : ''}</p>
                    </div>
                    <button
                      onClick={() => toast.success(`"${car.name}" from ${car.company} selected! Booking page coming soon.`)}
                      className="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-all flex items-center gap-2 text-sm"
                    >
                      Select <HiArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Car Empty State */}
        {!carResults && !isSearchingCars && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card text-center py-12">
            <FaCar className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Rent a Car</h3>
            <p className="text-slate-400 mb-4">Search for car rentals by pickup location and dates to find the best deals</p>
            <p className="text-xs text-slate-500">Economy, SUV, premium, luxury, electric and more available worldwide</p>
          </motion.div>
        )}
      </>
      )}

    </div>
  );
};

export default Travel;
