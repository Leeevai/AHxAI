// Frontend API client for communicating with the FastAPI backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Chat management
  async createChat() {
    return this.request('/api/chats', {
      method: 'POST',
    });
  }

  async getChats() {
    return this.request('/api/chats');
  }

  async getChat(chatId) {
    return this.request(`/api/chats/${chatId}`);
  }

  async deleteChat(chatId) {
    return this.request(`/api/chats/${chatId}`, {
      method: 'DELETE',
    });
  }

  async getChatMessages(chatId) {
    return this.request(`/api/chats/${chatId}/messages`);
  }

  async sendMessage(chatId, content, isUser = true) {
    return this.request(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      body: {
        content,
        is_user: isUser,
      },
    });
  }

  // Code analysis
  async analyzeCode(code, language = 'javascript', context = '', chatId = null) {
    return this.request('/api/analyze', {
      method: 'POST',
      body: {
        code,
        language,
        context,
        chat_id: chatId,
      },
    });
  }

  // Get visualization HTML
  async getVisualization(messageId) {
    const response = await fetch(`${this.baseUrl}/api/visualization/${messageId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.text();
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// Export individual functions for easier use
export const healthCheck = () => apiClient.healthCheck();
export const createChat = () => apiClient.createChat();
export const getChats = () => apiClient.getChats();
export const getChat = (chatId) => apiClient.getChat(chatId);
export const deleteChat = (chatId) => apiClient.deleteChat(chatId);
export const getChatMessages = (chatId) => apiClient.getChatMessages(chatId);
export const sendMessage = (chatId, content, isUser) => apiClient.sendMessage(chatId, content, isUser);
export const analyzeCode = (code, language, context, chatId) => apiClient.analyzeCode(code, language, context, chatId);
export const getVisualization = (messageId) => apiClient.getVisualization(messageId);

export default apiClient;