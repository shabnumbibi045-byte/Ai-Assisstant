// App constants
export const APP_NAME = 'LeStrap AI Assistant';

// API endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',

  // Chat
  SESSIONS: '/chat/sessions',
  MESSAGES: (sessionId) => `/chat/sessions/${sessionId}/messages`,
  SEND_MESSAGE: (sessionId) => `/chat/sessions/${sessionId}/message`,

  // Banking
  ACCOUNTS: '/banking/accounts',
  TRANSACTIONS: '/banking/transactions',
  EXPORT: '/banking/export',

  // Stocks
  PORTFOLIO: '/stocks/portfolio',
  QUOTES: '/stocks/quotes',
  ALERTS: '/stocks/alerts',

  // Travel
  SEARCH_FLIGHTS: '/travel/flights/search',
  SEARCH_HOTELS: '/travel/hotels/search',
  PRICE_ALERTS: '/travel/alerts',

  // Research
  SEARCH: '/research/search',
  PROJECTS: '/research/projects',
  BOOKMARKS: '/research/bookmarks',

  // Documents
  UPLOAD: '/rag/documents',
  QUERY: '/rag/query',

  // Voice
  TRANSCRIBE: '/voice/transcribe',
  SYNTHESIZE: '/voice/synthesize',

  // Memory
  MEMORY: '/memory',
  CONTEXT: '/memory/context',
};

// Navigation items
export const NAV_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: 'HiHome' },
  { name: 'Chat', href: '/chat', icon: 'HiChat' },
  { name: 'Banking', href: '/banking', icon: 'HiCurrencyDollar' },
  { name: 'Stocks', href: '/stocks', icon: 'HiTrendingUp' },
  { name: 'Travel', href: '/travel', icon: 'HiGlobe' },
  { name: 'Research', href: '/research', icon: 'HiLibrary' },
  { name: 'Documents', href: '/documents', icon: 'HiDocumentText' },
  { name: 'Voice', href: '/voice', icon: 'HiMicrophone' },
];

// Countries supported
export const COUNTRIES = [
  { code: 'CA', name: 'Canada', flag: '🇨🇦', currency: 'CAD' },
  { code: 'US', name: 'United States', flag: '🇺🇸', currency: 'USD' },
  { code: 'KE', name: 'Kenya', flag: '🇰🇪', currency: 'KES' },
];

// File types supported for upload
export const SUPPORTED_FILE_TYPES = [
  { ext: 'pdf', mime: 'application/pdf', label: 'PDF' },
  { ext: 'docx', mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', label: 'Word' },
  { ext: 'xlsx', mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', label: 'Excel' },
  { ext: 'csv', mime: 'text/csv', label: 'CSV' },
  { ext: 'txt', mime: 'text/plain', label: 'Text' },
];

// AI voices
export const AI_VOICES = [
  { id: 'alloy', name: 'Alloy', description: 'Neutral & balanced' },
  { id: 'echo', name: 'Echo', description: 'Deep & resonant' },
  { id: 'fable', name: 'Fable', description: 'British accent' },
  { id: 'onyx', name: 'Onyx', description: 'Deep & authoritative' },
  { id: 'nova', name: 'Nova', description: 'Warm & friendly' },
  { id: 'shimmer', name: 'Shimmer', description: 'Clear & expressive' },
];

// Languages
export const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'sw', name: 'Swahili' },
];

// Timezones
export const TIMEZONES = [
  { id: 'America/Toronto', name: 'Eastern Time (Toronto)', offset: '-05:00' },
  { id: 'America/New_York', name: 'Eastern Time (New York)', offset: '-05:00' },
  { id: 'America/Los_Angeles', name: 'Pacific Time', offset: '-08:00' },
  { id: 'Africa/Nairobi', name: 'East Africa Time', offset: '+03:00' },
  { id: 'Europe/London', name: 'GMT (London)', offset: '+00:00' },
];

// Chart colors
export const CHART_COLORS = {
  primary: '#7c3aed',
  secondary: '#06b6d4',
  teal: '#14b8a6',
  accent: '#f97316',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  neutral: '#64748b',
};

// Transaction categories
export const TRANSACTION_CATEGORIES = [
  'Income',
  'Business',
  'Software',
  'Food',
  'Transport',
  'Entertainment',
  'Utilities',
  'Shopping',
  'Healthcare',
  'Transfer',
  'Other',
];

// Research jurisdictions
export const JURISDICTIONS = [
  { code: 'CA', name: 'Canada', databases: ['CanLII', 'Westlaw Canada'] },
  { code: 'US', name: 'United States', databases: ['Westlaw', 'LexisNexis'] },
  { code: 'KE', name: 'Kenya', databases: ['Kenya Law'] },
  { code: 'UK', name: 'United Kingdom', databases: ['Westlaw UK'] },
];

// Stock exchanges
export const STOCK_EXCHANGES = [
  { code: 'NYSE', name: 'New York Stock Exchange', country: 'US' },
  { code: 'NASDAQ', name: 'NASDAQ', country: 'US' },
  { code: 'TSX', name: 'Toronto Stock Exchange', country: 'CA' },
  { code: 'NSE', name: 'Nairobi Securities Exchange', country: 'KE' },
];

// Error messages
export const ERROR_MESSAGES = {
  GENERIC: 'Something went wrong. Please try again.',
  NETWORK: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Your session has expired. Please login again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION: 'Please check your input and try again.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Welcome back!',
  REGISTER: 'Account created successfully!',
  LOGOUT: 'You have been logged out.',
  SAVE: 'Changes saved successfully.',
  DELETE: 'Deleted successfully.',
  UPLOAD: 'File uploaded successfully.',
  EXPORT: 'Export completed.',
};

export default {
  APP_NAME,
  API_ENDPOINTS,
  NAV_ITEMS,
  COUNTRIES,
  SUPPORTED_FILE_TYPES,
  AI_VOICES,
  LANGUAGES,
  TIMEZONES,
  CHART_COLORS,
  TRANSACTION_CATEGORIES,
  JURISDICTIONS,
  STOCK_EXCHANGES,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
};
