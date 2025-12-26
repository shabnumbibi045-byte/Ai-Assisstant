import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiTrendingUp,
  HiTrendingDown,
  HiRefresh,
  HiPlus,
  HiSearch,
  HiChartBar,
  HiClock,
  HiStar,
  HiBell,
} from 'react-icons/hi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Stocks = () => {
  const [activeTab, setActiveTab] = useState('portfolio');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  // Mock portfolio data
  const portfolio = [
    { symbol: 'AAPL', name: 'Apple Inc.', shares: 50, avgPrice: 168.50, currentPrice: 182.63, change: 1.23 },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 20, avgPrice: 125.00, currentPrice: 141.80, change: -0.45 },
    { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 35, avgPrice: 310.00, currentPrice: 397.58, change: 0.89 },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', shares: 25, avgPrice: 145.00, currentPrice: 185.07, change: 2.15 },
    { symbol: 'NVDA', name: 'NVIDIA Corp.', shares: 15, avgPrice: 450.00, currentPrice: 682.23, change: 3.45 },
    { symbol: 'TSLA', name: 'Tesla Inc.', shares: 30, avgPrice: 225.00, currentPrice: 207.83, change: -1.87 },
  ];

  const watchlist = [
    { symbol: 'META', name: 'Meta Platforms', price: 474.99, change: 2.34 },
    { symbol: 'NFLX', name: 'Netflix Inc.', price: 561.77, change: -0.78 },
    { symbol: 'AMD', name: 'AMD Inc.', price: 177.55, change: 1.56 },
    { symbol: 'CRM', name: 'Salesforce', price: 290.84, change: 0.92 },
  ];

  const priceAlerts = [
    { symbol: 'AAPL', condition: 'above', targetPrice: 190.00, currentPrice: 182.63, active: true },
    { symbol: 'TSLA', condition: 'below', targetPrice: 200.00, currentPrice: 207.83, active: true },
    { symbol: 'NVDA', condition: 'above', targetPrice: 700.00, currentPrice: 682.23, active: true },
  ];

  const totalValue = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.currentPrice), 0);
  const totalCost = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.avgPrice), 0);
  const totalGain = totalValue - totalCost;
  const totalGainPercent = ((totalGain / totalCost) * 100).toFixed(2);

  // Chart data
  const chartData = {
    labels: ['9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [155000, 156200, 155800, 157300, 158100, 157600, 158900, 159500, 158800, 160200, 161000, 160500, 161800, 162350],
        fill: true,
        borderColor: '#7c3aed',
        backgroundColor: 'rgba(124, 58, 237, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#fff',
        bodyColor: '#94a3b8',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: (context) => `$${context.parsed.y.toLocaleString()}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8' },
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: {
          color: '#94a3b8',
          callback: (value) => `$${(value / 1000).toFixed(0)}k`,
        },
      },
    },
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.success('Stock data refreshed');
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Stocks</h1>
          <p className="text-slate-400">Track your portfolio and market trends</p>
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
          <button className="btn-primary flex items-center gap-2">
            <HiPlus className="w-5 h-5" />
            Add Trade
          </button>
        </div>
      </div>

      {/* Portfolio Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-primary-600/20 to-secondary-600/20 border-primary-500/30"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <HiChartBar className="w-5 h-5 text-primary-400" />
            </div>
            <span className="text-slate-400">Portfolio Value</span>
          </div>
          <p className="text-3xl font-bold text-white">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
          <p className={`text-sm mt-2 flex items-center gap-1 ${totalGain >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {totalGain >= 0 ? <HiTrendingUp className="w-4 h-4" /> : <HiTrendingDown className="w-4 h-4" />}
            {totalGain >= 0 ? '+' : ''}{totalGainPercent}% all time
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <HiTrendingUp className="w-5 h-5 text-emerald-400" />
            </div>
            <span className="text-slate-400">Today's Gain</span>
          </div>
          <p className="text-3xl font-bold text-emerald-400">+$1,847.50</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingUp className="w-4 h-4" />
            +1.15%
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-secondary-500/20 flex items-center justify-center">
              <HiStar className="w-5 h-5 text-secondary-400" />
            </div>
            <span className="text-slate-400">Best Performer</span>
          </div>
          <p className="text-2xl font-bold text-white">NVDA</p>
          <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
            <HiTrendingUp className="w-4 h-4" />
            +51.6% gain
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <HiBell className="w-5 h-5 text-amber-400" />
            </div>
            <span className="text-slate-400">Active Alerts</span>
          </div>
          <p className="text-3xl font-bold text-white">{priceAlerts.filter(a => a.active).length}</p>
          <p className="text-sm text-slate-400 mt-2">Price alerts set</p>
        </motion.div>
      </div>

      {/* Chart */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <h3 className="text-lg font-semibold text-white">Portfolio Performance</h3>
          <div className="flex gap-2">
            {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeframe(tf)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  selectedTimeframe === tf
                    ? 'bg-primary-500 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
        <div className="h-[300px]">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <div className="flex gap-6">
          {['portfolio', 'watchlist', 'alerts'].map((tab) => (
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
                  layoutId="stocksTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'portfolio' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Stock</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Shares</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Avg Price</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Current</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Change</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Value</th>
                  <th className="text-right py-3 px-4 text-slate-400 font-medium">Gain/Loss</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.map((stock) => {
                  const value = stock.shares * stock.currentPrice;
                  const cost = stock.shares * stock.avgPrice;
                  const gain = value - cost;
                  const gainPercent = ((gain / cost) * 100).toFixed(2);

                  return (
                    <motion.tr
                      key={stock.symbol}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-slate-800 hover:bg-slate-800/50"
                    >
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold text-sm">
                            {stock.symbol.slice(0, 2)}
                          </div>
                          <div>
                            <p className="font-semibold text-white">{stock.symbol}</p>
                            <p className="text-sm text-slate-400">{stock.name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-right text-slate-300">{stock.shares}</td>
                      <td className="py-4 px-4 text-right text-slate-300">${stock.avgPrice.toFixed(2)}</td>
                      <td className="py-4 px-4 text-right text-white font-medium">${stock.currentPrice.toFixed(2)}</td>
                      <td className={`py-4 px-4 text-right ${stock.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {stock.change >= 0 ? '+' : ''}{stock.change}%
                      </td>
                      <td className="py-4 px-4 text-right text-white font-medium">${value.toLocaleString()}</td>
                      <td className={`py-4 px-4 text-right font-medium ${gain >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {gain >= 0 ? '+' : ''}${gain.toLocaleString()} ({gainPercent}%)
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'watchlist' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search stocks to add..."
                className="input pl-10"
              />
            </div>
          </div>

          {/* Watchlist Items */}
          {watchlist.map((stock, index) => (
            <motion.div
              key={stock.symbol}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:border-primary-500/50 cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold">
                    {stock.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <p className="font-semibold text-white">{stock.symbol}</p>
                    <p className="text-sm text-slate-400">{stock.name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-white">${stock.price.toFixed(2)}</p>
                  <p className={`text-sm ${stock.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change}%
                  </p>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button className="btn-primary flex-1 text-sm py-2">Buy</button>
                <button className="btn-ghost flex-1 text-sm py-2 border border-slate-700">Set Alert</button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="space-y-4">
          {/* Add Alert Button */}
          <div className="flex justify-end">
            <button className="btn-primary flex items-center gap-2">
              <HiPlus className="w-5 h-5" />
              New Alert
            </button>
          </div>

          {/* Alerts List */}
          <div className="card">
            <div className="space-y-4">
              {priceAlerts.map((alert, index) => {
                const isTriggered = alert.condition === 'above'
                  ? alert.currentPrice >= alert.targetPrice
                  : alert.currentPrice <= alert.targetPrice;

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex items-center justify-between p-4 rounded-xl ${
                      isTriggered ? 'bg-emerald-500/10 border border-emerald-500/30' : 'bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        isTriggered ? 'bg-emerald-500/20' : 'bg-amber-500/20'
                      }`}>
                        <HiBell className={`w-6 h-6 ${isTriggered ? 'text-emerald-400' : 'text-amber-400'}`} />
                      </div>
                      <div>
                        <p className="font-semibold text-white">{alert.symbol}</p>
                        <p className="text-sm text-slate-400">
                          Alert when price is {alert.condition} ${alert.targetPrice.toFixed(2)}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Current: ${alert.currentPrice.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {isTriggered && (
                        <span className="badge bg-emerald-500/20 text-emerald-400">Triggered</span>
                      )}
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" checked={alert.active} className="sr-only peer" readOnly />
                        <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Stocks;
