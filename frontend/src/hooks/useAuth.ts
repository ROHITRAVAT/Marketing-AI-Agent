import { useAuthStore } from '@/store/useAuthStore';

export const useAuth = () => {
  const { user, token, isAuthenticated, isLoading, setAuth, logout } = useAuthStore();

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    setAuth,
    logout,
  };
};
