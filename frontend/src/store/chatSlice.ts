import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai' | 'system';
  text: string;
  timestamp: string;
  toolExecuted?: string;
}

interface ChatState {
  messages: ChatMessage[];
  sessionId: string;
  isAiTyping: boolean;
  needsConfirmation: boolean;
  error: string | null;
}

const initialState: ChatState = {
  messages: [
    {
      id: 'welcome-1',
      sender: 'ai',
      text: 'Hello! I am your AI-First Healthcare CRM Assistant powered by LangGraph & Groq (`gemma2-9b-it`). Tell me about your HCP interaction today, or ask me to search for a doctor.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ],
  sessionId: `crm-session-${Date.now()}`,
  isAiTyping: false,
  needsConfirmation: false,
  error: null,
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    setAiTyping: (state, action: PayloadAction<boolean>) => {
      state.isAiTyping = action.payload;
    },
    setNeedsConfirmation: (state, action: PayloadAction<boolean>) => {
      state.needsConfirmation = action.payload;
    },
    clearMessages: (state) => {
      state.messages = initialState.messages;
    }
  },
});

export const { addMessage, setAiTyping, setNeedsConfirmation, clearMessages } = chatSlice.actions;
export default chatSlice.reducer;
