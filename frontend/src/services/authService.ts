import api from './api';
import type {
  User,
  UserLoginRequest,
  UserRegisterRequest,
  TokenResponse,
  ResetPasswordRequest,
} from '@/types';

export const authService = {
  /**
   * Register a new user
   */
  async register(data: UserRegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login user and obtain access token
   */
  async login(data: UserLoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  /**
   * Request password reset email
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/forgot-password', { email });
    return response.data;
  },

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/reset-password', data);
    return response.data;
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
    const response = await api.get<{
      user_id: number;
      email: string;
      username?: string;
      full_name?: string;
      role: string;
      message: string;
    }>('/auth-test/protected');
    return response.data;
  },
};

export default authService;
