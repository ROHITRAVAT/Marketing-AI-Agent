import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { campaignService } from '@/services/campaignService';
import type { Campaign } from '@/types';

const getCampaignError = (error: unknown) => {
  const axiosError = error as { response?: { data?: { detail?: string; message?: string } }; code?: string };
  return axiosError.response?.data?.detail || axiosError.response?.data?.message ||
    (axiosError.code === 'ERR_NETWORK' || !axiosError.response
      ? 'Unable to connect to server. Please try again.'
      : 'Unable to load campaigns. Please try again.');
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
    return () => { isMounted = false; };
  }, []);

  const stats = [
    { label: 'Total Campaigns', value: campaigns.length, icon: Rocket },
    { label: 'Active Campaigns', value: campaigns.filter((campaign) => campaign.status === 'active').length, icon: CheckCircle2 },
    { label: 'Drafts Awaiting Review', value: campaigns.filter((campaign) => campaign.status === 'draft').length, icon: ShieldCheck },
    { label: 'Paused Campaigns', value: campaigns.filter((campaign) => campaign.status === 'paused').length, icon: Clock },
  ];
  const recentCampaigns = [...campaigns]
    .sort((left, right) => right.updated_at.localeCompare(left.updated_at))
    .slice(0, 2);

  return (
    <div className="space-y-8 text-[#18181B]">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-2">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block" />
            Human-in-the-Loop Safeguard
            <span className="text-amber-400">·</span>
            <span className="text-[#71717A] font-normal">Approval Required Before Publishing</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-serif tracking-tight">Welcome back, {user?.full_name?.split(' ')[0] || user?.username || 'Marketer'}</h1>
          <p className="text-sm text-[#71717A] max-w-xl">Review your campaigns and approve every action before it is published.</p>
        </div>
        <div className="flex items-center gap-3 self-start md:self-center">
          <Link to="/chat" className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-xl shadow-sm transition-all"><Rocket className="w-3.5 h-3.5 text-amber-400" />Open AI Copilot</Link>
          <Link to="/campaigns" className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-white hover:bg-[#F3F3EE] border border-[#E4E4DC] text-xs font-semibold rounded-xl shadow-xs transition-all"><Plus className="w-3.5 h-3.5" />New Campaign</Link>
        </div>
      </div>

      {error && <div className="rounded-xl bg-rose-50 border border-rose-200 p-4 flex items-start gap-3 text-rose-800 text-xs font-medium"><AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600" /><span>{error}</span></div>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
            <div className="flex items-center justify-between"><span className="text-[11px] font-mono uppercase tracking-wider text-[#71717A]">{label}</span><div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center"><Icon className="w-4 h-4" /></div></div>
            <span className="text-3xl font-bold tracking-tight">{isLoading ? '...' : value}</span>
            <div className="pt-2 border-t border-[#F2F2ED] text-[11px] text-[#71717A]">From backend campaign data</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /><h2 className="text-base font-bold tracking-tight">Recent Campaigns</h2></div><Link to="/campaigns" className="text-xs font-semibold flex items-center gap-1">Manage All <ArrowRight className="w-3.5 h-3.5" /></Link></div>
          {isLoading ? <p className="text-sm text-[#71717A]">Loading campaigns...</p> : recentCampaigns.length === 0 ? <div className="bg-white border border-[#E8E8E3] rounded-2xl p-8 text-center space-y-3 shadow-xs"><p className="text-sm text-[#71717A]">No campaigns are available.</p><Link to="/campaigns" className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#18181B] text-white text-xs font-semibold rounded-xl"><Plus className="w-3.5 h-3.5 text-amber-400" />Create Campaign</Link></div> : <div className="space-y-3.5">{recentCampaigns.map((campaign) => <div key={campaign.id} className="bg-white border border-[#E8E8E3] rounded-2xl p-5 shadow-xs space-y-3"><div className="flex items-start justify-between gap-4"><div><span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F3EE] text-[#52525B] font-semibold">{campaign.status}</span><h3 className="text-sm font-bold mt-2">{campaign.name}</h3></div><Sparkles className="w-4 h-4 text-amber-500" /></div>{campaign.description && <p className="text-xs text-[#71717A] line-clamp-2">{campaign.description}</p>}<div className="flex items-center gap-4 text-xs text-[#71717A] pt-2 border-t border-[#F2F2ED]"><span className="flex items-center gap-1"><Calendar className="w-3 h-3" />Updated {new Date(campaign.updated_at).toLocaleDateString()}</span><span>Audience: {campaign.target_audience || 'Not specified'}</span></div></div>)}</div>}
        </div>
        <div className="space-y-4"><div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /><h2 className="text-base font-bold tracking-tight">Approval Workflow</h2></div><div className="bg-white border border-[#E8E8E3] rounded-2xl p-5 space-y-4 shadow-xs"><div className="flex items-center gap-2 text-amber-800 text-xs font-semibold"><ShieldCheck className="w-4 h-4" />Human approval required</div><p className="text-xs text-[#52525B] leading-relaxed">AI-generated copy and schedules remain drafts until you review and approve them.</p><Link to="/chat" className="inline-flex items-center gap-1.5 text-xs font-semibold">Review in Copilot <ArrowRight className="w-3.5 h-3.5" /></Link></div></div>
      </div>
    </div>
  );
};

export default DashboardPage;