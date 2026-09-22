import React, { useEffect, useState } from 'react';
import {
  Plus,
  Search,
  Megaphone,
  Edit2,
  Trash2,
  Play,
  Pause,
  X,
} from 'lucide-react';
import type { Campaign } from '@/types';
import { campaignService } from '@/services/campaignService';
import type { CampaignFormData } from '@/store/useCampaignStore';
import { useAuthStore } from '@/store/useAuthStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const AVAILABLE_CHANNELS = ['LinkedIn', 'Twitter/X', 'Instagram', 'Facebook'];

export const CampaignsPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [serverError, setServerError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Form State
  const [formData, setFormData] = useState<CampaignFormData>({
    name: '',
    description: '',
    status: 'active',
    target_audience: '',
    budget: 1000,
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    channels: ['LinkedIn'],
  });

  const loadCampaigns = async () => {
    setIsLoading(true);
    try {
      const response = await campaignService.listCampaigns({
        status: statusFilter,
        search: searchQuery,
        size: 100,
      });
      setCampaigns(response.items);
      setServerError(null);
    } catch (error) {
      console.error('Failed to load campaigns', error);
      setServerError('Unable to load campaigns from the server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, [statusFilter, searchQuery]);

  const openCreateModal = () => {
    setEditingId(null);
    setFormData({
      name: '',
      description: '',
      status: 'active',
      target_audience: '',
      budget: 2000,
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      channels: ['LinkedIn'],
    });
    setIsModalOpen(true);
  };

  const openEditModal = (c: (typeof campaigns)[0]) => {
    setEditingId(c.id);
    setFormData({
      name: c.name,
      description: c.description || '',
      status: c.status,
      target_audience: c.target_audience || '',
      budget: c.budget || 0,
      start_date: c.start_date || '',
      end_date: c.end_date || '',
      channels: ['LinkedIn'],
    });
    setIsModalOpen(true);
  };

  const handleChannelToggle = (channel: string) => {
    const current = formData.channels || [];
    if (current.includes(channel)) {
      setFormData({ ...formData, channels: current.filter((ch) => ch !== channel) });
    } else {
      setFormData({ ...formData, channels: [...current, channel] });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    if (editingId) {
      await campaignService.updateCampaign(editingId, formData);
    } else {
      if (!user) {
        setServerError('Your session is missing. Please sign in again.');
        return;
      }
      await campaignService.createCampaign(formData, user.id);
    }
    setIsModalOpen(false);
    await loadCampaigns();
  };

  // Filtering
  const filteredCampaigns = campaigns.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.target_audience && c.target_audience.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 text-[#18181B]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">Campaign Management</h2>
          <p className="text-sm text-[#71717A] mt-1">
            Create, schedule, edit, and orchestrate AI-powered marketing campaigns.
          </p>
        </div>
        <Button onClick={openCreateModal} icon={<Plus className="w-4 h-4 text-amber-400" />}>
          Create Campaign
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-[#E8E8E3] p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 shadow-xs">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-[#A1A1AA] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search campaigns or audience..."
            className="w-full bg-[#F3F3EE] border border-[#E4E4DC] focus:border-[#18181B] focus:bg-white rounded-xl pl-9 pr-4 py-2 text-xs text-[#18181B] placeholder-[#A1A1AA] focus:outline-none transition-all"
          />
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          {['all', 'active', 'paused', 'draft'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all ${
                statusFilter === status
                  ? 'bg-[#18181B] text-white shadow-xs'
                  : 'bg-[#F3F3EE] text-[#52525B] hover:text-[#18181B] hover:bg-[#EAEAE4]'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Campaigns Grid */}
      {serverError && (
        <div className="rounded-xl bg-rose-50 border border-rose-200 p-3 text-sm text-rose-800">{serverError}</div>
      )}

      {isLoading && <div className="text-sm text-[#71717A]">Loading campaigns...</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredCampaigns.map((c) => (
          <div
            key={c.id}
            className="bg-white border border-[#E8E8E3] hover:border-[#D1D1C7] rounded-2xl p-6 space-y-4 shadow-xs transition-all"
          >
            {/* Card Header */}
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-semibold flex items-center gap-1 ${
                      c.status === 'active'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : c.status === 'paused'
                        ? 'bg-amber-50 text-amber-800 border border-amber-200'
                        : 'bg-[#F3F3EE] text-[#71717A] border border-[#E4E4DC]'
                    }`}
                  >
                    {c.status === 'active' && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />}
                    {c.status}
                  </span>
                  <span className="text-[10px] font-mono text-[#71717A] bg-[#F3F3EE] px-1.5 py-0.5 rounded">
                    ID: #{c.id}
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#18181B] leading-tight">{c.name}</h3>
                <p className="text-xs text-[#71717A] leading-relaxed line-clamp-2">
                  {c.description || 'No description provided.'}
                </p>
              </div>

              {/* Status Toggle & Actions */}
              <div className="flex items-center gap-1.5 shrink-0">
                <button
                  onClick={async () => {
                    await campaignService.updateStatus(c.id, c.status === 'active' ? 'paused' : 'active');
                    await loadCampaigns();
                  }}
                  title={c.status === 'active' ? 'Pause Campaign' : 'Resume Campaign'}
                  className="p-1.5 rounded-lg bg-[#F8F8F6] border border-[#E8E8E3] hover:bg-[#F3F3EE] text-[#52525B] hover:text-[#18181B] transition-colors"
                >
                  {c.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 text-emerald-600" />}
                </button>
                <button
                  onClick={() => openEditModal(c)}
                  title="Edit Campaign"
                  className="p-1.5 rounded-lg bg-[#F8F8F6] border border-[#E8E8E3] hover:bg-[#F3F3EE] text-[#52525B] hover:text-[#18181B] transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={async () => {
                    await campaignService.deleteCampaign(c.id);
                    await loadCampaigns();
                  }}
                  title="Delete Campaign"
                  className="p-1.5 rounded-lg bg-[#F8F8F6] border border-[#E8E8E3] hover:bg-rose-50 text-[#71717A] hover:text-rose-600 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Campaign Meta details */}
            <div className="grid grid-cols-2 gap-3 pt-3 text-xs border-t border-[#F2F2ED]">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">Target Audience:</span>
                <span className="text-[#18181B] font-semibold truncate block">{c.target_audience || 'General'}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">Budget Allocated:</span>
                <span className="text-[#18181B] font-semibold">${c.budget ? c.budget.toLocaleString() : '0'}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">Schedule:</span>
                <span className="text-[#52525B] font-medium">{c.start_date || 'Ongoing'}</span>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#A1A1AA] block mb-0.5">Audience Reach:</span>
                <span className="text-[#71717A] font-medium">Not available</span>
              </div>
            </div>

            {/* Channels & Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-[#F2F2ED] text-xs">
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded bg-[#F3F3EE] text-[#71717A] border border-[#E4E4DC] text-[10px] font-mono uppercase">
                  Channels unavailable
                </span>
              </div>
              <span className="text-[11px] font-mono text-[#A1A1AA]">Active Tracking</span>
            </div>
          </div>
        ))}
      </div>

      {filteredCampaigns.length === 0 && (
        <div className="text-center py-12 bg-white border border-[#E8E8E3] rounded-2xl shadow-xs">
          <Megaphone className="w-12 h-12 text-[#A1A1AA] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#18181B]">No campaigns found</h3>
          <p className="text-xs text-[#71717A] mt-1">Try adjusting your search terms or create a new campaign.</p>
        </div>
      )}

      {/* Modal: Create or Edit Campaign */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border border-[#E8E8E3] rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative text-[#18181B]">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-[#18181B] font-serif">
                {editingId ? 'Edit Marketing Campaign' : 'Create New AI Campaign'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-[#71717A] hover:text-[#18181B] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Campaign Name"
                placeholder="e.g. Q4 AI Product Launch"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />

              <Input
                label="Target Audience"
                placeholder="e.g. SaaS Founders, Marketing Directors"
                value={formData.target_audience}
                onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
              />

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Budget ($)"
                  type="number"
                  placeholder="3000"
                  value={formData.budget || ''}
                  onChange={(e) => setFormData({ ...formData, budget: Number(e.target.value) })}
                />
                <div className="space-y-1.5">
                  <label className="block text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                    className="w-full bg-[#F3F3EE] border border-[#E4E4DC] focus:bg-white focus:border-[#18181B] rounded-xl py-2.5 px-3 text-xs sm:text-sm text-[#18181B] focus:outline-none transition-all"
                  >
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                    <option value="draft">Draft</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Start Date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
                <Input
                  label="End Date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </div>

              {/* Channels Selector */}
              <div className="space-y-1.5">
                <label className="block text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
                  Target Channels
                </label>
                <div className="flex flex-wrap gap-2 pt-1">
                  {AVAILABLE_CHANNELS.map((ch) => {
                    const isSelected = formData.channels?.includes(ch);
                    return (
                      <button
                        type="button"
                        key={ch}
                        onClick={() => handleChannelToggle(ch)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                          isSelected
                            ? 'bg-[#18181B] text-white border-[#18181B] shadow-xs'
                            : 'bg-[#F3F3EE] text-[#52525B] border-[#E4E4DC] hover:text-[#18181B]'
                        }`}
                      >
                        {ch}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
                  Brief / Description
                </label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Outline the core objective, value proposition, and key marketing angles..."
                  className="w-full bg-[#F3F3EE] border border-[#E4E4DC] focus:bg-white focus:border-[#18181B] rounded-xl p-3 text-xs sm:text-sm text-[#18181B] focus:outline-none transition-all"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">
                  {editingId ? 'Save Changes' : 'Launch Campaign'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignsPage;
