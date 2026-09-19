import React, { useState, useEffect } from 'react';
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
import { analyticsService, AnalyticsSummaryResponse } from '@/services/analytics';

export const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [data, setData] = useState<AnalyticsSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const today = new Date();
        const past = new Date();
        const days = parseInt(timeRange.replace('d', ''));
        past.setDate(today.getDate() - days);
        
        const summary = await analyticsService.getSummary(
          past.toISOString().split('T')[0],
          today.toISOString().split('T')[0]
        );
        setData(summary);
      } catch (error) {
        console.error('Failed to load analytics', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [timeRange]);

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

  const totalImpressions = data?.overall_impressions || 0;
  const totalEngagement = data?.overall_engagement || 0;
  const totalClicks = data?.platforms?.reduce((acc, p) => acc + p.total_clicks, 0) || 0;
  const averageCTR = totalImpressions > 0 ? ((totalClicks / totalImpressions) * 100).toFixed(1) : "0.0";
  
  const channelMetrics = data?.platforms?.map(p => ({
    name: p.platform,
    percentage: totalImpressions > 0 ? Math.round((p.total_impressions / totalImpressions) * 100) : 0,
    reach: p.total_impressions.toLocaleString(),
    color: p.platform === 'linkedin' ? 'bg-indigo-500' 
         : p.platform === 'twitter' ? 'bg-purple-500' 
         : p.platform === 'instagram' ? 'bg-pink-500' 
         : 'bg-blue-500'
  })) || [];

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Marketing Analytics</h2>
          <p className="text-sm text-slate-400">
            Real-time campaign performance metrics, conversions, and multi-channel attribution.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Time Range Selector */}
          <div className="flex bg-slate-900 border border-slate-800 rounded-xl p-1 text-xs font-semibold">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1.5 rounded-lg transition-colors uppercase ${
                  timeRange === range
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {range}
              </button>
            ))}
          </div>

          <Button
            variant="outline"
            onClick={handleExport}
            icon={<Download className="w-4 h-4" />}
          >
            {downloadSuccess ? 'Exported CSV' : 'Export Report'}
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Total Impressions</span>
            <Eye className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{isLoading ? '-' : totalImpressions.toLocaleString()}</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +0.0%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Analyzed {data?.total_posts_analyzed || 0} posts</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Clicks & Visits</span>
            <MousePointer className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{isLoading ? '-' : totalClicks.toLocaleString()}</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +0.0%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Average CTR: {isLoading ? '-' : averageCTR}%</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Qualified Leads</span>
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">642</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +31.5%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Cost per Lead: $14.20</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Return on Ad Spend</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">4.2x</span>
            <span className="text-xs font-medium text-emerald-400 flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5" /> +0.6x
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Target benchmark: 3.5x</p>
        </div>
      </div>

      {/* Visual Analytics Row: Performance Trend & Channels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Performance Trend Chart (2 Cols) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Engagement Trend</h3>
              <p className="text-xs text-slate-400">Daily organic and paid interactions over selected timeframe</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" /> Impressions
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" /> Clicks
              </span>
            </div>
          </div>

          {/* SVG Line / Bar Chart Simulation */}
          <div className="h-56 flex items-end justify-between gap-2 pt-6 border-b border-slate-800 pb-2">
            {[45, 62, 58, 78, 85, 92, 88, 95, 110, 105, 125, 140].map((val, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group">
                <div className="w-full flex justify-center gap-1 items-end h-44">
                  {/* Impressions bar */}
                  <div
                    style={{ height: `${(val / 140) * 100}%` }}
                    className="w-full max-w-[14px] bg-indigo-600/80 hover:bg-indigo-500 rounded-t transition-all"
                  />
                  {/* Clicks bar */}
                  <div
                    style={{ height: `${(val / 140) * 35}%` }}
                    className="w-full max-w-[14px] bg-emerald-500/80 hover:bg-emerald-400 rounded-t transition-all"
                  />
                </div>
                <span className="text-[10px] text-slate-500 group-hover:text-slate-300 transition-colors">
                  W{idx + 1}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Peak performance: Week 12 (+140k impressions)</span>
            <span className="text-emerald-400 font-medium">Consistently outperforming baseline</span>
          </div>
        </div>

        {/* Channel Distribution Breakdown (1 Col) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div>
            <h3 className="text-base font-bold text-white">Channel Attribution</h3>
            <p className="text-xs text-slate-400">Audience distribution across social networks</p>
          </div>

          <div className="space-y-4 pt-1">
            {channelMetrics.map((ch) => (
              <div key={ch.name} className="space-y-1.5">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-200">{ch.name}</span>
                  <span className="text-slate-400">{ch.reach} ({ch.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2.5">
                  <div
                    className={`${ch.color} h-2.5 rounded-full transition-all duration-500`}
                    style={{ width: `${ch.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-xl bg-slate-950 p-4 border border-slate-800 text-xs space-y-1">
            <span className="text-indigo-300 font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> AI Channel Insight:
            </span>
            <p className="text-slate-400 leading-relaxed">
              LinkedIn delivers our highest B2B conversion rate (6.2%), while Instagram drives the lowest cost-per-click ($0.42).
            </p>
          </div>
        </div>
      </div>

      {/* Top Performing Content Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Top Performing Marketing Content</h3>
            <p className="text-xs text-slate-400">Generated posts with highest viral coefficient and click-through</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Ranked by Engagement
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[11px] font-semibold border-b border-slate-800">
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
            <tbody className="divide-y divide-slate-800/60">
              {topPosts.map((post) => (
                <tr key={post.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-medium text-white max-w-xs truncate">{post.title}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[11px] font-medium border border-slate-700">
                      {post.channel}
                    </span>
                  </td>
                  <td className="py-3 px-4">{post.impressions}</td>
                  <td className="py-3 px-4">{post.clicks}</td>
                  <td className="py-3 px-4 text-indigo-300 font-semibold">{post.ctr}</td>
                  <td className="py-3 px-4 text-emerald-400 font-semibold">{post.engagement}</td>
                  <td className="py-3 px-4 text-slate-500">{post.date}</td>
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
