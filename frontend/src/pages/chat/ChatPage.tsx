import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  Copy,
  Check,
  Trash2,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { useCampaignStore } from '@/store/useCampaignStore';
import { Button } from '@/components/ui/Button';

export const ChatPage: React.FC = () => {
  const { messages, isTyping, agentTone, setAgentTone, selectedCampaignId, setSelectedCampaignId, sendMessage, clearChat, approveAction, rejectAction } =
    useChatStore();
  const { campaigns } = useCampaignStore();

  const [input, setInput] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;
    const text = input;
    setInput('');
    await sendMessage(text);
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const quickPrompts = [
    'Create a 5-day LinkedIn launch sequence for our AI product',
    'Generate 10 viral hooks for Instagram Reels & TikTok',
    'Suggest targeted SEO keywords for B2B SaaS',
    'Write high-converting cold email outreach copy',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto space-y-4">
      {/* Top Controls Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 p-3.5 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              Marketing AI Agent <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30">Online</span>
            </h2>
            <p className="text-xs text-slate-400">Qwen 3 + LangGraph Autonomous Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          {/* Tone Selector */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1.5 rounded-xl border border-slate-800">
            <span className="text-slate-400">Tone:</span>
            <select
              value={agentTone}
              onChange={(e) => setAgentTone(e.target.value as 'professional' | 'persuasive' | 'viral' | 'casual')}
              className="bg-transparent text-indigo-300 font-medium focus:outline-none cursor-pointer"
            >
              <option value="professional" className="bg-slate-900">Professional</option>
              <option value="persuasive" className="bg-slate-900">Persuasive</option>
              <option value="viral" className="bg-slate-900">Viral / Punchy</option>
              <option value="casual" className="bg-slate-900">Casual / Friendly</option>
            </select>
          </div>

          {/* Campaign Context Link */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1.5 rounded-xl border border-slate-800">
            <span className="text-slate-400">Campaign:</span>
            <select
              value={selectedCampaignId || ''}
              onChange={(e) => setSelectedCampaignId(Number(e.target.value) || null)}
              className="bg-transparent text-indigo-300 font-medium focus:outline-none cursor-pointer max-w-[140px] truncate"
            >
              <option value="" className="bg-slate-900">All Campaigns</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900">
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={clearChat}
            title="Clear Chat History"
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-xl transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 sm:p-6 overflow-y-auto space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'agent' && (
              <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 mt-1">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className="space-y-2 max-w-2xl">
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/80 rounded-tl-none shadow-md'
                }`}
              >
                <div className="whitespace-pre-wrap font-sans text-[13.5px]">{msg.content}</div>

                {/* Suggestions chips if any */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-700/60 space-y-2">
                    <p className="text-xs text-indigo-300 font-semibold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" /> Suggested Next Steps:
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.suggestions.map((suggestion, i) => (
                        <button
                          key={i}
                          onClick={() => sendMessage(suggestion)}
                          className="text-left text-xs bg-slate-900/80 hover:bg-indigo-900/50 hover:text-indigo-200 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700/80 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Approval UI */}
                {msg.approvalRequestId && (
                  <div className="mt-4 p-4 bg-slate-900/80 border border-amber-500/30 rounded-xl space-y-3">
                    <p className="text-amber-400 text-sm font-medium">Human Approval Required</p>
                    <p className="text-slate-300 text-xs">The agent needs your permission to proceed with the execution.</p>
                    <div className="flex gap-2 mt-2">
                      <Button 
                        onClick={() => approveAction("Looks good to me.")} 
                        className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3 py-1.5 h-8"
                        disabled={isTyping}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approve
                      </Button>
                      <Button 
                        onClick={() => rejectAction("Rejected by user.")} 
                        className="bg-rose-600 hover:bg-rose-500 text-white text-xs px-3 py-1.5 h-8"
                        disabled={isTyping}
                      >
                        <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp & Actions */}
              <div className={`flex items-center gap-2 text-[11px] text-slate-500 px-1 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <span>{msg.timestamp}</span>
                {msg.sender === 'agent' && (
                  <button
                    onClick={() => handleCopy(msg.content, msg.id)}
                    className="hover:text-slate-300 flex items-center gap-1 transition-colors"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1 font-semibold text-xs">
                You
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3.5 justify-start">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
              <Bot className="w-4 h-4 animate-pulse" />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-3.5 flex items-center gap-2 text-xs text-slate-400">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
              <span>Marketing AI is formulating marketing strategy...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Ideas */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-500 font-medium shrink-0 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Prompts:
        </span>
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => sendMessage(p)}
            className="shrink-0 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white rounded-lg border border-slate-800 transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Message Input Box */}
      <form onSubmit={handleSend} className="relative flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Marketing AI to create posts, strategies, ad hooks, or analyze campaigns..."
          className="flex-1 bg-slate-900 border border-slate-800 focus:border-indigo-500 text-white placeholder-slate-500 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all shadow-inner"
        />
        <Button
          type="submit"
          disabled={!input.trim() || isTyping}
          className="px-5 py-3 rounded-xl shadow-indigo-500/20"
          icon={<Send className="w-4 h-4" />}
        >
          Send
        </Button>
      </form>
    </div>
  );
};

export default ChatPage;
