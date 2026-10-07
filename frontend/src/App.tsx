import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/layouts/AuthLayout';
import { MainLayout } from '@/layouts/MainLayout';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { ChatPage } from '@/pages/chat/ChatPage';
import { CampaignsPage } from '@/pages/campaigns/CampaignsPage';
import { AnalyticsPage } from '@/pages/analytics/AnalyticsPage';
import { SettingsPage } from '@/pages/settings/SettingsPage';
import { ProfilePage } from '@/pages/profile/ProfilePage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/useAuthStore';

export function App() {
  const { token, user, setUser, setLoading } = useAuthStore();

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    if (!user) {
      setLoading(true);
    }

    authService.getProfile()
      .then((profile) => {
        if (isMounted && useAuthStore.getState().token === token) {
          setUser({
            id: profile.user_id,
            email: profile.email,
            username: profile.username,
            full_name: profile.full_name,
            role: (profile.role as 'admin' | 'manager' | 'user') || 'user',
            is_active: true,
            is_verified: true,
          });
        }
      })
      .catch(() => {
        // Do not force logout on background profile check; preserve workspace state
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  return (
    <Router>
      <Routes>
        {/* Auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
        </Route>

        {/* Main Application routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/campaigns" element={<CampaignsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route element={<ProtectedRoute allowedRoles={['admin', 'manager']} />}>
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Route>
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          </Route>
        </Route>

        {/* 404 & Fallback */}
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </Router>
  );
}

export default App;