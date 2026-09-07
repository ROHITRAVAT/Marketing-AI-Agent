import React from 'react';
import { Link } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white text-center">Sign In to Your Account</h3>
        <p className="text-sm text-slate-400 text-center mt-1">
          Welcome back! Please enter your details.
        </p>
      </div>

      <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center text-slate-400">
        <p className="text-sm">Login form placeholder (Ready for Task 2: Authentication Pages)</p>
      </div>

      <div className="text-center text-sm text-slate-400">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-medium">
          Sign up
        </Link>
      </div>
    </div>
  );
};

export default LoginPage;
