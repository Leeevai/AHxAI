import React from 'react';
import { Sparkles } from 'lucide-react';

const ChatMessage = ({ message, isUser }) => (
  <div className={`mb-4 ${isUser ? 'ml-8' : 'mr-8'}`}>
    <div className={`p-3 rounded-lg ${
      isUser 
        ? 'bg-blue-500 text-white ml-auto max-w-xs' 
        : 'bg-white border border-slate-200 text-slate-900'
    }`}>
      <div className="flex items-center gap-2 mb-1">
        {isUser ? (
          <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-xs">U</span>
          </div>
        ) : (
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
            <Sparkles size={10} className="text-white" />
          </div>
        )}
        <span className="text-xs font-medium">{isUser ? 'You' : 'AI'}</span>
      </div>
      <div className="text-sm">{message}</div>
    </div>
  </div>
);

export default ChatMessage;