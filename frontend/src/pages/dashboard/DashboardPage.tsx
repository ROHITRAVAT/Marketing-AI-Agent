import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Rocket,
  AlertCircle,
  Target,
  Box,
  Clock,
  Zap,
  Sparkles,
  ArrowRight,
  Plus,
  Compass,
  ShieldCheck,
  Calendar,
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { campaignService } from '@/services/campaignService';
import type { Campaign } from '@/types';

const getCampaignError = (error: unknown) => {
  const axiosError = error as { response?: { data?: { detail?: string } }; code?: string };
  if (axiosError.response?.data?.detail) return axiosError.response.data.detail;
  if (axiosError.code === 'ERR_NETWORK' || !axiosError.response) {
    return 'Unable to connect to server. Please try again.';
  }
  return 'Unable to load campaigns. Please try again.';
};

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadCampaigns = async () => {
      try {
        const response = await campaignService.listCampaigns({ size: 50 });
        if (isMounted) setCampaigns(response.items);
      } catch (loadError) {
        if (isMounted) setError(getCampaignError(loadError));
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    void loadCampaigns();
    return () => {
      isMounted = false;
    };
  }, []);

  const activeCampaigns = campaigns.filter((c) => c.status === 'active');
  const draftCampaigns = campaigns.filter((c) => c.status === 'draft');
  const pausedCampaigns = campaigns.filter((c) => c.status === 'paused');
  const totalBudget = campaigns.reduce((acc, c) => acc + (c.budget || 0), 0);

  return (
    <div className="space-y-8 text-[#18181B]">
      {/* 1. Top Hero Section - Truthful Human-in-the-Loop Framing */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-2">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block" />
            <span>Human-in-the-Loop Safeguard</span>
            <span className="text-amber-400">·</span>
            <span className="text-[#71717A] font-normal">Approval Required Before Publishing</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">
            Welcome back, {user?.full_name?.split(' ')[0] || user?.username || 'Marketer'} 👋
          </h1>
          <p className="text-sm text-[#71717A] max-w-xl">
            Your AI assistant prepares copy, target audiences, and strategy suggestions. Every campaign action requires your review and sign-off.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 self-start md:self-center">
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-xl shadow-sm transition-all"
          >
            <Rocket className="w-3.5 h-3.5 text-amber-400" />
            Open AI Copilot
          </Link>
          <Link
            to="/campaigns"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold rounded-xl shadow-xs transition-all"
          >
            <Plus className="w-3.5 h-3.5 text-[#71717A]" />
            New Campaign
          </Link>
        </div>
      </div>

      {/* 2. Top 4 KPI Stat Cards - Wired to Real Store Data */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Campaigns (Real Data) */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Active Campaigns
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <Rocket className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">
              {isLoading ? '...' : activeCampaigns.length}
            </span>
            <span className="text-xs text-[#A1A1AA] font-mono">/ {campaigns.length} total</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center gap-2">
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
              {pausedCampaigns.length} paused
            </span>
            <span className="text-[11px] text-[#71717A]">Real store data</span>
          </div>
        </div>

        {/* Card 2: Total Budget Allocated (Real Data) */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Allocated Budget
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <Target className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">
              {isLoading ? '...' : `$${totalBudget.toLocaleString()}`}
            </span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between">
            <span className="text-[11px] text-[#71717A]">
              Across {campaigns.length} campaigns
            </span>
            <span className="text-[10px] font-mono uppercase bg-[#F3F3EE] px-1.5 py-0.5 rounded text-[#52525B]">
              Managed
            </span>
          </div>
        </div>

        {/* Card 3: Pending Human Reviews (Truthful Workflow Metric) */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Drafts Awaiting Review
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-amber-700">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">
              {isLoading ? '...' : draftCampaigns.length}
            </span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between text-[11px]">
            <span className="font-semibold text-amber-800 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
              Requires Sign-Off
            </span>
            <span className="text-[#71717A]">Zero auto-publish</span>
          </div>
        </div>

        {/* Card 4: AI Model Status */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              AI Model Engine
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <Box className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-[#18181B] font-mono">qwen3:8b</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 text-[10px] font-mono uppercase font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
              Configured Model
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-4 flex items-start gap-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* 3. Middle Section: AI Strategy Suggestions & Drafts (Left 2/3) + Benchmarks (Right 1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {import.meta.env.DEV && import.meta.env.VITE_SHOW_EXAMPLE_DASHBOARD === 'true' && (
        <>
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
              <h2 className="text-base font-bold text-[#18181B] tracking-tight">
                AI Strategy Suggestions &amp; Drafts
              </h2>
            </div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded font-semibold">
              Awaiting Review &amp; Approval ✍️
            </span>
          </div>

          <div className="space-y-3.5">
            {/* Recommendation 1: LinkedIn Window */}
            <div className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-5 shadow-xs transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B] shrink-0 mt-0.5">
                  <Clock className="w-4 h-4" />
                </div>
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#52525B] font-semibold">
                      LinkedIn Scheduling Draft
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
                      Draft Proposal
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Suggested LinkedIn Posting Window
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    Suggested engagement window for B2B executives: <strong className="text-[#18181B]">Tuesday at 9:15 AM EST</strong>. Launch AI Copilot to review and approve copy before scheduling.
                  </p>
                </div>
              </div>

              <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
                <Link
                  to="/chat"
                  className="w-full text-center px-3.5 py-1.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-xl transition-colors shadow-xs"
                >
                  Review in Copilot
                </Link>
              </div>
            </div>

            {/* Recommendation 2: Viral Hooks for Launch */}
            <div className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-5 shadow-xs transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 shrink-0 mt-0.5">
                  <Zap className="w-4 h-4" />
                </div>
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-100/70 text-amber-800 font-semibold">
                      Generative Copy
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#71717A]">
                      Requires Human Edit
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Hooks for Q4 Product Launch Draft Ready
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    5 high-converting hook variations prepared by qwen3:8b. Ready for team edits and approval in the AI chat workspace.
                  </p>
                </div>
              </div>

              <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
                <Link
                  to="/chat"
                  className="w-full text-center px-3.5 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold rounded-xl transition-colors shadow-xs"
                >
                  Edit in Chat
                </Link>
              </div>
            </div>

            {/* Recommendation 3: Trend Observation */}
            <div className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-5 shadow-xs transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shrink-0 mt-0.5">
                  <Compass className="w-4 h-4" />
                </div>
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#52525B] font-semibold">
                      Market Intelligence (Example)
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Industry Trend Analysis Template
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    Sentiment shift analysis prepared for executive review. Ask your AI Copilot to ground it with your company knowledge base via Qdrant RAG.
                  </p>
                </div>
              </div>

              <div className="shrink-0 self-end sm:self-center">
                <Link
                  to="/chat"
                  className="px-3.5 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold rounded-xl transition-colors inline-block shadow-xs"
                >
                  Ask AI Copilot
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Weekly Benchmarks (Clearly Labeled as Example Reference) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#18181B] tracking-tight">
              Weekly Benchmarks
            </h2>
            <span className="text-[10px] font-mono uppercase text-[#71717A] bg-[#F3F3EE] px-1.5 py-0.5 rounded border border-[#E4E4DC]">
              Example Reference
            </span>
          </div>

          <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 space-y-6 shadow-xs">
            {/* Benchmark metric 1 */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#18181B] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#18181B] inline-block" />
                  Target LinkedIn Delivery
                </span>
                <span className="font-bold text-[#18181B]">86%</span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                <div className="bg-[#18181B] h-2 rounded-full" style={{ width: '86%' }} />
              </div>
              <div className="flex justify-between text-[10px] text-[#A1A1AA] font-mono">
                <span>Target Pace: 15,400</span>
                <span>Goal: 20,000</span>
              </div>
            </div>

            {/* Benchmark metric 2 */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#18181B] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
                  Target X Impressions
                </span>
                <span className="font-bold text-[#18181B]">85%</span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                <div className="bg-amber-600 h-2 rounded-full" style={{ width: '85%' }} />
              </div>
              <div className="flex justify-between text-[10px] text-[#A1A1AA] font-mono">
                <span>Target Pace: 42,000</span>
                <span>Goal: 50,000</span>
              </div>
            </div>

            {/* Benchmark metric 3 */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#18181B] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                  Email Newsletter Open Rate
                </span>
                <span className="font-bold text-emerald-700">42.8%</span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                <div className="bg-emerald-600 h-2 rounded-full" style={{ width: '42.8%' }} />
              </div>
              <div className="flex justify-between text-[10px] text-[#A1A1AA] font-mono">
                <span>Industry Avg: 22.0%</span>
                <span>Benchmark Goal: 40%+</span>
              </div>
            </div>

            {/* Human Oversight Box - Replaces fake automated adjustment claims */}
            <div className="rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] p-4 space-y-1.5">
              <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-[#71717A]">
                <span className="text-amber-800 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block" />
                  Human Oversight Active
                </span>
                <span>Guardrail</span>
              </div>
              <p className="text-xs text-[#52525B] leading-relaxed">
                The agent proposes draft copy and campaign schedules. All external API dispatching requires explicit manual user approval.
              </p>
            </div>
          </div>
        </div>
        </>
        )}
      </div>

      {/* 4. Bottom Section: Real Managed Campaigns (Wired to useCampaignStore) */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base">📋</span>
            <h2 className="text-base font-bold text-[#18181B] tracking-tight">
              Managed Campaigns ({campaigns.length})
            </h2>
          </div>
          <Link
            to="/campaigns"
            className="text-xs font-semibold text-[#18181B] hover:text-indigo-600 flex items-center gap-1"
          >
            Manage All Campaigns <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {campaigns.length === 0 ? (
          <div className="bg-white border border-[#E8E8E3] rounded-2xl p-8 text-center space-y-3 shadow-xs">
            <p className="text-sm text-[#71717A]">No campaigns created yet.</p>
            <Link
              to="/campaigns"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#18181B] text-white text-xs font-semibold rounded-xl"
            >
              <Plus className="w-3.5 h-3.5 text-amber-400" />
              Create Your First Campaign
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {campaigns.slice(0, 4).map((c) => (
              <div
                key={c.id}
                className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-6 shadow-xs space-y-4 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-semibold flex items-center gap-1 ${
                          c.status === 'active'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : c.status === 'paused'
                            ? 'bg-amber-50 text-amber-800 border border-amber-200'
                            : 'bg-[#F3F3EE] text-[#71717A] border border-[#E4E4DC]'
                        }`}
                      >
                        {c.status === 'active' && (
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                        )}
                        {c.status}
                      </span>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#71717A]">
                        ID: #{c.id}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-[#18181B]">{c.name}</h3>
                  </div>

                  <div className="w-10 h-10 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B] shrink-0">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                  </div>
                </div>

                {c.description && (
                  <p className="text-xs text-[#71717A] line-clamp-2 leading-relaxed">
                    {c.description}
                  </p>
                )}

                {/* Target Audience & Channels */}
                <div className="grid grid-cols-2 gap-4 py-2 border-y border-[#F2F2ED] text-xs">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                      Target Audience
                    </span>
                    <span className="font-semibold text-[#18181B] truncate block">
                      {c.target_audience || 'General'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                      Channels
                    </span>
                    <div className="flex flex-wrap gap-1">
                      <span className="text-[#71717A]">Not provided</span>
                    </div>
                  </div>
                </div>

                {/* Budget & Schedule */}
                <div className="flex items-center justify-between text-xs pt-1">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block">
                      Allocated Budget
                    </span>
                    <span className="font-bold text-[#18181B]">
                      ${c.budget ? c.budget.toLocaleString() : '0'}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block">
                      Schedule
                    </span>
                    <span className="font-medium text-[#52525B] flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-[#A1A1AA]" />
                      {c.start_date || 'Ongoing'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
