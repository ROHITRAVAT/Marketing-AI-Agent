import { create } from 'zustand';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

const getInitialUser = (): User | null => {
  try {
    const raw = localStorage.getItem('auth_user');
    if (raw) {
      return JSON.parse(raw);
    }
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Fallback session so refresh never kicks the user out
      return {
        id: 1,
        email: 'user@marketing.ai',
        username: 'marketer',
        full_name: 'Marketing Lead',
        role: 'admin',
        is_active: true,
        is_verified: true,
      };
    }
    return null;
  } catch {
    return null;
  }
};

const initialToken = localStorage.getItem('auth_token');
const initialUser = getInitialUser();

export const useAuthStore = create<AuthState>((set) => ({
  user: initialUser,
  token: initialToken,
  isAuthenticated: !!initialToken || !!initialUser,
  isLoading: false,

  setAuth: (user, token) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
    set({ user, token, isAuthenticated: true, isLoading: false });
  },

  setUser: (user) => {
    localStorage.setItem('auth_user', JSON.stringify(user));
    set({ user });
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    set({ user: null, token: null, isAuthenticated: false, isLoading: false });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },
}));
