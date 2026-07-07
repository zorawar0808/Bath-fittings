import { defineStore } from 'pinia';
import api from '../services/api';

export const useChatStore = defineStore('chat', {
  state: () => ({
    isOpen: false,
    messages: [
      {
        role: 'model',
        content: "Hello! I am your store AI Assistant. Ask me about stock levels (e.g. 'What is low in stock?'), job projects (e.g. 'What was used in Sharma Bathroom?'), or overall store valuation.",
        timestamp: new Date(),
      },
    ],
    loading: false,
    error: null,
  }),
  actions: {
    toggleSidebar() {
      this.isOpen = !this.isOpen;
    },
    setSidebarOpen(open) {
      this.isOpen = open;
    },
    async sendQuery(text) {
      if (!text.trim()) return;

      const userMsg = {
        role: 'user',
        content: text,
        timestamp: new Date(),
      };
      
      this.messages.push(userMsg);
      this.loading = true;
      this.error = null;

      try {
        // Build simple conversational history for Gemini context (max last 6 messages to optimize token count)
        const contextHistory = this.messages
          .slice(-6, -1)
          .map((m) => ({
            role: m.role,
            content: m.content,
          }));

        const response = await api.post('/chatbot/query', {
          message: text,
          chat_history: contextHistory,
        });

        const modelMsg = {
          role: 'model',
          content: response.data.response,
          timestamp: new Date(),
        };
        this.messages.push(modelMsg);
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to reach AI Assistant';
        this.messages.push({
          role: 'model',
          content: `⚠️ Sorry, I encountered an issue: ${this.error}. Please try again later or consult the system logs.`,
          timestamp: new Date(),
        });
      } finally {
        this.loading = false;
      }
    },
    clearHistory() {
      this.messages = [
        {
          role: 'model',
          content: "Chat history cleared. How can I help you today?",
          timestamp: new Date(),
        },
      ];
    },
  },
});
