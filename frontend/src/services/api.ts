import axios from 'axios';

// Base API configuration pointing to FastAPI server
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export interface FormStateDTO {
  id?: number;
  hcp_id?: number;
  hcp_name?: string;
  hospital?: string;
  interaction_type: string;
  date?: string;
  time?: string;
  attendees?: string;
  topics_discussed?: string;
  materials_shared?: string;
  samples_distributed?: string;
  observed_sentiment: string;
  outcomes?: string;
  follow_up_actions?: string;
  ai_summary?: string;
  status: string;
}

export interface ChatRequestDTO {
  session_id: string;
  message: string;
  current_form_data: FormStateDTO;
}

export interface ToolBadgeDTO {
  tool_name: string;
  tool_summary: string;
  parameters: Record<string, any>;
  status: string;
  execution_time_ms: number;
}

export interface ChatResponseDTO {
  response: string;
  updated_form_data: FormStateDTO;
  tool_execution?: ToolBadgeDTO;
  needs_confirmation: boolean;
  saved_interaction_id?: number;
}

export const crmApiService = {
  async sendChatMessage(payload: ChatRequestDTO): Promise<ChatResponseDTO> {
    const response = await apiClient.post<ChatResponseDTO>('/chat', payload);
    return response.data;
  },

  async getAllHCPs(search?: string) {
    const response = await apiClient.get('/hcp', { params: search ? { search } : {} });
    return response.data;
  },

  async getHCPHistory(hcpId: number) {
    const response = await apiClient.get(`/history/${hcpId}`);
    return response.data;
  },

  async getAllInteractions(hcpId?: number, status?: string) {
    const response = await apiClient.get('/interaction', { params: { hcp_id: hcpId, status } });
    return response.data;
  },

  async getInteractionById(id: number) {
    const response = await apiClient.get(`/interaction/${id}`);
    return response.data;
  },

  async createInteraction(payload: any) {
    const response = await apiClient.post('/interaction', payload);
    return response.data;
  },

  async updateInteraction(id: number, payload: any) {
    const response = await apiClient.put(`/interaction/${id}`, payload);
    return response.data;
  },

  async deleteInteraction(id: number) {
    const response = await apiClient.delete(`/interaction/${id}`);
    return response.data;
  }
};
