import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiCurrencyDollar,
  HiTrendingUp,
  HiTrendingDown,
  HiRefresh,
  HiDownload,
  HiFilter,
  HiCalendar,
  HiSearch,
  HiCreditCard,
  HiPlus,
} from 'react-icons/hi';

const Banking = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCountry, setSelectedCountry] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [dateRange, setDateRange] = useState('7');

  // Mock data - would come from API
  const accounts = [
    { id: 1, bank: 'TD Canada Trust', country: 'CA', type: 'Checking', balance: 15420.50, currency: 'CAD', change: 2.3 },
    { id: 2, bank: 'RBC Royal Bank', country: 'CA', type: 'Savings', balance: 45000.00, currency: 'CAD', change: 0.5 },
    { id: 3, bank: 'Chase Bank', country: 'US', type: 'Checking', balance: 28500.00, currency: 'USD', change: -1.2 },
    { id: 4, bank: 'Bank of America', country: 'US', type: 'Savings', balance: 52000.00, currency: 'USD', change: 1.8 },
    { id: 5, bank: 'KCB Bank', country: 'KE', type: 'Business', balance: 850000.00, currency: 'KES', change: 3.5 },
    { id: 6, bank: 'Equity Bank', country: 'KE', type: 'Savings', balance: 450000.00, currency: 'KES', change: 0.8 },
  ];

  const transactions = [
    { id: 1, date: '2024-01-20', description: 'Shopify Sales', amount: 2500.00, type: 'credit', category: 'Income', account: 'TD Canada Trust' },
    { id: 2, date: '2024-01-19', description: 'Office Supplies', amount: -250.00, type: 'debit', category: 'Business', account: 'Chase Bank' },
    { id: 3, date: '2024-01-19', description: 'Client Payment', amount: 5000.00, type: 'credit', category: 'Income', account: 'RBC Royal Bank' },
    { id: 4, date: '2024-01-18', description: 'Software Subscription', amount: -99.00, type: 'debit', category: 'Software', account: 'Chase Bank' },
    { id: 5, date: '2024-01-18', description: 'Restaurant', amount: -85.50, type: 'debit', category: 'Food', account: 'TD Canada Trust' },
    { id: 6, date: '2024-01-17', description: 'Transfer from KCB', amount: 1200.00, type: 'credit', category: 'Transfer', account: 'Equity Bank' },
  ];

  const countries = [
    { code: 'all', name: 'All Countries', flag: '🌍' },
    { code: 'CA', name: 'Canada', flag: '🇨🇦' },
    { code: 'US', name: 'United States', flag: '🇺🇸' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
  ];

  const filteredAccounts = selectedCountry === 'all'
    ? accounts
    : accounts.filter(a => a.country === selectedCountry);

  const totalBalance = filteredAccounts.reduce((sum, acc) => {
    // Simple USD conversion for display
    const usdAmount = acc.currency === 'KES' ? acc.balance / 130 : acc.currency === 'CAD' ? acc.balance * 0.74 : acc.balance;
    return sum + usdAmount;
  }, 0);

  const handleExport = () => {
    toast.success('Exporting transactions to Excel...');
    // Would trigger actual export
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.success('Account data refreshed');
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Banking</h1>
          <p className="text-slate-400">Manage your accounts across Canada, US, and Kenya</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-ghost flex items-center gap-2 border border-slate-700"
          >
            <HiRefresh className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button onClick={handleExport} className="btn-primary flex items-center gap-2">
            <HiDownload className="w-5 h-5" />
            Export
          </button>
        </div>
      </div>

      {/* Country Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {countries.map((country) => (
          <button
            key={country.code}
            onClick={() => setSelectedCountry(country.code)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl whitespace-nowrap transition-all ${
              selectedCountry === country.code
                ? 'bg-primary-500 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <span>{country.flag}</span>
            <span>{country.name}</span>
          </button>
        ))}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-emerald-600/20 to-teal-600/20 border-emerald-500/30"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <HiCurrencyDollar className="w-5 h-5 text-emerald-400" />
            </div>
            <span className="text-slate-400">Total Balance (USD)</span>
          </div>
          <p className="text-3xl font-bold text-white">${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingUp className="w-4 h-4" />
            +2.5% this month
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiCreditCard className="w-5 h-5 text-primary-400" />
            </div>
            <span className="text-slate-400">Active Accounts</span>
          </div>
          <p className="text-3xl font-bold text-white">{filteredAccounts.length}</p>
          <p className="text-sm text-slate-400 mt-2">Across {selectedCountry === 'all' ? '3 countries' : '1 country'}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-secondary-500/20 flex items-center justify-center">
              <HiTrendingUp className="w-5 h-5 text-secondary-400" />
            </div>
            <span className="text-slate-400">Income (7 days)</span>
          </div>
          <p className="text-3xl font-bold text-white">$8,700</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingUp className="w-4 h-4" />
            +15% vs last week
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <HiTrendingDown className="w-5 h-5 text-red-400" />
            </div>
            <span className="text-slate-400">Expenses (7 days)</span>
          </div>
          <p className="text-3xl font-bold text-white">$434.50</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingDown className="w-4 h-4" />
            -8% vs last week
          </p>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <div className="flex gap-6">
          {['overview', 'transactions', 'reports'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 capitalize transition-colors relative ${
                activeTab === tab
                  ? 'text-white'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              {tab}
              {activeTab === tab && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Accounts List */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Accounts</h3>
              <button className="btn-ghost text-sm flex items-center gap-1">
                <HiPlus className="w-4 h-4" />
                Add Account
              </button>
            </div>
            <div className="space-y-3">
              {filteredAccounts.map((account, index) => (
                <motion.div
                  key={account.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold text-sm">
                      {account.bank.split(' ').map(w => w[0]).join('').slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium text-white">{account.bank}</p>
                      <p className="text-sm text-slate-400">{account.type} • {account.country}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-white">
                      {account.currency} {account.balance.toLocaleString()}
                    </p>
                    <p className={`text-sm ${account.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {account.change >= 0 ? '+' : ''}{account.change}%
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Recent Transactions</h3>
              <button
                onClick={() => setActiveTab('transactions')}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                View All
              </button>
            </div>
            <div className="space-y-3">
              {transactions.slice(0, 5).map((tx, index) => (
                <motion.div
                  key={tx.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      tx.type === 'credit' ? 'bg-emerald-500/20' : 'bg-red-500/20'
                    }`}>
                      {tx.type === 'credit' ? (
                        <HiTrendingUp className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <HiTrendingDown className="w-5 h-5 text-red-400" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-white">{tx.description}</p>
                      <p className="text-sm text-slate-400">{tx.date} • {tx.category}</p>
                    </div>
                  </div>
                  <p className={`font-semibold ${tx.amount >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {tx.amount >= 0 ? '+' : ''}${Math.abs(tx.amount).toLocaleString()}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="card">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="relative flex-1 min-w-[200px]">
              <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search transactions..."
                className="input pl-10"
              />
            </div>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="input w-auto"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 3 months</option>
              <option value="365">Last year</option>
            </select>
            <button className="btn-ghost flex items-center gap-2 border border-slate-700">
              <HiFilter className="w-5 h-5" />
              Filters
            </button>
          </div>

          {/* Transactions Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Date</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Description</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Category</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Account</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="py-4 px-4 text-slate-300">{tx.date}</td>
                    <td className="py-4 px-4 text-white">{tx.description}</td>
                    <td className="py-4 px-4">
                      <span className="badge-primary">{tx.category}</span>
                    </td>
                    <td className="py-4 px-4 text-slate-300">{tx.account}</td>
                    <td className={`py-4 px-4 text-right font-semibold ${tx.amount >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {tx.amount >= 0 ? '+' : ''}${Math.abs(tx.amount).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'reports' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { title: 'Weekly Transaction Report', desc: 'Detailed breakdown of all transactions', icon: HiCalendar, format: 'Excel' },
            { title: 'QuickBooks Export', desc: 'Compatible with QuickBooks format', icon: HiDownload, format: 'QBO' },
            { title: 'Monthly Summary', desc: 'High-level overview for accountant', icon: HiCurrencyDollar, format: 'PDF' },
          ].map((report, index) => (
            <motion.div
              key={report.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card cursor-pointer hover:border-primary-500/50"
              onClick={() => toast.success(`Generating ${report.title}...`)}
            >
              <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center mb-4">
                <report.icon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{report.title}</h3>
              <p className="text-slate-400 text-sm mb-4">{report.desc}</p>
              <span className="badge-secondary">{report.format}</span>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Banking;
