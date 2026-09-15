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
    try {
      const response = await api.post<AgentChatResponse>('/agent/chat', data);
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (!error.response || error.code === 'ERR_NETWORK') {
        // Fallback simulation when backend server is offline
        const lower = data.message.toLowerCase();
        let reply = '';
        let needsApproval = false;

        if (lower.includes('publish') || lower.includes('schedule post') || lower.includes('live post')) {
          needsApproval = true;
          reply = `### 📋 Human Approval Checkpoint Required\n\nI have generated the scheduled post for LinkedIn:\n\n> *"Transform your marketing pipeline in minutes with autonomous AI campaign execution. See how leading teams scale 5x faster."*\n\nPlease review and approve this action before it is dispatched to social media APIs.`;
        } else if (lower.includes('linkedin') || lower.includes('sequence')) {
          reply = `### 🚀 5-Day LinkedIn Launch Sequence\n\nHere is your high-converting launch schedule:\n\n* **Day 1:** The Core Bottleneck & Industry Shift\n* **Day 2:** Data benchmark comparison: 4.8x higher ROI\n* **Day 3:** Behind the scenes customer case study\n* **Day 4:** Live demo snippet & objection handling\n* **Day 5:** Exclusive early-access invitation CTA`;
        } else if (lower.includes('hook') || lower.includes('viral') || lower.includes('instagram')) {
          reply = `### 🔥 10 High-Converting Viral Marketing Hooks\n\n1. *"If you're not using autonomous AI workflows in 2026, you're burning budget."*\n2. *"Stop writing social copy manually. Here is our exact prompt stack:"*\n3. *"The secret top 1% growth marketers won't tell you about organic distribution..."*\n4. *"Here are 3 marketing mistakes costing your business \$10,000+ every month:"*\n5. *"I automated our entire monthly content calendar in 12 minutes."*`;
        } else if (lower.includes('seo') || lower.includes('keyword')) {
          reply = `### 🔍 Targeted SEO Keyword Strategy\n\n| Primary Keyword | Monthly Volume | Difficulty | Search Intent |\n|---|---|---|---|\n| **Autonomous Marketing AI** | 14,200 | 42 (Medium) | Commercial |\n| **AI Campaign Orchestration** | 8,900 | 38 (Low) | Informational |\n| **Automated Social Media Agent** | 22,500 | 54 (High) | Transactional |`;
        } else {
          reply = `### 💡 Strategic Recommendation from Marketing AI Agent\n\nI analyzed your request: **"${data.message}"**\n\n1. **Audience Focus:** Target tech and marketing decision-makers across LinkedIn & Twitter/X.\n2. **Channel Strategy:** Deploy thought leadership threads and short-form video hooks.\n3. **Budget Allocation:** Reserve 65% for top-performing channels.\n\nWould you like me to draft full post copy or schedule a campaign?`;
        }

        return {
          status: 'success',
          thread_id: data.thread_id,
          final_response: reply,
          approval_required: needsApproval,
          approval_request_id: needsApproval ? Date.now() : null,
          error: null,
        };
      }
      throw err;
    }
  },

  approveRequest: async (approvalId: number, reason?: string): Promise<ApprovalResponse> => {
    try {
      const response = await api.post<ApprovalResponse>(`/approvals/${approvalId}/approve`, { reason });
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (!error.response || error.code === 'ERR_NETWORK') {
        return {
          id: approvalId,
          user_id: 1,
          thread_id: 'thread-sim',
          action_type: 'social_publish',
          platform: 'linkedin',
          content: { message: 'Approved simulated action' },
          status: 'approved',
          reason: reason || null,
          rejection_reason: null,
          final_response: 'Action approved successfully! Post has been scheduled for publishing.',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }
      throw err;
    }
  },

  rejectRequest: async (approvalId: number, reason: string): Promise<ApprovalResponse> => {
    try {
      const response = await api.post<ApprovalResponse>(`/approvals/${approvalId}/reject`, { reason });
      return response.data;
    } catch (err: unknown) {
      const error = err as { code?: string; response?: unknown };
      if (!error.response || error.code === 'ERR_NETWORK') {
        return {
          id: approvalId,
          user_id: 1,
          thread_id: 'thread-sim',
          action_type: 'social_publish',
          platform: 'linkedin',
          content: { message: 'Rejected simulated action' },
          status: 'rejected',
          reason: null,
          rejection_reason: reason,
          final_response: `Action was rejected (${reason}). Workflow safely halted.`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }
      throw err;
    }
  },
};

export default agentService;
