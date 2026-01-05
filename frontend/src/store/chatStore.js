import { create } from 'zustand';

export const useChatStore = create((set, get) => ({
  messages: [],
  sessions: [],
  currentSessionId: null,
  isTyping: false,
  
  // Add a message
  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...message,
      }],
    }));
  },
  
  // Set all messages
  setMessages: (messages) => {
    set({ messages });
  },
  
  // Clear messages
  clearMessages: () => {
    set({ messages: [] });
  },
  
  // Set typing indicator
  setTyping: (isTyping) => {
    set({ isTyping });
  },
  
  // Set current session
  setCurrentSession: (sessionId) => {
    set({ currentSessionId: sessionId });
  },
  
  // Set sessions list
  setSessions: (sessions) => {
    set({ sessions: sessions || [] });
  },
  
  // Add session
  addSession: (session) => {
    set((state) => ({
      sessions: [session, ...state.sessions],
    }));
  },
  
  // Remove session
  removeSession: (sessionId) => {
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
    }));
  },
}));
