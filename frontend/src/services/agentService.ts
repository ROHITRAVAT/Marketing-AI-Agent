import api from './api';

export interface AgentChatRequest {
  thread_id: string;
  message: string;
  mode?: 'workflow' | 'copilot';
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
  content: Record<string, unknown>;
  status: string;
  reason: string | null;
  rejection_reason: string | null;
  final_response: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentChatJobResponse {
  job_id: string;
  status: string;
}

export interface AgentJobStatusResponse {
  job_id: string;
  status: string;
  result: AgentChatResponse | null;
  error: string | null;
}

export const agentService = {
  chat: async (data: AgentChatRequest): Promise<AgentChatResponse> => {
    // 1. Submit the job
    const submitResponse = await api.post<AgentChatJobResponse>('/agent/chat', {
      ...data,
      mode: data.mode || 'copilot',
    });
    
    const jobId = submitResponse.data.job_id;
    
    // 2. Poll until completed, failed, or approval_pending
    while (true) {
      // Wait 2 seconds before polling
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      const statusResponse = await api.get<AgentJobStatusResponse>(`/agent/jobs/${jobId}`);
      const statusData = statusResponse.data;
      
      if (statusData.status === 'completed' || statusData.status === 'approval_pending') {
        if (statusData.result) {
          return statusData.result;
        }
        throw new Error('Job completed but no result was provided.');
      } else if (statusData.status === 'failed') {
        throw new Error(statusData.error || 'Agent job failed');
      }
      
      // If queued or running, continue polling
    }
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

export default agentService;
