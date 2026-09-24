import React, { useState, useEffect } from 'react';
import {
  Users,
  Eye,
  MousePointer,
  Download,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  analyticsService,
  type AnalyticsSummaryResponse,
  type SocialAnalyticsResponse,
  type ScheduledPostResponse,
} from '@/services/analytics';

interface TopPost {
  id: number;
  title: string;
  channel: string;
  impressions: number;
  clicks: number;
  engagement: number;
  date: string;
}

const toTopPost = (post: ScheduledPostResponse, analytics: SocialAnalyticsResponse): TopPost => ({
  id: post.id,
  title: post.content?.split('\n')[0]?.slice(0, 120) || `Published ${post.platform} post`,
  channel: post.platform,
  impressions: analytics.impressions || 0,
  clicks: analytics.clicks || 0,
  engagement: analytics.impressions
    ? ((analytics.engagement || 0) / analytics.impressions) * 100
    : 0,
  date: post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Unknown',
});

export const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [data, setData] = useState<AnalyticsSummaryResponse | null>(null);
  const [topPosts, setTopPosts] = useState<TopPost[]>([]);
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

        const publishedPosts = await analyticsService.listPublishedPosts();
        const postsWithAnalytics = await Promise.all(
          publishedPosts
            .filter((post) => {
              if (!post.external_post_id || !post.published_at) return false;
              const publishedAt = new Date(post.published_at).getTime();
              return publishedAt >= past.getTime() && publishedAt <= today.getTime();
            })
            .map(async (post) => {
              try {
                const snapshots = await analyticsService.getPostAnalytics(post.external_post_id!);
                return { post, analytics: snapshots[0] };
              } catch {
                return { post, analytics: undefined };
              }
            })
        );

        setTopPosts(
          postsWithAnalytics
            .filter(({ analytics }) => analytics)
            .map(({ post, analytics }) => toTopPost(post, analytics!))
            .sort((left, right) => right.engagement - left.engagement)
            .slice(0, 10)
        );
      } catch (error) {
        console.error('Failed to load analytics', error);
        setTopPosts([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [timeRange]);

  const handleExport = () => {
    if (!data) return;

    const rows = [
      ['Metric', 'Value'],
      ['Date range', `${data.start_date} to ${data.end_date}`],
      ['Total impressions', data.overall_impressions],
      ['Total clicks', totalClicks],
      ['Average CTR', `${averageCTR}%`],
      [],
      ['Post', 'Platform', 'Impressions', 'Clicks', 'Engagement', 'Published'],
      ...topPosts.map((post) => [
        post.title,
        post.channel,
        post.impressions,
        post.clicks,
        `${post.engagement.toFixed(1)}%`,
        post.date,
      ]),
    ];
    const csv = rows
      .map((row) => row.map((value) => `"${String(value ?? '').replaceAll('"', '""')}"`).join(','))
      .join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${timeRange}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  const totalImpressions = data?.overall_impressions || 0;

  const totalClicks = data?.platforms?.reduce((acc, p) => acc + p.total_clicks, 0) || 0;
  const averageCTR = totalImpressions > 0 ? ((totalClicks / totalImpressions) * 100).toFixed(1) : '0.0';
  
  const channelMetrics = data?.platforms?.map(p => ({
    name: p.platform,
    percentage: totalImpressions > 0 ? Math.round((p.total_impressions / totalImpressions) * 100) : 0,
    reach: p.total_impressions.toLocaleString(),
    color: p.platform === 'linkedin' ? 'bg-indigo-500' 
         : p.platform === 'twitter' ? 'bg-purple-500' 
         : p.platform === 'instagram' ? 'bg-pink-500' 
         : 'bg-blue-500'
  })) || [];

  const largestChannel = channelMetrics.reduce((largest, channel) =>
    channel.percentage > largest.percentage ? channel : largest,
    { name: 'No channel', percentage: 0, reach: '0' }
  );

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
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">{isLoading ? '-' : totalImpressions.toLocaleString()}</span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Analyzed {data?.total_posts_analyzed || 0} posts</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Clicks & Visits</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
              <MousePointer className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#18181B]">{isLoading ? '-' : totalClicks.toLocaleString()}</span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Average CTR: {isLoading ? '-' : averageCTR}%</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Qualified Leads</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-emerald-700">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold tracking-tight text-[#71717A]">Coming soon</span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Not provided by the analytics API</p>
        </div>

        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            <span>Return on Ad Spend</span>
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-amber-700">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold tracking-tight text-[#71717A]">Coming soon</span>
          </div>
          <p className="text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]">Ad spend and revenue data are not available</p>
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

          {/* Real channel totals are available; daily history is not exposed yet. */}
          <div className="h-56 flex items-end justify-between gap-2 pt-6 border-b border-[#F2F2ED] pb-2">
            {channelMetrics.map((channel) => (
              <div key={channel.name} className="flex-1 flex flex-col items-center gap-1.5 group">
                <div className="w-full flex justify-center gap-1 items-end h-44">
                  <div
                    style={{ height: `${channel.percentage}%` }}
                    className="w-full max-w-[14px] bg-[#18181B] hover:bg-[#27272A] rounded-t transition-all"
                  />
                </div>
                <span className="text-[10px] font-mono text-[#A1A1AA] group-hover:text-[#18181B] transition-colors">
                  {channel.name}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-[#71717A]">
            <span>Channel totals for the selected timeframe</span>
            <span className="text-[#52525B] font-semibold">Daily trend data coming soon</span>
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
            <span className="text-[#18181B] font-semibold">Channel summary</span>
            <p className="text-[#52525B] leading-relaxed">
              {largestChannel.percentage > 0
                ? `${largestChannel.name} has the largest share of recorded impressions at ${largestChannel.percentage}%.`
                : 'No channel analytics are available for this timeframe.'}
            </p>
          </div>
        </div>
      </div>

      {/* Top Performing Content Table */}
      <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#18181B]">Top Performing Marketing Content</h3>
            <p className="text-xs text-[#71717A]">Published posts with collected analytics, ranked by engagement rate</p>
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
                  <td className="py-3 px-4 font-mono">{post.impressions.toLocaleString()}</td>
                  <td className="py-3 px-4 font-mono">{post.clicks.toLocaleString()}</td>
                  <td className="py-3 px-4 text-emerald-700 font-bold font-mono">
                    {post.impressions ? `${((post.clicks / post.impressions) * 100).toFixed(1)}%` : '0.0%'}
                  </td>
                  <td className="py-3 px-4 text-emerald-700 font-bold font-mono">{post.engagement.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-[#71717A]">{post.date}</td>
                </tr>
              ))}
              {!isLoading && topPosts.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 px-4 text-center text-[#71717A]">
                    No published posts with collected analytics are available for this timeframe.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
