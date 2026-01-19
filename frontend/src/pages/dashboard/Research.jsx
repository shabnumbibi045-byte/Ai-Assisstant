import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../store/authStore';
import {
  HiSearch,
  HiDocumentText,
  HiFolder,
  HiClock,
  HiBookmark,
  HiPlus,
  HiFilter,
  HiDownload,
  HiExternalLink,
  HiStar,
  HiScale,
  HiLibrary,
  HiCheckCircle,
  HiXCircle,
} from 'react-icons/hi';
import { FaGavel, FaFileContract, FaBalanceScale } from 'react-icons/fa';

// API base URL from environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const Research = () => {
  const { token, user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('federal');
  const [selectedCourt, setSelectedCourt] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const jurisdictions = [
    { code: 'federal', name: 'Federal Courts', flag: '🇺🇸', description: 'Supreme Court, Circuit Courts, District Courts' },
    { code: 'state', name: 'State Courts', flag: '🏛️', description: 'State Supreme and Appellate Courts' },
  ];

  const commonCourts = [
    { code: '', name: 'All Courts' },
    { code: 'scotus', name: 'Supreme Court of the United States' },
    { code: 'ca1', name: '1st Circuit Court of Appeals' },
    { code: 'ca2', name: '2nd Circuit Court of Appeals' },
    { code: 'ca3', name: '3rd Circuit Court of Appeals' },
    { code: 'ca4', name: '4th Circuit Court of Appeals' },
    { code: 'ca5', name: '5th Circuit Court of Appeals' },
    { code: 'ca6', name: '6th Circuit Court of Appeals' },
    { code: 'ca7', name: '7th Circuit Court of Appeals' },
    { code: 'ca8', name: '8th Circuit Court of Appeals' },
    { code: 'ca9', name: '9th Circuit Court of Appeals' },
    { code: 'ca10', name: '10th Circuit Court of Appeals' },
    { code: 'ca11', name: '11th Circuit Court of Appeals' },
    { code: 'cadc', name: 'D.C. Circuit Court of Appeals' },
    { code: 'cafc', name: 'Federal Circuit Court of Appeals' },
    { code: 'nysd', name: 'S.D. New York' },
    { code: 'cand', name: 'N.D. California' },
    { code: 'cacd', name: 'C.D. California' },
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    if (!token) {
      toast.error('Please log in to search cases');
      return;
    }

    setIsSearching(true);
    setSearchResults([]);

    try {
      const response = await fetch(`${API_BASE_URL}/tools/invoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.user_id || user?.id || 'unknown',
          tool_name: 'search_legal_us',
          parameters: {
            query: searchQuery,
            jurisdiction: selectedJurisdiction,
            court: selectedCourt || undefined,
            date_filed_after: dateFrom || undefined,
            date_filed_before: dateTo || undefined,
            limit: 10
          }
        })
      });

      const data = await response.json();

      if (data.success && data.data) {
        const results = data.data.results || [];
        setSearchResults(results);
        setTotalResults(data.data.total_results || 0);

        if (results.length > 0) {
          toast.success(`Found ${data.data.total_results} cases from CourtListener API`, {
            duration: 4000,
            icon: '⚖️'
          });
        } else {
          toast.error('No cases found. Try different search terms or filters.');
        }
      } else {
        toast.error(data.message || 'Failed to search cases');
      }
    } catch (error) {
      toast.error('Failed to search cases. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr || dateStr === 'Unknown') return 'Date unknown';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      return dateStr;
    }
  };

  const getCourtBadgeColor = (court) => {
    if (court.includes('Supreme Court')) return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
    if (court.includes('Circuit') || court.includes('Appeals')) return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    if (court.includes('District')) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white flex items-center gap-2">
            <FaBalanceScale className="w-7 h-7 text-primary-400" />
            Legal Research
          </h1>
          <p className="text-slate-400">Search millions of US court opinions via CourtListener API</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="badge badge-primary flex items-center gap-1">
            <HiCheckCircle className="w-4 h-4" />
            Real-Time Data
          </span>
        </div>
      </div>

      {/* Search Section */}
      <div className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80">
        <div className="flex flex-col gap-4">
          {/* Main Search Bar */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <HiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search US case law (e.g., habeas corpus, Fourth Amendment, negligence)..."
                className="input pl-12 py-3.5"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="btn-primary flex items-center gap-2 px-6 whitespace-nowrap"
            >
              {isSearching ? (
                <>
                  <span className="spinner-small" />
                  Searching...
                </>
              ) : (
                <>
                  <HiSearch className="w-5 h-5" />
                  Search Cases
                </>
              )}
            </button>
          </div>

          {/* Filters Row */}
          <div className="flex flex-col md:flex-row gap-4">
            <select
              value={selectedJurisdiction}
              onChange={(e) => setSelectedJurisdiction(e.target.value)}
              className="input flex-1"
            >
              {jurisdictions.map(j => (
                <option key={j.code} value={j.code}>{j.flag} {j.name}</option>
              ))}
            </select>

            <select
              value={selectedCourt}
              onChange={(e) => setSelectedCourt(e.target.value)}
              className="input flex-1"
            >
              {commonCourts.map(c => (
                <option key={c.code} value={c.code}>{c.name}</option>
              ))}
            </select>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-ghost flex items-center gap-2 border border-slate-700"
            >
              <HiFilter className="w-5 h-5" />
              Date Filters
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="flex flex-col md:flex-row gap-4 pt-4 border-t border-slate-700"
            >
              <div className="flex-1">
                <label className="text-sm text-slate-400 mb-2 block">Filed After</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="input"
                />
              </div>
              <div className="flex-1">
                <label className="text-sm text-slate-400 mb-2 block">Filed Before</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="input"
                />
              </div>
            </motion.div>
          )}

          {/* Quick Search Examples */}
          <div className="flex flex-wrap gap-2">
            <span className="text-xs text-slate-500">Try:</span>
            {['habeas corpus', 'Fourth Amendment', 'negligence', 'employment discrimination'].map((example) => (
              <button
                key={example}
                onClick={() => setSearchQuery(example)}
                className="px-3 py-1.5 rounded-lg text-xs bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results Stats */}
      {totalResults > 0 && (
        <div className="flex items-center gap-4 text-sm text-slate-400">
          <span className="flex items-center gap-2">
            <HiCheckCircle className="w-5 h-5 text-emerald-400" />
            Found <span className="font-bold text-white">{totalResults.toLocaleString()}</span> total results
          </span>
          <span className="text-slate-600">•</span>
          <span>Showing {searchResults.length} cases</span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            CourtListener API
          </span>
        </div>
      )}

      {/* Search Results */}
      <div className="space-y-4">
        {searchResults.map((result, index) => (
          <motion.div
            key={`${result.case_id}-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="card hover:border-primary-500/50 cursor-pointer group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-4 flex-1">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-primary-500/20 group-hover:bg-primary-500/30 transition-colors">
                  <FaGavel className="w-6 h-6 text-primary-400" />
                </div>
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded-md text-xs font-medium border ${getCourtBadgeColor(result.court || 'Unknown')}`}>
                      {result.court || 'Unknown Court'}
                    </span>
                    {result.docket_number && result.docket_number !== 'N/A' && (
                      <>
                        <span className="text-slate-600">•</span>
                        <span className="text-xs text-slate-500">Docket: {result.docket_number}</span>
                      </>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors">
                    {result.title || 'Untitled Case'}
                  </h3>

                  {result.citation && result.citation !== 'No citation' && (
                    <div className="text-sm text-slate-300 mb-2 font-mono">
                      📜 {result.citation}
                    </div>
                  )}

                  {result.summary && result.summary !== 'No summary available' && (
                    <p className="text-slate-400 text-sm line-clamp-2 mb-3">
                      {result.summary}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-4">
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <HiClock className="w-4 h-4" />
                      {formatDate(result.date)}
                    </span>
                    <span className="text-xs text-emerald-400 flex items-center gap-1">
                      <HiCheckCircle className="w-4 h-4" />
                      {result.data_source || 'CourtListener API'}
                    </span>
                    {result.case_id && (
                      <>
                        <span className="text-slate-600">•</span>
                        <span className="text-xs text-slate-500">ID: {result.case_id}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex flex-col items-end gap-2">
                {result.url && (
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-ghost flex items-center gap-2 text-sm"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <HiExternalLink className="w-4 h-4" />
                    View Case
                  </a>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {/* Empty State */}
        {!isSearching && searchResults.length === 0 && !totalResults && (
          <div className="card text-center py-16">
            <FaBalanceScale className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Search US Case Law</h3>
            <p className="text-slate-400 max-w-md mx-auto mb-4">
              Access millions of court opinions from CourtListener API - the same database used by lawyers and legal researchers.
            </p>
            <div className="flex flex-col gap-2 text-sm text-slate-500 max-w-lg mx-auto">
              <p className="flex items-center justify-center gap-2">
                <HiCheckCircle className="w-5 h-5 text-emerald-400" />
                Supreme Court, Circuit Courts, District Courts
              </p>
              <p className="flex items-center justify-center gap-2">
                <HiCheckCircle className="w-5 h-5 text-emerald-400" />
                Real-time data from PACER and court records
              </p>
              <p className="flex items-center justify-center gap-2">
                <HiCheckCircle className="w-5 h-5 text-emerald-400" />
                Free access to millions of opinions
              </p>
            </div>
          </div>
        )}

        {/* No Results Found */}
        {!isSearching && searchResults.length === 0 && totalResults === 0 && searchQuery && (
          <div className="card text-center py-12">
            <HiXCircle className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-white mb-2">No Cases Found</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              Try different search terms, adjust filters, or search for common legal topics.
            </p>
          </div>
        )}
      </div>

      {/* Info Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-gradient-to-br from-primary-500/10 to-primary-500/5 border-primary-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiScale className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide">Data Source</p>
              <p className="text-sm font-semibold text-white">CourtListener API</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border-emerald-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <HiCheckCircle className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide">Coverage</p>
              <p className="text-sm font-semibold text-white">Millions of Opinions</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <HiLibrary className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide">Access</p>
              <p className="text-sm font-semibold text-white">FREE Forever</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default Research;
