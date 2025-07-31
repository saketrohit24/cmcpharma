/**
 * Backend API service for all CMC Regulatory Writer API calls
 */

import { apiClient, type ApiResponse } from './apiClient';

// Backend API Types (matching Pydantic models)
export interface TOCItem {
  id: string;
  title: string;
  level: number;
  children?: TOCItem[];
}

export interface Template {
  id: string;
  name: string;
  description: string;
  toc: TOCItem[];
}

export interface TemplateCreationRequest {
  name: string;
  description?: string;
  toc_text: string;
}

export interface TemplateStructure {
  id: string;
  name: string;
  description: string;
  type: string;
  sections: TemplateSection[];
}

export interface TemplateSection {
  id: string;
  title: string;
  level: number;
  children: TemplateSection[];
}

export interface TemplateUpdateRequest {
  name?: string;
  description?: string;
  toc?: TOCItem[];
}

export interface FileItem {
  id: string;
  name: string;
  size: number;
  mime_type: string;
  path: string;
}

export interface GeneratedSection {
  id: string;
  title: string;
  content: string;
  source_count: number;
}

export interface GeneratedDocument {
  id: string;
  title: string;
  sections: GeneratedSection[];
  template_id: string;
  session_id: string;
  generated_at: string;
}

export interface RefinementRequest {
  section_title: string;
  current_content: string;
  refinement_request: string;
}

export interface ExportRequest {
  format: 'pdf' | 'docx';
  document: GeneratedDocument;
}

export interface HealthStatus {
  status: string;
  message: string;
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  context?: Record<string, string> | null;
  metadata?: Record<string, string> | null;
  session_id: string;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  created_at: string;
  last_activity: string;
  title: string | null;
  user_id: string | null;
  context: Record<string, string> | null;
  is_active: boolean;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  context?: Record<string, string>;
  max_tokens?: number;
  temperature?: number;
  include_citations?: boolean;
  use_rag?: boolean;
}

export interface ChatResponse {
  message: ChatMessage;
  session: ChatSession;
  citations?: string[] | null;
  tokens_used?: number | null;
  processing_time?: number | null;
}

export class BackendApiService {
  private sessionId: string;

  constructor(sessionId?: string) {
    this.sessionId = sessionId || this.generateSessionId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getSessionId(): string {
    return this.sessionId;
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<HealthStatus>> {
    return apiClient.get<HealthStatus>('/health');
  }

  // File Management
  async uploadFile(file: File): Promise<ApiResponse<FileItem>> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.postFormData<FileItem>(
      `/files/upload/${this.sessionId}`,
      formData
    );
  }

  // Template Management
  async parseTemplate(request: TemplateCreationRequest): Promise<ApiResponse<Template>> {
    return apiClient.post<Template>('/templates/parse', request);
  }

  async getTemplates(): Promise<ApiResponse<Template[]>> {
    return apiClient.get<Template[]>('/templates');
  }

  async getTemplate(templateId: string): Promise<ApiResponse<Template>> {
    return apiClient.get<Template>(`/templates/${templateId}`);
  }

  async saveTemplate(template: Template): Promise<ApiResponse<Template>> {
    return apiClient.post<Template>('/templates', template);
  }

  async updateTemplate(templateId: string, templateData: TemplateUpdateRequest): Promise<ApiResponse<Template>> {
    return apiClient.put<Template>(`/templates/${templateId}`, templateData);
  }

  async deleteTemplate(templateId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/templates/${templateId}`);
  }

  async uploadTemplateFile(file: File, name?: string, description?: string): Promise<ApiResponse<Template>> {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    if (description) formData.append('description', description);
    
    return apiClient.postFormData<Template>('/templates/upload', formData);
  }

  async getTemplateStructure(templateId: string): Promise<ApiResponse<TemplateStructure>> {
    return apiClient.get<TemplateStructure>(`/templates/structure/${templateId}`);
  }

  // Document Generation
  async generateDocument(template: Template): Promise<ApiResponse<GeneratedDocument>> {
    return apiClient.post<GeneratedDocument>(
      `/generation/generate/${this.sessionId}`,
      template
    );
  }

  async refineSection(request: RefinementRequest): Promise<ApiResponse<{ refined_content: string }>> {
    return apiClient.post<{ refined_content: string }>('/generation/refine', request);
  }

  // Export
  async exportDocument(request: ExportRequest): Promise<Response> {
    const url = `${apiClient['baseUrl']}/export/export`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return response;
  }

  // Chat functionality
  async sendChatMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    return apiClient.post<ChatResponse>('/chat/message', request);
  }

  async getChatSessions(): Promise<ApiResponse<ChatSession[]>> {
    return apiClient.get<ChatSession[]>('/chat/sessions');
  }

  async getChatSession(sessionId: string): Promise<ApiResponse<ChatSession>> {
    return apiClient.get<ChatSession>(`/chat/sessions/${sessionId}`);
  }

  async createChatSession(title?: string): Promise<ApiResponse<ChatSession>> {
    return apiClient.post<ChatSession>('/chat/sessions', {
      title: title || 'New Chat Session',
      user_id: this.sessionId
    });
  }

  async deleteChatSession(sessionId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/chat/sessions/${sessionId}`);
  }

  // Connection Test
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.healthCheck();
      return response.status === 200 && response.data?.status === 'ok';
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

// Singleton instance
export const backendApi = new BackendApiService();
