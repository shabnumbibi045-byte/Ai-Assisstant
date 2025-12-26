import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiCog,
  HiKey,
  HiBell,
  HiShieldCheck,
  HiDatabase,
  HiCode,
  HiSave,
  HiRefresh,
  HiCheck,
  HiExclamation,
  HiEye,
  HiEyeOff,
} from 'react-icons/hi';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [isSaving, setIsSaving] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState({});

  // Settings state
  const [settings, setSettings] = useState({
    // General
    theme: 'dark',
    language: 'en',
    timezone: 'America/Toronto',

    // API Keys
    openaiKey: 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxx',
    anthropicKey: 'sk-ant-xxxxxxxxxxxxxxxxxx',
    geminiKey: 'AIzaSyxxxxxxxxxxxxxxxxxx',

    // Banking
    tdApiKey: '',
    rbcApiKey: '',
    chaseApiKey: '',
    kcbApiKey: '',

    // Communication
    gmailConnected: true,
    outlookConnected: false,
    slackConnected: true,
    twilioSid: '',
    twilioToken: '',

    // Notifications
    emailNotifications: true,
    pushNotifications: true,
    priceAlerts: true,
    transactionAlerts: true,

    // Privacy
    analyticsEnabled: true,
    dataSharingEnabled: false,
    retentionDays: 90,
  });

  const tabs = [
    { id: 'general', label: 'General', icon: HiCog },
    { id: 'api', label: 'API Keys', icon: HiKey },
    { id: 'banking', label: 'Banking', icon: HiDatabase },
    { id: 'communication', label: 'Communication', icon: HiCode },
    { id: 'notifications', label: 'Notifications', icon: HiBell },
    { id: 'privacy', label: 'Privacy', icon: HiShieldCheck },
  ];

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise(r => setTimeout(r, 1500));
    toast.success('Settings saved successfully');
    setIsSaving(false);
  };

  const toggleApiKeyVisibility = (key) => {
    setShowApiKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const maskApiKey = (key) => {
    if (!key) return '';
    return key.slice(0, 4) + '•'.repeat(20) + key.slice(-4);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Settings</h1>
          <p className="text-slate-400">Configure your AI assistant preferences and integrations</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary flex items-center gap-2"
        >
          {isSaving ? (
            <>
              <span className="spinner-small" />
              Saving...
            </>
          ) : (
            <>
              <HiSave className="w-5 h-5" />
              Save Changes
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Tabs */}
        <div className="lg:col-span-1">
          <div className="card p-2">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary-500 text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          {/* General Settings */}
          {activeTab === 'general' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-white mb-6">General Settings</h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Theme</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                    className="input"
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                    <option value="system">System</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Language</label>
                  <select
                    value={settings.language}
                    onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                    className="input"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="sw">Swahili</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Timezone</label>
                  <select
                    value={settings.timezone}
                    onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                    className="input"
                  >
                    <option value="America/Toronto">Eastern Time (Toronto)</option>
                    <option value="America/New_York">Eastern Time (New York)</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Africa/Nairobi">East Africa Time</option>
                    <option value="Europe/London">GMT (London)</option>
                  </select>
                </div>
              </div>
            </motion.div>
          )}

          {/* API Keys */}
          {activeTab === 'api' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-white mb-2">LLM API Keys</h2>
              <p className="text-slate-400 text-sm mb-6">Configure your AI provider API keys</p>

              <div className="space-y-6">
                {[
                  { key: 'openaiKey', label: 'OpenAI API Key', placeholder: 'sk-...' },
                  { key: 'anthropicKey', label: 'Anthropic API Key', placeholder: 'sk-ant-...' },
                  { key: 'geminiKey', label: 'Google Gemini API Key', placeholder: 'AIzaSy...' },
                ].map((api) => (
                  <div key={api.key}>
                    <label className="block text-sm font-medium text-slate-300 mb-2">{api.label}</label>
                    <div className="relative">
                      <input
                        type={showApiKeys[api.key] ? 'text' : 'password'}
                        value={settings[api.key]}
                        onChange={(e) => setSettings({ ...settings, [api.key]: e.target.value })}
                        placeholder={api.placeholder}
                        className="input pr-12"
                      />
                      <button
                        onClick={() => toggleApiKeyVisibility(api.key)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-white"
                      >
                        {showApiKeys[api.key] ? <HiEyeOff className="w-5 h-5" /> : <HiEye className="w-5 h-5" />}
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      {settings[api.key] ? (
                        <span className="text-xs text-emerald-400 flex items-center gap-1">
                          <HiCheck className="w-4 h-4" /> Configured
                        </span>
                      ) : (
                        <span className="text-xs text-amber-400 flex items-center gap-1">
                          <HiExclamation className="w-4 h-4" /> Not configured
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Banking Settings */}
          {activeTab === 'banking' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-2">Banking Integrations</h2>
                <p className="text-slate-400 text-sm mb-6">Connect your bank accounts</p>

                <div className="space-y-4">
                  {[
                    { id: 'td', name: 'TD Canada Trust', country: '🇨🇦', connected: true },
                    { id: 'rbc', name: 'RBC Royal Bank', country: '🇨🇦', connected: true },
                    { id: 'chase', name: 'Chase Bank', country: '🇺🇸', connected: false },
                    { id: 'kcb', name: 'KCB Bank', country: '🇰🇪', connected: true },
                    { id: 'equity', name: 'Equity Bank', country: '🇰🇪', connected: false },
                  ].map((bank) => (
                    <div
                      key={bank.id}
                      className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{bank.country}</span>
                        <div>
                          <p className="font-medium text-white">{bank.name}</p>
                          <p className="text-sm text-slate-400">
                            {bank.connected ? 'Last synced: 2 hours ago' : 'Not connected'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {bank.connected && (
                          <button className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                            <HiRefresh className="w-5 h-5" />
                          </button>
                        )}
                        <button
                          className={`px-4 py-2 rounded-lg font-medium transition-all ${
                            bank.connected
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-primary-500 text-white'
                          }`}
                        >
                          {bank.connected ? 'Connected' : 'Connect'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">Export Settings</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Default Export Format</label>
                    <select className="input">
                      <option>Excel (.xlsx)</option>
                      <option>CSV (.csv)</option>
                      <option>QuickBooks (.qbo)</option>
                      <option>PDF (.pdf)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Date Range for Reports</label>
                    <select className="input">
                      <option>Last 7 days</option>
                      <option>Last 30 days</option>
                      <option>Last 90 days</option>
                      <option>Custom</option>
                    </select>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Communication Settings */}
          {activeTab === 'communication' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-2">Email Integration</h2>
                <p className="text-slate-400 text-sm mb-6">Connect your email accounts</p>

                <div className="space-y-4">
                  {[
                    { id: 'gmail', name: 'Gmail', icon: '📧', connected: settings.gmailConnected },
                    { id: 'outlook', name: 'Outlook', icon: '📨', connected: settings.outlookConnected },
                  ].map((email) => (
                    <div
                      key={email.id}
                      className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{email.icon}</span>
                        <span className="font-medium text-white">{email.name}</span>
                      </div>
                      <button
                        onClick={() => {
                          const key = `${email.id}Connected`;
                          setSettings({ ...settings, [key]: !settings[key] });
                        }}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${
                          email.connected
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-primary-500 text-white'
                        }`}
                      >
                        {email.connected ? 'Connected' : 'Connect'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-2">Twilio (SMS/Voice)</h2>
                <p className="text-slate-400 text-sm mb-6">Configure SMS and voice calling</p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Account SID</label>
                    <input
                      type="password"
                      value={settings.twilioSid}
                      onChange={(e) => setSettings({ ...settings, twilioSid: e.target.value })}
                      placeholder="ACxxxxxxxxxxxxxxxx"
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Auth Token</label>
                    <input
                      type="password"
                      value={settings.twilioToken}
                      onChange={(e) => setSettings({ ...settings, twilioToken: e.target.value })}
                      placeholder="xxxxxxxxxxxxxxxxxxxxxxxx"
                      className="input"
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Notifications */}
          {activeTab === 'notifications' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-white mb-6">Notification Preferences</h2>

              <div className="space-y-4">
                {[
                  { key: 'emailNotifications', label: 'Email Notifications', desc: 'Receive updates via email' },
                  { key: 'pushNotifications', label: 'Push Notifications', desc: 'Browser push notifications' },
                  { key: 'priceAlerts', label: 'Price Alerts', desc: 'Stock and travel price alerts' },
                  { key: 'transactionAlerts', label: 'Transaction Alerts', desc: 'Banking transaction notifications' },
                ].map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                  >
                    <div>
                      <p className="font-medium text-white">{item.label}</p>
                      <p className="text-sm text-slate-400">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings[item.key]}
                        onChange={(e) => setSettings({ ...settings, [item.key]: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                    </label>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Privacy */}
          {activeTab === 'privacy' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-white mb-6">Privacy & Data</h2>

              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50">
                  <div>
                    <p className="font-medium text-white">Analytics</p>
                    <p className="text-sm text-slate-400">Help improve the AI assistant</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.analyticsEnabled}
                      onChange={(e) => setSettings({ ...settings, analyticsEnabled: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Data Retention Period</label>
                  <select
                    value={settings.retentionDays}
                    onChange={(e) => setSettings({ ...settings, retentionDays: parseInt(e.target.value) })}
                    className="input"
                  >
                    <option value={30}>30 days</option>
                    <option value={60}>60 days</option>
                    <option value={90}>90 days</option>
                    <option value={180}>180 days</option>
                    <option value={365}>1 year</option>
                  </select>
                </div>

                <div className="pt-4 border-t border-slate-700">
                  <button className="btn-ghost text-red-400 border border-red-500/30 hover:bg-red-500/10">
                    Delete All My Data
                  </button>
                  <p className="text-xs text-slate-500 mt-2">
                    This will permanently delete all your data including chat history, documents, and settings.
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
