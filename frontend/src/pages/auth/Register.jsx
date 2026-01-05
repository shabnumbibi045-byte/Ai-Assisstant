import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../store/authStore';
import toast from 'react-hot-toast';
import { HiMail, HiLockClosed, HiEye, HiEyeOff, HiUser } from 'react-icons/hi';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation error toast styling
    const errorToastStyle = {
      duration: 4000,
      icon: '⚠️',
      position: 'top-right',
      style: {
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        color: '#ffffff',
        border: '1px solid #d97706',
        borderRadius: '12px',
        padding: '16px 24px',
        fontSize: '15px',
        fontWeight: '600',
        boxShadow: '0 10px 25px -5px rgba(245, 158, 11, 0.4)',
        zIndex: 999999,
      },
    };

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match', errorToastStyle);
      return;
    }

    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters', errorToastStyle);
      return;
    }

    if (formData.password.length > 72) {
      toast.error('Password cannot exceed 72 characters', errorToastStyle);
      return;
    }

    setIsLoading(true);

    const result = await register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
    });

    if (result.success) {
      // Show success message with custom styling
      toast.success(result.message || 'Account created successfully! Please login to continue.', {
        duration: 4000,
        icon: '✅',
        position: 'top-right',
        style: {
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          color: '#ffffff',
          border: '1px solid #059669',
          borderRadius: '12px',
          padding: '16px 24px',
          fontSize: '15px',
          fontWeight: '600',
          boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.4)',
          zIndex: 999999,
        },
      });

      // Redirect to login page after a brief delay
      setTimeout(() => {
        navigate('/login');
      }, 1000);
    } else {
      // Show error message with custom styling
      toast.error(result.error, {
        duration: 4000,
        icon: '❌',
        position: 'top-right',
        style: {
          background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
          color: '#ffffff',
          border: '1px solid #dc2626',
          borderRadius: '12px',
          padding: '16px 24px',
          fontSize: '15px',
          fontWeight: '600',
          boxShadow: '0 10px 25px -5px rgba(239, 68, 68, 0.4)',
          zIndex: 999999,
        },
      });
    }

    setIsLoading(false);
  };

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
        <h1 className="text-2xl font-display font-bold gradient-text">Salim AI</h1>
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-display font-bold text-white mb-2">Create Account</h2>
        <p className="text-slate-400">Start your journey with Salim AI</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Name */}
        <div className="input-group">
          <HiUser className="input-icon w-5 h-5" />
          <input
            type="text"
            name="name"
            placeholder="Full name"
            value={formData.name}
            onChange={handleChange}
            className="input-with-icon"
            required
          />
        </div>

        {/* Email */}
        <div className="input-group">
          <HiMail className="input-icon w-5 h-5" />
          <input
            type="email"
            name="email"
            placeholder="Email address"
            value={formData.email}
            onChange={handleChange}
            className="input-with-icon"
            required
          />
        </div>

        {/* Password */}
        <div className="input-group">
          <HiLockClosed className="input-icon w-5 h-5" />
          <input
            type={showPassword ? 'text' : 'password'}
            name="password"
            placeholder="Password (min. 8 characters)"
            value={formData.password}
            onChange={handleChange}
            className="input-with-icon pr-12"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
          >
            {showPassword ? <HiEyeOff className="w-5 h-5" /> : <HiEye className="w-5 h-5" />}
          </button>
        </div>

        {/* Confirm Password */}
        <div className="input-group">
          <HiLockClosed className="input-icon w-5 h-5" />
          <input
            type={showPassword ? 'text' : 'password'}
            name="confirmPassword"
            placeholder="Confirm password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="input-with-icon"
            required
          />
        </div>

        {/* Terms */}
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            id="terms"
            className="mt-1 w-4 h-4 rounded border-slate-600 bg-slate-800 text-primary-500 focus:ring-primary-500 focus:ring-offset-slate-900"
            required
          />
          <label htmlFor="terms" className="text-sm text-slate-400">
            I agree to the{' '}
            <a href="#" className="text-primary-400 hover:text-primary-300">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-primary-400 hover:text-primary-300">
              Privacy Policy
            </a>
          </label>
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
              <span>Creating account...</span>
            </>
          ) : (
            'Create Account'
          )}
        </button>
      </form>

      {/* Divider */}
      <div className="relative my-8">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-700"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-slate-900 text-slate-400">or sign up with</span>
        </div>
      </div>

      {/* Social signup */}
      <div className="grid grid-cols-2 gap-4">
        <button className="btn-ghost flex items-center justify-center gap-2 py-3 border border-slate-700 rounded-xl hover:border-slate-600">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          <span className="text-slate-300">Google</span>
        </button>
        <button className="btn-ghost flex items-center justify-center gap-2 py-3 border border-slate-700 rounded-xl hover:border-slate-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          <span className="text-slate-300">GitHub</span>
        </button>
      </div>

      {/* Sign in link */}
      <p className="mt-8 text-center text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </Link>
      </p>
    </motion.div>
  );
};

export default Register;
