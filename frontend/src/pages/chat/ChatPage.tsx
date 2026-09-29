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
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-[#E8E8E3] p-4 rounded-2xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B]">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-[#18181B] flex items-center gap-2">
              Marketing AI Agent{' '}
              <span className="text-[10px] font-mono uppercase bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-200 font-semibold">
                Online
              </span>
            </h2>
            <p className="text-xs text-[#71717A]">Qwen 3 8B + LangGraph Autonomous Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          {/* Tone Selector */}
          <div className="flex items-center gap-1.5 bg-[#F3F3EE] px-3 py-1.5 rounded-xl border border-[#E4E4DC]">
            <span className="text-[11px] font-mono uppercase text-[#71717A]">Tone:</span>
            <select
              value={agentTone}
              onChange={(e) => setAgentTone(e.target.value as 'professional' | 'persuasive' | 'viral' | 'casual')}
              className="bg-transparent text-[#18181B] text-xs font-semibold focus:outline-none cursor-pointer"
            >
              <option value="professional" className="bg-white text-[#18181B]">Professional</option>
              <option value="persuasive" className="bg-white text-[#18181B]">Persuasive</option>
              <option value="viral" className="bg-white text-[#18181B]">Viral / Punchy</option>
              <option value="casual" className="bg-white text-[#18181B]">Casual / Friendly</option>
            </select>
          </div>

          {/* Campaign Context Link */}
          <div className="flex items-center gap-1.5 bg-[#F3F3EE] px-3 py-1.5 rounded-xl border border-[#E4E4DC]">
            <span className="text-[11px] font-mono uppercase text-[#71717A]">Campaign:</span>
            <select
              value={selectedCampaignId || ''}
              onChange={(e) => setSelectedCampaignId(Number(e.target.value) || null)}
              className="bg-transparent text-[#18181B] text-xs font-semibold focus:outline-none cursor-pointer max-w-[140px] truncate"
            >
              <option value="" className="bg-white text-[#18181B]">All Campaigns</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id} className="bg-white text-[#18181B]">
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={clearChat}
            title="Clear Chat History"
            className="p-2 text-[#71717A] hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 bg-white border border-[#E8E8E3] rounded-2xl p-4 sm:p-6 overflow-y-auto space-y-6 shadow-xs">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'agent' && (
              <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B] shrink-0 mt-1 shadow-2xs">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className="space-y-2 max-w-2xl">
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-[#18181B] text-white rounded-tr-none shadow-xs'
                    : 'bg-[#F8F8F6] text-[#18181B] border border-[#E8E8E3] rounded-tl-none shadow-2xs'
                }`}
              >
                <div className="whitespace-pre-wrap font-sans text-[13.5px]">{msg.content}</div>

                {/* Suggestions chips if any */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-[#E8E8E3] space-y-2">
                    <p className="text-xs text-[#18181B] font-semibold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Suggested Next Steps:
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.suggestions.map((suggestion, i) => (
                        <button
                          key={i}
                          onClick={() => sendMessage(suggestion)}
                          className="text-left text-xs bg-white hover:bg-[#F3F3EE] hover:text-[#18181B] text-[#52525B] px-3 py-1.5 rounded-lg border border-[#E4E4DC] transition-colors shadow-2xs font-medium"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Approval UI */}
                {msg.approvalRequestId && (
                  <div className="mt-4 p-4 bg-amber-50/70 border border-amber-200 rounded-xl space-y-3">
                    <p className="text-amber-900 text-sm font-bold">Human Approval Required</p>
                    <p className="text-amber-800 text-xs">The agent needs your permission to proceed with the execution.</p>
                    <div className="flex gap-2 mt-2">
                      <Button 
                        onClick={() => approveAction("Looks good to me.")} 
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1.5 h-8 border-none"
                        disabled={isTyping}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approve
                      </Button>
                      <Button 
                        onClick={() => rejectAction("Rejected by user.")} 
                        className="bg-rose-600 hover:bg-rose-700 text-white text-xs px-3 py-1.5 h-8 border-none"
                        disabled={isTyping}
                      >
                        <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp & Actions */}
              <div className={`flex items-center gap-2 text-[11px] text-[#A1A1AA] px-1 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <span>{msg.timestamp}</span>
                {msg.sender === 'agent' && (
                  <button
                    onClick={() => handleCopy(msg.content, msg.id)}
                    className="hover:text-[#18181B] flex items-center gap-1 transition-colors"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-600" />
                        <span className="text-emerald-700 font-medium">Copied</span>
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
              <div className="w-8 h-8 rounded-xl bg-[#18181B] text-white flex items-center justify-center shrink-0 mt-1 font-semibold text-xs shadow-xs">
                You
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3.5 justify-start">
            <div className="w-8 h-8 rounded-xl bg-[#F8F8F6] border border-[#E8E8E3] flex items-center justify-center text-[#18181B] shrink-0">
              <Bot className="w-4 h-4 animate-pulse" />
            </div>
            <div className="bg-[#F8F8F6] border border-[#E8E8E3] rounded-2xl rounded-tl-none p-3.5 flex items-center gap-2 text-xs text-[#71717A]">
              <Sparkles className="w-4 h-4 text-amber-500 animate-spin" />
              <span>Marketing AI is formulating marketing strategy...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Ideas */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-[#71717A] text-[11px] font-mono uppercase font-semibold shrink-0 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Prompts:
        </span>
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => sendMessage(p)}
            className="shrink-0 px-3 py-1.5 bg-white hover:bg-[#F3F3EE] text-[#52525B] hover:text-[#18181B] rounded-xl border border-[#E4E4DC] transition-colors shadow-2xs font-medium"
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
          className="flex-1 bg-[#F3F3EE] border border-[#E4E4DC] focus:border-[#18181B] focus:bg-white text-[#18181B] placeholder-[#A1A1AA] rounded-xl px-4 py-3 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-[#18181B]/10 transition-all shadow-inner"
        />
        <Button
          type="submit"
          disabled={!input.trim() || isTyping}
          className="px-5 py-3 rounded-xl shadow-xs"
          icon={<Send className="w-4 h-4 text-amber-400" />}
        >
          Send
        </Button>
      </form>
    </div>
  );
};

export default ChatPage;
