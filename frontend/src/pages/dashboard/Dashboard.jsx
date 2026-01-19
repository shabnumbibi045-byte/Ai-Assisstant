import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import {
  HiCurrencyDollar,
  HiTrendingUp,
  HiGlobe,
  HiBookOpen,
  HiChatAlt2,
  HiArrowRight,
  HiSparkles,
} from 'react-icons/hi';

const Dashboard = () => {
  const { user } = useAuthStore();

  // Module cards data - without fake stats
  const modules = [
    {
      name: 'Banking',
      icon: HiCurrencyDollar,
      href: '/banking',
      gradient: 'from-emerald-600 to-teal-600',
      description: 'Connect and manage your bank accounts across Canada, US, and Kenya',
      features: ['Multi-currency support', 'Transaction history', 'Account analytics'],
    },
    {
      name: 'Stocks',
      icon: HiTrendingUp,
      href: '/stocks',
      gradient: 'from-primary-600 to-violet-600',
      description: 'Track real-time stock prices and manage your portfolio',
      features: ['Real-time quotes', 'Portfolio tracking', 'Market analysis'],
    },
    {
      name: 'Travel',
      icon: HiGlobe,
      href: '/travel',
      gradient: 'from-secondary-600 to-blue-600',
      description: 'Search flights, hotels, and plan your trips with AI assistance',
      features: ['Flight search', 'Hotel bookings', 'VIP benefits'],
    },
    {
      name: 'Research',
      icon: HiBookOpen,
      href: '/research',
      gradient: 'from-amber-600 to-orange-600',
      description: 'Access legal research databases for US court opinions',
      features: ['Case law search', 'Court opinions', 'Legal citations'],
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-900/50 via-slate-900 to-secondary-900/50 p-8"
      >
        {/* Background decorations */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary-500/10 rounded-full blur-3xl"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <HiSparkles className="w-6 h-6 text-primary-400" />
            <span className="text-primary-400 font-medium">AN INTELLIGENT AI</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-display font-bold text-white mb-2">
            Welcome back, {user?.name?.split(' ')[0] || 'there'}!
          </h1>
          <p className="text-slate-400 text-lg mb-6 max-w-2xl">
            Your AI-powered assistant for banking, stocks, travel, and legal research.
            Start a conversation or explore the modules below.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link to="/chat" className="btn-primary">
              <HiChatAlt2 className="w-5 h-5 mr-2" />
              Start Conversation
            </Link>
            <Link to="/banking" className="btn-outline">
              Connect Bank Account
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Module Cards */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Explore Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((module, index) => (
            <motion.div
              key={module.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
            >
              <Link to={module.href} className="block group">
                <div className={`module-card bg-gradient-to-br ${module.gradient}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <module.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-1">{module.name}</h3>
                      <p className="text-white/70 text-sm mb-4">{module.description}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 pt-4 border-t border-white/20">
                    {module.features.map((feature, i) => (
                      <span key={i} className="px-2 py-1 bg-white/10 rounded-lg text-xs text-white/80">
                        {feature}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center gap-2 mt-4 text-white/80 group-hover:text-white transition-colors">
                    <span className="text-sm font-medium">Open {module.name}</span>
                    <HiArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* AI Chat Highlight */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card bg-gradient-to-r from-slate-800/50 to-slate-800/30 border border-slate-700/50"
      >
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center flex-shrink-0">
            <HiChatAlt2 className="w-8 h-8 text-white" />
          </div>
          <div className="flex-1 text-center md:text-left">
            <h3 className="text-lg font-semibold text-white mb-1">Chat with AN INTELLIGENT AI</h3>
            <p className="text-slate-400">
              Ask questions, get banking insights, search for flights, check stock prices,
              or research legal cases - all through natural conversation.
            </p>
          </div>
          <Link to="/chat" className="btn-primary flex-shrink-0">
            <HiChatAlt2 className="w-5 h-5 mr-2" />
            Open Chat
          </Link>
        </div>
      </motion.div>

      {/* Quick Actions Grid */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'View Accounts', href: '/banking', icon: HiCurrencyDollar, color: 'from-emerald-500 to-teal-500' },
            { label: 'Stock Quotes', href: '/stocks', icon: HiTrendingUp, color: 'from-primary-500 to-violet-500' },
            { label: 'Search Flights', href: '/travel', icon: HiGlobe, color: 'from-secondary-500 to-blue-500' },
            { label: 'Legal Research', href: '/research', icon: HiBookOpen, color: 'from-amber-500 to-orange-500' },
          ].map((action, index) => (
            <motion.div
              key={action.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <Link
                to={action.href}
                className="block p-4 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 hover:border-slate-600/50 transition-all group"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-slate-200 font-medium">{action.label}</span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
