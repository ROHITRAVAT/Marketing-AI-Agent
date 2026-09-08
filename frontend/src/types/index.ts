export type UserRole = 'admin' | 'manager' | 'user';

export interface User {
  id: number;
  email: string;
  username?: string | null;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  is_superuser?: boolean;
  is_verified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserRegisterRequest {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface Campaign {
  id: number;
  user_id: number;
  name: string;
  description?: string | null;
  status: 'draft' | 'active' | 'paused' | 'completed';
  target_audience?: string | null;
  budget?: number | null;
  start_date?: string | null;
  end_date?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  metadata?: Record<string, unknown>;
}

export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  success?: boolean;
}
