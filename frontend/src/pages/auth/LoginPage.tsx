import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { loginSchema, type LoginFormData } from '@/utils/validators';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/useAuthStore';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuth, setLoading } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);

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
        setLoading(false);
      } catch {
        localStorage.removeItem('auth_token');
        throw new Error('Unable to load your profile. Please try again.');
      }

      navigate('/', { replace: true });
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
    <div className="space-y-6 text-[#18181B]">
      <div className="text-center">
        <h3 className="text-2xl font-serif font-bold text-[#18181B] tracking-tight">Sign In</h3>
        <p className="text-xs text-[#71717A] mt-1">
          Enter your credentials to access your marketing workspace
        </p>
      </div>

      {serverError && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-3.5 flex items-start gap-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600 mt-0.5" />
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

        <div className="flex items-center justify-between text-xs pt-1">
          <label className="flex items-center gap-2 cursor-pointer text-[#71717A] hover:text-[#18181B]">
            <input
              type="checkbox"
              className="rounded bg-[#F3F3EE] border-[#E4E4DC] text-[#18181B] accent-[#18181B] focus:ring-[#18181B] w-4 h-4"
              {...register('rememberMe')}
            />
            <span>Remember me</span>
          </label>

          <Link
            to="/forgot-password"
            className="text-[#18181B] hover:underline font-semibold transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full mt-2"
          isLoading={isSubmitting}
          icon={<ArrowRight className="w-4 h-4 ml-1 order-last text-amber-400" />}
        >
          Sign In
        </Button>
      </form>

      <div className="border-t border-[#F2F2ED] pt-5 text-center text-xs text-[#71717A]">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="text-[#18181B] hover:underline font-bold">
          Create an account
        </Link>
      </div>
    </div>
  );
};

export default LoginPage;
