import { create } from 'zustand';

export interface AISettings {
  model: string;
  temperature: number;
  maxTokens: number;
  defaultTone: string;
  systemPrompt: string;
  enableAutoReview: boolean;
  enableRagSearch: boolean;
}

export interface FacebookPage {
  id: string;
  name: string;
}

export interface PlatformIntegration {
  id: string;
  name: string;
  category: string;
  connected: boolean;
  accountName?: string;
  lastSynced?: string;
  icon: string;
  pages?: FacebookPage[];
  selectedPageId?: string;
}

interface SettingsState {
  aiSettings: AISettings;
  integrations: PlatformIntegration[];
  emailNotifications: boolean;
  weeklyReports: boolean;
  theme: 'dark' | 'light' | 'system';
  updateAISettings: (newSettings: Partial<AISettings>) => void;
  toggleIntegration: (id: string) => void;
  updateNotificationSettings: (notifications: { emailNotifications?: boolean; weeklyReports?: boolean }) => void;
  fetchLinkedInStatus: () => Promise<void>;
  connectLinkedIn: () => Promise<void>;
  fetchFacebookStatus: () => Promise<void>;
  connectFacebook: () => Promise<void>;
  selectFacebookPage: (pageId: string) => Promise<void>;
  fetchInstagramStatus: () => Promise<void>;
  connectInstagram: () => Promise<void>;
  selectInstagramAccount: (accountId: string) => Promise<void>;
  fetchTwitterStatus: () => Promise<void>;
  connectTwitter: () => Promise<void>;
}

const DEFAULT_AI_SETTINGS: AISettings = {
  model: 'qwen3:latest',
  temperature: 0.7,
  maxTokens: 2048,
  defaultTone: 'professional',
  systemPrompt:
    'You are an expert Marketing AI Agent. You create high-converting marketing campaigns, write compelling B2B and B2C copy, and optimize ad metrics across LinkedIn, Twitter/X, Instagram, and Facebook.',
  enableAutoReview: true,
  enableRagSearch: true,
};

const DEFAULT_INTEGRATIONS: PlatformIntegration[] = [
  {
    id: 'linkedin',
    name: 'LinkedIn Business',
    category: 'Social Media',
    connected: false,
    accountName: 'Not Connected',
    icon: 'linkedin',
  },
  {
    id: 'twitter',
    name: 'Twitter / X',
    category: 'Social Media',
    connected: true,
    accountName: '@acmegrowth',
    lastSynced: '25 mins ago',
    icon: 'twitter',
  },
  {
    id: 'facebook',
    name: 'Facebook Pages',
    category: 'Social Media',
    connected: false,
    accountName: 'Not Connected',
    icon: 'facebook',
    pages: [],
  },
  {
    id: 'instagram',
    name: 'Instagram Business',
    category: 'Social Media',
    connected: false,
    accountName: 'Not Connected',
    icon: 'instagram',
    pages: [], // using 'pages' to represent 'accounts' for UI reuse
  },
  {
    id: 'qdrant',
    name: 'Qdrant Vector Database',
    category: 'AI Knowledge / RAG',
    connected: true,
    accountName: 'marketing_documents (384-dim)',
    lastSynced: 'Just now',
    icon: 'database',
  },
  {
    id: 'ollama',
    name: 'Ollama LLM Engine',
    category: 'AI Runtime',
    connected: true,
    accountName: 'qwen3:latest',
    lastSynced: 'Active',
    icon: 'bot',
  },
];

import { integrationService } from '../services/integrationService';

export const useSettingsStore = create<SettingsState>((set, get) => ({
  aiSettings: DEFAULT_AI_SETTINGS,
  integrations: DEFAULT_INTEGRATIONS,
  emailNotifications: true,
  weeklyReports: true,
  theme: 'dark',

  updateAISettings: (newSettings) =>
    set({ aiSettings: { ...get().aiSettings, ...newSettings } }),

  toggleIntegration: (id) => {
    if (id === 'linkedin') {
      const integration = get().integrations.find(i => i.id === 'linkedin');
      if (!integration?.connected) {
        get().connectLinkedIn();
        return;
      }
    }
    if (id === 'facebook') {
      const integration = get().integrations.find(i => i.id === 'facebook');
      if (!integration?.connected) {
        get().connectFacebook();
        return;
      }
    }
    if (id === 'instagram') {
      const integration = get().integrations.find(i => i.id === 'instagram');
      if (!integration?.connected) {
        get().connectInstagram();
        return;
      }
    }
    if (id === 'twitter') {
      const integration = get().integrations.find(i => i.id === 'twitter');
      if (!integration?.connected) {
        get().connectTwitter();
        return;
      }
    }
    
    set({
      integrations: get().integrations.map((item) =>
        item.id === id
          ? {
              ...item,
              connected: !item.connected,
              lastSynced: !item.connected ? 'Just now' : undefined,
              accountName: !item.connected ? item.accountName : 'Not Connected',
            }
          : item
      ),
    });
  },

  updateNotificationSettings: (notifications) =>
    set((state) => ({ ...state, ...notifications })),
    
  fetchLinkedInStatus: async () => {
    try {
      const data = await integrationService.getLinkedInStatus();
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'linkedin'
            ? {
                ...item,
                connected: data.connected,
                accountName: data.connected ? (data.account_name || 'LinkedIn Account') : 'Not Connected',
                lastSynced: data.connected ? 'Just now' : undefined,
              }
            : item
        ),
      });
    } catch (error) {
      console.error('Failed to fetch LinkedIn status', error);
    }
  },
  
  connectLinkedIn: async () => {
    try {
      const data = await integrationService.getLinkedInAuthUrl();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Failed to get LinkedIn auth URL', error);
    }
  },

  fetchFacebookStatus: async () => {
    try {
      const data = await integrationService.getFacebookStatus();
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'facebook'
            ? {
                ...item,
                connected: data.connected,
                accountName: data.connected
                  ? (data.account_name || 'Facebook Account')
                  : 'Not Connected',
                lastSynced: data.connected ? 'Just now' : undefined,
                pages: (data.pages || []).map((p: { id: string; name: string }) => ({
                  id: p.id,
                  name: p.name,
                })),
                selectedPageId: data.selected_page?.id,
              }
            : item
        ),
      });
    } catch (error) {
      console.error('Failed to fetch Facebook status', error);
    }
  },

  connectFacebook: async () => {
    try {
      const data = await integrationService.getFacebookAuthUrl();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Failed to get Facebook auth URL', error);
    }
  },

  selectFacebookPage: async (pageId: string) => {
    try {
      await integrationService.selectFacebookPage(pageId);
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'facebook'
            ? { ...item, selectedPageId: pageId }
            : item
        ),
      });
    } catch (error) {
      console.error('Failed to select Facebook Page', error);
    }
  },

  fetchInstagramStatus: async () => {
    try {
      const data = await integrationService.getInstagramStatus();
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'instagram'
            ? {
                ...item,
                connected: data.connected,
                accountName: data.connected
                  ? (data.selected_account?.username || data.accounts?.[0]?.username || 'Instagram Business')
                  : 'Not Connected',
                lastSynced: data.connected ? 'Just now' : undefined,
                pages: (data.accounts || []).map((a: { id: string; username: string }) => ({
                  id: a.id,
                  name: `@${a.username}`,
                })),
                selectedPageId: data.selected_account?.id,
              }
            : item
        ),
      });
    } catch (error) {
      console.error('Failed to fetch Instagram status', error);
    }
  },

  connectInstagram: async () => {
    try {
      const data = await integrationService.getInstagramAuthUrl();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Failed to get Instagram auth URL', error);
    }
  },

  selectInstagramAccount: async (accountId: string) => {
    try {
      await integrationService.selectInstagramAccount(accountId);
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'instagram'
            ? { ...item, selectedPageId: accountId }
            : item
        ),
      });
      // Refresh status to get the updated accountName
      get().fetchInstagramStatus();
    } catch (error) {
      console.error('Failed to select Instagram Account', error);
    }
  },

  fetchTwitterStatus: async () => {
    try {
      const data = await integrationService.getTwitterStatus();
      set({
        integrations: get().integrations.map((item) =>
          item.id === 'twitter'
            ? {
                ...item,
                connected: data.connected,
                accountName: data.connected ? data.account_name : 'Not Connected',
                lastSynced: data.connected ? 'Just now' : undefined,
              }
            : item
        ),
      });
    } catch (error) {
      console.error('Failed to fetch Twitter status', error);
    }
  },

  connectTwitter: async () => {
    try {
      const data = await integrationService.getTwitterAuthUrl();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Failed to get Twitter auth URL', error);
    }
  },
}));
