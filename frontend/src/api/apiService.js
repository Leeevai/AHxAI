// api/apiService.js
const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('auth_token') || 'mock-token';
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Code processing
  async processCode(code, language, action, prompt) {
    return this.request('/process-code', {
      method: 'POST',
      body: JSON.stringify({
        code,
        language,
        action,
        prompt
      })
    });
  }

  // Chat
  async sendChatMessage(message, chatId = null) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        chat_id: chatId
      })
    });
  }

  // Chat history
  async getChatHistory() {
    return this.request('/chat-history');
  }

  async deleteChatSession(sessionId) {
    return this.request(`/chat-session/${sessionId}`, {
      method: 'DELETE'
    });
  }

  // Code sessions
  async getCodeSessions() {
    return this.request('/code-sessions');
  }

  async getCodeSession(sessionId) {
    return this.request(`/code-session/${sessionId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Database health check
  async dbHealthCheck() {
    return this.request('/api/db/health');
  }

  // Database initialization
  async initializeDatabase() {
    return this.request('/api/db/init', {
      method: 'POST'
    });
  }

  // Database Chat Management
  async createChatDB(title, userId = null) {
    return this.request(`/api/db/chats?title=${encodeURIComponent(title)}${userId ? `&user_id=${userId}` : ''}`, {
      method: 'POST'
    });
  }

  async getChatsDB(userId = null, limit = 50, offset = 0) {
    const params = new URLSearchParams({ limit, offset });
    if (userId) params.append('user_id', userId);
    return this.request(`/api/db/chats?${params}`);
  }

  async getChatDB(chatId) {
    return this.request(`/api/db/chats/${chatId}`);
  }

  async deleteChatDB(chatId) {
    return this.request(`/api/db/chats/${chatId}`, {
      method: 'DELETE'
    });
  }

  // Database Chat Messages
  async createMessageDB(chatId, content, isUser, metadata = null) {
    const params = new URLSearchParams({
      content,
      is_user: isUser
    });
    if (metadata) params.append('metadata', JSON.stringify(metadata));
    
    return this.request(`/api/db/chats/${chatId}/messages?${params}`, {
      method: 'POST'
    });
  }

  async getChatMessagesDB(chatId, limit = 100, offset = 0) {
    return this.request(`/api/db/chats/${chatId}/messages?limit=${limit}&offset=${offset}`);
  }

  // Database Code Projects
  async createCodeProjectDB(name, language, codeContent, description = null, userId = null) {
    const params = new URLSearchParams({
      name,
      language,
      code_content: codeContent
    });
    if (description) params.append('description', description);
    if (userId) params.append('user_id', userId);

    return this.request(`/api/db/projects?${params}`, {
      method: 'POST'
    });
  }

  async getCodeProjectsDB(language = null, userId = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (language) params.append('language', language);
    if (userId) params.append('user_id', userId);
    
    return this.request(`/api/db/projects?${params}`);
  }

  async updateCodeProjectDB(projectId, codeContent, name = null) {
    const params = new URLSearchParams({ code_content: codeContent });
    if (name) params.append('name', name);

    return this.request(`/api/db/projects/${projectId}?${params}`, {
      method: 'PUT'
    });
  }

  // Database Code Analysis
  async createCodeAnalysisDB(projectId, originalCode, correctedCode = null, explanation = null, suggestions = null, warnings = null, analysisType = 'general') {
    const params = new URLSearchParams({
      project_id: projectId,
      original_code: originalCode,
      analysis_type: analysisType
    });
    if (correctedCode) params.append('corrected_code', correctedCode);
    if (explanation) params.append('explanation', explanation);
    if (suggestions) params.append('suggestions', JSON.stringify(suggestions));
    if (warnings) params.append('warnings', JSON.stringify(warnings));

    return this.request(`/api/db/analysis?${params}`, {
      method: 'POST'
    });
  }

  async getProjectAnalysisDB(projectId, analysisType = null) {
    const params = analysisType ? `?analysis_type=${analysisType}` : '';
    return this.request(`/api/db/analysis/project/${projectId}${params}`);
  }

  // Database Search and Analytics
  async searchCodeProjectsDB(query, language = null, limit = 20) {
    const params = new URLSearchParams({ query, limit });
    if (language) params.append('language', language);
    
    return this.request(`/api/db/search/code?${params}`);
  }

  async getAnalyticsSummaryDB() {
    return this.request('/api/db/analytics/summary');
  }

  async getLanguageStatsDB() {
    return this.request('/api/db/stats/languages');
  }
}

const apiService = new ApiService();
export default apiService;

// hooks/useApi.js
import { useState, useEffect } from 'react';

export const useCodeProcessor = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const processCode = async (code, language, action, prompt) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const result = await apiService.processCode(code, language, action, prompt);
      setResult(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsProcessing(false);
    }
  };

  return { processCode, isProcessing, result, error };
};

export const useChat = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  const sendMessage = async (message, chatId = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.sendChatMessage(message, chatId);
      setMessages(prev => [...prev, {
        id: response.id,
        message: response.message,
        response: response.response,
        timestamp: response.timestamp,
        isUser: false
      }]);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return { sendMessage, messages, isLoading, error, clearMessages };
};

export const useChatHistory = () => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getChatHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await apiService.deleteChatSession(sessionId);
      setHistory(prev => prev.filter(chat => chat.id !== sessionId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return { history, isLoading, error, refetch: fetchHistory, deleteSession };
};

export const useCodeSessions = () => {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSessions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getCodeSessions();
      setSessions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getSession = async (sessionId) => {
    try {
      return await apiService.getCodeSession(sessionId);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return { sessions, isLoading, error, refetch: fetchSessions, getSession };
};

// Database-related hooks
export const useDatabase = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const initializeDatabase = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiService.initializeDatabase();
      setIsInitialized(true);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const result = await apiService.dbHealthCheck();
      return result.status === 'healthy';
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  return { initializeDatabase, checkHealth, isInitialized, isLoading, error };
};

export const useChatDB = () => {
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createChat = async (title, userId = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const newChat = await apiService.createChatDB(title, userId);
      setChats(prev => [newChat, ...prev]);
      setCurrentChat(newChat);
      setMessages([]);
      return newChat;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loadChats = async (userId = null, limit = 50, offset = 0) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const chatList = await apiService.getChatsDB(userId, limit, offset);
      setChats(chatList);
      return chatList;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loadChatMessages = async (chatId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const messageList = await apiService.getChatMessagesDB(chatId);
      setMessages(messageList);
      return messageList;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = async (chatId, content, isUser, metadata = null) => {
    try {
      const newMessage = await apiService.createMessageDB(chatId, content, isUser, metadata);
      setMessages(prev => [...prev, newMessage]);
      return newMessage;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteChat = async (chatId) => {
    try {
      await apiService.deleteChatDB(chatId);
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      if (currentChat && currentChat.id === chatId) {
        setCurrentChat(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return {
    chats,
    currentChat,
    messages,
    isLoading,
    error,
    createChat,
    loadChats,
    loadChatMessages,
    addMessage,
    deleteChat,
    setCurrentChat
  };
};

export const useCodeProjectsDB = () => {
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createProject = async (name, language, codeContent, description = null, userId = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const newProject = await apiService.createCodeProjectDB(name, language, codeContent, description, userId);
      setProjects(prev => [newProject, ...prev]);
      setCurrentProject(newProject);
      return newProject;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loadProjects = async (language = null, userId = null, limit = 50) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const projectList = await apiService.getCodeProjectsDB(language, userId, limit);
      setProjects(projectList);
      return projectList;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProject = async (projectId, codeContent, name = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedProject = await apiService.updateCodeProjectDB(projectId, codeContent, name);
      setProjects(prev => prev.map(p => p.id === projectId ? updatedProject : p));
      if (currentProject && currentProject.id === projectId) {
        setCurrentProject(updatedProject);
      }
      return updatedProject;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const searchProjects = async (query, language = null, limit = 20) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const results = await apiService.searchCodeProjectsDB(query, language, limit);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    projects,
    currentProject,
    isLoading,
    error,
    createProject,
    loadProjects,
    updateProject,
    searchProjects,
    setCurrentProject
  };
};

export const useAnalyticsDB = () => {
  const [summary, setSummary] = useState(null);
  const [languageStats, setLanguageStats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadSummary = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getAnalyticsSummaryDB();
      setSummary(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loadLanguageStats = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getLanguageStatsDB();
      setLanguageStats(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    summary,
    languageStats,
    isLoading,
    error,
    loadSummary,
    loadLanguageStats
  };
};

// utils/codeLanguageDetector.js
export const detectLanguage = (code) => {
  const patterns = {
    javascript: /\b(function|const|let|var|=>|console\.log)\b/,
    python: /\b(def|import|print|if __name__|class)\b/,
    java: /\b(public class|public static void main|System\.out\.println)\b/,
    cpp: /\b(#include|std::|cout|cin|int main)\b/,
    csharp: /\b(using System|public class|Console\.WriteLine)\b/,
    go: /\b(package main|func main|fmt\.Println)\b/,
    rust: /\b(fn main|println!|use std)\b/,
    php: /<\?php|\$\w+/,
    ruby: /\b(def|puts|require|class)\b/,
    swift: /\b(func|var|let|print|import Foundation)\b/,
    kotlin: /\b(fun main|println|val|var)\b/,
    typescript: /\b(interface|type|enum|namespace)\b/,
    sql: /\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE)\b/i,
    html: /<\/?[a-z][\s\S]*>/i,
    css: /\{[\s\S]*:[^}]*\}/,
    json: /^\s*[\{\[]/,
    yaml: /^[\s]*\w+:\s/m,
    xml: /<\?xml|<\w+[^>]*>/,
    shell: /\b(echo|ls|cd|mkdir|rm|grep|awk|sed)\b/,
    powershell: /\b(Get-|Set-|New-|Remove-|Write-Host)\b/,
    matlab: /\b(function|end|plot|disp|clc)\b/,
    r: /\b(library|data\.frame|plot|summary|str)\b/,
    scala: /\b(object|def|val|var|extends|trait)\b/,
    perl: /\b(use strict|my \$|print|chomp)\b/,
    lua: /\b(local|function|end|print|require)\b/,
    dart: /\b(main|void|print|import 'dart:)\b/,
    elixir: /\b(defmodule|def|IO\.puts|import)\b/,
    erlang: /\b(start|spawn|receive|io:format)\b/,
    haskell: /\b(main|putStrLn|import|where|let|in)\b/,
    clojure: /\(defn|\(println|\(let/,
    fsharp: /\b(let|printfn|open|module)\b/,
    vb: /\b(Sub Main|Console\.WriteLine|Dim|Public|Private)\b/,
    assembly: /\b(mov|add|sub|cmp|jmp|call|ret)\b/i,
    fortran: /\b(program|end program|write|read|integer|real)\b/i,
    cobol: /\b(IDENTIFICATION DIVISION|PROGRAM-ID|DISPLAY)\b/i,
    pascal: /\b(program|begin|end|writeln|var)\b/i,
    ada: /\b(procedure|function|begin|end|Put_Line)\b/i,
    vhdl: /\b(entity|architecture|signal|process|begin|end)\b/i,
    verilog: /\b(module|endmodule|always|begin|end|wire|reg)\b/i
  };

  const codeLines = code.split('\n');
  const sampleSize = Math.min(10, codeLines.length);
  const sample = codeLines.slice(0, sampleSize).join('\n');

  for (const [language, pattern] of Object.entries(patterns)) {
    if (pattern.test(sample)) {
      return language;
    }
  }

  return 'text';
};

// utils/codeFormatter.js
export const formatCode = (code, language) => {
  // Simple code formatting - in a real app, you'd use a proper formatter
  const lines = code.split('\n');
  let indentLevel = 0;
  const indentSize = 2;
  
  const formatted = lines.map(line => {
    const trimmed = line.trim();
    
    if (trimmed.includes('}') || trimmed.includes('end') || trimmed.includes('</')) {
      indentLevel = Math.max(0, indentLevel - 1);
    }
    
    const indentedLine = ' '.repeat(indentLevel * indentSize) + trimmed;
    
    if (trimmed.includes('{') || trimmed.includes('begin') || trimmed.includes('<')) {
      indentLevel++;
    }
    
    return indentedLine;
  });
  
  return formatted.join('\n');
};

// utils/errorHandler.js
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.message.includes('Network')) {
    return 'Unable to connect to the server. Please check your connection.';
  }
  
  if (error.message.includes('401')) {
    return 'Authentication failed. Please log in again.';
  }
  
  if (error.message.includes('403')) {
    return 'You do not have permission to perform this action.';
  }
  
  if (error.message.includes('404')) {
    return 'The requested resource was not found.';
  }
  
  if (error.message.includes('500')) {
    return 'Server error. Please try again later.';
  }
  
  return error.message || 'An unexpected error occurred.';
};

// constants/actionTypes.js
export const CODE_ACTIONS = {
  DEBUG: 'debug',
  EXPLAIN: 'explain',
  OPTIMIZE: 'optimize',
  VISUALIZE: 'visualize',
  REVIEW: 'review',
  REFACTOR: 'refactor',
  TEST: 'test',
  DOCUMENT: 'document'
};

export const SUPPORTED_LANGUAGES = [
  'javascript', 'typescript', 'python', 'java', 'cpp', 'csharp', 'go', 'rust',
  'php', 'ruby', 'swift', 'kotlin', 'sql', 'html', 'css', 'json', 'yaml',
  'xml', 'shell', 'powershell', 'matlab', 'r', 'scala', 'perl', 'lua',
  'dart', 'elixir', 'erlang', 'haskell', 'clojure', 'fsharp', 'vb'
];

// package.json dependencies for React frontend
/*
{
  "name": "coding-ai-agent-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
*/