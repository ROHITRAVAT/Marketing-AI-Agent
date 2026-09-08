import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Home } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-slate-100">
      <AlertCircle className="w-16 h-16 text-rose-500 mb-4" />
      <h1 className="text-4xl font-extrabold text-white mb-2">404</h1>
      <p className="text-lg text-slate-400 mb-6">Page not found</p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors text-sm font-medium"
      >
        <Home className="w-4 h-4" />
        Return Home
      </Link>
    </div>
  );
};

export default NotFoundPage;
