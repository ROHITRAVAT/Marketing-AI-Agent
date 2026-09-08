import React from 'react';
import { Link } from 'react-router-dom';
import {
  Megaphone,
  TrendingUp,
  Sparkles,
  ArrowUpRight,
  Plus,
  Users,
  CheckCircle2,
  Clock,
  ArrowRight,
  BarChart2,
  Calendar,
  Layers,
} from 'lucide-react';
import { useCampaignStore } from '@/store/useCampaignStore';
import { useAuthStore } from '@/store/useAuthStore';

export const DashboardPage: React.FC = () => {
  const { campaigns } = useCampaignStore();
  const { user } = useAuthStore();

  const activeCount = campaigns.filter((c) => c.status === 'active').length;
  const scheduledCount = campaigns.filter((c) => c.status === 'draft' || c.status === 'paused').length;
  const totalReach = campaigns.reduce((acc, c) => acc + (c.reach || 0), 0);
  const avgEngagement =
    campaigns.length > 0
      ? (campaigns.reduce((acc, c) => acc + (c.engagement || 0), 0) / campaigns.length).toFixed(1)
      : '0.0';

  const aiSuggestions = [
    {
      id: 1,
      type: 'Optimization',
      title: 'Optimal LinkedIn Posting Window Identified',
      description: 'Your audience engagement peaks between 1:30 PM – 3:30 PM EST on Tuesdays & Thursdays.',
      action: 'Schedule Post',
      link: '/campaigns',
      badge: 'High Impact',
    },
    {
      id: 2,
      type: 'Content Idea',
      title: 'Generate Viral Hooks for Q4 AI Copilot',
      description: 'Competitor keyword analysis suggests adding 3 new carousel posts covering cost-efficiency.',
      action: 'Ask AI Agent',
      link: '/chat',
      badge: 'Recommended',
    },
    {
      id: 3,
      type: 'Audience Insight',
      title: 'High Tech-Decision Maker Density on Twitter/X',
      description: 'Impressions among SaaS founders grew +34% this week. Consider boosting B2B ad budget.',
      action: 'View Analytics',
      link: '/analytics',
      badge: 'Trend Alert',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 p-6 rounded-2xl border border-indigo-500/20 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Welcome back, {user?.username || user?.full_name || 'Marketer'} 👋
            </h2>
          </div>
          <p className="text-sm text-slate-300 max-w-xl">
            Your Marketing AI Agent is active. 2 campaigns are actively running and 3 optimization suggestions are ready for review.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl shadow-lg shadow-indigo-600/30 transition-all transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-4 h-4" />
            Launch AI Assistant
          </Link>
          <Link
            to="/campaigns"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium rounded-xl transition-all"
          >
            <Plus className="w-4 h-4" />
            New Campaign
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Active Campaigns
            </span>
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Megaphone className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{activeCount}</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +2 this month
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" /> {scheduledCount} drafts / paused
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Total Audience Reach
            </span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{totalReach.toLocaleString()}</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +18.4%
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Across LinkedIn, X, and Instagram</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Avg Engagement Rate
            </span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{avgEngagement}%</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +2.1%
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Industry avg benchmark: 2.8%</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              AI Content Generated
            </span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">42</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5" /> 100% QA reviewed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">Posts, hooks & email sequences</p>
        </div>
      </div>

      {/* Main Grid: AI Suggestions & Weekly Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* AI Recommendations Box (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h3 className="text-lg font-bold text-white">Autonomous AI Suggestions</h3>
            </div>
            <Link to="/chat" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
              Open Chat Agent <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {aiSuggestions.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900 border border-slate-800/90 hover:border-indigo-500/40 rounded-xl p-4 transition-all duration-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {item.badge}
                    </span>
                    <h4 className="text-sm font-semibold text-white">{item.title}</h4>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-xl">{item.description}</p>
                </div>
                <Link
                  to={item.link}
                  className="self-start sm:self-center shrink-0 px-3.5 py-1.5 bg-slate-800 hover:bg-indigo-600 hover:text-white text-slate-200 text-xs font-semibold rounded-lg transition-colors border border-slate-700"
                >
                  {item.action}
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Analytics Summary Box (1 Col) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">Weekly Performance</h3>
              </div>
              <span className="text-xs text-emerald-400 font-medium">+15.2% vs last wk</span>
            </div>

            {/* Custom Interactive SVG Chart */}
            <div className="space-y-3 pt-2">
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>LinkedIn Outreach</span>
                  <span className="text-white font-medium">68% goal</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2">
                  <div className="bg-indigo-500 h-2 rounded-full" style={{ width: '68%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Twitter/X Impressions</span>
                  <span className="text-white font-medium">84% goal</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '84%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Email Open Rate</span>
                  <span className="text-white font-medium">42.8%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '42.8%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <Link
              to="/analytics"
              className="flex items-center justify-between text-xs text-slate-400 hover:text-white transition-colors"
            >
              <span>Explore deep analytics & KPIs</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Campaigns Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Active & Recent Campaigns</h3>
          </div>
          <Link to="/campaigns" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
            View All Campaigns ({campaigns.length})
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campaigns.slice(0, 4).map((c) => (
            <div
              key={c.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors space-y-3"
            >
              <div className="flex items-center justify-between">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${
                    c.status === 'active'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : c.status === 'paused'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-slate-700/30 text-slate-400 border border-slate-700'
                  }`}
                >
                  {c.status}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Budget: ${c.budget ? c.budget.toLocaleString() : '0'}
                </span>
              </div>

              <div>
                <h4 className="text-base font-semibold text-white">{c.name}</h4>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {c.description || 'No description provided.'}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5">
                  {c.channels?.map((ch) => (
                    <span key={ch} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">
                      {ch}
                    </span>
                  ))}
                </div>
                <span>Reach: {c.reach?.toLocaleString() || 0}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
