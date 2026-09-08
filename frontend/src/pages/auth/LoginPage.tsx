import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Mail, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { loginSchema, type LoginFormData } from '@/utils/validators';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/useAuthStore';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      // 1. Authenticate and obtain JWT
      const tokenResponse = await authService.login({
        email: data.email,
        password: data.password,
      });

      // Temporarily store token for protected requests
      localStorage.setItem('auth_token', tokenResponse.access_token);

      // 2. Fetch authenticated user profile
      try {
        const profile = await authService.getProfile();
        setAuth(
          {
            id: profile.user_id,
            email: profile.email,
            username: profile.username,
            full_name: profile.full_name,
            role: (profile.role as 'admin' | 'manager' | 'user') || 'user',
            is_active: true,
            is_verified: true,
          },
          tokenResponse.access_token
        );
      } catch {
        // Fallback user object if profile endpoint isn't fully populated
        setAuth(
          {
            id: 1,
            email: data.email,
            username: data.email.split('@')[0],
            role: 'user',
            is_active: true,
            is_verified: true,
          },
          tokenResponse.access_token
        );
      }

      navigate(from, { replace: true });
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(axiosErr.response?.data?.detail || 'Invalid email or password.');
      } else {
        setServerError('Unable to connect to the authentication server.');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-white tracking-tight">Sign In</h3>
        <p className="text-sm text-slate-400 mt-1">
          Enter your credentials to access your marketing workspace
        </p>
      </div>

      {serverError && (
        <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 p-3.5 flex items-start gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400 mt-0.5" />
          <span>{serverError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Email Address"
          type="email"
          placeholder="name@company.com"
          icon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          {...register('email')}
        />

        <div className="space-y-1">
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            icon={<Lock className="w-4 h-4" />}
            error={errors.password?.message}
            {...register('password')}
          />
        </div>

        <div className="flex items-center justify-between text-xs sm:text-sm pt-1">
          <label className="flex items-center gap-2 cursor-pointer text-slate-400 hover:text-slate-300">
            <input
              type="checkbox"
              className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
              {...register('rememberMe')}
            />
            <span>Remember me</span>
          </label>

          <Link
            to="/forgot-password"
            className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full mt-2"
          isLoading={isSubmitting}
          icon={<ArrowRight className="w-4 h-4 ml-1 order-last" />}
        >
          Sign In
        </Button>
      </form>

      <div className="border-t border-slate-800 pt-5 text-center text-sm text-slate-400">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-semibold">
          Create an account
        </Link>
      </div>
    </div>
  );
};

export default LoginPage;
