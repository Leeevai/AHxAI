import React, { useState, useRef } from 'react';
import {
  Send, Code, MessageSquare, Eye, ChevronLeft, ChevronRight,
  Play, Copy, Download, Settings, History, Sparkles
} from 'lucide-react';

const CodeBlock = ({ code, language = 'javascript', title }) => {
  const [copied, setCopied] = useState(false);
  
  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-700">
      <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
        <span className="text-slate-300 text-sm font-medium">{title || language}</span>
        <button
          onClick={copyCode}
          className="text-slate-400 hover:text-slate-200 transition-colors"
        >
          {copied ? <span className="text-green-400">Copied!</span> : <Copy size={16} />}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm text-slate-100">
        <code>{code}</code>
      </pre>
    </div>
  );
};

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

export default function CodingAIAgent() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('code');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory] = useState([
    { id: 1, title: 'Debug Python Function', timestamp: '2 hours ago' },
    { id: 2, title: 'Optimize Algorithm', timestamp: '1 day ago' },
    { id: 3, title: 'Create Data Structure', timestamp: '3 days ago' },
  ]);
  const [currentChat, setCurrentChat] = useState([
    { message: "Hello! I'm your AI coding assistant. What can I help you with today?", isUser: false }
  ]);
  const [code, setCode] = useState(`function bubbleSort(arr) {
    let n = arr.length;
    for (let i = 0; i < n - 1; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                let temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    return arr;
}`);

  const explanation = `This bubble sort implementation has O(n²) time complexity. The algorithm repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.`;

  const visualizationCode = `// Binary Search Tree
class TreeNode {
    constructor(val) {
        this.val = val;
        this.left = null;
        this.right = null;
    }
}

function insert(root, val) {
    if (!root) return new TreeNode(val);
    if (val < root.val) {
        root.left = insert(root.left, val);
    } else {
        root.right = insert(root.right, val);
    }
    return root;
}`;

  const handleSubmit = () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    setCurrentChat(prev => [...prev, { message: prompt, isUser: true }]);
    
    setTimeout(() => {
      setCurrentChat(prev => [...prev, { 
        message: "I've analyzed your code. Here are some optimization suggestions and explanations.",
        isUser: false 
      }]);
      setIsLoading(false);
    }, 1500);
    
    setPrompt('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const tabs = [
    { id: 'code', label: 'Code', icon: Code },
    { id: 'explain', label: 'Explanation', icon: MessageSquare },
    { id: 'visualize', label: 'Visualize', icon: Eye }
  ];

  return (
    <div className="h-screen bg-slate-50 flex">
      {/* Sidebar */}
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

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Coding AI Agent</h1>
              <p className="text-slate-600 text-sm">Your intelligent coding companion</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-slate-100 rounded">
                <Settings size={20} className="text-slate-600" />
              </button>
              <div className="w-8 h-8 bg-blue-500 rounded-full"></div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 flex">
          {/* Left Panel */}
          <div className="flex-1 p-6">
            {/* Tabs */}
            <div className="flex space-x-1 mb-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
                    activeTab === tab.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <tab.icon size={16} />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="h-full">
              {activeTab === 'code' && (
                <div className="h-full flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900">Code Editor</h2>
                    <div className="flex gap-2">
                      <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                        <Play size={16} />
                        Run
                      </button>
                      <button className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded-lg flex items-center gap-2">
                        <Download size={16} />
                        Download
                      </button>
                    </div>
                  </div>
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="flex-1 bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your code here..."
                  />
                </div>
              )}
              
              {activeTab === 'explain' && (
                <div className="h-full flex flex-col">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">Code Explanation</h2>
                  <div className="flex-1 bg-white rounded-lg p-4 border border-slate-200 overflow-y-auto">
                    <p className="text-slate-700 mb-4">{explanation}</p>
                    
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                      <h4 className="text-yellow-800 font-medium mb-2">⚠️ Performance Warning</h4>
                      <p className="text-yellow-700 text-sm">
                        O(n²) complexity - consider quicksort for larger datasets.
                      </p>
                    </div>
                    
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h4 className="text-green-800 font-medium mb-2">✅ Suggestions</h4>
                      <ul className="text-green-700 text-sm space-y-1">
                        <li>• Add input validation</li>
                        <li>• Early termination optimization</li>
                        <li>• TypeScript types</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTab === 'visualize' && (
                <div className="h-full flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900">Visualization</h2>
                    <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                      <Play size={16} />
                      Run Visualization
                    </button>
                  </div>
                  <div className="flex-1 space-y-4">
                    <CodeBlock code={visualizationCode} title="Data Structure Visualization" />
                    <div className="bg-white border-2 border-dashed border-slate-300 rounded-lg p-8 flex items-center justify-center">
                      <div className="text-center text-slate-500">
                        <Eye size={32} className="mx-auto mb-2 opacity-50" />
                        <p>Visualization output will appear here</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chat Panel */}
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
        </div>
      </div>
    </div>
  );
}