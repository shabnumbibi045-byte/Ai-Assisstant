import React from 'react';
import { motion } from 'framer-motion';

// Loading Spinner
export const Spinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  return (
    <div className={`spinner ${sizeClasses[size]} ${className}`} />
  );
};

// Loading Overlay
export const LoadingOverlay = ({ message = 'Loading...' }) => (
  <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50">
    <div className="text-center">
      <Spinner size="lg" />
      <p className="mt-4 text-white font-medium">{message}</p>
    </div>
  </div>
);

// Page Loading
export const PageLoading = () => (
  <div className="min-h-[400px] flex items-center justify-center">
    <Spinner size="lg" />
  </div>
);

// Empty State
export const EmptyState = ({ icon: Icon, title, description, action }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="text-center py-16"
  >
    {Icon && (
      <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-slate-800 flex items-center justify-center">
        <Icon className="w-10 h-10 text-slate-500" />
      </div>
    )}
    <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
    {description && <p className="text-slate-400 max-w-md mx-auto mb-6">{description}</p>}
    {action && action}
  </motion.div>
);

// Card Skeleton
export const CardSkeleton = ({ count = 1 }) => (
  <>
    {[...Array(count)].map((_, i) => (
      <div key={i} className="card animate-pulse">
        <div className="h-4 bg-slate-700 rounded w-3/4 mb-4" />
        <div className="h-3 bg-slate-700 rounded w-1/2 mb-2" />
        <div className="h-3 bg-slate-700 rounded w-2/3" />
      </div>
    ))}
  </>
);

// Table Skeleton
export const TableSkeleton = ({ rows = 5, cols = 4 }) => (
  <div className="animate-pulse">
    <div className="border-b border-slate-700 py-3">
      <div className="flex gap-4">
        {[...Array(cols)].map((_, i) => (
          <div key={i} className="h-4 bg-slate-700 rounded flex-1" />
        ))}
      </div>
    </div>
    {[...Array(rows)].map((_, i) => (
      <div key={i} className="border-b border-slate-800 py-4">
        <div className="flex gap-4">
          {[...Array(cols)].map((_, j) => (
            <div key={j} className="h-3 bg-slate-800 rounded flex-1" />
          ))}
        </div>
      </div>
    ))}
  </div>
);

// Modal
export const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 overflow-y-auto"
    >
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="flex min-h-full items-center justify-center p-4">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={`relative w-full ${sizeClasses[size]} card`}
        >
          {title && (
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">{title}</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
          {children}
        </motion.div>
      </div>
    </motion.div>
  );
};

// Confirmation Dialog
export const ConfirmDialog = ({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', danger = false }) => (
  <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
    <p className="text-slate-400 mb-6">{message}</p>
    <div className="flex gap-3 justify-end">
      <button onClick={onClose} className="btn-ghost border border-slate-700">
        Cancel
      </button>
      <button
        onClick={() => {
          onConfirm();
          onClose();
        }}
        className={danger ? 'btn-ghost bg-red-500 hover:bg-red-600 border-red-500' : 'btn-primary'}
      >
        {confirmText}
      </button>
    </div>
  </Modal>
);

// Badge
export const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-slate-700 text-slate-300',
    primary: 'bg-primary-500/20 text-primary-400',
    secondary: 'bg-secondary-500/20 text-secondary-400',
    success: 'bg-emerald-500/20 text-emerald-400',
    warning: 'bg-amber-500/20 text-amber-400',
    danger: 'bg-red-500/20 text-red-400',
  };

  return (
    <span className={`badge ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

// Avatar
export const Avatar = ({ src, name, size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  const initials = name
    ? name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={`${sizeClasses[size]} rounded-full object-cover ${className}`}
      />
    );
  }

  return (
    <div className={`${sizeClasses[size]} rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold ${className}`}>
      {initials}
    </div>
  );
};

// Progress Bar
export const ProgressBar = ({ value, max = 100, color = 'primary', showLabel = false, size = 'md' }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const colors = {
    primary: 'bg-primary-500',
    secondary: 'bg-secondary-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
  };

  const heights = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className="w-full">
      <div className={`w-full bg-slate-700 rounded-full overflow-hidden ${heights[size]}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5 }}
          className={`${colors[color]} ${heights[size]} rounded-full`}
        />
      </div>
      {showLabel && (
        <p className="text-sm text-slate-400 mt-1">{percentage.toFixed(0)}%</p>
      )}
    </div>
  );
};

// Tooltip
export const Tooltip = ({ children, content, position = 'top' }) => {
  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div className="relative group">
      {children}
      <div className={`absolute ${positions[position]} hidden group-hover:block z-50`}>
        <div className="bg-slate-800 text-white text-sm px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
          {content}
        </div>
      </div>
    </div>
  );
};

export default {
  Spinner,
  LoadingOverlay,
  PageLoading,
  EmptyState,
  CardSkeleton,
  TableSkeleton,
  Modal,
  ConfirmDialog,
  Badge,
  Avatar,
  ProgressBar,
  Tooltip,
};
