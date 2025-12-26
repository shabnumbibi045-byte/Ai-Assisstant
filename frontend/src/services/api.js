import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const { token, isAuthenticated } = useAuthStore.getState();
    
    // Skip auth header for demo mode
    if (token === 'demo-token') {
      return config;
    }
    
    if (token && isAuthenticated) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const { token, logout, refreshAccessToken } = useAuthStore.getState();

    // Skip error handling for demo mode
    if (token === 'demo-token') {
      // Return mock data for demo mode
      return handleDemoModeRequest(originalRequest);
    }

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Try to refresh token
      const refreshed = await refreshAccessToken();
      
      if (refreshed) {
        // Retry original request with new token
        const newToken = useAuthStore.getState().token;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } else {
        // Refresh failed, logout
        logout();
        window.location.href = '/login';
      }
    }

    // Log error for debugging
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });

    return Promise.reject(error);
  }
);

// Demo mode mock responses
function handleDemoModeRequest(config) {
  const url = config.url;
  const method = config.method?.toLowerCase();
  
  // Mock responses for demo mode
  const mockResponses = {
    'GET:/auth/me': {
      id: 1,
      user_id: 'demo-uuid',
      email: 'demo@lestrap.com',
      full_name: 'Demo User',
      is_active: true,
      is_verified: true,
      modules_enabled: ['chat', 'memory', 'banking', 'stocks', 'travel', 'research'],
    },
    'POST:/chat/': {
      response: "I'm running in demo mode. Connect to the backend for full functionality! I can help you with banking queries, stock market analysis, travel bookings, and legal research.",
      tokens_used: 50,
      tool_calls: [],
      sources: [],
      session_id: 'demo-session-123',
    },
    'GET:/tools/list': {
      tools: [
        { name: 'get_balance', category: 'banking', description: 'Get bank account balances' },
        { name: 'get_transactions', category: 'banking', description: 'Get recent transactions' },
        { name: 'get_portfolio', category: 'stocks', description: 'Get stock portfolio' },
        { name: 'search_flights', category: 'travel', description: 'Search for flights' },
      ],
      total: 4,
      categories: ['banking', 'stocks', 'travel', 'research'],
    },
    'POST:/tools/invoke': {
      success: true,
      result: { message: 'Demo mode - Tool execution simulated' },
      tool_name: 'demo_tool',
      execution_time: 0.1,
    },
    'GET:/rag/documents': {
      documents: [],
      total: 0,
    },
    'GET:/setup/modules': {
      modules: [
        { name: 'chat', enabled: true, description: 'Chat with AI' },
        { name: 'banking', enabled: true, description: 'Banking tools' },
        { name: 'stocks', enabled: true, description: 'Stock market tools' },
        { name: 'travel', enabled: true, description: 'Travel booking tools' },
        { name: 'research', enabled: true, description: 'Research tools' },
      ],
    },
    'GET:/chat/sessions': [],
    'GET:/memory/summaries': [],
  };

  const key = `${method.toUpperCase()}:${url}`;
  const mockData = mockResponses[key];

  if (mockData) {
    return Promise.resolve({ data: mockData, status: 200 });
  }

  // Default mock response
  return Promise.resolve({ 
    data: { message: 'Demo mode - Feature not available', demo: true }, 
    status: 200 
  });
}

export default api;

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Chat API
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/', data),
  getHistory: (sessionId) => api.get(`/chat/history/${sessionId}`),
  getSessions: () => api.get('/chat/sessions'),
  deleteSession: (sessionId) => api.delete(`/chat/sessions/${sessionId}`),
  submitFeedback: (data) => api.post('/chat/feedback', null, { params: data }),
  getStats: () => api.get('/chat/stats'),
};

// Banking API
export const bankingAPI = {
  getBalances: (country) => api.get('/tools/invoke', { 
    params: { tool_name: 'get_balance', parameters: { country } } 
  }),
  getTransactions: (params) => api.post('/tools/invoke', {
    tool_name: 'get_transactions',
    parameters: params,
  }),
  exportTransactions: (params) => api.post('/tools/invoke', {
    tool_name: 'export_transactions',
    parameters: params,
  }),
};

// Stocks API
export const stocksAPI = {
  getPortfolio: () => api.post('/tools/invoke', {
    tool_name: 'get_portfolio',
    parameters: {},
  }),
  getQuote: (symbol) => api.post('/tools/invoke', {
    tool_name: 'get_stock_quote',
    parameters: { symbol },
  }),
  getTransactions: () => api.post('/tools/invoke', {
    tool_name: 'get_stock_transactions',
    parameters: {},
  }),
};

// Travel API
export const travelAPI = {
  searchFlights: (params) => api.post('/tools/invoke', {
    tool_name: 'search_flights',
    parameters: params,
  }),
  searchHotels: (params) => api.post('/tools/invoke', {
    tool_name: 'search_hotels',
    parameters: params,
  }),
  searchCars: (params) => api.post('/tools/invoke', {
    tool_name: 'search_car_rentals',
    parameters: params,
  }),
  setPriceAlert: (params) => api.post('/tools/invoke', {
    tool_name: 'set_price_alert',
    parameters: params,
  }),
};

// Research API
export const researchAPI = {
  searchLegal: (params) => api.post('/tools/invoke', {
    tool_name: 'search_legal',
    parameters: params,
  }),
  getProjects: () => api.post('/tools/invoke', {
    tool_name: 'list_projects',
    parameters: {},
  }),
  createProject: (params) => api.post('/tools/invoke', {
    tool_name: 'create_project',
    parameters: params,
  }),
  conductResearch: (params) => api.post('/tools/invoke', {
    tool_name: 'conduct_research',
    parameters: params,
  }),
};

// RAG/Documents API
export const documentsAPI = {
  upload: (formData) => api.post('/rag/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  query: (query, topK = 5) => api.post('/rag/query', { query, top_k: topK }),
  list: () => api.get('/rag/documents'),
  delete: (documentId) => api.delete(`/rag/documents/${documentId}`),
};

// Memory API
export const memoryAPI = {
  addFact: (data) => api.post('/memory/add', data),
  getFacts: (category) => api.post('/memory/get', { category }),
  getConversation: (sessionId) => api.get(`/memory/conversation/${sessionId}`),
  deleteConversation: (sessionId) => api.delete(`/memory/conversation/${sessionId}`),
  getSummaries: () => api.get('/memory/summaries'),
};

// Voice API
export const voiceAPI = {
  transcribe: (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    return api.post('/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  processCommand: (data) => api.post('/voice/command', data),
  textToSpeech: (text, voiceId = 'default') => api.post('/voice/tts', { text, voice_id: voiceId }),
  getVoices: () => api.get('/voice/voices'),
};

// Setup API
export const setupAPI = {
  getProfile: () => api.get('/setup/profile'),
  updateProfile: (data) => api.post('/setup/profile', data),
  updatePreferences: (data) => api.put('/setup/preferences', data),
  getModules: () => api.get('/setup/modules'),
  updateModules: (data) => api.post('/setup/modules', data),
  enableModule: (moduleName) => api.post(`/setup/modules/${moduleName}/enable`),
  disableModule: (moduleName) => api.post(`/setup/modules/${moduleName}/disable`),
  getAvailableModules: () => api.get('/setup/modules/available'),
};

// Tools API
export const toolsAPI = {
  list: () => api.get('/tools/list'),
  invoke: (toolName, parameters) => api.post('/tools/invoke', {
    tool_name: toolName,
    parameters,
  }),
  getDetails: (toolName) => api.get(`/tools/${toolName}`),
  getCategories: () => api.get('/tools/categories/list'),
};
