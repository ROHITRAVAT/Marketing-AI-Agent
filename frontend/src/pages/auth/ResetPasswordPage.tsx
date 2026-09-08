import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, KeyRound, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';
import { resetPasswordSchema, type ResetPasswordFormData } from '@/utils/validators';
import { authService } from '@/services/authService';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const tokenParam = searchParams.get('token') || '';

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      token: tokenParam,
      new_password: '',
      confirmPassword: '',
    },
  });

  useEffect(() => {
    if (tokenParam) {
      setValue('token', tokenParam);
    }
  }, [tokenParam, setValue]);

  const onSubmit = async (data: ResetPasswordFormData) => {
    setServerError(null);
    try {
      await authService.resetPassword({
        token: data.token,
        new_password: data.new_password,
      });

      setIsSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(
          axiosErr.response?.data?.detail || 'Invalid or expired reset token. Please try again.'
        );
      } else {
        setServerError('Unable to connect to the server.');
      }
    }
  };

  if (isSuccess) {
    return (
      <div className="text-center py-6 space-y-4">
        <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-white">Password Reset Successful!</h3>
        <p className="text-sm text-slate-400">
          Your password has been updated. Redirecting to login page...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-white tracking-tight">Set New Password</h3>
        <p className="text-sm text-slate-400 mt-1">
          Enter your security reset token and new password
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
          label="Reset Token"
          type="text"
          placeholder="Paste your reset token"
          icon={<KeyRound className="w-4 h-4" />}
          error={errors.token?.message}
          {...register('token')}
        />

        <Input
          label="New Password"
          type="password"
          placeholder="Min. 8 characters"
          icon={<Lock className="w-4 h-4" />}
          error={errors.new_password?.message}
          {...register('new_password')}
        />

        <Input
          label="Confirm New Password"
          type="password"
          placeholder="Re-enter new password"
          icon={<Lock className="w-4 h-4" />}
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />

        <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
          Update Password
        </Button>
      </form>

      <div className="border-t border-slate-800 pt-5 text-center text-sm text-slate-400">
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to login
        </Link>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
