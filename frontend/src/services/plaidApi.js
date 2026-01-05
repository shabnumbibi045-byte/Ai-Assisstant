import api from './api';

/**
 * Plaid API Service - Frontend integration for banking
 */

const plaidApi = {
  /**
   * Create a link token for Plaid Link
   * @param {Array<string>} countryCodes - List of country codes (e.g., ["US", "CA"])
   * @returns {Promise} - Link token response
   */
  createLinkToken: async (countryCodes = ['US', 'CA']) => {
    try {
      const response = await api.post('/plaid/create_link_token', {
        country_codes: countryCodes,
      });
      return response.data;
    } catch (error) {
      console.error('Error creating link token:', error);
      throw error;
    }
  },

  /**
   * Exchange public token for access token
   * @param {string} publicToken - Public token from Plaid Link
   * @returns {Promise} - Access token response
   */
  exchangePublicToken: async (publicToken) => {
    try {
      const response = await api.post('/plaid/exchange_public_token', {
        public_token: publicToken,
      });
      return response.data;
    } catch (error) {
      console.error('Error exchanging public token:', error);
      throw error;
    }
  },

  /**
   * Get account information and balances
   * @param {string} accessToken - Plaid access token
   * @returns {Promise} - Accounts data
   */
  getAccounts: async (accessToken) => {
    try {
      const response = await api.post('/plaid/accounts', {
        access_token: accessToken,
      });
      return response.data;
    } catch (error) {
      console.error('Error getting accounts:', error);
      throw error;
    }
  },

  /**
   * Get account and routing numbers
   * @param {string} accessToken - Plaid access token
   * @returns {Promise} - Auth data
   */
  getAuthData: async (accessToken) => {
    try {
      const response = await api.post('/plaid/auth', {
        access_token: accessToken,
      });
      return response.data;
    } catch (error) {
      console.error('Error getting auth data:', error);
      throw error;
    }
  },

  /**
   * Get transaction history
   * @param {Object} params - Transaction parameters
   * @param {string} params.accessToken - Plaid access token
   * @param {string} params.startDate - Start date (YYYY-MM-DD)
   * @param {string} params.endDate - End date (YYYY-MM-DD)
   * @param {Array<string>} params.accountIds - Optional account ID filter
   * @returns {Promise} - Transactions data
   */
  getTransactions: async ({ accessToken, startDate, endDate, accountIds }) => {
    try {
      const response = await api.post('/plaid/transactions', {
        access_token: accessToken,
        start_date: startDate,
        end_date: endDate,
        account_ids: accountIds,
      });
      return response.data;
    } catch (error) {
      console.error('Error getting transactions:', error);
      throw error;
    }
  },

  /**
   * Health check for Plaid integration
   * @returns {Promise} - Health status
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/plaid/health');
      return response.data;
    } catch (error) {
      console.error('Error checking Plaid health:', error);
      throw error;
    }
  },
};

export default plaidApi;
