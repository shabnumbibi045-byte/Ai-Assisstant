import React, { useState, useEffect } from 'react';

let toastId = 0;
const toasts = [];
let setToastsCallback = null;

export const showToast = (message, type = 'error') => {
  const id = ++toastId;
  const newToast = { id, message, type };

  toasts.push(newToast);
  if (setToastsCallback) {
    setToastsCallback([...toasts]);
  }

  // Auto remove after 4 seconds
  setTimeout(() => {
    removeToast(id);
  }, 4000);
};

const removeToast = (id) => {
  const index = toasts.findIndex(t => t.id === id);
  if (index !== -1) {
    toasts.splice(index, 1);
    if (setToastsCallback) {
      setToastsCallback([...toasts]);
    }
  }
};

const CustomToast = () => {
  const [activeToasts, setActiveToasts] = useState([]);

  useEffect(() => {
    setToastsCallback = setActiveToasts;
    return () => {
      setToastsCallback = null;
    };
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 999999,
      pointerEvents: 'none',
    }}>
      {activeToasts.map((toast) => (
        <div
          key={toast.id}
          style={{
            marginBottom: '8px',
            padding: '16px 24px',
            borderRadius: '12px',
            fontSize: '15px',
            fontWeight: '600',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)',
            pointerEvents: 'auto',
            cursor: 'pointer',
            minWidth: '300px',
            background: toast.type === 'error'
              ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
              : toast.type === 'success'
              ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
              : 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            color: '#ffffff',
            border: toast.type === 'error'
              ? '1px solid #dc2626'
              : toast.type === 'success'
              ? '1px solid #059669'
              : '1px solid #d97706',
          }}
          onClick={() => removeToast(toast.id)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '20px' }}>
              {toast.type === 'error' ? '❌' : toast.type === 'success' ? '✅' : '⚠️'}
            </span>
            <span>{toast.message}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CustomToast;
