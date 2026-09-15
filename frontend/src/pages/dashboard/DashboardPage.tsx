import React from 'react';
import { Link } from 'react-router-dom';
import {
  Rocket,
  Share2,
  Target,
  Box,
  Clock,
  Zap,
  Sparkles,
  ArrowRight,
  Plus,
  Compass,
  CheckCircle2,
  MoreVertical,
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="space-y-8 text-[#18181B]">
      {/* 1. Top Hero Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-2">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-ping" />
            <span className="font-semibold text-emerald-800">Autopilot Active</span>
            <span className="text-emerald-400">·</span>
            <span className="text-[#71717A]">Latency: 42ms</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">
            Welcome back, {user?.full_name?.split(' ')[0] || user?.username || 'Marketer'} 👋
          </h1>
          <p className="text-sm text-[#71717A] max-w-xl">
            Your autonomous agent has optimized <strong className="text-[#18181B] font-semibold">14 campaign parameters</strong> today across LinkedIn &amp; X.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 self-start md:self-center">
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-xl shadow-sm transition-all"
          >
            <Rocket className="w-3.5 h-3.5 text-amber-400" />
            Launch AI Assistant
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

      {/* 2. Top 4 KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Campaigns */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Active Campaigns
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#71717A]">
              <Rocket className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">2</span>
            <span className="text-xs text-[#A1A1AA] font-mono">/ 4 max alloc.</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center gap-2">
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
              ↗ +100%
            </span>
            <span className="text-[11px] text-[#71717A]">+2 this month</span>
          </div>
        </div>

        {/* Card 2: Audience Reach */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Audience Reach
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#71717A]">
              <Share2 className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">150,000+</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
                ↗ +18.4%
              </span>
              <span className="text-[11px] text-[#71717A]">vs last wk</span>
            </div>
            {/* Sparkline simulation */}
            <svg className="w-16 h-4 text-emerald-500" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M 0 12 Q 10 4, 20 8 T 40 2 T 60 0" />
            </svg>
          </div>
        </div>

        {/* Card 3: Avg Engagement Rate */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              Avg. Engagement Rate
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-emerald-600">
              <Target className="w-4 h-4" />
            </div>
          </div>
          <div>
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">5.8%</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between text-[11px]">
            <span className="font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
              +3.0% vs industry
            </span>
            <span className="text-[#71717A]">bm: 2.8%</span>
          </div>
        </div>

        {/* Card 4: AI Content Generated */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
              AI Content Generated
            </span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#71717A]">
              <Box className="w-4 h-4 text-[#18181B]" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">42</span>
            <span className="text-xs text-[#71717A]">assets</span>
          </div>
          <div className="pt-2 border-t border-[#F2F2ED] flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-800 bg-[#F3F3EE] border border-[#E4E4DC] px-2 py-0.5 rounded">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              100% QA Reviewed
            </span>
          </div>
        </div>
      </div>

      {/* 3. Middle Section: Autonomous AI Recommendations (Left 2/3) + Weekly Benchmarks (Right 1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left Column: Recommendations */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
              <h2 className="text-base font-bold text-[#18181B] tracking-tight">
                Autonomous AI Recommendations
              </h2>
            </div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
              Real-Time Stream ⚡
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
                      LinkedIn Insight
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                      +46% Surge Projected
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Optimal LinkedIn Posting Window Detected
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    AI detected a significant engagement surge on <strong className="text-[#18181B]">Tuesday at 9:15 AM EST</strong> for high-intent B2B executives. Scheduling high-priority product thought leadership now will capture peak feeds.
                  </p>
                </div>
              </div>

              <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
                <button className="w-full px-3.5 py-1.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-lg transition-colors">
                  Schedule Post
                </button>
                <button className="w-full px-3.5 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#71717A] border border-[#E4E4DC] text-xs font-medium rounded-lg transition-colors">
                  Dismiss
                </button>
              </div>
            </div>

            {/* Recommendation 2: Viral Hooks for Q4 */}
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
                      Competitor Intel Cross-Ref
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Viral Hooks for Q4 Product Launch Ready
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    5 high-converting hooks synthesized from top-performing competitor launches. Model suggests pairing with short-form technical architecture diagrams for maximum reach.
                  </p>
                  <p className="text-[11px] text-amber-700 font-medium flex items-center gap-1 pt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block" />
                    Est. Conversion uplift: +1.6%
                  </p>
                </div>
              </div>

              <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
                <Link
                  to="/chat"
                  className="w-full text-center px-3.5 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold rounded-lg transition-colors"
                >
                  Review in Chat
                </Link>
                <button className="w-full px-3.5 py-1.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-lg transition-colors">
                  Apply to Campaign
                </button>
              </div>
            </div>

            {/* Recommendation 3: Decision-Maker Sentiment on X */}
            <div className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-5 shadow-xs transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shrink-0 mt-0.5">
                  <Compass className="w-4 h-4" />
                </div>
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                      X Pulse Analysis
                    </span>
                    <span className="text-[10px] font-mono text-[#71717A]">
                      4,120 posts indexed
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-[#18181B]">
                    Decision-Maker Sentiment Shift on X
                  </h3>
                  <p className="text-xs text-[#71717A] leading-relaxed max-w-xl">
                    Real-time trend analysis highlights a <strong className="text-emerald-700">62% positive shift</strong> in AI operational automation discussions among CTOs and Engineering Directors over the past 48 hours.
                  </p>
                </div>
              </div>

              <div className="shrink-0 self-end sm:self-center">
                <Link
                  to="/chat"
                  className="px-3.5 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold rounded-lg transition-colors inline-block"
                >
                  Ask AI Agent
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Weekly Benchmarks */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-[#18181B] tracking-tight">
            Weekly Benchmarks
          </h2>

          <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 space-y-6 shadow-xs">
            {/* Progress metric 1 */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#18181B] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#18181B] inline-block" />
                  LinkedIn Impressions
                </span>
                <span className="font-bold text-[#18181B]">86%</span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                <div className="bg-[#18181B] h-2 rounded-full" style={{ width: '86%' }} />
              </div>
              <div className="flex justify-between text-[10px] text-[#A1A1AA] font-mono">
                <span>15,400 delivered</span>
                <span>Goal: 20,000</span>
              </div>
            </div>

            {/* Progress metric 2 */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#18181B] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
                  Twitter/X Impressions
                </span>
                <span className="font-bold text-[#18181B]">85%</span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                <div className="bg-amber-600 h-2 rounded-full" style={{ width: '85%' }} />
              </div>
              <div className="flex justify-between text-[10px] text-[#A1A1AA] font-mono">
                <span>42,000 delivered</span>
                <span>Goal: 50,000</span>
              </div>
            </div>

            {/* Progress metric 3 */}
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
                <span>Active: 42.8%</span>
                <span>Benchmark: 22.0%</span>
              </div>
            </div>

            {/* Agent Pacing Box */}
            <div className="rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] p-4 space-y-1.5">
              <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-[#71717A]">
                <span className="text-emerald-700 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                  Agent Pacing Active
                </span>
                <span>v2.4</span>
              </div>
              <p className="text-xs text-[#52525B] leading-relaxed">
                <strong className="text-[#18181B]">23 adjustments</strong> made today across bidding scheduler, budget reallocation, and prompt variations.
              </p>
            </div>

            {/* Token Inference Budget Box */}
            <div className="pt-2 border-t border-[#F2F2ED] flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <Box className="w-4 h-4 text-amber-600" />
                <div>
                  <span className="text-[10px] font-mono uppercase text-[#71717A] block">Inference Budget</span>
                  <span className="text-xs font-semibold text-[#18181B]">92,780 / 150k Tokens</span>
                </div>
              </div>
              <span className="font-bold text-[#18181B] font-mono">61.8%</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Bottom Section: Recent Autonomous Campaigns */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base">✨</span>
            <h2 className="text-base font-bold text-[#18181B] tracking-tight">
              Recent Autonomous Campaigns
            </h2>
          </div>
          <Link
            to="/campaigns"
            className="text-xs font-semibold text-[#18181B] hover:text-indigo-600 flex items-center gap-1"
          >
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Campaign Card 1 */}
          <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 shadow-xs space-y-5">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" /> Active
                  </span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#71717A]">
                    ID: CMP-9042
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#18181B]">
                  Q4 Enterprise SaaS AI Copilot
                </h3>
              </div>

              {/* Thumbnail preview badge */}
              <div className="w-12 h-10 rounded-xl bg-gradient-to-br from-indigo-950 to-slate-900 border border-[#E8E8E3] flex items-center justify-center text-white shrink-0 shadow-inner">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            </div>

            {/* Persona & Channels */}
            <div className="grid grid-cols-2 gap-4 py-2 border-y border-[#F2F2ED] text-xs">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                  Target Persona
                </span>
                <span className="font-semibold text-[#18181B]">VP of Engineering, CTOs</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                  Channels
                </span>
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-[#F3F3EE] text-[10px] font-mono text-[#52525B]">
                    LinkedIn
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-[#F3F3EE] text-[10px] font-mono text-[#52525B]">
                    X / Twitter
                  </span>
                </div>
              </div>
            </div>

            {/* Budget progress */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-[#71717A] text-[11px]">Budget Burn</span>
                <span className="font-mono text-xs font-semibold text-[#18181B]">
                  $3,000 / $5,000 spent
                </span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-1.5">
                <div className="bg-[#18181B] h-1.5 rounded-full" style={{ width: '60%' }} />
              </div>
            </div>

            {/* Footer metrics */}
            <div className="flex items-center justify-between pt-1 text-xs">
              <div className="flex items-center gap-6">
                <div>
                  <span className="text-[10px] text-[#A1A1AA] block">Audience Reach</span>
                  <span className="font-bold text-[#18181B]">84,200</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#A1A1AA] block">CTR Ratio</span>
                  <span className="font-bold text-emerald-700">4.8%</span>
                </div>
              </div>
              <button className="p-1.5 text-[#A1A1AA] hover:text-[#18181B] rounded-lg hover:bg-[#F3F3EE] transition-colors">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Campaign Card 2 */}
          <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 shadow-xs space-y-5">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" /> Active
                  </span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#71717A]">
                    ID: CMP-8819
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#18181B]">
                  B2B Marketing Automation Playbook
                </h3>
              </div>

              {/* Thumbnail preview badge */}
              <div className="w-12 h-10 rounded-xl bg-gradient-to-br from-emerald-950 to-slate-900 border border-[#E8E8E3] flex items-center justify-center text-white shrink-0 shadow-inner">
                <Target className="w-4 h-4 text-emerald-400" />
              </div>
            </div>

            {/* Persona & Channels */}
            <div className="grid grid-cols-2 gap-4 py-2 border-y border-[#F2F2ED] text-xs">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                  Target Persona
                </span>
                <span className="font-semibold text-[#18181B]">Growth Marketers, CMOs</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">
                  Channels
                </span>
                <div className="flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 rounded bg-[#F3F3EE] text-[10px] font-mono text-[#52525B]">
                    LinkedIn
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-[#F3F3EE] text-[10px] font-mono text-[#52525B]">
                    Meta Ads
                  </span>
                </div>
              </div>
            </div>

            {/* Budget progress */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-[#71717A] text-[11px]">Budget Burn</span>
                <span className="font-mono text-xs font-semibold text-[#18181B]">
                  $1,800 / $2,500 spent
                </span>
              </div>
              <div className="w-full bg-[#F3F3EE] rounded-full h-1.5">
                <div className="bg-amber-700 h-1.5 rounded-full" style={{ width: '72%' }} />
              </div>
            </div>

            {/* Footer metrics */}
            <div className="flex items-center justify-between pt-1 text-xs">
              <div className="flex items-center gap-6">
                <div>
                  <span className="text-[10px] text-[#A1A1AA] block">Audience Reach</span>
                  <span className="font-bold text-[#18181B]">65,800</span>
                </div>
                <div>
                  <span className="text-[10px] text-[#A1A1AA] block">CTR Ratio</span>
                  <span className="font-bold text-emerald-700">6.2%</span>
                </div>
              </div>
              <button className="p-1.5 text-[#A1A1AA] hover:text-[#18181B] rounded-lg hover:bg-[#F3F3EE] transition-colors">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
