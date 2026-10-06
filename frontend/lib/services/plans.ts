import { apiJson } from "../api";
import type { PlanResponse, PlanItemResponse } from "@/types";

export const plansService = {
  async listPlans(): Promise<PlanResponse[]> {
    return apiJson<PlanResponse[]>("/plans");
  },

  async createPlan(data: { title: string; description?: string; start_date?: string; end_date?: string }): Promise<PlanResponse> {
    return apiJson<PlanResponse>("/plans", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getPlan(id: string): Promise<PlanResponse> {
    return apiJson<PlanResponse>(`/plans/${id}`);
  },

  async deletePlan(id: string): Promise<void> {
    return apiJson<void>(`/plans/${id}`, { method: "DELETE" });
  },

  async addPlanItem(planId: string, data: {
    title: string;
    description?: string;
    item_type?: string;
    day_of_week?: number;
    duration_minutes?: number;
    sort_order?: number;
  }): Promise<PlanItemResponse> {
    return apiJson<PlanItemResponse>(`/plans/${planId}/items`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async completePlanItem(planId: string, itemId: string): Promise<PlanItemResponse> {
    return apiJson<PlanItemResponse>(`/plans/${planId}/items/${itemId}/complete`, {
      method: "POST",
    });
  },
};
