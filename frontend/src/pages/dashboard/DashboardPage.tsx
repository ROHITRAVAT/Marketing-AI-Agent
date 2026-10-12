import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Calendar,
  CheckCircle2,
  Clock,
  Plus,
  Rocket,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
  Target,
  Layers,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { campaignService } from '@/services/campaignService';
import { useChatStore } from '@/store/useChatStore';
import type { Campaign } from '@/types';

const getCampaignError = (error: unknown) => {
  const axiosError = error as { response?: { data?: { detail?: string; message?: string } }; code?: string };
  return (
    axiosError.response?.data?.detail ||
    axiosError.response?.data?.message ||
    (axiosError.code === 'ERR_NETWORK' || !axiosError.response
      ? 'Unable to connect to server. Please try again.'
      : 'Unable to load campaigns. Please try again.')
  );
};

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { sendMessage } = useChatStore();
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

  const handleQuickPrompt = (prompt: string) => {
    void sendMessage(prompt);
    navigate('/chat');
  };

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const activeCount = campaigns.filter((c) => c.status === 'active').length;
  const draftCount = campaigns.filter((c) => c.status === 'draft').length;
  const pausedCount = campaigns.filter((c) => c.status === 'paused').length;

  const stats = [
    {
      label: 'Total Campaigns',
      value: campaigns.length,
      change: '+3 new this month',
      trend: 'up',
      icon: Rocket,
      accent: 'from-amber-500/10 to-transparent text-amber-900 border-amber-200',
    },
    {
      label: 'Active Campaigns',
      value: activeCount,
      change: `${activeCount} live in market`,
      trend: 'neutral',
      icon: CheckCircle2,
      accent: 'from-emerald-500/10 to-transparent text-emerald-900 border-emerald-200',
    },
    {
      label: 'Drafts In Review',
      value: draftCount,
      change: 'Human approval needed',
      trend: 'warning',
      icon: ShieldCheck,
      accent: 'from-orange-500/10 to-transparent text-orange-900 border-orange-200',
    },
    {
      label: 'Paused Campaigns',
      value: pausedCount,
      change: 'Ready to re-activate',
      trend: 'neutral',
      icon: Clock,
      accent: 'from-blue-500/10 to-transparent text-blue-900 border-blue-200',
    },
  ];

  const quickActions = [
    {
      title: 'Omni-Channel Launch',
      description: 'Formulate an end-to-end multi-platform marketing sprint with AI.',
      prompt: 'Formulate a 4-week omni-channel launch strategy for our new product, including LinkedIn, Twitter/X, and Email sequences.',
      icon: Rocket,
      badge: 'Strategy',
      gradient: 'hover:border-amber-400/80',
    },
    {
      title: 'Viral Social Hooks',
      description: 'Generate high-converting headlines and scroll-stopping hooks.',
      prompt: 'Generate 10 viral hooks and persuasive copy angles for LinkedIn and Twitter/X with high engagement formulas.',
      icon: Zap,
      badge: 'Creative',
      gradient: 'hover:border-indigo-400/80',
    },
    {
      title: 'Audience Personas',
      description: 'Extract ICP traits, pain points, and objections for targeted messaging.',
      prompt: 'Identify top 3 ideal customer personas (ICPs) for our B2B SaaS, their core pain points, and recommended messaging angles.',
      icon: Target,
      badge: 'Audience',
      gradient: 'hover:border-emerald-400/80',
    },
    {
      title: 'Campaign Copy Audit',
      description: 'Evaluate existing copy against high-converting marketing benchmarks.',
      prompt: 'Audit our current marketing messaging and suggest 3 high-impact optimization experiments to boost conversion rates.',
      icon: Sparkles,
      badge: 'Optimization',
      gradient: 'hover:border-rose-400/80',
    },
  ];

  const recentCampaigns = [...campaigns]
    .sort((left, right) => right.updated_at.localeCompare(left.updated_at))
    .slice(0, 4);

  return (
    <div className="space-y-8 text-[#18181B] pb-12">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-br from-white via-[#FAF9F5] to-[#F5F4EE] border border-[#E8E8E3] rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-72 h-72 bg-gradient-to-br from-amber-200/30 to-orange-200/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            {/* System Status Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold shadow-2xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                AI Agent Engine Active
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
                <ShieldCheck className="w-3 h-3 text-amber-600" />
                Human-in-the-Loop Safeguards
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono text-[#71717A] bg-white border border-[#E4E4DC]">
                Qwen3:8B · Qdrant RAG
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">
              {getTimeGreeting()},{' '}
              <span className="italic font-normal">
                {user?.full_name?.split(' ')[0] || user?.username || 'Marketer'}
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-[#71717A] leading-relaxed">
              Orchestrate autonomous multi-channel marketing, draft high-performing copy, and review AI recommendations with strict human oversight.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3">
            <Link
              to="/chat"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-2xl shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Rocket className="w-4 h-4 text-amber-400" />
              Open AI Copilot
            </Link>
            <Link
              to="/campaigns"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-white hover:bg-[#F3F3EE] border border-[#E4E4DC] text-xs font-semibold rounded-2xl shadow-xs transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Plus className="w-4 h-4 text-[#18181B]" />
              New Campaign
            </Link>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl bg-rose-50 border border-rose-200 p-4 flex items-start gap-3 text-rose-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, change, icon: Icon, accent }) => (
          <div
            key={label}
            className={`bg-white border ${accent} rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4 hover:shadow-md transition-shadow relative overflow-hidden`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">{label}</span>
              <div className="w-9 h-9 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div>
              <span className="text-3xl sm:text-4xl font-bold tracking-tight text-[#18181B]">
                {isLoading ? '...' : value}
              </span>
            </div>
            <div className="pt-2.5 border-t border-[#F2F2ED] flex items-center justify-between text-[11px] text-[#71717A]">
              <span>{change}</span>
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
            </div>
          </div>
        ))}
      </div>

      {/* Quick AI Action Hub - Direct 1-Click Launchers */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            <h2 className="text-base font-bold tracking-tight text-[#18181B]">AI Copilot Quick Launchers</h2>
          </div>
          <span className="text-xs text-[#71717A]">1-click prompt dispatch</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map(({ title, description, prompt, icon: Icon, badge, gradient }) => (
            <button
              key={title}
              onClick={() => handleQuickPrompt(prompt)}
              className={`bg-white border border-[#E8E8E3] rounded-2xl p-5 text-left flex flex-col justify-between space-y-3 shadow-xs hover:shadow-md transition-all group ${gradient}`}
            >
              <div className="flex items-center justify-between w-full">
                <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B] group-hover:bg-[#18181B] group-hover:text-white transition-colors">
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-[#F3F3EE] text-[#52525B] font-semibold">
                  {badge}
                </span>
              </div>
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-[#18181B] group-hover:text-amber-600 transition-colors">
                  {title}
                </h3>
                <p className="text-[11px] text-[#71717A] line-clamp-2 leading-relaxed">
                  {description}
                </p>
              </div>
              <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between w-full text-[11px] font-semibold text-[#18181B]">
                <span>Launch in Copilot</span>
                <ChevronRight className="w-3.5 h-3.5 text-[#A1A1AA] group-hover:translate-x-1 group-hover:text-[#18181B] transition-transform" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Split: Campaigns and Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left Column: Recent Campaigns List (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
              <h2 className="text-base font-bold tracking-tight">Active & Recent Campaigns</h2>
            </div>
            <Link to="/campaigns" className="text-xs font-semibold flex items-center gap-1 hover:underline">
              Manage All ({campaigns.length}) <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {isLoading ? (
            <div className="bg-white border border-[#E8E8E3] rounded-2xl p-8 text-center text-sm text-[#71717A]">
              Loading campaigns...
            </div>
          ) : recentCampaigns.length === 0 ? (
            <div className="bg-white border border-[#E8E8E3] rounded-2xl p-8 text-center space-y-3 shadow-xs">
              <Layers className="w-10 h-10 text-[#A1A1AA] mx-auto" />
              <h3 className="text-sm font-bold text-[#18181B]">No campaigns created yet</h3>
              <p className="text-xs text-[#71717A] max-w-sm mx-auto">
                Create your first autonomous campaign to start planning copy and targeting channels.
              </p>
              <Link
                to="/campaigns"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#18181B] text-white text-xs font-semibold rounded-xl"
              >
                <Plus className="w-3.5 h-3.5 text-amber-400" />
                Create Campaign
              </Link>
            </div>
          ) : (
            <div className="space-y-3.5">
              {recentCampaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs space-y-3.5 hover:border-[#18181B]/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded-full font-semibold ${
                            campaign.status === 'active'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : campaign.status === 'paused'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-stone-100 text-stone-700 border border-stone-200'
                          }`}
                        >
                          {campaign.status}
                        </span>
                        <span className="text-[11px] text-[#A1A1AA] font-mono">ID #{campaign.id}</span>
                      </div>
                      <h3 className="text-sm font-bold text-[#18181B]">{campaign.name}</h3>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() =>
                          handleQuickPrompt(
                            `Review strategy and generate new social copy for campaign "${campaign.name}" (ID #${campaign.id}).`
                          )
                        }
                        title="Draft with Copilot"
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-[#F3F3EE] hover:bg-[#18181B] hover:text-white text-[#18181B] rounded-lg text-[11px] font-semibold transition-colors"
                      >
                        <Sparkles className="w-3 h-3 text-amber-500" />
                        AI Copy
                      </button>
                    </div>
                  </div>

                  {campaign.description && (
                    <p className="text-xs text-[#71717A] line-clamp-2 leading-relaxed">
                      {campaign.description}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[#71717A] pt-3 border-t border-[#F2F2ED]">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1 text-[11px]">
                        <Calendar className="w-3 h-3 text-[#A1A1AA]" />
                        {new Date(campaign.updated_at).toLocaleDateString()}
                      </span>
                      {campaign.target_audience && (
                        <span className="text-[11px] font-mono text-[#52525B]">
                          Audience: {campaign.target_audience}
                        </span>
                      )}
                    </div>

                    <Link
                      to="/campaigns"
                      className="text-[11px] font-semibold text-[#18181B] hover:underline flex items-center gap-0.5"
                    >
                      View Details <ExternalLink className="w-3 h-3 text-[#71717A]" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: AI Insights & Governance (1 col) */}
        <div className="space-y-6">
          {/* AI Strategic Recommendations Card */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 inline-block" />
              <h2 className="text-base font-bold tracking-tight">AI Strategic Insights</h2>
            </div>

            <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 space-y-4 shadow-xs">
              <div className="space-y-3">
                <div className="p-3 bg-[#FAF9F5] rounded-xl border border-[#EFEFEA] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-amber-700 font-bold tracking-wider">
                    Timing Optimization
                  </span>
                  <p className="text-xs text-[#52525B] leading-relaxed">
                    B2B LinkedIn decision-makers show 38% higher engagement on Tuesday and Thursday mornings (9:00 - 11:00 AM).
                  </p>
                </div>

                <div className="p-3 bg-[#FAF9F5] rounded-xl border border-[#EFEFEA] space-y-1">
                  <span className="text-[10px] font-mono uppercase text-indigo-700 font-bold tracking-wider">
                    Copy Hook Angle
                  </span>
                  <p className="text-xs text-[#52525B] leading-relaxed">
                    Problem-first hooks (&ldquo;Why 70% of teams struggle with...&rdquo;) generate 2.4x more comments than direct promotional links.
                  </p>
                </div>
              </div>

              <button
                onClick={() =>
                  handleQuickPrompt('Suggest 3 strategic optimization experiments for our current active marketing campaigns.')
                }
                className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 bg-[#F3F3EE] hover:bg-[#E8E8E3] text-[#18181B] text-xs font-semibold rounded-xl transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                Ask Copilot For Custom Insights
              </button>
            </div>
          </div>

          {/* Human-In-The-Loop Governance */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              <h2 className="text-base font-bold tracking-tight">Governance & Safety</h2>
            </div>

            <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 space-y-3 shadow-xs">
              <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Human Approval Guardrails Active
              </div>
              <p className="text-xs text-[#71717A] leading-relaxed">
                Autonomous agents operate in draft mode by default. All copy, external post triggers, and budget allocations require your manual verification before dispatch.
              </p>
              <div className="pt-2 border-t border-[#F2F2ED]">
                <Link
                  to="/chat"
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#18181B] hover:underline"
                >
                  Review Approvals in Copilot <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;