import api, { IS_DEV_FALLBACK_ENABLED } from './api';
import type { Campaign } from '@/types';
import type { CampaignFormData } from '@/store/useCampaignStore';

export interface CampaignListApiResponse {
  items: Campaign[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const campaignService = {
  /**
   * Fetch paginated and filtered campaigns from backend API
   */
  async listCampaigns(params?: {
    status?: string;
    search?: string;
    page?: number;
    size?: number;
  }): Promise<CampaignListApiResponse> {
    try {
      const response = await api.get<CampaignListApiResponse>('/campaigns/', {
        params: {
          status: params?.status && params.status !== 'all' ? params.status : undefined,
          search: params?.search || undefined,
          page: params?.page || 1,
          size: params?.size || 50,
        },
      });
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        console.warn('[DEV MOCK ACTIVE] Backend server offline. Returning local development campaigns.');
        const local = JSON.parse(localStorage.getItem('marketing_campaigns_list') || '[]');
        return {
          items: local,
          total: local.length,
          page: 1,
          size: 50,
          pages: 1,
        };
      }
      throw err;
    }
  },

  /**
   * Create campaign via backend API
   */
  async createCampaign(data: CampaignFormData): Promise<Campaign> {
    try {
      const response = await api.post<Campaign>('/campaigns/', {
        name: data.name,
        description: data.description,
        status: data.status,
        target_audience: data.target_audience,
        budget: data.budget,
        start_date: data.start_date ? new Date(data.start_date).toISOString() : undefined,
        end_date: data.end_date ? new Date(data.end_date).toISOString() : undefined,
      });
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (IS_DEV_FALLBACK_ENABLED && (!error.response || error.code === 'ERR_NETWORK')) {
        console.warn('[DEV MOCK ACTIVE] Backend server offline. Creating local mock campaign.');
        const fallback: Campaign = {
          id: Date.now(),
          user_id: 1,
          name: data.name,
          description: data.description || null,
          status: data.status,
          target_audience: data.target_audience || null,
          budget: data.budget || null,
          start_date: data.start_date || null,
          end_date: data.end_date || null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        return fallback;
      }
      throw err;
    }
  },

  /**
   * Update campaign
   */
  async updateCampaign(id: number, data: Partial<CampaignFormData>): Promise<Campaign> {
    const response = await api.put<Campaign>(`/campaigns/${id}`, data);
    return response.data;
  },

  /**
   * Delete campaign
   */
  async deleteCampaign(id: number): Promise<void> {
    await api.delete(`/campaigns/${id}`);
  },

  /**
   * Update status
   */
  async updateStatus(id: number, status: string): Promise<Campaign> {
    const response = await api.patch<Campaign>(`/campaigns/${id}/status`, { status });
    return response.data;
  },
};

export default campaignService;
