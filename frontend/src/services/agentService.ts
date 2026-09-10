import api from './api';

export interface AgentChatRequest {
  thread_id: string;
  message: string;
  product?: string;
  target_audience?: string;
  platform?: string;
  campaign_goal?: string;
}

export interface AgentChatResponse {
  status: string;
  thread_id: string;
  final_response: string | null;
  approval_required: boolean;
  approval_request_id: number | null;
  error: string | null;
}

export interface ApprovalResponse {
  id: number;
  user_id: number;
  thread_id: string;
  action_type: string;
  platform: string | null;
  content: Record<string, any>;
  status: string;
  reason: string | null;
  rejection_reason: string | null;
  final_response: string | null;
  created_at: string;
  updated_at: string;
}

export const agentService = {
  chat: async (data: AgentChatRequest): Promise<AgentChatResponse> => {
    const response = await api.post<AgentChatResponse>('/agent/chat', data);
    return response.data;
  },

  approveRequest: async (approvalId: number, reason?: string): Promise<ApprovalResponse> => {
    const response = await api.post<ApprovalResponse>(`/approvals/${approvalId}/approve`, { reason });
    return response.data;
  },

  rejectRequest: async (approvalId: number, reason: string): Promise<ApprovalResponse> => {
    const response = await api.post<ApprovalResponse>(`/approvals/${approvalId}/reject`, { reason });
    return response.data;
  },
};
