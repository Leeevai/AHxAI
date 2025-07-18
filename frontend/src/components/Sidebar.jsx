import React from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  MessageSquare, 
  History, 
  Sparkles 
} from 'lucide-react';

const Sidebar = ({ 
  sidebarCollapsed, 
  setSidebarCollapsed, 
  chatHistory = [] 
}) => {
  return (
    <div className={`bg-white border-r border-slate-200 transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-72'}`}>
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center justify-between">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <Sparkles size={16} className="text-white" />
              </div>
              <div>
                <div className="font-semibold text-slate-900">AI Code Agent</div>
                <div className="text-xs text-slate-500">Coding assistant</div>
              </div>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1 hover:bg-slate-100 rounded"
          >
            {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        </div>
      </div>
      
      {!sidebarCollapsed && (
        <div className="p-4">
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 mb-4">
            <MessageSquare size={16} />
            New Chat
          </button>
          
          <div>
            <div className="flex items-center gap-2 text-slate-600 text-sm font-medium mb-3">
              <History size={16} />
              Recent Chats
            </div>
            {chatHistory.map((chat) => (
              <div key={chat.id} className="p-2 hover:bg-slate-100 rounded cursor-pointer mb-1">
                <div className="font-medium text-sm text-slate-700 truncate">{chat.title}</div>
                <div className="text-xs text-slate-500">{chat.timestamp}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;