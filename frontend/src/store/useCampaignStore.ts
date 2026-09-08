import { create } from 'zustand';
import type { Campaign } from '@/types';

export interface CampaignFormData {
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  target_audience?: string;
  budget?: number;
  start_date?: string;
  end_date?: string;
  channels?: string[];
}

interface CampaignState {
  campaigns: (Campaign & { channels?: string[]; reach?: number; engagement?: number })[];
  isLoading: boolean;
  searchQuery: string;
  statusFilter: string;
  setSearchQuery: (query: string) => void;
  setStatusFilter: (status: string) => void;
  addCampaign: (campaign: CampaignFormData) => void;
  updateCampaign: (id: number, campaign: Partial<CampaignFormData>) => void;
  deleteCampaign: (id: number) => void;
}

const INITIAL_CAMPAIGNS: (Campaign & { channels?: string[]; reach?: number; engagement?: number })[] = [
  {
    id: 1,
    user_id: 1,
    name: 'Q4 Product Launch - AI Copilot',
    description: 'Autonomous multi-channel marketing push highlighting our new AI features.',
    status: 'active',
    target_audience: 'Tech Leads, Marketing Directors, SaaS Founders',
    budget: 5000,
    start_date: '2026-09-01',
    end_date: '2026-09-30',
    created_at: '2026-08-28T10:00:00Z',
    updated_at: '2026-09-01T12:00:00Z',
    channels: ['LinkedIn', 'Twitter/X', 'Instagram'],
    reach: 48500,
    engagement: 4.8,
  },
  {
    id: 2,
    user_id: 1,
    name: 'Autumn B2B Lead Gen Series',
    description: 'Weekly thought leadership articles and case studies promoting enterprise tier.',
    status: 'active',
    target_audience: 'Enterprise Decision Makers & VP Marketing',
    budget: 3200,
    start_date: '2026-09-05',
    end_date: '2026-10-15',
    created_at: '2026-09-02T14:30:00Z',
    updated_at: '2026-09-05T09:15:00Z',
    channels: ['LinkedIn'],
    reach: 22100,
    engagement: 6.2,
  },
  {
    id: 3,
    user_id: 1,
    name: 'Social Media Viral Hooks Experiment',
    description: 'AI-generated viral short-form hooks comparing organic vs paid engagement.',
    status: 'paused',
    target_audience: 'Gen-Z and Millennial Creators',
    budget: 1500,
    start_date: '2026-08-15',
    end_date: '2026-09-15',
    created_at: '2026-08-10T11:00:00Z',
    updated_at: '2026-09-02T16:00:00Z',
    channels: ['Instagram', 'Twitter/X'],
    reach: 79400,
    engagement: 8.9,
  },
  {
    id: 4,
    user_id: 1,
    name: 'Holiday Season Early-Bird Campaign',
    description: 'Pre-holiday discounts and targeted newsletter promotions.',
    status: 'draft',
    target_audience: 'Small Business Owners & Agencies',
    budget: 2500,
    start_date: '2026-10-01',
    end_date: '2026-11-15',
    created_at: '2026-09-06T08:00:00Z',
    updated_at: '2026-09-06T08:00:00Z',
    channels: ['LinkedIn', 'Facebook'],
    reach: 0,
    engagement: 0,
  },
];

const loadCampaigns = () => {
  try {
    const data = localStorage.getItem('marketing_campaigns_list');
    return data ? JSON.parse(data) : INITIAL_CAMPAIGNS;
  } catch {
    return INITIAL_CAMPAIGNS;
  }
};

export const useCampaignStore = create<CampaignState>((set, get) => ({
  campaigns: loadCampaigns(),
  isLoading: false,
  searchQuery: '',
  statusFilter: 'all',

  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setStatusFilter: (statusFilter) => set({ statusFilter }),

  addCampaign: (formData) => {
    const newCampaign = {
      id: Date.now(),
      user_id: 1,
      name: formData.name,
      description: formData.description || '',
      status: formData.status,
      target_audience: formData.target_audience || 'General Audience',
      budget: formData.budget || 0,
      start_date: formData.start_date || new Date().toISOString().split('T')[0],
      end_date: formData.end_date || '',
      channels: formData.channels || ['LinkedIn'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      reach: 0,
      engagement: 0,
    };

    const updated = [newCampaign, ...get().campaigns];
    localStorage.setItem('marketing_campaigns_list', JSON.stringify(updated));
    set({ campaigns: updated });
  },

  updateCampaign: (id, formData) => {
    const updated = get().campaigns.map((c) =>
      c.id === id
        ? {
            ...c,
            ...formData,
            updated_at: new Date().toISOString(),
          }
        : c
    );
    localStorage.setItem('marketing_campaigns_list', JSON.stringify(updated));
    set({ campaigns: updated });
  },

  deleteCampaign: (id) => {
    const updated = get().campaigns.filter((c) => c.id !== id);
    localStorage.setItem('marketing_campaigns_list', JSON.stringify(updated));
    set({ campaigns: updated });
  },
}));
