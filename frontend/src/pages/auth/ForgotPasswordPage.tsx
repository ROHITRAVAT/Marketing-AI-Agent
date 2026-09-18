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
    <div className="space-y-6 text-[#18181B]">
      <div className="text-center">
        <h3 className="text-2xl font-serif font-bold text-[#18181B] tracking-tight">Forgot Password</h3>
        <p className="text-xs text-[#71717A] mt-1">
          Enter your email and we&apos;ll send instructions to reset your password.
        </p>
      </div>

      {serverError && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-3.5 flex items-start gap-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600 mt-0.5" />
          <span>{serverError}</span>
        </div>
      )}

      {successMessage ? (
        <div className="space-y-4">
          <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4 flex items-start gap-3 text-emerald-800 text-xs font-medium shadow-xs">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600 mt-0.5" />
            <div>
              <p className="font-bold text-emerald-900">Reset Link Sent</p>
              <p className="mt-1 text-[#52525B] leading-relaxed">{successMessage}</p>
            </div>
          </div>

          <div className="text-center pt-2">
            <Link
              to="/reset-password"
              className="inline-flex items-center gap-1.5 text-xs text-[#18181B] hover:underline font-semibold"
            >
              <KeyRound className="w-3.5 h-3.5 text-amber-500" />
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

      <div className="border-t border-[#F2F2ED] pt-5 text-center text-xs text-[#71717A]">
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-[#71717A] hover:text-[#18181B] transition-colors font-semibold"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to login
        </Link>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
