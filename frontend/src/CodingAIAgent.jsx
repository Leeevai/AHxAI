import React, { useState, useRef, useEffect } from 'react';
import {
  Send, Code, MessageSquare, Eye, ChevronLeft, ChevronRight,
  Play, Copy, Download, Settings, Zap, Brain, History, X
} from 'lucide-react';


const CodeBlock = ({ code, language = 'javascript', title }) => {
  const [copied, setCopied] = useState(false);
  
  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden">
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <span className="text-gray-300 text-sm font-medium">{title || language}</span>
        <button
          onClick={copyCode}
          className="text-gray-400 hover:text-white transition-colors"
        >
          {copied ? <span className="text-green-400">Copied!</span> : <Copy size={16} />}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm">
        <code className="text-gray-100">{code}</code>
      </pre>
    </div>
  );
};

const ChatMessage = ({ message, isUser }) => (
  <div className={`mb-4 ${isUser ? 'ml-8' : 'mr-8'}`}>
    <div className={`p-4 rounded-lg ${isUser ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-100 text-gray-900'}`}>
      <div className="flex items-center gap-2 mb-2">
        {isUser ? (
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-xs font-bold">U</span>
          </div>
        ) : (
          <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Brain size={12} />
          </div>
        )}
        <span className="text-sm font-medium">{isUser ? 'You' : 'AI Agent'}</span>
      </div>
      <div className="text-sm leading-relaxed">{message}</div>
    </div>
  </div>
);

const VisualizationPanel = ({ visualizationCode }) => {
  const [isRunning, setIsRunning] = useState(false);
  
  const runVisualization = () => {
    setIsRunning(true);
    // Simulate running visualization
    setTimeout(() => setIsRunning(false), 2000);
  };

  return (
    <div className="h-full bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Eye size={20} />
          Visualization
        </h3>
        <button
          onClick={runVisualization}
          disabled={isRunning}
          className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Play size={16} />
          {isRunning ? 'Running...' : 'Run'}
        </button>
      </div>
      
      {visualizationCode ? (
        <div className="space-y-4">
          <CodeBlock code={visualizationCode} language="javascript" title="Visualization Code" />
          <div className="bg-white rounded-lg p-6 border-2 border-dashed border-gray-300 min-h-48 flex items-center justify-center">
            {isRunning ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Generating visualization...</p>
              </div>
            ) : (
              <div className="text-center text-gray-500">
                <Eye size={48} className="mx-auto mb-2 opacity-50" />
                <p>Visualization output will appear here</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <Eye size={48} className="mx-auto mb-2 opacity-50" />
            <p>No visualization code available</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default function CodingAIAgent() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('code');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: 'Debug Python Function', timestamp: '2 hours ago' },
    { id: 2, title: 'Optimize Algorithm', timestamp: '1 day ago' },
    { id: 3, title: 'Create Data Structure', timestamp: '3 days ago' },
  ]);
  const [currentChat, setCurrentChat] = useState([]);
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
  const [explanation, setExplanation] = useState('This bubble sort implementation has a time complexity of O(n²). The algorithm repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order. The pass through the list is repeated until the list is sorted.');
  const [visualizationCode, setVisualizationCode] = useState(`// Linked List Visualization
class Node {
    constructor(data) {
        this.data = data;
        this.next = null;
    }
}

class LinkedList {
    constructor() {
        this.head = null;
    }
    
    append(data) {
        const newNode = new Node(data);
        if (!this.head) {
            this.head = newNode;
            return;
        }
        let current = this.head;
        while (current.next) {
            current = current.next;
        }
        current.next = newNode;
    }
}`);

  const textareaRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    
    // Add user message to chat
    setChatHistory([...chatHistory, { id: Date.now(), title: prompt.slice(0, 50) + '...', timestamp: 'now' }]);
    setCurrentChat(prev => [...prev, { message: prompt, isUser: true }]);
    
    try {
      // Simulate API call
      setTimeout(() => {
        setCurrentChat(prev => [...prev, { 
          message: "I've analyzed your code and found several optimization opportunities. Let me provide you with an improved version and explain the changes.",
          isUser: false 
        }]);
        setIsLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Error:', error);
      setIsLoading(false);
    }
    
    setPrompt('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const tabs = [
    { id: 'code', label: 'Code', icon: Code },
    { id: 'explain', label: 'Explanation', icon: MessageSquare },
    { id: 'visualize', label: 'Visualize', icon: Eye }
  ];

  return (
    <div className="h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <div className={`bg-gray-800 border-r border-gray-700 transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-80'}`}>
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <Zap size={16} />
                </div>
                <span className="font-semibold">AI Code Agent</span>
              </div>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            </button>
          </div>
        </div>
        
        {!sidebarCollapsed && (
          <div className="p-4">
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors mb-4">
              <MessageSquare size={16} />
              New Chat
            </button>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-400 text-sm font-medium mb-2">
                <History size={16} />
                Recent Chats
              </div>
              {chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  className="w-full text-left p-3 hover:bg-gray-700 rounded-lg transition-colors group"
                >
                  <div className="font-medium text-sm text-gray-200 truncate">{chat.title}</div>
                  <div className="text-xs text-gray-500 mt-1">{chat.timestamp}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold">Coding AI Agent</h1>
            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
                <Settings size={20} />
              </button>
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 flex">
          {/* Left Panel - Code/Explanation/Visualization */}
          <div className="flex-1 p-6">
            {/* Tabs */}
            <div className="flex space-x-4 mb-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
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
                <div className="h-full">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Code Editor</h2>
                    <div className="flex gap-2">
                      <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
                        <Play size={16} />
                        Run
                      </button>
                      <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
                        <Download size={16} />
                        Download
                      </button>
                    </div>
                  </div>
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full h-96 bg-gray-800 text-white p-4 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your code here..."
                  />
                </div>
              )}
              
              {activeTab === 'explain' && (
                <div className="h-full">
                  <h2 className="text-lg font-semibold mb-4">Code Explanation & Debug Info</h2>
                  <div className="bg-gray-800 rounded-lg p-6 h-96 overflow-y-auto">
                    <div className="prose prose-invert max-w-none">
                      <p className="text-gray-300 leading-relaxed">{explanation}</p>
                      
                      <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-500/20 rounded-lg">
                        <h4 className="text-yellow-400 font-medium mb-2">⚠️ Performance Warning</h4>
                        <p className="text-yellow-300 text-sm">
                          The current implementation has O(n²) time complexity. Consider using a more efficient sorting algorithm like quicksort or mergesort for larger datasets.
                        </p>
                      </div>
                      
                      <div className="mt-4 p-4 bg-green-900/20 border border-green-500/20 rounded-lg">
                        <h4 className="text-green-400 font-medium mb-2">✅ Suggestions</h4>
                        <ul className="text-green-300 text-sm space-y-1">
                          <li>• Add input validation for array parameter</li>
                          <li>• Consider early termination if no swaps occur</li>
                          <li>• Add TypeScript types for better type safety</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTab === 'visualize' && (
                <VisualizationPanel visualizationCode={visualizationCode} />
              )}
            </div>
          </div>

          {/* Right Panel - Chat */}
          <div className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-semibold">Chat with AI Agent</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {currentChat.map((msg, index) => (
                <ChatMessage key={index} message={msg.message} isUser={msg.isUser} />
              ))}
              
              {isLoading && (
                <div className="flex items-center gap-2 text-gray-400">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <span>AI is thinking...</span>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-gray-700">
              <div className="flex gap-2">
                <textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me to debug, explain, or optimize your code..."
                  className="flex-1 bg-gray-700 text-white p-3 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  rows="3"
                />
                <button
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white p-3 rounded-lg transition-colors"
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