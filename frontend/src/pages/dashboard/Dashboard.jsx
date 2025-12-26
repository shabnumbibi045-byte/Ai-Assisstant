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
  HiArrowUp,
  HiArrowDown,
  HiDotsHorizontal,
} from 'react-icons/hi';

const Dashboard = () => {
  const { user } = useAuthStore();

  // Module cards data
  const modules = [
    {
      name: 'Banking',
      icon: HiCurrencyDollar,
      href: '/banking',
      gradient: 'from-emerald-600 to-teal-600',
      stats: { label: 'Total Balance', value: '$98,500', change: '+2.5%', up: true },
      description: 'Manage accounts in Canada, US, and Kenya',
    },
    {
      name: 'Stocks',
      icon: HiTrendingUp,
      href: '/stocks',
      gradient: 'from-primary-600 to-violet-600',
      stats: { label: 'Portfolio Value', value: '$287,450', change: '+1.8%', up: true },
      description: 'Track your stock portfolio performance',
    },
    {
      name: 'Travel',
      icon: HiGlobe,
      href: '/travel',
      gradient: 'from-secondary-600 to-blue-600',
      stats: { label: 'Active Alerts', value: '3', change: '2 price drops', up: true },
      description: 'Search flights, hotels with VIP benefits',
    },
    {
      name: 'Research',
      icon: HiBookOpen,
      href: '/research',
      gradient: 'from-amber-600 to-orange-600',
      stats: { label: 'Projects', value: '4', change: '12 documents', up: true },
      description: 'Legal research for Canada & US',
    },
  ];

  // Recent activities
  const activities = [
    { type: 'banking', text: 'Weekly transaction export sent to accountant', time: '2 hours ago', icon: HiCurrencyDollar },
    { type: 'stocks', text: 'Portfolio gained $1,250.50 today', time: '4 hours ago', icon: HiTrendingUp },
    { type: 'travel', text: 'Price dropped $45 for Toronto → Dubai flight', time: '6 hours ago', icon: HiGlobe },
    { type: 'chat', text: 'Completed research on contract law', time: '1 day ago', icon: HiChatAlt2 },
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
          <h1 className="text-3xl md:text-4xl font-display font-bold text-white mb-2">
            Welcome back, {user?.name?.split(' ')[0] || 'there'}! 👋
          </h1>
          <p className="text-slate-400 text-lg mb-6">
            Here's what's happening with your accounts today.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <Link to="/chat" className="btn-primary">
              <HiChatAlt2 className="w-5 h-5 mr-2" />
              Start Chat
            </Link>
            <Link to="/banking" className="btn-outline">
              View Reports
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Assets', value: '$385,950', change: '+3.2%', up: true, color: 'emerald' },
          { label: 'Monthly Spending', value: '$4,250', change: '-12%', up: true, color: 'primary' },
          { label: 'Active Investments', value: '24', change: '+2', up: true, color: 'secondary' },
          { label: 'Pending Actions', value: '3', change: 'Review', up: null, color: 'amber' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">{stat.label}</span>
              {stat.up !== null && (
                <span className={`flex items-center text-xs ${stat.up ? 'text-emerald-400' : 'text-red-400'}`}>
                  {stat.up ? <HiArrowUp className="w-3 h-3" /> : <HiArrowDown className="w-3 h-3" />}
                  {stat.change}
                </span>
              )}
              {stat.up === null && (
                <span className="badge-warning text-xs">{stat.change}</span>
              )}
            </div>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Module Cards */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Your Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((module, index) => (
            <motion.div
              key={module.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
            >
              <Link to={module.href} className="block group">
                <div className={`module-card bg-gradient-to-br ${module.gradient}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <module.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-1">{module.name}</h3>
                      <p className="text-white/70 text-sm mb-4">{module.description}</p>
                    </div>
                    <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
                      <HiDotsHorizontal className="w-5 h-5 text-white/70" />
                    </button>
                  </div>
                  
                  <div className="flex items-end justify-between pt-4 border-t border-white/20">
                    <div>
                      <p className="text-white/70 text-sm">{module.stats.label}</p>
                      <p className="text-2xl font-bold text-white">{module.stats.value}</p>
                    </div>
                    <span className={`flex items-center gap-1 text-sm ${module.stats.up ? 'text-emerald-300' : 'text-red-300'}`}>
                      {module.stats.up ? <HiArrowUp className="w-4 h-4" /> : <HiArrowDown className="w-4 h-4" />}
                      {module.stats.change}
                    </span>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Feed */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {activities.map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-700/30 transition-colors"
                >
                  <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center flex-shrink-0">
                    <activity.icon className="w-5 h-5 text-primary-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-slate-200 truncate">{activity.text}</p>
                    <p className="text-slate-500 text-sm">{activity.time}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {[
              { label: 'Export Transactions', href: '/banking', color: 'emerald' },
              { label: 'Check Stock Prices', href: '/stocks', color: 'primary' },
              { label: 'Search Flights', href: '/travel', color: 'secondary' },
              { label: 'New Research Project', href: '/research', color: 'amber' },
              { label: 'Upload Document', href: '/documents', color: 'teal' },
            ].map((action, index) => (
              <Link
                key={action.label}
                to={action.href}
                className="block p-3 rounded-xl bg-slate-700/30 hover:bg-slate-700/50 transition-colors"
              >
                <span className="text-slate-200">{action.label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
