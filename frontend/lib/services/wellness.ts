import { apiJson } from "../api";
import type {
  GoalResponse, GoalCreate, GoalUpdate,
  ActivityResponse, ActivityCreate, ActivityLogResponse, ActivityLogCreate,
  CheckInCreate, CheckInResponse, InsightResponse,
} from "@/types";

export const wellnessService = {
  // Goals
  async listGoals(): Promise<GoalResponse[]> {
    return apiJson<GoalResponse[]>("/wellness/goals");
  },

  async createGoal(data: GoalCreate): Promise<GoalResponse> {
    return apiJson<GoalResponse>("/wellness/goals", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateGoal(id: string, data: GoalUpdate): Promise<GoalResponse> {
    return apiJson<GoalResponse>(`/wellness/goals/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async deleteGoal(id: string): Promise<void> {
    return apiJson<void>(`/wellness/goals/${id}`, { method: "DELETE" });
  },

  // Activities
  async listActivities(): Promise<ActivityResponse[]> {
    return apiJson<ActivityResponse[]>("/wellness/activities");
  },

  async createActivity(data: ActivityCreate): Promise<ActivityResponse> {
    return apiJson<ActivityResponse>("/wellness/activities", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async logActivity(data: ActivityLogCreate): Promise<ActivityLogResponse> {
    return apiJson<ActivityLogResponse>("/wellness/activities/log", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getActivityHistory(): Promise<ActivityLogResponse[]> {
    return apiJson<ActivityLogResponse[]>("/wellness/activities/history");
  },

  // Check-ins
  async checkIn(data: CheckInCreate): Promise<CheckInResponse> {
    return apiJson<CheckInResponse>("/progress/check-in", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getRecentCheckins(limit = 7): Promise<CheckInResponse[]> {
    return apiJson<CheckInResponse[]>(`/progress/check-ins?limit=${limit}`);
  },

  // Insights
  async getInsights(): Promise<InsightResponse[]> {
    return apiJson<InsightResponse[]>("/wellness/insights");
  },
};
