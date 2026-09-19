import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { registerSchema, type RegisterFormData } from '@/utils/validators';
import { authService } from '@/services/authService';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    try {
      await authService.register({
        email: data.email,
        password: data.password,
        username: data.username,
        full_name: data.full_name,
      });

      setIsSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string; message?: string } } };
        setServerError(axiosErr.response?.data?.detail || axiosErr.response?.data?.message || 'Failed to register account.');
      } else {
        setServerError('Unable to connect to the server.');
      }
    }
  };

  if (isSuccess) {
    return (
      <div className="text-center py-6 space-y-4 text-[#18181B]">
        <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center mx-auto shadow-xs">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-serif font-bold text-[#18181B]">Registration Successful!</h3>
        <p className="text-xs text-[#71717A]">
          Your account has been created. Redirecting to login page...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-[#18181B]">
      <div className="text-center">
        <h3 className="text-2xl font-serif font-bold text-[#18181B] tracking-tight">Create Account</h3>
        <p className="text-xs text-[#71717A] mt-1">
          Join to automate and supercharge your marketing campaigns
        </p>
      </div>

      {serverError && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-3.5 flex items-start gap-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600 mt-0.5" />
          <span>{serverError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3.5">
        <Input
          label="Full Name"
          type="text"
          placeholder="Jane Doe"
          icon={<User className="w-4 h-4" />}
          error={errors.full_name?.message}
          {...register('full_name')}
        />

        <Input
          label="Username"
          type="text"
          placeholder="janedoe"
          icon={<User className="w-4 h-4" />}
          error={errors.username?.message}
          {...register('username')}
        />

        <Input
          label="Email Address"
          type="email"
          placeholder="jane@company.com"
          icon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          {...register('email')}
        />

        <Input
          label="Password"
          type="password"
          placeholder="Min. 8 characters"
          icon={<Lock className="w-4 h-4" />}
          error={errors.password?.message}
          {...register('password')}
        />

        <Input
          label="Confirm Password"
          type="password"
          placeholder="Re-enter password"
          icon={<Lock className="w-4 h-4" />}
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />

        <Button
          type="submit"
          className="w-full mt-4"
          isLoading={isSubmitting}
          icon={<ArrowRight className="w-4 h-4 ml-1 order-last text-amber-400" />}
        >
          Create Account
        </Button>
      </form>

      <div className="border-t border-[#F2F2ED] pt-5 text-center text-xs text-[#71717A]">
        Already have an account?{' '}
        <Link to="/login" className="text-[#18181B] hover:underline font-bold">
          Sign in
        </Link>
      </div>
    </div>
  );
};

export default RegisterPage;
