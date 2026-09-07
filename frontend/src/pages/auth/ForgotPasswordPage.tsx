import React from 'react';
import { Link } from 'react-router-dom';

export const ForgotPasswordPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white text-center">Reset Your Password</h3>
        <p className="text-sm text-slate-400 text-center mt-1">
          Enter your email to receive a password reset link.
        </p>
      </div>

      <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center text-slate-400">
        <p className="text-sm">Password reset form placeholder (Ready for Task 2)</p>
      </div>

      <div className="text-center text-sm text-slate-400">
        Remember your password?{' '}
        <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
          Back to login
        </Link>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
