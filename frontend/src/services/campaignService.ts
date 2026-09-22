import api from './api';
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
    const response = await api.get<CampaignListApiResponse>('/campaigns/', {
      params: {
        status: params?.status && params.status !== 'all' ? params.status : undefined,
        search: params?.search || undefined,
        page: params?.page || 1,
        size: params?.size || 50,
      },
    });
    return response.data;
  },

  /**
   * Create campaign via backend API
   */
  async createCampaign(data: CampaignFormData, userId: number): Promise<Campaign> {
    const response = await api.post<Campaign>('/campaigns/', {
      user_id: userId,
      name: data.name,
      description: data.description,
      status: data.status,
      target_audience: data.target_audience,
      budget: data.budget,
      start_date: data.start_date ? new Date(data.start_date).toISOString() : undefined,
      end_date: data.end_date ? new Date(data.end_date).toISOString() : undefined,
    });
    return response.data;
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
