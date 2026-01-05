import React, { useCallback, useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import toast from 'react-hot-toast';
import { HiLockClosed, HiCheckCircle } from 'react-icons/hi';
import plaidApi from '../services/plaidApi';

/**
 * PlaidLink Component - Bank Account Connection
 *
 * This component handles the Plaid Link flow:
 * 1. Creates a link token
 * 2. Opens Plaid Link UI
 * 3. Exchanges public token for access token
 * 4. Fetches account data
 */
const PlaidLink = ({ onSuccess, onExit, countryCodes = ['US', 'CA'] }) => {
  const [linkToken, setLinkToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch link token on component mount
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        setIsLoading(true);
        const response = await plaidApi.createLinkToken(countryCodes);
        setLinkToken(response.link_token);
        setIsLoading(false);
      } catch (error) {
        console.error('Error creating link token:', error);
        toast.error('Failed to initialize bank connection', {
          duration: 4000,
          icon: '❌',
          style: {
            background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            color: '#ffffff',
            border: '1px solid #dc2626',
            borderRadius: '12px',
            padding: '16px 24px',
            fontSize: '15px',
            fontWeight: '600',
            boxShadow: '0 10px 25px -5px rgba(239, 68, 68, 0.4)',
          },
        });
        setIsLoading(false);
      }
    };

    createLinkToken();
  }, [countryCodes]);

  // Handle successful connection
  const onPlaidSuccess = useCallback(
    async (publicToken, metadata) => {
      try {
        // Show loading toast
        const loadingToast = toast.loading('Connecting your bank account...', {
          style: {
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            color: '#ffffff',
            border: '1px solid #2563eb',
            borderRadius: '12px',
            padding: '16px 24px',
            fontSize: '15px',
            fontWeight: '600',
          },
        });

        // Exchange public token for access token
        const tokenResponse = await plaidApi.exchangePublicToken(publicToken);
        const accessToken = tokenResponse.access_token;

        // Fetch account data
        const accountsData = await plaidApi.getAccounts(accessToken);

        // Dismiss loading toast
        toast.dismiss(loadingToast);

        // Show success toast
        toast.success(
          `Successfully connected ${metadata.institution.name}!`,
          {
            duration: 4000,
            icon: '🏦',
            style: {
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#ffffff',
              border: '1px solid #059669',
              borderRadius: '12px',
              padding: '16px 24px',
              fontSize: '15px',
              fontWeight: '600',
              boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.4)',
            },
          }
        );

        // Call parent success handler
        if (onSuccess) {
          onSuccess({
            accessToken,
            itemId: tokenResponse.item_id,
            accounts: accountsData.accounts,
            institution: metadata.institution,
          });
        }
      } catch (error) {
        console.error('Error processing bank connection:', error);
        toast.error('Failed to connect bank account. Please try again.', {
          duration: 4000,
          icon: '❌',
          style: {
            background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            color: '#ffffff',
            border: '1px solid #dc2626',
            borderRadius: '12px',
            padding: '16px 24px',
            fontSize: '15px',
            fontWeight: '600',
            boxShadow: '0 10px 25px -5px rgba(239, 68, 68, 0.4)',
          },
        });
      }
    },
    [onSuccess]
  );

  // Handle exit/cancel
  const onPlaidExit = useCallback(
    (error, metadata) => {
      // Prevent any default behavior that might cause page refresh
      if (error) {
        console.error('Plaid Link error:', error);

        // Don't show toast for user-initiated cancellations
        if (error.error_code !== 'USER_EXIT') {
          // Show different messages based on error type
          let errorMessage = 'Bank connection failed. Please try again.';

          if (error.error_code === 'INVALID_CREDENTIALS') {
            errorMessage = 'Invalid credentials. Please check your username and password.';
          } else if (error.error_code === 'ITEM_LOGIN_REQUIRED') {
            errorMessage = 'Authentication failed. Please verify your credentials.';
          } else if (error.error_code === 'INSTITUTION_NOT_RESPONDING') {
            errorMessage = 'Bank is not responding. Please try again later.';
          }

          toast.error(errorMessage, {
            duration: 5000,
            icon: '⚠️',
            position: 'top-right',
            style: {
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: '#ffffff',
              border: '2px solid #d97706',
              borderRadius: '12px',
              padding: '16px 24px',
              fontSize: '15px',
              fontWeight: '600',
              boxShadow: '0 10px 25px -5px rgba(245, 158, 11, 0.6)',
              zIndex: 999999,
            },
          });
        }
      }

      // Call parent exit handler without causing navigation
      if (onExit) {
        onExit(error, metadata);
      }
    },
    [onExit]
  );

  // Configure Plaid Link
  const config = {
    token: linkToken,
    onSuccess: onPlaidSuccess,
    onExit: onPlaidExit,
  };

  const { open, ready } = usePlaidLink(config);

  // Auto-open when ready (optional - you can also trigger manually)
  // useEffect(() => {
  //   if (ready) {
  //     open();
  //   }
  // }, [ready, open]);

  return (
    <div className="plaid-link-container">
      <button
        type="button"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          open();
        }}
        disabled={!ready || isLoading}
        className="btn-primary w-full flex items-center justify-center gap-3 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <div className="spinner w-5 h-5"></div>
            <span>Initializing...</span>
          </>
        ) : !ready ? (
          <>
            <div className="spinner w-5 h-5"></div>
            <span>Loading...</span>
          </>
        ) : (
          <>
            <HiLockClosed className="w-6 h-6" />
            <span>Connect Bank Account</span>
          </>
        )}
      </button>

      <p className="text-xs text-slate-400 text-center mt-3">
        <HiCheckCircle className="inline w-4 h-4 mr-1 text-green-400" />
        Secured by Plaid • Your credentials are never stored
      </p>
    </div>
  );
};

export default PlaidLink;
