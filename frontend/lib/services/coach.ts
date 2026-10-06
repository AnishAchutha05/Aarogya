import { apiJson } from "../api";
import type { ChatSessionResponse, ChatMessageResponse } from "@/types";

export const coachService = {
  async listSessions(): Promise<ChatSessionResponse[]> {
    return apiJson<ChatSessionResponse[]>("/coach/sessions");
  },

  async createSession(title?: string): Promise<ChatSessionResponse> {
    return apiJson<ChatSessionResponse>("/coach/sessions", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
  },

  async deleteSession(sessionId: string): Promise<void> {
    return apiJson<void>(`/coach/sessions/${sessionId}`, { method: "DELETE" });
  },

  async getMessages(sessionId: string): Promise<ChatMessageResponse[]> {
    return apiJson<ChatMessageResponse[]>(`/coach/sessions/${sessionId}/messages`);
  },

  async sendMessage(sessionId: string, content: string): Promise<ChatMessageResponse> {
    return apiJson<ChatMessageResponse>(`/coach/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
  },
};
