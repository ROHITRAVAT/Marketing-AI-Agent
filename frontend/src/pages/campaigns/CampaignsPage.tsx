import React, { useState } from 'react';
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
import { useCampaignStore, type CampaignFormData } from '@/store/useCampaignStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const AVAILABLE_CHANNELS = ['LinkedIn', 'Twitter/X', 'Instagram', 'Facebook'];

export const CampaignsPage: React.FC = () => {
  const {
    campaigns,
    searchQuery,
    statusFilter,
    setSearchQuery,
    setStatusFilter,
    addCampaign,
    updateCampaign,
    deleteCampaign,
  } = useCampaignStore();

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
      channels: c.channels || ['LinkedIn'],
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    if (editingId) {
      updateCampaign(editingId, formData);
    } else {
      addCampaign(formData);
    }
    setIsModalOpen(false);
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Campaign Management</h2>
          <p className="text-sm text-slate-400">
            Create, schedule, edit, and orchestrate AI-powered marketing campaigns.
          </p>
        </div>
        <Button onClick={openCreateModal} icon={<Plus className="w-4 h-4" />}>
          Create Campaign
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search campaigns or audience..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
          />
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          {['all', 'active', 'paused', 'draft'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                statusFilter === status
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredCampaigns.map((c) => (
          <div
            key={c.id}
            className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-6 space-y-4 shadow-lg transition-all"
          >
            {/* Card Header */}
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${
                      c.status === 'active'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : c.status === 'paused'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {c.status}
                  </span>
                  <h3 className="text-lg font-bold text-white leading-tight">{c.name}</h3>
                </div>
                <p className="text-xs text-slate-400 mt-1.5 leading-relaxed line-clamp-2">
                  {c.description || 'No description provided.'}
                </p>
              </div>

              {/* Status Toggle & Actions */}
              <div className="flex items-center gap-1.5 shrink-0">
                <button
                  onClick={() =>
                    updateCampaign(c.id, {
                      status: c.status === 'active' ? 'paused' : 'active',
                    })
                  }
                  title={c.status === 'active' ? 'Pause Campaign' : 'Resume Campaign'}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  {c.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 text-emerald-400" />}
                </button>
                <button
                  onClick={() => openEditModal(c)}
                  title="Edit Campaign"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteCampaign(c.id)}
                  title="Delete Campaign"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Campaign Meta details */}
            <div className="grid grid-cols-2 gap-3 pt-2 text-xs text-slate-400 border-t border-slate-800/80">
              <div>
                <span className="text-slate-500 block mb-0.5">Target Audience:</span>
                <span className="text-slate-200 font-medium truncate block">{c.target_audience || 'General'}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-0.5">Budget Allocated:</span>
                <span className="text-white font-semibold">${c.budget ? c.budget.toLocaleString() : '0'}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-0.5">Schedule:</span>
                <span className="text-slate-200 font-medium">{c.start_date || 'Ongoing'}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-0.5">Audience Reach:</span>
                <span className="text-indigo-300 font-semibold">{c.reach ? c.reach.toLocaleString() : '0'}</span>
              </div>
            </div>

            {/* Channels & Footer */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs">
              <div className="flex flex-wrap gap-1.5">
                {c.channels?.map((channel) => (
                  <span
                    key={channel}
                    className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[11px]"
                  >
                    {channel}
                  </span>
                ))}
              </div>
              <span className="text-slate-500">ID: #{c.id}</span>
            </div>
          </div>
        ))}
      </div>

      {filteredCampaigns.length === 0 && (
        <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
          <Megaphone className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No campaigns found</h3>
          <p className="text-xs text-slate-400 mt-1">Try adjusting your search terms or create a new campaign.</p>
        </div>
      )}

      {/* Modal: Create or Edit Campaign */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">
                {editingId ? 'Edit Marketing Campaign' : 'Create New AI Campaign'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
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
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-lg py-2.5 px-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
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
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                          isSelected
                            ? 'bg-indigo-600 text-white border-indigo-500'
                            : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                        }`}
                      >
                        {ch}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Brief / Description
                </label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Outline the core objective, value proposition, and key marketing angles..."
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-lg p-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <Button variant="outline" onClick={() => setIsModalOpen(false)}>
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
