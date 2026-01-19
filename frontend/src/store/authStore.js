import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      // Initialize auth state
      initialize: async () => {
        const token = get().token;
        if (token && token !== 'demo-token') {
          try {
            const response = await api.get('/auth/me');
            set({ 
              user: transformUserResponse(response.data), 
              isAuthenticated: true, 
              isLoading: false 
            });
          } catch (error) {
            set({ user: null, token: null, refreshToken: null, isAuthenticated: false, isLoading: false });
          }
        } else if (token === 'demo-token') {
          // Already in demo mode
          set({ isLoading: false });
        } else {
          set({ isLoading: false });
        }
      },

      // Login - Backend returns Token (access_token, refresh_token, token_type, expires_in)
      // Then we need to fetch user data from /auth/me
      login: async (email, password) => {
        try {
          // Validate inputs
          if (!email || !password) {
            return {
              success: false,
              error: 'Please enter both email and password'
            };
          }

          // Step 1: Get tokens
          const tokenResponse = await api.post('/auth/login', { email, password });
          const { access_token, refresh_token } = tokenResponse.data;

          // Store tokens first so interceptor can use them
          set({
            token: access_token,
            refreshToken: refresh_token,
          });

          // Step 2: Get user data with new token
          const userResponse = await api.get('/auth/me');

          set({
            user: transformUserResponse(userResponse.data),
            isAuthenticated: true,
            isLoading: false,
          });

          return {
            success: true,
            message: `Welcome back, ${transformUserResponse(userResponse.data).firstName || 'User'}!`
          };
        } catch (error) {
          // Clear any partial state
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
          });

          // Provide specific error messages based on status code
          let errorMessage = 'Login failed. Please try again.';

          if (error.response) {
            const status = error.response.status;
            const detail = error.response.data?.detail;

            if (status === 401) {
              errorMessage = detail || 'Invalid email or password. Please check your credentials and try again.';
            } else if (status === 403) {
              errorMessage = 'Your account has been disabled. Please contact support.';
            } else if (status === 500) {
              errorMessage = 'Server error. Please try again later.';
            } else if (detail) {
              errorMessage = detail;
            }
          } else if (error.request) {
            errorMessage = 'Cannot connect to server. Please check your internet connection.';
          }

          return {
            success: false,
            error: errorMessage
          };
        }
      },

      // Register - Only create account, user must login separately
      register: async (userData) => {
        try {
          // Register user only - no automatic login
          const response = await api.post('/auth/register', {
            email: userData.email,
            password: userData.password,
            full_name: userData.name || userData.full_name || `${userData.firstName || ''} ${userData.lastName || ''}`.trim(),
            phone: userData.phone || null,
          });

          // Return success with user data (but don't login)
          return {
            success: true,
            user: response.data,
            message: 'Account created successfully! Please login to continue.'
          };
        } catch (error) {
          return {
            success: false,
            error: error.response?.data?.detail || 'Registration failed. Please try again.'
          };
        }
      },

      // Logout
      logout: () => {
        // Clear Plaid banking data on logout
        localStorage.removeItem('plaid_access_token');
        localStorage.removeItem('plaid_item_id');
        localStorage.removeItem('plaid_accounts');
        localStorage.removeItem('plaid_transactions');

        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      // Update user
      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } });
      },

      // Refresh token
      refreshAccessToken: async () => {
        const refreshToken = get().refreshToken;
        if (!refreshToken || refreshToken === 'demo-refresh') return false;

        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
          const { access_token, refresh_token: newRefreshToken } = response.data;
          set({ 
            token: access_token,
            refreshToken: newRefreshToken || refreshToken 
          });
          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },

      // Demo Mode - bypass authentication for testing
      setDemoMode: () => {
        set({
          user: {
            id: 'demo-user',
            user_id: 'demo-user-uuid',
            email: 'demo@lestrap.com',
            firstName: 'Demo',
            lastName: 'User',
            full_name: 'Demo User',
            company: 'LeStrap Enterprises',
            role: 'Demo Account',
            is_active: true,
            is_verified: true,
            modules_enabled: ['chat', 'memory', 'banking', 'stocks', 'travel', 'research'],
          },
          token: 'demo-token',
          refreshToken: 'demo-refresh',
          isAuthenticated: true,
          isLoading: false,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Helper function to transform backend UserResponse to frontend user object
function transformUserResponse(data) {
  const nameParts = (data.full_name || '').split(' ');
  return {
    id: data.id,
    user_id: data.user_id,
    email: data.email,
    full_name: data.full_name,
    firstName: nameParts[0] || '',
    lastName: nameParts.slice(1).join(' ') || '',
    phone: data.phone,
    is_active: data.is_active,
    is_verified: data.is_verified,
    created_at: data.created_at,
    last_active: data.last_active,
    modules_enabled: data.modules_enabled || ['chat', 'memory'],
  };
}

// Initialize on app load
if (typeof window !== 'undefined') {
  useAuthStore.getState().initialize();
}
