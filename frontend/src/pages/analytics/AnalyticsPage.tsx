import React, { useState } from 'react';
import {
  Users,
  Eye,
  MousePointer,
  Download,
  DollarSign,
  ArrowUpRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleExport = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  const topPosts = [
    {
      id: 1,
      title: '5 AI Workflow Hacks that Saved us 20 Hours / Week',
      channel: 'LinkedIn',
      impressions: '42,800',
      clicks: '2,140',
      ctr: '5.0%',
      engagement: '6.4%',
      date: 'Sep 4, 2026',
    },
    {
      id: 2,
      title: 'Stop hardcoding prompts: The Autonomous Agent paradigm',
      channel: 'Twitter/X',
      impressions: '31,500',
      clicks: '1,890',
      ctr: '6.0%',
      engagement: '7.8%',
      date: 'Sep 2, 2026',
    },
    {
      id: 3,
      title: 'Behind the Scenes: Training Qwen 3 on Brand Voice Guidelines',
      channel: 'LinkedIn',
      impressions: '19,200',
      clicks: '980',
      ctr: '5.1%',
      engagement: '4.9%',
      date: 'Aug 29, 2026',
    },
    {
      id: 4,
      title: 'Viral Hook Breakdown: 10 Carousel slides for SaaS founders',
      channel: 'Instagram',
      impressions: '28,400',
      clicks: '1,420',
      ctr: '5.0%',
      engagement: '9.2%',
      date: 'Aug 26, 2026',
    },
  ];

  const channelMetrics = [
    { name: 'LinkedIn', percentage: 48, reach: '88.4K', color: 'bg-indigo-500' },
    { name: 'Twitter / X', percentage: 32, reach: '58.9K', color: 'bg-purple-500' },
    { name: 'Instagram', percentage: 16, reach: '29.5K', color: 'bg-pink-500' },
    { name: 'Facebook', percentage: 4, reach: '7.4K', color: 'bg-blue-500' },
  ];

  return (
    <div className="space-y-8 text-[#18181B]">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">Marketing Analytics</h2>
          <p className="text-sm text-[#71717A] mt-1">
            Real-time campaign performance metrics, conversions, and multi-channel attribution.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Time Range Selector */}
          <div className="flex bg-[#F3F3EE] border border-[#E4E4DC] rounded-xl p-1 text-xs font-semibold">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1.5 rounded-lg transition-all uppercase font-mono text-[11px] ${
                  timeRange === range
                    ? 'bg-[#18181B] text-white shadow-xs'
                    : 'text-[#71717A] hover:text-[#18181B]'
                }`}
              >
                {range}
              </button>
            ))}
          </div>

          <Button
            variant="secondary"
            onClick={handleExport}
            icon={<Download className="w-4 h-4 text-[#71717A]" />}
          >
            {downloadSuccess ? 'Exported CSV' : 'Export Report'}
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Total Impressions</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <Eye className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">184.2K</span>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded flex items-center">
              <ArrowUpRight className="w-3 h-3" /> +24.8%
            </span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">vs 147.6K in prior period</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Clicks & Visits</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <MousePointer className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">9,420</span>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded flex items-center">
              <ArrowUpRight className="w-3 h-3" /> +16.2%
            </span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Average CTR: 5.1%</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Qualified Leads</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-emerald-700">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">642</span>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded flex items-center">
              <ArrowUpRight className="w-3 h-3" /> +31.5%
            </span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Cost per Lead: $14.20</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Return on Ad Spend</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-amber-700">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">4.2x</span>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded flex items-center">
              <ArrowUpRight className="w-3 h-3" /> +0.6x
            </span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Target benchmark: 3.5x</p>
        </div>
      </div>

      {/* Visual Analytics Row: Performance Trend & Channels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Performance Trend Chart (2 Cols) */}
        <div className="lg:col-span-2 bg-white border border-[#E8E8E3] rounded-2xl p-6 space-y-6 shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-[#18181B]">Engagement Trend</h3>
              <p className="text-xs text-[#71717A]">Daily organic and paid interactions over selected timeframe</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-[#52525B]">
                <span className="w-2.5 h-2.5 rounded-full bg-[#18181B] inline-block" /> Impressions
              </span>
              <span className="flex items-center gap-1.5 text-[#52525B]">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 inline-block" /> Clicks
              </span>
            </div>
          </div>

          {/* SVG Line / Bar Chart Simulation */}
          <div className="h-56 flex items-end justify-between gap-2 pt-6 border-b border-[#F2F2ED] pb-2">
            {[45, 62, 58, 78, 85, 92, 88, 95, 110, 105, 125, 140].map((val, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group">
                <div className="w-full flex justify-center gap-1 items-end h-44">
                  {/* Impressions bar */}
                  <div
                    style={{ height: `${(val / 140) * 100}%` }}
                    className="w-full max-w-[14px] bg-[#18181B] hover:bg-[#27272A] rounded-t transition-all"
                  />
                  {/* Clicks bar */}
                  <div
                    style={{ height: `${(val / 140) * 35}%` }}
                    className="w-full max-w-[14px] bg-emerald-600 hover:bg-emerald-500 rounded-t transition-all"
                  />
                </div>
                <span className="text-[10px] font-mono text-[#A1A1AA] group-hover:text-[#18181B] transition-colors">
                  W{idx + 1}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-[#71717A]">
            <span>Peak performance: Week 12 (+140k impressions)</span>
            <span className="text-emerald-700 font-semibold">Consistently outperforming baseline</span>
          </div>
        </div>

        {/* Channel Distribution Breakdown (1 Col) */}
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 space-y-6 shadow-xs">
          <div>
            <h3 className="text-base font-bold text-[#18181B]">Channel Attribution</h3>
            <p className="text-xs text-[#71717A]">Audience distribution across social networks</p>
          </div>

          <div className="space-y-4 pt-1">
            {channelMetrics.map((ch) => (
              <div key={ch.name} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-[#18181B] font-semibold">{ch.name}</span>
                  <span className="text-[#71717A] font-mono">{ch.reach} ({ch.percentage}%)</span>
                </div>
                <div className="w-full bg-[#F3F3EE] rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      ch.name === 'LinkedIn' ? 'bg-[#18181B]' : ch.name.includes('Twitter') ? 'bg-amber-600' : 'bg-emerald-600'
                    }`}
                    style={{ width: `${ch.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-xl bg-[#F8F8F6] p-4 border border-[#E8E8E3] text-xs space-y-1">
            <span className="text-[#18181B] font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" /> AI Channel Insight:
            </span>
            <p className="text-[#52525B] leading-relaxed">
              LinkedIn delivers our highest B2B conversion rate (6.2%), while Instagram drives the lowest cost-per-click ($0.42).
            </p>
          </div>
        </div>
      </div>

      {/* Top Performing Content Table */}
      <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#18181B]">Top Performing Marketing Content</h3>
            <p className="text-xs text-[#71717A]">Generated posts with highest viral coefficient and click-through</p>
          </div>
          <span className="text-[10px] font-mono uppercase font-semibold px-2.5 py-1 rounded bg-[#F3F3EE] text-[#52525B] border border-[#E4E4DC]">
            Ranked by Engagement
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#52525B]">
            <thead className="bg-[#FBFBFA] text-[#71717A] uppercase text-[10px] font-mono font-semibold border-b border-[#E8E8E3]">
              <tr>
                <th className="py-3 px-4">Post Topic / Content</th>
                <th className="py-3 px-4">Platform</th>
                <th className="py-3 px-4">Impressions</th>
                <th className="py-3 px-4">Clicks</th>
                <th className="py-3 px-4">CTR</th>
                <th className="py-3 px-4">Engagement</th>
                <th className="py-3 px-4">Published</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F2F2ED]">
              {topPosts.map((post) => (
                <tr key={post.id} className="hover:bg-[#F8F8F6] transition-colors">
                  <td className="py-3 px-4 font-medium text-[#18181B] max-w-xs truncate">{post.title}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-[#F3F3EE] text-[#52525B] text-[10px] font-mono border border-[#E4E4DC]">
                      {post.channel}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono">{post.impressions}</td>
                  <td className="py-3 px-4 font-mono">{post.clicks}</td>
                  <td className="py-3 px-4 text-emerald-700 font-bold font-mono">{post.ctr}</td>
                  <td className="py-3 px-4 text-emerald-700 font-bold font-mono">{post.engagement}</td>
                  <td className="py-3 px-4 text-[#71717A]">{post.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
