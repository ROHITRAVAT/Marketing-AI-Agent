import React from 'react';
import { Link } from 'react-router-dom';

export const RegisterPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white text-center">Create Your Account</h3>
        <p className="text-sm text-slate-400 text-center mt-1">
          Start generating and automating your marketing with AI.
        </p>
      </div>

      <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center text-slate-400">
        <p className="text-sm">Register form placeholder (Ready for Task 2: Authentication Pages)</p>
      </div>

      <div className="text-center text-sm text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
          Sign in
        </Link>
      </div>
    </div>
  );
};

export default RegisterPage;
