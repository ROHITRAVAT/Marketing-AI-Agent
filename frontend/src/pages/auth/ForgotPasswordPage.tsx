import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { Mail, CheckCircle2, AlertCircle, ArrowLeft, KeyRound } from 'lucide-react';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/utils/validators';
import { authService } from '@/services/authService';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const ForgotPasswordPage: React.FC = () => {
  const [serverError, setServerError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setServerError(null);
    setSuccessMessage(null);
    try {
      const res = await authService.forgotPassword(data.email);
      setSuccessMessage(
        res.message || 'If an account exists for this email, a password reset link has been sent.'
      );
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(axiosErr.response?.data?.detail || 'Failed to request password reset.');
      } else {
        setServerError('Unable to connect to the server.');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-white tracking-tight">Forgot Password</h3>
        <p className="text-sm text-slate-400 mt-1">
          Enter your email and we&apos;ll send instructions to reset your password.
        </p>
      </div>

      {serverError && (
        <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 p-3.5 flex items-start gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400 mt-0.5" />
          <span>{serverError}</span>
        </div>
      )}

      {successMessage ? (
        <div className="space-y-4">
          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-4 flex items-start gap-3 text-emerald-300 text-sm">
            <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400 mt-0.5" />
            <div>
              <p className="font-semibold text-emerald-200">Reset Link Sent</p>
              <p className="mt-1 text-slate-300">{successMessage}</p>
            </div>
          </div>

          <div className="text-center pt-2">
            <Link
              to="/reset-password"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
            >
              <KeyRound className="w-3.5 h-3.5" />
              Already have a reset token? Click here to set a new password
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Account Email"
            type="email"
            placeholder="name@company.com"
            icon={<Mail className="w-4 h-4" />}
            error={errors.email?.message}
            {...register('email')}
          />

          <Button type="submit" className="w-full mt-2" isLoading={isSubmitting}>
            Send Reset Instructions
          </Button>
        </form>
      )}

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

export default ForgotPasswordPage;
