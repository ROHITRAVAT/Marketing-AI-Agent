import { create } from 'zustand';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  category?: 'strategy' | 'copywriting' | 'seo' | 'analytics' | 'general';
  suggestions?: string[];
}

interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  selectedCampaignId: number | null;
  agentTone: 'professional' | 'persuasive' | 'viral' | 'casual';
  setSelectedCampaignId: (id: number | null) => void;
  setAgentTone: (tone: 'professional' | 'persuasive' | 'viral' | 'casual') => void;
  sendMessage: (text: string) => Promise<void>;
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
  selectedCampaignId: 1,
  agentTone: 'professional',

  setSelectedCampaignId: (selectedCampaignId) => set({ selectedCampaignId }),
  setAgentTone: (agentTone) => set({ agentTone }),

  sendMessage: async (text: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isTyping: true,
    }));

    // Generate intelligent contextual response
    setTimeout(() => {
      let agentReply = '';
      const lower = text.toLowerCase();
      const currentTone = get().agentTone;

      if (lower.includes('linkedin') || lower.includes('sequence')) {
        agentReply = `### 🚀 5-Day LinkedIn Launch Sequence (${currentTone.toUpperCase()} TONE)\n\n` +
          `Here is an optimized sequence designed for high organic reach and inbound leads:\n\n` +
          `**Day 1: The Problem Agitation**\n` +
          `> *"Most marketing teams spend 70% of their week executing tasks that an AI agent could solve in 3 minutes. Here's what happens when you automate content orchestration..."*\n\n` +
          `**Day 2: The Data & Benchmark**\n` +
          `> Share key industry benchmark metrics: 4.8x higher engagement when pairing AI keyword clustering with personalized outreach.\n\n` +
          `**Day 3: Behind the Scenes / Case Study**\n` +
          `> Step-by-step breakdown of how one beta customer scaled from 2 to 14 weekly multi-channel campaigns in under 30 minutes.\n\n` +
          `**Day 4: Objection Handling & Proof**\n` +
          `> *"Isn't AI content generic?"* Show side-by-side prompt tuning results using your unique brand guide.\n\n` +
          `**Day 5: The Offer / Soft Launch**\n` +
          `> Clear Call-To-Action inviting followers to request access or join the upcoming interactive demo webinar.`;
      } else if (lower.includes('hook') || lower.includes('viral') || lower.includes('instagram')) {
        agentReply = `### 🔥 10 High-Converting Viral Marketing Hooks\n\n` +
          `1. *"If you're not using autonomous AI workflows for your campaigns in 2026, you're literally burning budget."*\n` +
          `2. *"Stop writing social copy manually. Here is the exact prompt stack that gained us 45k impressions last week:"*\n` +
          `3. *"The secret top 1% growth marketers won't tell you about organic distribution..."*\n` +
          `4. *"Here are 3 marketing mistakes costing your business \$10,000+ every month:"*\n` +
          `5. *"I automated our entire monthly content calendar in 12 minutes using this AI agent flow."*\n` +
          `6. *"Why traditional ad agencies are scrambling right now (and what you should do instead):"*\n` +
          `7. *"Steal our exact B2B funnel that converts cold traffic at 6.8%:"*\n` +
          `8. *"The easiest way to double your LinkedIn engagement without spending a dime on ads:"*\n` +
          `9. *"Here is why 90% of marketing campaigns fail before they even launch:"*\n` +
          `10. *"Bookmark this before your competitors find out about autonomous campaign orchestration."*`;
      } else if (lower.includes('seo') || lower.includes('keyword')) {
        agentReply = `### 🔍 Targeted SEO Keyword Strategy\n\n` +
          `Based on current search intent and competitiveness indices, here are recommended keyword clusters:\n\n` +
          `| Primary Keyword | Monthly Volume | Difficulty | Search Intent |\n` +
          `|---|---|---|---|\n` +
          `| **Autonomous Marketing AI** | 14,200 | 42 (Medium) | Commercial |\n` +
          `| **AI Campaign Orchestration** | 8,900 | 38 (Low) | Informational/Commercial |\n` +
          `| **Automated Social Media Agent** | 22,500 | 54 (High) | Transactional |\n` +
          `| **RAG Marketing Content Engine** | 4,100 | 29 (Low) | Technical / SaaS |\n\n` +
          `**Actionable Tip:** Build a pillar page around *"The Guide to Autonomous Marketing Agents"* and link cluster posts to capture top-of-funnel search volume.`;
      } else {
        agentReply = `### 💡 Strategic Recommendation from Marketing AI Agent\n\n` +
          `I analyzed your prompt: **"${text}"** with **${currentTone}** tone and brand parameters.\n\n` +
          `Here is our recommended course of action:\n\n` +
          `1. **Audience Segmentation:** Focus primarily on Decision Makers (Tech & Marketing) across LinkedIn and Twitter/X.\n` +
          `2. **Key Messaging Angle:** Emphasize speed-to-market, ROI clarity, and verifiable metric improvements.\n` +
          `3. **Content Distribution Schedule:** Deploy daily teaser snippets leading up to the main campaign launch window.\n\n` +
          `Would you like me to draft the full copy or create a scheduled campaign in your campaign dashboard?`;
      }

      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        content: agentReply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        category: 'strategy',
      };

      set((state) => ({
        messages: [...state.messages, agentMsg],
        isTyping: false,
      }));
    }, 1000);
  },

  clearChat: () => {
    set({ messages: INITIAL_MESSAGES });
  },
}));
