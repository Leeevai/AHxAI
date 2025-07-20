import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import TabNavigation from './TabNavigation';
import CodeTab from './CodeTab';
import ExplanationTab from './ExplanationTab';
import VisualizationTab from './VisualizationTab';
import ChatPanel from './ChatPanel';

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function CodingAIAgent() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('code');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChat, setCurrentChat] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
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
  const [explanation, setExplanation] = useState('');
  const [visualizationCode, setVisualizationCode] = useState('');
  const [visualizationHtml, setVisualizationHtml] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('javascript');
  const [codeContext, setCodeContext] = useState('');

  // API Functions
  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
  });

  // Health Check
  const checkHealth = async () => {
    try {
      const response = await apiClient.get('/health');
      console.log('API Health:', response.data);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return null;
    }
  };

  // Chat Management
  const createNewChat = async () => {
    try {
      const response = await apiClient.post('/api/chats');
      const newChat = response.data;
      setCurrentChatId(newChat.id);
      setCurrentChat([{
        message: "Hello! I'm your AI coding assistant. What can I help you with today?",
        isUser: false,
        id: 'welcome-' + Date.now()
      }]);
      await loadChatHistory();
      return newChat;
    } catch (error) {
      console.error('Error creating chat:', error);
      return null;
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await apiClient.get('/api/chats');
      setChatHistory(response.data.map(chat => ({
        id: chat.id,
        title: chat.title,
        timestamp: new Date(chat.updated_at).toLocaleString()
      })));
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const loadChat = async (chatId) => {
    try {
      const response = await apiClient.get(`/api/chats/${chatId}/messages`);
      const messages = response.data.map(msg => ({
        message: msg.content,
        isUser: msg.is_user,
        id: msg.id,
        metadata: msg.metadata
      }));
      setCurrentChat(messages);
      setCurrentChatId(chatId);
      
      // Load the latest code analysis data if available
      const lastAiMessage = messages.filter(msg => !msg.isUser && msg.metadata).pop();
      if (lastAiMessage && lastAiMessage.metadata) {
        const metadata = lastAiMessage.metadata;
        if (metadata.corrected_code) setCode(metadata.corrected_code);
        if (metadata.explanation) setExplanation(metadata.explanation);
        if (metadata.visualization_html) setVisualizationHtml(metadata.visualization_html);
        if (metadata.suggestions) setSuggestions(metadata.suggestions);
        if (metadata.warnings) setWarnings(metadata.warnings);
      }
    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  const deleteChat = async (chatId) => {
    try {
      await apiClient.delete(`/api/chats/${chatId}`);
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setCurrentChat([]);
      }
      await loadChatHistory();
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  const sendMessage = async (chatId, content, isUser = true) => {
    try {
      const response = await apiClient.post(`/api/chats/${chatId}/messages`, {
        content,
        is_user: isUser
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      return null;
    }
  };

  // Code Analysis
  const analyzeCode = async (codeToAnalyze = code, language = selectedLanguage, context = codeContext) => {
    try {
      setIsLoading(true);
      
      // Ensure we have a chat
      let chatId = currentChatId;
      if (!chatId) {
        const newChat = await createNewChat();
        chatId = newChat.id;
      }

      const request = {
        code: codeToAnalyze,
        language: language,
        context: context,
        chat_id: chatId
      };

      console.log('Sending analyze request:', request);
      const response = await apiClient.post('/api/analyze', request);
      const result = response.data;
      console.log('Analyze response:', result);
      
      // Update state with analysis results
      if (result.ai_response) {
        setCode(result.ai_response.corrected_code);
        setExplanation(result.ai_response.explanation);
        setVisualizationHtml(result.ai_response.visualization_html);
        setSuggestions(result.ai_response.suggestions || []);
        setWarnings(result.ai_response.warnings || []);
      }

      // Update chat with user message and AI response
      setCurrentChatId(result.chat_id);
      
      // Add user message to chat
      setCurrentChat(prev => [...prev, {
        message: `Analyzing ${language} code...`,
        isUser: true,
        id: 'user-' + Date.now()
      }]);

      // Add AI response to chat
      setCurrentChat(prev => [...prev, {
        message: result.message.content,
        isUser: false,
        id: result.message.id,
        metadata: result.message.metadata
      }]);

      await loadChatHistory();
      return result;
    } catch (error) {
      console.error('Error analyzing code:', error);
      setCurrentChat(prev => [...prev, {
        message: "Sorry, I encountered an error while analyzing your code. Please try again.",
        isUser: false,
        id: 'error-' + Date.now()
      }]);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // LLM Query
  const executeLLMQuery = async (query, systemPrompt = "you are a smart coding assistant") => {
    try {
      setIsLoading(true);
      
      // Ensure we have a chat
      let chatId = currentChatId;
      if (!chatId) {
        const newChat = await createNewChat();
        chatId = newChat.id;
      }

      const request = {
        query: query,
        system_prompt: systemPrompt,
        chat_id: chatId
      };

      console.log('Sending query request:', request);
      const response = await apiClient.post('/api/query', request);
      const result = response.data;
      console.log('Query response:', result);
      
      // Update chat with LLM response
      setCurrentChat(prev => [...prev, {
        message: result.result.content,
        isUser: false,
        id: 'ai-' + Date.now(),
        metadata: {
          tool_calls: result.tool_calls,
          full_messages: result.full_messages
        }
      }]);

      return result;
    } catch (error) {
      console.error('Error executing LLM query:', error);
      setCurrentChat(prev => [...prev, {
        message: "Sorry, I encountered an error while processing your query. Please try again.",
        isUser: false,
        id: 'error-' + Date.now()
      }]);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Get Visualization HTML
  const getVisualization = async (messageId) => {
    try {
      const response = await apiClient.get(`/api/visualization/${messageId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting visualization:', error);
      return null;
    }
  };

  // Handle Submit
  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    console.log('Submitting prompt:', prompt);
    
    // Add user message to chat first
    setCurrentChat(prev => [...prev, { 
      message: prompt, 
      isUser: true, 
      id: 'user-' + Date.now() 
    }]);
    
    const userPrompt = prompt;
    setPrompt(''); // Clear prompt immediately

    // If no current chat, create one
    if (!currentChatId) {
      await createNewChat();
    }

    // Determine if this is a code analysis or general query
    const isCodeAnalysis = (
      userPrompt.toLowerCase().includes('analyze') || 
      userPrompt.toLowerCase().includes('code') ||
      userPrompt.toLowerCase().includes('debug') ||
      userPrompt.toLowerCase().includes('optimize') ||
      userPrompt.toLowerCase().includes('review')
    ) && code.trim();

    console.log('Is code analysis:', isCodeAnalysis);

    if (isCodeAnalysis) {
      // Use code analysis endpoint
      await analyzeCode(code, selectedLanguage, userPrompt);
    } else {
      // Use LLM query endpoint
      await executeLLMQuery(userPrompt);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Handle code analysis button
  const handleAnalyzeCode = async () => {
    if (!code.trim()) {
      alert('Please enter some code to analyze');
      return;
    }

    console.log('Analyzing code:', code);

    // Add user message to chat
    setCurrentChat(prev => [...prev, { 
      message: `Analyzing ${selectedLanguage} code...`, 
      isUser: true,
      id: 'user-' + Date.now()
    }]);

    if (!currentChatId) {
      await createNewChat();
    }

    await analyzeCode();
  };

  // Load initial data
  useEffect(() => {
    const initializeApp = async () => {
      await checkHealth();
      await loadChatHistory();
    };
    
    initializeApp();
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'code':
        return (
          <CodeTab 
            code={code} 
            setCode={setCode}
            selectedLanguage={selectedLanguage}
            setSelectedLanguage={setSelectedLanguage}
            codeContext={codeContext}
            setCodeContext={setCodeContext}
            onAnalyze={handleAnalyzeCode}
            suggestions={suggestions}
            warnings={warnings}
            isLoading={isLoading}
          />
        );
      case 'explain':
        return <ExplanationTab explanation={explanation} />;
      case 'visualize':
        return (
          <VisualizationTab 
            visualizationCode={visualizationCode} 
            visualizationHtml={visualizationHtml}
          />
        );
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
        onChatSelect={loadChat}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        currentChatId={currentChatId}
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
            onVisualizationRequest={getVisualization}
          />
        </div>
      </div>
    </div>
  );
}