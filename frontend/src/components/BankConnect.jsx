import React, { useState, useCallback, useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import plaidApi from '../services/plaidApi';

/**
 * BankConnect Component
 *
 * Handles the complete Plaid Link integration flow:
 * 1. Creates link token
 * 2. Opens Plaid Link UI
 * 3. Exchanges public token for access token
 * 4. Fetches and displays account data
 */
const BankConnect = ({ onSuccess, onError }) => {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [accessToken, setAccessToken] = useState(null);
  const [error, setError] = useState(null);

  // Step 1: Create link token when component mounts
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        setLoading(true);
        const response = await plaidApi.createLinkToken(['US', 'CA']);
        setLinkToken(response.link_token);
        setError(null);
      } catch (err) {
        setError('Failed to initialize bank connection. Please try again.');
        if (onError) onError(err);
      } finally {
        setLoading(false);
      }
    };

    createLinkToken();
  }, [onError]);

  // Step 3: Handle successful bank connection
  const onPlaidSuccess = useCallback(async (publicToken, metadata) => {
    try {
      setLoading(true);

      // Exchange public token for access token
      const tokenResponse = await plaidApi.exchangePublicToken(publicToken);
      const { access_token, item_id } = tokenResponse;

      setAccessToken(access_token);

      // Fetch account data
      const accountsData = await plaidApi.getAccounts(access_token);
      setAccounts(accountsData.accounts || []);

      // Fetch recent transactions (last 30 days)
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const transactionsData = await plaidApi.getTransactions({
        accessToken: access_token,
        startDate,
        endDate,
      });
      setTransactions(transactionsData.transactions || []);

      // Store access token in localStorage for AI assistant to use
      localStorage.setItem('plaid_access_token', access_token);
      localStorage.setItem('plaid_item_id', item_id);
      localStorage.setItem('plaid_accounts', JSON.stringify(accountsData.accounts || []));
      localStorage.setItem('plaid_transactions', JSON.stringify(transactionsData.transactions || []));

      setError(null);
      if (onSuccess) {
        onSuccess({
          accessToken: access_token,
          itemId: item_id,
          accounts: accountsData.accounts,
          transactions: transactionsData.transactions,
        });
      }
    } catch (err) {
      setError('Failed to fetch account data. Please try again.');
      if (onError) onError(err);
    } finally {
      setLoading(false);
    }
  }, [onSuccess, onError]);

  // Step 2: Initialize Plaid Link
  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: onPlaidSuccess,
    onExit: (err, metadata) => {
      if (err) {
        setError('Bank connection was cancelled or failed.');
      }
    },
  });

  // Format currency
  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  // Calculate total balance
  const totalBalance = accounts.reduce((sum, account) => {
    return sum + (account.balance?.current || 0);
  }, 0);

  return (
    <div className="bank-connect-container" style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>🏦 Connect Your Bank Account</h2>
        <p style={styles.subtitle}>
          Securely connect your bank to get real-time balance and transaction data
        </p>
      </div>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {!accessToken ? (
        <div style={styles.connectSection}>
          <button
            onClick={() => open()}
            disabled={!ready || loading}
            style={{
              ...styles.connectButton,
              ...((!ready || loading) && styles.connectButtonDisabled),
            }}
          >
            {loading ? '🔄 Loading...' : '🔗 Connect Bank Account'}
          </button>
          <p style={styles.secureNote}>
            🔒 Secured by Plaid - Your credentials are never stored
          </p>
        </div>
      ) : (
        <div style={styles.dataSection}>
          <div style={styles.successBanner}>
            ✅ Bank connected successfully!
          </div>

          {/* Account Summary */}
          <div style={styles.summaryCard}>
            <h3 style={styles.sectionTitle}>Account Summary</h3>
            <div style={styles.totalBalance}>
              <span style={styles.balanceLabel}>Total Balance</span>
              <span style={styles.balanceAmount}>{formatCurrency(totalBalance)}</span>
            </div>
            <div style={styles.accountCount}>
              {accounts.length} account{accounts.length !== 1 ? 's' : ''} connected
            </div>
          </div>

          {/* Accounts List */}
          {accounts.length > 0 && (
            <div style={styles.accountsSection}>
              <h3 style={styles.sectionTitle}>Your Accounts</h3>
              <div style={styles.accountsList}>
                {accounts.map((account) => (
                  <div key={account.account_id} style={styles.accountCard}>
                    <div style={styles.accountHeader}>
                      <div>
                        <div style={styles.accountName}>{account.name}</div>
                        {account.official_name && (
                          <div style={styles.accountOfficial}>{account.official_name}</div>
                        )}
                      </div>
                      <div style={styles.accountMask}>****{account.mask}</div>
                    </div>
                    <div style={styles.accountDetails}>
                      <div style={styles.accountType}>
                        {account.subtype} • {account.type}
                      </div>
                      <div style={styles.accountBalance}>
                        {formatCurrency(account.balance?.current, account.balance?.currency)}
                      </div>
                    </div>
                    {account.balance?.available !== null && account.balance?.available !== account.balance?.current && (
                      <div style={styles.availableBalance}>
                        Available: {formatCurrency(account.balance?.available, account.balance?.currency)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Transactions */}
          {transactions.length > 0 && (
            <div style={styles.transactionsSection}>
              <h3 style={styles.sectionTitle}>Recent Transactions (Last 30 Days)</h3>
              <div style={styles.transactionsList}>
                {transactions.slice(0, 10).map((transaction) => (
                  <div key={transaction.transaction_id} style={styles.transactionCard}>
                    <div style={styles.transactionMain}>
                      <div>
                        <div style={styles.transactionName}>
                          {transaction.merchant_name || transaction.name}
                        </div>
                        <div style={styles.transactionDate}>
                          {new Date(transaction.date).toLocaleDateString()}
                        </div>
                      </div>
                      <div
                        style={{
                          ...styles.transactionAmount,
                          color: transaction.amount > 0 ? '#dc2626' : '#059669',
                        }}
                      >
                        {transaction.amount > 0 ? '-' : '+'}
                        {formatCurrency(Math.abs(transaction.amount), transaction.currency)}
                      </div>
                    </div>
                    {transaction.category && transaction.category.length > 0 && (
                      <div style={styles.transactionCategory}>
                        {transaction.category.join(' > ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {transactions.length > 10 && (
                <div style={styles.moreTransactions}>
                  + {transactions.length - 10} more transactions
                </div>
              )}
            </div>
          )}

          <button
            onClick={() => {
              setAccessToken(null);
              setAccounts([]);
              setTransactions([]);
              localStorage.removeItem('plaid_access_token');
              localStorage.removeItem('plaid_item_id');
              localStorage.removeItem('plaid_accounts');
              localStorage.removeItem('plaid_transactions');
            }}
            style={styles.disconnectButton}
          >
            🔌 Disconnect Bank
          </button>
        </div>
      )}
    </div>
  );
};

// Styles
const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '10px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#6b7280',
  },
  error: {
    backgroundColor: '#fee2e2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '12px 16px',
    marginBottom: '20px',
    color: '#991b1b',
  },
  connectSection: {
    textAlign: 'center',
    padding: '40px 20px',
  },
  connectButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    padding: '14px 32px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 4px 6px rgba(59, 130, 246, 0.3)',
  },
  connectButtonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  secureNote: {
    marginTop: '16px',
    fontSize: '14px',
    color: '#6b7280',
  },
  dataSection: {
    animation: 'fadeIn 0.5s',
  },
  successBanner: {
    backgroundColor: '#d1fae5',
    border: '1px solid #6ee7b7',
    borderRadius: '8px',
    padding: '12px 16px',
    marginBottom: '24px',
    color: '#065f46',
    textAlign: 'center',
    fontWeight: '500',
  },
  summaryCard: {
    backgroundColor: '#f9fafb',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px',
    border: '1px solid #e5e7eb',
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '16px',
  },
  totalBalance: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  balanceLabel: {
    fontSize: '14px',
    color: '#6b7280',
  },
  balanceAmount: {
    fontSize: '32px',
    fontWeight: '700',
    color: '#059669',
  },
  accountCount: {
    fontSize: '14px',
    color: '#6b7280',
  },
  accountsSection: {
    marginBottom: '24px',
  },
  accountsList: {
    display: 'grid',
    gap: '12px',
  },
  accountCard: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '16px',
    transition: 'all 0.2s',
  },
  accountHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '12px',
  },
  accountName: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
  },
  accountOfficial: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '2px',
  },
  accountMask: {
    fontSize: '14px',
    color: '#6b7280',
    fontFamily: 'monospace',
  },
  accountDetails: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  accountType: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'capitalize',
  },
  accountBalance: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#1f2937',
  },
  availableBalance: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '8px',
  },
  transactionsSection: {
    marginBottom: '24px',
  },
  transactionsList: {
    display: 'grid',
    gap: '8px',
  },
  transactionCard: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '12px 16px',
  },
  transactionMain: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transactionName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#1f2937',
  },
  transactionDate: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '2px',
  },
  transactionAmount: {
    fontSize: '16px',
    fontWeight: '600',
  },
  transactionCategory: {
    fontSize: '11px',
    color: '#6b7280',
    marginTop: '8px',
    fontStyle: 'italic',
  },
  moreTransactions: {
    textAlign: 'center',
    padding: '12px',
    fontSize: '14px',
    color: '#6b7280',
  },
  disconnectButton: {
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    width: '100%',
    marginTop: '16px',
  },
};

export default BankConnect;
