import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import TabNavigation from './TabNavigation';
import CodeTab from './CodeTab';
import ExplanationTab from './ExplanationTab';
import VisualizationTab from './VisualizationTab';
import ChatPanel from './ChatPanel';

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

  const renderTabContent = () => {
    switch (activeTab) {
      case 'code':
        return <CodeTab code={code} setCode={setCode} />;
      case 'explain':
        return <ExplanationTab explanation={explanation} />;
      case 'visualize':
        return <VisualizationTab visualizationCode={visualizationCode} />;
      default:
        return null;
    }
  };

  return (
    <div className="h-screen bg-slate-50 flex">
      <Sidebar 
        sidebarCollapsed={sidebarCollapsed}
        setSidebarCollapsed={setSidebarCollapsed}
        chatHistory={chatHistory}
      />

      <div className="flex-1 flex flex-col">
        <Header />

        <div className="flex-1 flex">
          <div className="flex-1 p-6">
            <TabNavigation 
              activeTab={activeTab} 
              setActiveTab={setActiveTab} 
            />
            
            <div className="h-full">
              {renderTabContent()}
            </div>
          </div>

          <ChatPanel 
            currentChat={currentChat}
            isLoading={isLoading}
            prompt={prompt}
            setPrompt={setPrompt}
            handleSubmit={handleSubmit}
            handleKeyPress={handleKeyPress}
          />
        </div>
      </div>
    </div>
  );
}