import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Home } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F8F8F6] flex flex-col items-center justify-center p-4 text-[#18181B]">
      <AlertCircle className="w-12 h-12 text-[#18181B] mb-3" />
      <h1 className="text-4xl font-serif font-bold text-[#18181B] mb-2">404</h1>
      <p className="text-sm text-[#71717A] mb-6">Page not found</p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181B] hover:bg-[#27272A] text-white rounded-xl transition-all text-xs font-semibold shadow-xs"
      >
        <Home className="w-4 h-4 text-amber-400" />
        Return Home
      </Link>
    </div>
  );
};

export default NotFoundPage;
