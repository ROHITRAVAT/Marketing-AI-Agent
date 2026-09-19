import React, { useState } from 'react';
import {
  Share2,
  Bell,
  CheckCircle2,
  Save,
  Cpu,
  Bot,
  Database,
} from 'lucide-react';
import { useSettingsStore } from '@/store/useSettingsStore';
import { Button } from '@/components/ui/Button';

export const SettingsPage: React.FC = () => {
  const {
    aiSettings,
    integrations,
    emailNotifications,
    weeklyReports,
    updateAISettings,
    toggleIntegration,
    updateNotificationSettings,
    fetchLinkedInStatus,
    fetchFacebookStatus,
    selectFacebookPage,
    fetchInstagramStatus,
    selectInstagramAccount,
    fetchTwitterStatus,
  } = useSettingsStore();

  React.useEffect(() => {
    fetchLinkedInStatus();
    fetchFacebookStatus();
    fetchInstagramStatus();
    fetchTwitterStatus();
  }, [fetchLinkedInStatus, fetchFacebookStatus, fetchInstagramStatus, fetchTwitterStatus]);

  const [activeTab, setActiveTab] = useState<'integrations' | 'ai' | 'notifications'>('integrations');
  const [saveBanner, setSaveBanner] = useState(false);

  // Local AI form state
  const [model, setModel] = useState(aiSettings.model);
  const [temperature, setTemperature] = useState(aiSettings.temperature);
  const [maxTokens, setMaxTokens] = useState(aiSettings.maxTokens);
  const [defaultTone, setDefaultTone] = useState(aiSettings.defaultTone);
  const [systemPrompt, setSystemPrompt] = useState(aiSettings.systemPrompt);
  const [enableAutoReview, setEnableAutoReview] = useState(aiSettings.enableAutoReview);
  const [enableRagSearch, setEnableRagSearch] = useState(aiSettings.enableRagSearch);

  const handleSaveAI = (e: React.FormEvent) => {
    e.preventDefault();
    updateAISettings({
      model,
      temperature,
      maxTokens,
      defaultTone,
      systemPrompt,
      enableAutoReview,
      enableRagSearch,
    });
    setSaveBanner(true);
    setTimeout(() => setSaveBanner(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Settings & Integrations</h2>
        <p className="text-sm text-slate-400">
          Configure platform integrations, AI agent parameters, and notification preferences.
        </p>
      </div>

      {saveBanner && (
        <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4 flex items-center gap-3 text-emerald-300 text-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>Settings saved successfully. Changes applied to active AI agent workflows.</span>
        </div>
      )}

      {/* Tabs Bar */}
      <div className="border-b border-slate-800 flex gap-6">
        <button
          onClick={() => setActiveTab('integrations')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'integrations'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Share2 className="w-4 h-4" />
          Platform Integrations ({integrations.filter((i) => i.connected).length} Connected)
        </button>

        <button
          onClick={() => setActiveTab('ai')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'ai'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Cpu className="w-4 h-4" />
          AI Model & Agent Preferences
        </button>

        <button
          onClick={() => setActiveTab('notifications')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'notifications'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Bell className="w-4 h-4" />
          Notifications & System
        </button>
      </div>

      {/* Tab 1: Platform Integrations */}
      {activeTab === 'integrations' && (
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h3 className="text-base font-bold text-white">Connected Marketing & AI Channels</h3>
            <p className="text-xs text-slate-400 mt-1">
              Connect external social accounts and backend AI engines to enable automated publishing and retrieval.
            </p>

            <div className="divide-y divide-slate-800 mt-6">
              {integrations.map((item) => (
                <div
                  key={item.id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-indigo-400">
                      {item.id === 'qdrant' ? (
                        <Database className="w-5 h-5" />
                      ) : item.id === 'ollama' ? (
                        <Bot className="w-5 h-5" />
                      ) : (
                        <Share2 className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-white">{item.name}</h4>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {item.accountName}{' '}
                        {item.lastSynced && (
                          <span className="text-slate-500">· Synced {item.lastSynced}</span>
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        item.connected
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          item.connected ? 'bg-emerald-400' : 'bg-slate-500'
                        }`}
                      />
                      {item.connected ? 'Connected' : 'Disconnected'}
                    </span>

                    <button
                      onClick={() => toggleIntegration(item.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                        item.connected
                          ? 'border-slate-700 bg-slate-800/80 hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/30 text-slate-300'
                          : 'bg-indigo-600 hover:bg-indigo-500 text-white border-indigo-500 shadow-sm'
                      }`}
                    >
                      {item.connected ? 'Disconnect' : 'Connect'}
                    </button>
                  </div>

                  {/* Facebook Page Selector */}
                  {item.id === 'facebook' && item.connected && item.pages && item.pages.length > 0 && (
                    <div className="w-full mt-2 pl-[3.375rem]">
                      <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                        Publishing Page
                      </label>
                      <select
                        value={item.selectedPageId || ''}
                        onChange={(e) => selectFacebookPage(e.target.value)}
                        className="w-full max-w-xs bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        {item.pages.map((page) => (
                          <option key={page.id} value={page.id}>
                            {page.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Instagram Account Selector */}
                  {item.id === 'instagram' && item.connected && item.pages && item.pages.length > 0 && (
                    <div className="w-full mt-2 pl-[3.375rem]">
                      <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                        Publishing Account
                      </label>
                      <select
                        value={item.selectedPageId || ''}
                        onChange={(e) => selectInstagramAccount(e.target.value)}
                        className="w-full max-w-xs bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        {item.pages.map((page) => (
                          <option key={page.id} value={page.id}>
                            {page.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: AI Preferences */}
      {activeTab === 'ai' && (
        <form onSubmit={handleSaveAI} className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
            <div>
              <h3 className="text-base font-bold text-white">Language Model & Generation Parameters</h3>
              <p className="text-xs text-slate-400 mt-1">
                Fine-tune how the LangGraph Marketing Agent reasons, writes, and cites company knowledge.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Primary LLM Engine
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="qwen3:latest">Qwen 3 (Local Ollama - High Speed)</option>
                  <option value="llama3.3:70b">Llama 3.3 70B (Enterprise Reasoning)</option>
                  <option value="deepseek-r1:latest">DeepSeek R1 (Strategic Planning)</option>
                  <option value="gpt-4o">GPT-4o (Cloud API)</option>
                </select>
                <p className="text-[11px] text-slate-500">Connected to local Ollama inference service.</p>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Default Content Tone
                </label>
                <select
                  value={defaultTone}
                  onChange={(e) => setDefaultTone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="professional">Professional / B2B Authority</option>
                  <option value="persuasive">Persuasive / High-Converting</option>
                  <option value="viral">Viral / Punchy / Hooks</option>
                  <option value="casual">Casual / Engaging</option>
                </select>
                <p className="text-[11px] text-slate-500">Applied automatically during prompt expansion.</p>
              </div>
            </div>

            {/* Temperature & Max Tokens Sliders */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <label className="font-semibold uppercase tracking-wider text-slate-300">
                    Creativity / Temperature ({temperature})
                  </label>
                  <span className="text-indigo-400 font-medium">
                    {temperature <= 0.3 ? 'Deterministic' : temperature <= 0.7 ? 'Balanced' : 'Creative'}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-indigo-600 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <label className="font-semibold uppercase tracking-wider text-slate-300">
                    Max Output Length ({maxTokens} tokens)
                  </label>
                  <span className="text-indigo-400 font-medium">
                    ~{Math.round(maxTokens * 0.75)} words
                  </span>
                </div>
                <input
                  type="range"
                  min="512"
                  max="4096"
                  step="256"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full accent-indigo-600 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* Brand Voice / System Prompt */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Custom Brand Voice & System Directive
              </label>
              <textarea
                rows={4}
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-lg p-3 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono leading-relaxed"
              />
              <p className="text-[11px] text-slate-500">
                Injects custom brand guidelines and terminology into all LangGraph generation nodes.
              </p>
            </div>

            {/* Agent Workflow Switches */}
            <div className="space-y-3 pt-3 border-t border-slate-800">
              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
                <div>
                  <span className="text-sm font-semibold text-white block">Auto Review Node</span>
                  <span className="text-xs text-slate-400">
                    Agent automatically evaluates content against brand criteria before publishing.
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={enableAutoReview}
                  onChange={(e) => setEnableAutoReview(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
                <div>
                  <span className="text-sm font-semibold text-white block">RAG Context Search (Qdrant)</span>
                  <span className="text-xs text-slate-400">
                    Retrieves internal brand manuals and PDF assets to ground generated marketing copy.
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={enableRagSearch}
                  onChange={(e) => setEnableRagSearch(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
                />
              </label>
            </div>

            <div className="flex justify-end pt-2">
              <Button type="submit" icon={<Save className="w-4 h-4" />}>
                Save AI Configuration
              </Button>
            </div>
          </div>
        </form>
      )}

      {/* Tab 3: Notifications & System */}
      {activeTab === 'notifications' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div>
            <h3 className="text-base font-bold text-white">Notification & Delivery Preferences</h3>
            <p className="text-xs text-slate-400 mt-1">Configure automated email summaries and threshold alerts.</p>
          </div>

          <div className="space-y-4">
            <label className="flex items-center justify-between p-4 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
              <div>
                <span className="text-sm font-semibold text-white block">Campaign Milestones Email</span>
                <span className="text-xs text-slate-400">
                  Receive alerts when a scheduled post goes live or reaches 10k impressions.
                </span>
              </div>
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => updateNotificationSettings({ emailNotifications: e.target.checked })}
                className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
              />
            </label>

            <label className="flex items-center justify-between p-4 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer">
              <div>
                <span className="text-sm font-semibold text-white block">Weekly Executive Performance Digest</span>
                <span className="text-xs text-slate-400">
                  Delivers a consolidated weekly summary of ROI, conversions, and AI suggestions every Monday.
                </span>
              </div>
              <input
                type="checkbox"
                checked={weeklyReports}
                onChange={(e) => updateNotificationSettings({ weeklyReports: e.target.checked })}
                className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700"
              />
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
