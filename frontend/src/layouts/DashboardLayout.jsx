import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import {
  HiHome,
  HiChatAlt2,
  HiCurrencyDollar,
  HiTrendingUp,
  HiGlobe,
  HiBookOpen,
  HiDocumentText,
  HiMicrophone,
  HiCog,
  HiUser,
  HiLogout,
  HiMenu,
  HiX,
  HiBell,
  HiSearch,
} from 'react-icons/hi';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HiHome },
  { name: 'AI Chat', href: '/chat', icon: HiChatAlt2 },
  { name: 'Banking', href: '/banking', icon: HiCurrencyDollar },
  { name: 'Stocks', href: '/stocks', icon: HiTrendingUp },
  { name: 'Travel', href: '/travel', icon: HiGlobe },
  { name: 'Research', href: '/research', icon: HiBookOpen },
  { name: 'Documents', href: '/documents', icon: HiDocumentText },
  { name: 'Voice', href: '/voice', icon: HiMicrophone },
];

const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-72 bg-slate-900 border-r border-slate-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <span className="text-xl font-display font-bold gradient-text">Salim AI</span>
            </div>
            <button
              className="lg:hidden text-slate-400 hover:text-white"
              onClick={() => setSidebarOpen(false)}
            >
              <HiX className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  isActive ? 'sidebar-item-active' : 'sidebar-item'
                }
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>

          {/* Bottom section */}
          <div className="p-4 border-t border-slate-800 space-y-1">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                isActive ? 'sidebar-item-active' : 'sidebar-item'
              }
              onClick={() => setSidebarOpen(false)}
            >
              <HiCog className="w-5 h-5" />
              <span>Settings</span>
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? 'sidebar-item-active' : 'sidebar-item'
              }
              onClick={() => setSidebarOpen(false)}
            >
              <HiUser className="w-5 h-5" />
              <span>Profile</span>
            </NavLink>
            <button
              onClick={handleLogout}
              className="sidebar-item w-full text-red-400 hover:text-red-300 hover:bg-red-500/10"
            >
              <HiLogout className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-slate-900/80 backdrop-blur-lg border-b border-slate-800">
          <div className="flex items-center justify-between h-full px-4 lg:px-8">
            {/* Left side */}
            <div className="flex items-center gap-4">
              <button
                className="lg:hidden text-slate-400 hover:text-white"
                onClick={() => setSidebarOpen(true)}
              >
                <HiMenu className="w-6 h-6" />
              </button>

              {/* Search */}
              <div className="hidden sm:block relative">
                <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-64 pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
              {/* Mobile search */}
              <button
                className="sm:hidden text-slate-400 hover:text-white"
                onClick={() => setSearchOpen(!searchOpen)}
              >
                <HiSearch className="w-6 h-6" />
              </button>

              {/* Notifications */}
              <button className="relative text-slate-400 hover:text-white">
                <HiBell className="w-6 h-6" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-accent-500 rounded-full"></span>
              </button>

              {/* User menu */}
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-slate-100">{user?.name || 'User'}</p>
                  <p className="text-xs text-slate-400">{user?.email}</p>
                </div>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-semibold">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              </div>
            </div>
          </div>

          {/* Mobile search bar */}
          <AnimatePresence>
            {searchOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="sm:hidden px-4 pb-4 overflow-hidden"
              >
                <div className="relative">
                  <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search..."
                    className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-primary-500"
                    autoFocus
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
