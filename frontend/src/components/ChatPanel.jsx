import React from 'react';
import { MessageSquare, Send } from 'lucide-react';
import ChatMessage from './ChatMessage';

const ChatPanel = ({ 
  currentChat, 
  isLoading, 
  prompt, 
  setPrompt, 
  handleSubmit, 
  handleKeyPress 
}) => {
  return (
    <div className="w-80 bg-white border-l border-slate-200 flex flex-col">
      <div className="p-4 border-b border-slate-200">
        <h3 className="font-semibold text-slate-900 flex items-center gap-2">
          <MessageSquare size={16} />
          Chat with AI Agent
        </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        {currentChat.map((msg, index) => (
          <ChatMessage key={index} message={msg.message} isUser={msg.isUser} />
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-2 text-slate-500 bg-slate-50 rounded-lg p-3">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span>AI is thinking...</span>
          </div>
        )}
      </div>
      
      <div className="p-4 border-t border-slate-200">
        <div className="flex gap-2">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about your code..."
            className="flex-1 bg-slate-50 border border-slate-200 text-slate-900 p-3 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            rows="2"
          />
          <button
            onClick={handleSubmit}
            disabled={!prompt.trim() || isLoading}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-400 text-white p-3 rounded-lg"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;