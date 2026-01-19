import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { HiMail, HiArrowLeft } from 'react-icons/hi';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    
    setIsSubmitted(true);
    toast.success('Password reset link sent!');
    setIsLoading(false);
  };

  if (isSubmitted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">Check Your Email</h2>
        <p className="text-slate-400 mb-8">
          We've sent a password reset link to<br />
          <span className="text-white">{email}</span>
        </p>
        <p className="text-sm text-slate-500 mb-6">
          Didn't receive the email? Check your spam folder or
        </p>
        <button
          onClick={() => setIsSubmitted(false)}
          className="text-primary-400 hover:text-primary-300 font-medium"
        >
          Try another email address
        </button>
        <div className="mt-8">
          <Link
            to="/login"
            className="text-slate-400 hover:text-white flex items-center justify-center gap-2"
          >
            <HiArrowLeft className="w-4 h-4" />
            Back to login
          </Link>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Mobile logo */}
      <div className="lg:hidden text-center mb-8">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-glow">
          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h1 className="text-2xl font-display font-bold gradient-text">AN INTELLIGENT AI</h1>
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-display font-bold text-white mb-2">Forgot Password?</h2>
        <p className="text-slate-400">
          No worries, we'll send you reset instructions.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div className="input-group">
          <HiMail className="input-icon w-5 h-5" />
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-with-icon"
            required
          />
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="spinner w-5 h-5"></div>
              <span>Sending...</span>
            </>
          ) : (
            'Send Reset Link'
          )}
        </button>
      </form>

      {/* Back to login */}
      <div className="mt-8 text-center">
        <Link
          to="/login"
          className="text-slate-400 hover:text-white flex items-center justify-center gap-2"
        >
          <HiArrowLeft className="w-4 h-4" />
          Back to login
        </Link>
      </div>
    </motion.div>
  );
};

export default ForgotPassword;
