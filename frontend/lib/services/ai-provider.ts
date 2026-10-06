import { apiJson } from "../api";
import type { ProviderResponse } from "@/types";

export const aiProviderService = {
  async listProviders(): Promise<ProviderResponse[]> {
    return apiJson<ProviderResponse[]>("/ai-provider");
  },

  async addProvider(provider: string, apiKey: string): Promise<ProviderResponse> {
    return apiJson<ProviderResponse>("/ai-provider", {
      method: "POST",
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  },

  async setActiveProvider(provider: string): Promise<ProviderResponse> {
    return apiJson<ProviderResponse>("/ai-provider/active", {
      method: "POST",
      body: JSON.stringify({ provider }),
    });
  },

  async removeProvider(provider: string): Promise<void> {
    return apiJson<void>(`/ai-provider/${provider}`, { method: "DELETE" });
  },
};
