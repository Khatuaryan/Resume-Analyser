import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, isHR, isCandidate, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole === 'hr' && !isHR) {
    return <Navigate to="/candidate" replace />;
  }

  if (requiredRole === 'candidate' && !isCandidate) {
    return <Navigate to="/hr" replace />;
  }

  return children;
};

export default ProtectedRoute;
