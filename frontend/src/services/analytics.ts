import api from './api';

export interface PlatformSummary {
  platform: string;
  total_impressions: number;
  total_engagement: number;
  total_clicks: number;
  total_likes: number;
  total_comments: number;
}

export interface AnalyticsSummaryResponse {
  start_date: string;
  end_date: string;
  platforms: PlatformSummary[];
  total_posts_analyzed: number;
  overall_impressions: number;
  overall_engagement: number;
}

export interface SocialAnalyticsResponse {
  id: number;
  user_id: number;
  campaign_id?: number;
  scheduled_post_id?: number;
  platform: string;
  external_post_id: string;
  metric_date: string;
  impressions?: number;
  reach?: number;
  engagement?: number;
  clicks?: number;
  likes?: number;
  comments?: number;
  shares?: number;
  saves?: number;
  video_views?: number;
  followers?: number;
  collected_at: string;
}

export interface ScheduledPostResponse {
  id: number;
  platform: string;
  content?: string;
  scheduled_time: string;
  status: string;
  published_at?: string;
  external_post_id?: string;
}

export const analyticsService = {
  getSummary: async (
    startDate: string,
    endDate: string,
    platforms?: string,
    campaignId?: number
  ): Promise<AnalyticsSummaryResponse> => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    if (platforms) params.append('platforms', platforms);
    if (campaignId) params.append('campaign_id', campaignId.toString());

    const response = await api.get(`/api/v1/analytics/summary?${params.toString()}`);
    return response.data;
  },

  getPostAnalytics: async (postId: string): Promise<SocialAnalyticsResponse[]> => {
    const response = await api.get(`/api/v1/analytics/posts/${postId}`);
    return response.data;
  },

  listPublishedPosts: async (): Promise<ScheduledPostResponse[]> => {
    const response = await api.get<ScheduledPostResponse[]>('/scheduled-posts/', {
      params: { status_filter: 'published' },
    });
    return response.data;
  },
};
