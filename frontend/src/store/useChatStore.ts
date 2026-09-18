import { create } from 'zustand';
import { agentService } from '../services/agentService';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  category?: 'strategy' | 'copywriting' | 'seo' | 'analytics' | 'general';
  suggestions?: string[];
  approvalRequestId?: number;
}

interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  threadId: string | null;
  pendingApproval: { id: number; messageId: string } | null;
  selectedCampaignId: number | null;
  agentTone: 'professional' | 'persuasive' | 'viral' | 'casual';
  setSelectedCampaignId: (id: number | null) => void;
  setAgentTone: (tone: 'professional' | 'persuasive' | 'viral' | 'casual') => void;
  sendMessage: (text: string) => Promise<void>;
  approveAction: (reason?: string) => Promise<void>;
  rejectAction: (reason: string) => Promise<void>;
  clearChat: () => void;
}

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: '1',
    sender: 'agent',
    content:
      "Hello! I'm your autonomous **Marketing AI Agent**. I can formulate multi-channel marketing campaigns, generate high-converting social copy, conduct SEO keyword research, and optimize ad performance.\n\nHow can I help you accelerate your marketing goals today?",
    timestamp: new Date(Date.now() - 3600000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    category: 'general',
    suggestions: [
      'Create a 5-day LinkedIn launch sequence for our AI product',
      'Generate 10 viral hooks for Instagram Reels & TikTok',
      'Suggest SEO keywords for enterprise B2B SaaS',
      'Analyze and optimize our Q4 campaign budget allocation',
    ],
  },
];

export const useChatStore = create<ChatState>((set, get) => ({
  messages: INITIAL_MESSAGES,
  isTyping: false,
  threadId: null,
  pendingApproval: null,
  selectedCampaignId: 1,
  agentTone: 'professional',

  setSelectedCampaignId: (selectedCampaignId) => set({ selectedCampaignId }),
  setAgentTone: (agentTone) => set({ agentTone }),

  sendMessage: async (text: string) => {
    let currentThreadId = get().threadId;
    if (!currentThreadId) {
      currentThreadId = `thread-${Date.now()}`;
      set({ threadId: currentThreadId });
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isTyping: true,
      pendingApproval: null,
    }));

    try {
      const response = await agentService.chat({
        thread_id: currentThreadId,
        message: text,
      });

      const messageId = (Date.now() + 1).toString();
      const agentMsg: ChatMessage = {
        id: messageId,
        sender: 'agent',
        content: response.final_response || "Workflow is waiting for approval.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        approvalRequestId: response.approval_required ? response.approval_request_id || undefined : undefined,
      };

      set((state) => ({
        messages: [...state.messages, agentMsg],
        isTyping: false,
        pendingApproval: response.approval_required ? { id: response.approval_request_id!, messageId } : null,
      }));
    } catch (err: unknown) {
      const error = err as { code?: string; response?: { data?: { detail?: string } } };
      const isNetworkError = error?.code === 'ERR_NETWORK' || !error?.response;
      const content = isNetworkError
        ? 'Unable to connect to server. Please try again.'
        : (error?.response?.data?.detail || "Unable to process your request. Please try again.");

      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        content,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      set((state) => ({
        messages: [...state.messages, errorMsg],
        isTyping: false,
      }));
    }
  },

  approveAction: async (reason?: string) => {
    const { pendingApproval, messages } = get();
    if (!pendingApproval) return;

    set({ isTyping: true });

    try {
      const response = await agentService.approveRequest(pendingApproval.id, reason);
      const messageId = (Date.now() + 1).toString();
      
      const updatedMessages = messages.map(m => 
        m.id === pendingApproval.messageId ? { ...m, approvalRequestId: undefined } : m
      );

      const agentMsg: ChatMessage = {
        id: messageId,
        sender: 'agent',
        content: response.final_response || "Action approved successfully.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      set({
        messages: [...updatedMessages, agentMsg],
        isTyping: false,
        pendingApproval: null,
      });
    } catch (error) {
      set({ isTyping: false });
    }
  },

  rejectAction: async (reason: string) => {
    const { pendingApproval, messages } = get();
    if (!pendingApproval) return;

    set({ isTyping: true });

    try {
      const response = await agentService.rejectRequest(pendingApproval.id, reason);
      const messageId = (Date.now() + 1).toString();
      
      const updatedMessages = messages.map(m => 
        m.id === pendingApproval.messageId ? { ...m, approvalRequestId: undefined } : m
      );

      const agentMsg: ChatMessage = {
        id: messageId,
        sender: 'agent',
        content: response.final_response || "Action was rejected. Workflow terminated.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      set({
        messages: [...updatedMessages, agentMsg],
        isTyping: false,
        pendingApproval: null,
      });
    } catch (error) {
      set({ isTyping: false });
    }
  },

  clearChat: () => {
    set({ messages: INITIAL_MESSAGES, threadId: null, pendingApproval: null });
  },
}));
