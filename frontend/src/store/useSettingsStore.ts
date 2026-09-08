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

export interface PlatformIntegration {
  id: string;
  name: string;
  category: string;
  connected: boolean;
  accountName?: string;
  lastSynced?: string;
  icon: string;
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
    connected: true,
    accountName: 'Acme Growth Labs',
    lastSynced: '10 mins ago',
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
    id: 'meta',
    name: 'Meta (Instagram & Facebook)',
    category: 'Social Media',
    connected: false,
    accountName: 'Not Connected',
    icon: 'instagram',
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

export const useSettingsStore = create<SettingsState>((set, get) => ({
  aiSettings: DEFAULT_AI_SETTINGS,
  integrations: DEFAULT_INTEGRATIONS,
  emailNotifications: true,
  weeklyReports: true,
  theme: 'dark',

  updateAISettings: (newSettings) =>
    set({ aiSettings: { ...get().aiSettings, ...newSettings } }),

  toggleIntegration: (id) =>
    set({
      integrations: get().integrations.map((item) =>
        item.id === id
          ? {
              ...item,
              connected: !item.connected,
              lastSynced: !item.connected ? 'Just now' : undefined,
            }
          : item
      ),
    }),

  updateNotificationSettings: (notifications) =>
    set((state) => ({ ...state, ...notifications })),
}));
