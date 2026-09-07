import React from 'react';
import { Megaphone, MessageSquare, TrendingUp, Sparkles } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Marketing Dashboard</h2>
          <p className="text-sm text-slate-400">
            Overview of your campaigns, AI suggestions, and marketing performance.
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-indigo-600/20">
          <Sparkles className="w-4 h-4" />
          Ask Marketing Agent
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Active Campaigns</span>
            <Megaphone className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-3 text-3xl font-bold text-white">0</div>
          <p className="text-xs text-slate-500 mt-1">Ready to create your first campaign</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">AI Interactions</span>
            <MessageSquare className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-3 text-3xl font-bold text-white">0</div>
          <p className="text-xs text-slate-500 mt-1">LangGraph Agent connected</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Average Engagement</span>
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 text-3xl font-bold text-white">0%</div>
          <p className="text-xs text-slate-500 mt-1">Tracked across social channels</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
