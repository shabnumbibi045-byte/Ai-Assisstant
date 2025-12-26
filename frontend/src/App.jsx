import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layouts
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';

// Dashboard Pages
import Dashboard from './pages/dashboard/Dashboard';
import Chat from './pages/dashboard/Chat';
import Banking from './pages/dashboard/Banking';
import Stocks from './pages/dashboard/Stocks';
import Travel from './pages/dashboard/Travel';
import Research from './pages/dashboard/Research';
import Documents from './pages/dashboard/Documents';
import Voice from './pages/dashboard/Voice';
import Settings from './pages/dashboard/Settings';
import Profile from './pages/dashboard/Profile';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="spinner w-12 h-12"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="spinner w-12 h-12"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />
      </Route>

      {/* Dashboard Routes */}
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/banking" element={<Banking />} />
        <Route path="/stocks" element={<Stocks />} />
        <Route path="/travel" element={<Travel />} />
        <Route path="/research" element={<Research />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/voice" element={<Voice />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* Redirect root to dashboard or login */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* 404 - Not Found */}
      <Route
        path="*"
        element={
          <div className="min-h-screen flex items-center justify-center bg-slate-900">
            <div className="text-center">
              <h1 className="text-6xl font-bold gradient-text mb-4">404</h1>
              <p className="text-slate-400 mb-8">Page not found</p>
              <a href="/dashboard" className="btn-primary">
                Go to Dashboard
              </a>
            </div>
          </div>
        }
      />
    </Routes>
  );
}

export default App;
