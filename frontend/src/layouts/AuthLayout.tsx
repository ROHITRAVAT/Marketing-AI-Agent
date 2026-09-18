import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F8F8F6] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-[#18181B]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-[#18181B] text-white mb-4 shadow-sm">
          <Sparkles className="w-6 h-6 text-amber-400" />
        </div>
        <h2 className="text-3xl font-serif tracking-tight text-[#18181B]">
          Marketing AI Agent
        </h2>
        <p className="mt-1.5 text-xs text-[#71717A]">
          Autonomous AI marketing campaigns and analytics
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xs border border-[#E8E8E3] sm:rounded-2xl sm:px-10">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
