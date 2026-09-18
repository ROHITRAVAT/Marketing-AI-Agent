import api, { IS_DEV_FALLBACK_ENABLED } from './api';
import type {
  User,
  UserLoginRequest,
  UserRegisterRequest,
  TokenResponse,
  ResetPasswordRequest,
} from '@/types';

// Helper for dev mock persistence when backend is offline
const getMockUsers = (): Array<UserRegisterRequest & { id: number; role: string }> => {
  try {
    return JSON.parse(localStorage.getItem('dev_mock_users') || '[]');
  } catch {
    return [];
  }
};

const saveMockUser = (user: UserRegisterRequest & { id: number; role: string }) => {
  const users = getMockUsers();
  users.push(user);
  localStorage.setItem('dev_mock_users', JSON.stringify(users));
};

export const authService = {
  /**
   * Register a new user
   */
  async register(data: UserRegisterRequest): Promise<User> {
    try {
      const response = await api.post<User>('/auth/register', data);
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      // Fallback only if dev fallback is explicitly enabled
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        console.warn('[DEV MOCK ACTIVE] Backend server offline. Using local development mock fallback.');
        const newUser: User = {
          id: Date.now(),
          email: data.email,
          username: data.username || data.email.split('@')[0],
          full_name: data.full_name || 'User',
          role: 'user',
          is_active: true,
          is_verified: true,
        };
        saveMockUser({ ...data, id: newUser.id, role: 'user' });
        return newUser;
      }
      throw err;
    }
  },

  /**
   * Login user and obtain access token
   */
  async login(data: UserLoginRequest): Promise<TokenResponse> {
    try {
      const response = await api.post<TokenResponse>('/auth/login', data);
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        console.warn('[DEV MOCK ACTIVE] Backend server offline. Using local development mock fallback.');
        const mockUsers = getMockUsers();
        const found = mockUsers.find((u) => u.email.toLowerCase() === data.email.toLowerCase());

        // Create dev token and stash user details for getProfile
        const devToken = `dev_mock_token_${Date.now()}`;
        const profile = {
          user_id: found?.id || 1,
          email: data.email,
          username: found?.username || data.email.split('@')[0],
          full_name: found?.full_name || 'Marketing Specialist',
          role: found?.role || 'user',
        };
        localStorage.setItem('dev_mock_profile', JSON.stringify(profile));

        return {
          access_token: devToken,
          token_type: 'bearer',
        };
      }
      throw err;
    }
  },

  /**
   * Request password reset email
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    try {
      const response = await api.post<{ message: string }>('/auth/forgot-password', { email });
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        return {
          message:
            'If an account exists for this email, a password reset link has been sent. (Dev fallback token: mock-token-123)',
        };
      }
      throw err;
    }
  },

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
    try {
      const response = await api.post<{ message: string }>('/auth/reset-password', data);
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        return {
          message: 'Password reset successfully (Dev fallback simulation)',
        };
      }
      throw err;
    }
  },

  /**
   * Fetch current authenticated user info
   */
  async getProfile(): Promise<{
    user_id: number;
    email: string;
    username?: string;
    full_name?: string;
    role: string;
    message: string;
  }> {
    try {
      const response = await api.get<{
        user_id: number;
        email: string;
        username?: string;
        full_name?: string;
        role: string;
        message: string;
      }>('/auth-test/protected');
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        try {
          const profile = JSON.parse(localStorage.getItem('dev_mock_profile') || '{}');
          if (profile.email) {
            return {
              user_id: profile.user_id || 1,
              email: profile.email,
              username: profile.username,
              full_name: profile.full_name,
              role: profile.role || 'user',
              message: 'Dev fallback active',
            };
          }
        } catch {
          // ignore
        }
      }
      throw err;
    }
  },
};

export default authService;
