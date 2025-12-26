import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
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
} from 'react-icons/hi';
import { FaGavel, FaFileContract, FaBalanceScale } from 'react-icons/fa';

const Research = () => {
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('all');
  const [isSearching, setIsSearching] = useState(false);

  // Mock search results
  const searchResults = [
    {
      id: 1,
      title: 'Smith v. Jones Corporation (2023)',
      type: 'Case Law',
      jurisdiction: 'Canada',
      court: 'Supreme Court of Canada',
      date: '2023-08-15',
      relevance: 95,
      summary: 'Landmark decision on corporate liability in environmental damage cases...',
      citations: 45,
    },
    {
      id: 2,
      title: 'Contract Law Amendment Act, 2023',
      type: 'Legislation',
      jurisdiction: 'Kenya',
      court: 'National Assembly',
      date: '2023-06-20',
      relevance: 88,
      summary: 'Amendments to contract formation requirements and electronic signatures...',
      citations: 23,
    },
    {
      id: 3,
      title: 'Johnson v. Tech Industries Inc.',
      type: 'Case Law',
      jurisdiction: 'United States',
      court: 'US Court of Appeals',
      date: '2023-09-10',
      relevance: 82,
      summary: 'Important ruling on intellectual property rights in AI-generated content...',
      citations: 67,
    },
  ];

  // Mock projects
  const projects = [
    {
      id: 1,
      name: 'Corporate Merger Review',
      client: 'ABC Holdings',
      documents: 24,
      lastUpdated: '2024-01-18',
      status: 'Active',
    },
    {
      id: 2,
      name: 'IP Litigation Research',
      client: 'Tech Startup Inc.',
      documents: 15,
      lastUpdated: '2024-01-15',
      status: 'Active',
    },
    {
      id: 3,
      name: 'Real Estate Due Diligence',
      client: 'Property Group Ltd.',
      documents: 31,
      lastUpdated: '2024-01-10',
      status: 'Completed',
    },
  ];

  // Mock bookmarks
  const bookmarks = [
    { id: 1, title: 'Anti-Trust Guidelines 2023', type: 'Regulation', date: '2024-01-15' },
    { id: 2, title: 'Corporate Governance Best Practices', type: 'Article', date: '2024-01-12' },
    { id: 3, title: 'Cross-Border Transaction Framework', type: 'Legislation', date: '2024-01-08' },
  ];

  const jurisdictions = [
    { code: 'all', name: 'All Jurisdictions', flag: '🌍' },
    { code: 'CA', name: 'Canada', flag: '🇨🇦' },
    { code: 'US', name: 'United States', flag: '🇺🇸' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'UK', name: 'United Kingdom', flag: '🇬🇧' },
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }
    setIsSearching(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    toast.success(`Found ${searchResults.length} results`);
    setIsSearching(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Legal Research</h1>
          <p className="text-slate-400">Search case law, statutes, and regulations across jurisdictions</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-ghost flex items-center gap-2 border border-slate-700">
            <HiBookmark className="w-5 h-5" />
            Bookmarks
          </button>
          <button className="btn-primary flex items-center gap-2">
            <HiPlus className="w-5 h-5" />
            New Project
          </button>
        </div>
      </div>

      {/* Search Section */}
      <div className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80">
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <HiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search case law, statutes, regulations..."
              className="input pl-12 py-3.5"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <select
            value={selectedJurisdiction}
            onChange={(e) => setSelectedJurisdiction(e.target.value)}
            className="input w-full md:w-48"
          >
            {jurisdictions.map(j => (
              <option key={j.code} value={j.code}>{j.flag} {j.name}</option>
            ))}
          </select>
          <button className="btn-ghost flex items-center gap-2 border border-slate-700">
            <HiFilter className="w-5 h-5" />
            Filters
          </button>
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="btn-primary flex items-center gap-2 px-6"
          >
            {isSearching ? (
              <>
                <span className="spinner-small" />
                Searching...
              </>
            ) : (
              <>
                <HiSearch className="w-5 h-5" />
                Search
              </>
            )}
          </button>
        </div>

        {/* Quick Filters */}
        <div className="flex flex-wrap gap-2">
          {['Case Law', 'Legislation', 'Regulations', 'Commentary', 'Treaties'].map((filter) => (
            <button
              key={filter}
              className="px-3 py-1.5 rounded-lg text-sm bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <div className="flex gap-6">
          {['search', 'projects', 'bookmarks'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 capitalize transition-colors relative ${
                activeTab === tab
                  ? 'text-white'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              {tab === 'search' ? 'Results' : tab}
              {activeTab === tab && (
                <motion.div
                  layoutId="researchTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Search Results */}
      {activeTab === 'search' && (
        <div className="space-y-4">
          {searchResults.map((result, index) => (
            <motion.div
              key={result.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:border-primary-500/50 cursor-pointer"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    result.type === 'Case Law' ? 'bg-primary-500/20' : 'bg-secondary-500/20'
                  }`}>
                    {result.type === 'Case Law' ? (
                      <FaGavel className={`w-6 h-6 ${result.type === 'Case Law' ? 'text-primary-400' : 'text-secondary-400'}`} />
                    ) : (
                      <HiLibrary className="w-6 h-6 text-secondary-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`badge ${result.type === 'Case Law' ? 'badge-primary' : 'badge-secondary'}`}>
                        {result.type}
                      </span>
                      <span className="text-sm text-slate-400">{result.jurisdiction}</span>
                      <span className="text-sm text-slate-500">•</span>
                      <span className="text-sm text-slate-400">{result.court}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{result.title}</h3>
                    <p className="text-slate-400 text-sm line-clamp-2">{result.summary}</p>
                    <div className="flex items-center gap-4 mt-3">
                      <span className="text-xs text-slate-500 flex items-center gap-1">
                        <HiClock className="w-4 h-4" />
                        {result.date}
                      </span>
                      <span className="text-xs text-slate-500 flex items-center gap-1">
                        <HiDocumentText className="w-4 h-4" />
                        {result.citations} citations
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-400">Relevance</span>
                    <span className={`font-bold ${
                      result.relevance >= 90 ? 'text-emerald-400' : result.relevance >= 80 ? 'text-amber-400' : 'text-slate-400'
                    }`}>
                      {result.relevance}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                      <HiBookmark className="w-5 h-5" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                      <HiDownload className="w-5 h-5" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                      <HiExternalLink className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}

          {searchResults.length === 0 && (
            <div className="card text-center py-16">
              <FaBalanceScale className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Start Your Research</h3>
              <p className="text-slate-400 max-w-md mx-auto">
                Search across case law, legislation, and regulations from Canada, United States, Kenya, and more.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Projects */}
      {activeTab === 'projects' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:border-primary-500/50 cursor-pointer"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                  <HiFolder className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{project.name}</h3>
                  <p className="text-sm text-slate-400">{project.client}</p>
                </div>
                <span className={`badge ${project.status === 'Active' ? 'badge-primary' : 'bg-slate-700 text-slate-300'}`}>
                  {project.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400 flex items-center gap-1">
                  <HiDocumentText className="w-4 h-4" />
                  {project.documents} documents
                </span>
                <span className="text-slate-500 flex items-center gap-1">
                  <HiClock className="w-4 h-4" />
                  {project.lastUpdated}
                </span>
              </div>
            </motion.div>
          ))}

          {/* Add Project Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: projects.length * 0.1 }}
            className="card border-dashed cursor-pointer hover:border-primary-500/50 flex items-center justify-center py-12"
            onClick={() => toast.success('Opening new project dialog...')}
          >
            <div className="text-center">
              <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto mb-3">
                <HiPlus className="w-6 h-6 text-slate-400" />
              </div>
              <p className="font-medium text-white">New Research Project</p>
              <p className="text-sm text-slate-400">Organize your research</p>
            </div>
          </motion.div>
        </div>
      )}

      {/* Bookmarks */}
      {activeTab === 'bookmarks' && (
        <div className="card">
          <div className="space-y-3">
            {bookmarks.map((bookmark, index) => (
              <motion.div
                key={bookmark.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                    <HiStar className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">{bookmark.title}</p>
                    <p className="text-sm text-slate-400">{bookmark.type} • Saved {bookmark.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                    <HiExternalLink className="w-5 h-5" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                    <HiDownload className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiScale className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">1,247</p>
              <p className="text-sm text-slate-400">Cases Researched</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-secondary-500/20 flex items-center justify-center">
              <HiDocumentText className="w-5 h-5 text-secondary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">70</p>
              <p className="text-sm text-slate-400">Documents Saved</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <HiClock className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">48h</p>
              <p className="text-sm text-slate-400">Research Time Saved</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Research;
