import React from 'react';
import { Bot } from 'lucide-react';

export const ChatPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">AI Chat Interface</h2>
        <p className="text-sm text-slate-400">
          Communicate directly with the LangGraph Marketing AI Agent for content and strategy generation.
        </p>
      </div>

      <div className="h-96 rounded-xl border border-dashed border-slate-800 bg-slate-900/50 flex flex-col items-center justify-center text-center p-6">
        <Bot className="w-12 h-12 text-indigo-400 mb-3" />
        <h3 className="text-lg font-semibold text-white">Interactive Agent Chat</h3>
        <p className="text-sm text-slate-400 max-w-sm mt-1">
          Chat streaming, campaign ideation, and autonomous tool calling interface (Ready for Task 4).
        </p>
      </div>
    </div>
  );
};

export default ChatPage;
