import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';

interface ProtectedRouteProps {
  allowedRoles?: Array<'admin' | 'manager' | 'user'>;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const { isAuthenticated, user, isLoading, token } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F8F8F6] flex flex-col items-center justify-center text-sm text-[#71717A] gap-3">
        <div className="w-8 h-8 border-2 border-stone-300 border-t-stone-900 rounded-full animate-spin" />
        <span className="font-mono text-xs">Restoring workspace session...</span>
      </div>
    );
  }

  // Only redirect if there is genuinely no authentication session
  if (!isAuthenticated && !token && !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
