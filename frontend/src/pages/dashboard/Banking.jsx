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
  HiX,
  HiLink,
} from 'react-icons/hi';
import PlaidLink from '../../components/PlaidLink';
import plaidApi from '../../services/plaidApi';

const Banking = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [showPlaidModal, setShowPlaidModal] = useState(false);
  const [plaidAccounts, setPlaidAccounts] = useState([]);
  const [plaidTransactions, setPlaidTransactions] = useState([]);
  const [connectedItems, setConnectedItems] = useState([]);
  const [dateRange, setDateRange] = useState('30');

  // Load saved Plaid data from localStorage on mount
  useEffect(() => {
    const loadSavedBankData = () => {
      const savedAccessToken = localStorage.getItem('plaid_access_token');
      const savedAccounts = localStorage.getItem('plaid_accounts');
      const savedTransactions = localStorage.getItem('plaid_transactions');
      const savedItemId = localStorage.getItem('plaid_item_id');

      if (savedAccessToken && savedAccounts) {
        try {
          const accounts = JSON.parse(savedAccounts);
          const transactions = savedTransactions ? JSON.parse(savedTransactions) : [];
          setPlaidAccounts(accounts);
          setPlaidTransactions(transactions);
          if (savedItemId) {
            setConnectedItems([{ itemId: savedItemId, accessToken: savedAccessToken }]);
          }

        } catch (error) {
          // Clear corrupted data
          localStorage.removeItem('plaid_access_token');
          localStorage.removeItem('plaid_item_id');
          localStorage.removeItem('plaid_accounts');
          localStorage.removeItem('plaid_transactions');
        }
      }
    };

    loadSavedBankData();
  }, []);

  const hasConnectedAccounts = plaidAccounts.length > 0;

  // Calculate total balance from real accounts
  const totalBalance = plaidAccounts.reduce((sum, acc) => {
    return sum + (acc.balance?.current || 0);
  }, 0);

  // Calculate income and expenses from real transactions
  const calculateTransactionStats = () => {
    const now = new Date();
    const daysAgo = parseInt(dateRange);
    const startDate = new Date(now.setDate(now.getDate() - daysAgo));

    let income = 0;
    let expenses = 0;

    plaidTransactions.forEach((tx) => {
      const txDate = new Date(tx.date);
      if (txDate >= startDate) {
        if (tx.amount < 0) {
          income += Math.abs(tx.amount);
        } else {
          expenses += tx.amount;
        }
      }
    });

    return { income, expenses };
  };

  const { income, expenses } = calculateTransactionStats();

  const handleRefresh = async () => {
    if (!connectedItems.length) {
      toast.error('No bank accounts connected');
      return;
    }

    setIsLoading(true);
    try {
      const accessToken = connectedItems[0].accessToken;

      // Fetch updated account data
      const accountsData = await plaidApi.getAccounts(accessToken);
      const updatedAccounts = accountsData.accounts || [];
      setPlaidAccounts(updatedAccounts);
      localStorage.setItem('plaid_accounts', JSON.stringify(updatedAccounts));

      // Fetch updated transactions
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const transactionsData = await plaidApi.getTransactions({
        accessToken,
        startDate,
        endDate,
      });
      const updatedTransactions = transactionsData.transactions || [];
      setPlaidTransactions(updatedTransactions);
      localStorage.setItem('plaid_transactions', JSON.stringify(updatedTransactions));

      toast.success('Account data refreshed successfully', {
        duration: 3000,
        icon: '✅',
      });

    } catch (error) {
      toast.error('Failed to refresh account data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    if (!plaidTransactions.length) {
      toast.error('No transactions to export');
      return;
    }

    // Convert transactions to CSV
    const headers = ['Date', 'Description', 'Merchant', 'Category', 'Amount', 'Currency'];
    const rows = plaidTransactions.map(tx => [
      tx.date,
      tx.name,
      tx.merchant_name || '',
      (tx.category || []).join(' > '),
      tx.amount,
      tx.currency || 'USD'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast.success('Transactions exported to CSV');
  };

  // Handle successful Plaid connection
  const handlePlaidSuccess = async (data) => {
    const { accessToken, itemId, accounts: newAccounts, transactions: newTransactions } = data;

    // Save to state
    setPlaidAccounts(newAccounts || []);
    setPlaidTransactions(newTransactions || []);
    setConnectedItems([{ itemId, accessToken }]);

    // Save to localStorage for persistence
    localStorage.setItem('plaid_access_token', accessToken);
    localStorage.setItem('plaid_item_id', itemId);
    localStorage.setItem('plaid_accounts', JSON.stringify(newAccounts || []));
    localStorage.setItem('plaid_transactions', JSON.stringify(newTransactions || []));

    setShowPlaidModal(false);

    toast.success('Bank account connected successfully!', {
      duration: 4000,
      icon: '🏦',
    });

  };

  const handlePlaidExit = (error, metadata) => {
    if (!error || error.error_code === 'USER_EXIT') {
      setShowPlaidModal(false);
    }
  };

  const handleDisconnect = () => {
    const institutionName = plaidAccounts[0]?.name || 'your bank';
    if (window.confirm(`Are you sure you want to disconnect ${institutionName}? You will need to reconnect to access your banking data.`)) {
      setPlaidAccounts([]);
      setPlaidTransactions([]);
      setConnectedItems([]);
      localStorage.removeItem('plaid_access_token');
      localStorage.removeItem('plaid_item_id');
      localStorage.removeItem('plaid_accounts');
      localStorage.removeItem('plaid_transactions');

      toast.success('Bank account disconnected successfully', {
        duration: 4000,
        icon: '🔌',
      });
    }
  };

  // Format currency
  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  // Empty state - no accounts connected
  if (!hasConnectedAccounts) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Banking</h1>
          <p className="text-slate-400">Connect your bank account to get started</p>
        </div>

        {/* Empty State */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card text-center py-16"
        >
          <div className="w-20 h-20 rounded-full bg-primary-500/20 flex items-center justify-center mx-auto mb-6">
            <HiLink className="w-10 h-10 text-primary-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Connect Your Bank Account</h2>
          <p className="text-slate-400 mb-8 max-w-md mx-auto">
            Securely link your bank account using Plaid to view balances, transactions, and manage your finances in one place.
          </p>
          <button
            onClick={() => setShowPlaidModal(true)}
            className="btn-primary inline-flex items-center gap-2 mx-auto"
          >
            <HiPlus className="w-5 h-5" />
            Connect Bank Account
          </button>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="p-6 bg-slate-800/50 rounded-xl">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                <HiCurrencyDollar className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Real-time Balances</h3>
              <p className="text-sm text-slate-400">See all your account balances updated in real-time</p>
            </div>
            <div className="p-6 bg-slate-800/50 rounded-xl">
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mx-auto mb-4">
                <HiTrendingUp className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Transaction History</h3>
              <p className="text-sm text-slate-400">Track all your spending and income automatically</p>
            </div>
            <div className="p-6 bg-slate-800/50 rounded-xl">
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mx-auto mb-4">
                <HiCreditCard className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Secure & Private</h3>
              <p className="text-sm text-slate-400">Bank-level encryption keeps your data safe</p>
            </div>
          </div>
        </motion.div>

        {/* Plaid Modal */}
        {showPlaidModal && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowPlaidModal(false);
              }
            }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">Connect Bank Account</h2>
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    setShowPlaidModal(false);
                  }}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <HiX className="w-6 h-6" />
                </button>
              </div>

              <p className="text-slate-400 mb-6">
                Securely connect your bank account using Plaid. Your credentials are encrypted and never stored.
              </p>

              <PlaidLink
                onSuccess={handlePlaidSuccess}
                onExit={handlePlaidExit}
                countryCodes={['US', 'CA']}
              />

              <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                <p className="text-sm text-blue-400">
                  <strong>Note:</strong> Currently in sandbox mode. Use Plaid's test credentials to test the integration.
                </p>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    );
  }

  // Main banking view - with connected accounts
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-display font-bold text-white">Banking</h1>
            {hasConnectedAccounts && (
              <span className="px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-medium flex items-center gap-1">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                Connected
              </span>
            )}
          </div>
          <p className="text-slate-400">
            {hasConnectedAccounts
              ? `Managing ${plaidAccounts.length} account${plaidAccounts.length !== 1 ? 's' : ''}`
              : 'Manage your connected bank accounts'
            }
          </p>
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
            <span className="text-slate-400">Total Balance</span>
          </div>
          <p className="text-3xl font-bold text-white">{formatCurrency(totalBalance)}</p>
          <p className="text-sm text-slate-400 mt-2">
            Across {plaidAccounts.length} account{plaidAccounts.length !== 1 ? 's' : ''}
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
          <p className="text-3xl font-bold text-white">{plaidAccounts.length}</p>
          <p className="text-sm text-slate-400 mt-2">Connected via Plaid</p>
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
            <span className="text-slate-400">Income ({dateRange} days)</span>
          </div>
          <p className="text-3xl font-bold text-white">{formatCurrency(income)}</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingUp className="w-4 h-4" />
            From transactions
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
            <span className="text-slate-400">Expenses ({dateRange} days)</span>
          </div>
          <p className="text-3xl font-bold text-white">{formatCurrency(expenses)}</p>
          <p className="text-sm text-slate-400 mt-2 flex items-center gap-1">
            From transactions
          </p>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <div className="flex gap-6">
          {['overview', 'transactions'].map((tab) => (
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
              <h3 className="text-lg font-semibold text-white">Your Accounts</h3>
              <button
                onClick={handleDisconnect}
                className="text-sm text-red-400 hover:text-red-300"
              >
                Disconnect
              </button>
            </div>
            <div className="space-y-3">
              {plaidAccounts.map((account, index) => (
                <motion.div
                  key={account.account_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold text-sm">
                      {account.name?.substring(0, 2).toUpperCase() || 'AC'}
                    </div>
                    <div>
                      <p className="font-medium text-white">{account.name || 'Account'}</p>
                      <p className="text-sm text-slate-400">
                        {account.subtype || account.type} {account.mask ? `• ****${account.mask}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-white">
                      {formatCurrency(account.balance?.current || 0, account.balance?.currency)}
                    </p>
                    {account.balance?.available !== null &&
                     account.balance?.available !== undefined &&
                     account.balance?.available !== account.balance?.current && (
                      <p className="text-xs text-slate-400">
                        Available: {formatCurrency(account.balance?.available, account.balance?.currency)}
                      </p>
                    )}
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
              {plaidTransactions.length === 0 ? (
                <p className="text-slate-400 text-center py-8">No transactions found</p>
              ) : (
                plaidTransactions.slice(0, 5).map((tx, index) => (
                  <motion.div
                    key={tx.transaction_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        tx.amount < 0 ? 'bg-emerald-500/20' : 'bg-red-500/20'
                      }`}>
                        {tx.amount < 0 ? (
                          <HiTrendingUp className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <HiTrendingDown className="w-5 h-5 text-red-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-white">{tx.merchant_name || tx.name}</p>
                        <p className="text-sm text-slate-400">
                          {new Date(tx.date).toLocaleDateString()}
                          {tx.category && tx.category.length > 0 && ` • ${tx.category[0]}`}
                        </p>
                      </div>
                    </div>
                    <p className={`font-semibold ${tx.amount < 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {tx.amount < 0 ? '+' : '-'}{formatCurrency(Math.abs(tx.amount), tx.currency)}
                    </p>
                  </motion.div>
                ))
              )}
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
            </select>
          </div>

          {/* Transactions Table */}
          <div className="overflow-x-auto">
            {plaidTransactions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-400">No transactions found</p>
                <button
                  onClick={handleRefresh}
                  className="btn-ghost mt-4"
                >
                  Refresh Data
                </button>
              </div>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Date</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Description</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Category</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {plaidTransactions.map((tx) => (
                    <tr key={tx.transaction_id} className="border-b border-slate-800 hover:bg-slate-800/50">
                      <td className="py-4 px-4 text-slate-300">
                        {new Date(tx.date).toLocaleDateString()}
                      </td>
                      <td className="py-4 px-4">
                        <div>
                          <p className="text-white">{tx.merchant_name || tx.name}</p>
                          {tx.pending && (
                            <span className="text-xs text-yellow-400">Pending</span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        {tx.category && tx.category.length > 0 && (
                          <span className="badge-primary text-xs">{tx.category[0]}</span>
                        )}
                      </td>
                      <td className={`py-4 px-4 text-right font-semibold ${
                        tx.amount < 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {tx.amount < 0 ? '+' : '-'}{formatCurrency(Math.abs(tx.amount), tx.currency)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Banking;
