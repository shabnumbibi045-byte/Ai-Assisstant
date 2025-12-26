import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiCheckCircle, HiXCircle, HiExclamation, HiInformationCircle, HiX } from 'react-icons/hi';

const variants = {
  success: {
    icon: HiCheckCircle,
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    iconColor: 'text-emerald-400',
    titleColor: 'text-emerald-400',
  },
  error: {
    icon: HiXCircle,
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    iconColor: 'text-red-400',
    titleColor: 'text-red-400',
  },
  warning: {
    icon: HiExclamation,
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    iconColor: 'text-amber-400',
    titleColor: 'text-amber-400',
  },
  info: {
    icon: HiInformationCircle,
    bg: 'bg-primary-500/10',
    border: 'border-primary-500/30',
    iconColor: 'text-primary-400',
    titleColor: 'text-primary-400',
  },
};

const Alert = ({ type = 'info', title, message, onClose, className = '' }) => {
  const variant = variants[type];
  const Icon = variant.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`${variant.bg} ${variant.border} border rounded-xl p-4 ${className}`}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 ${variant.iconColor} flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          {title && <p className={`font-medium ${variant.titleColor}`}>{title}</p>}
          {message && <p className="text-slate-300 text-sm mt-1">{message}</p>}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <HiX className="w-5 h-5" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

// Alert Banner (full width)
export const AlertBanner = ({ type = 'info', message, onClose }) => {
  const variant = variants[type];
  const Icon = variant.icon;

  return (
    <div className={`${variant.bg} ${variant.border} border-b px-4 py-3`}>
      <div className="flex items-center justify-center gap-3">
        <Icon className={`w-5 h-5 ${variant.iconColor}`} />
        <p className="text-slate-300 text-sm">{message}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors ml-auto"
          >
            <HiX className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
};

// Alert List (for multiple alerts)
export const AlertList = ({ alerts, onDismiss }) => {
  return (
    <AnimatePresence>
      <div className="space-y-3">
        {alerts.map((alert, index) => (
          <Alert
            key={alert.id || index}
            type={alert.type}
            title={alert.title}
            message={alert.message}
            onClose={onDismiss ? () => onDismiss(alert.id || index) : undefined}
          />
        ))}
      </div>
    </AnimatePresence>
  );
};

export default Alert;
