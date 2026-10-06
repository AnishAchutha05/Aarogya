import { apiJson } from "../api";
import type { RoadmapResponse } from "@/types";

export const roadmapService = {
  async generateFromSession(sessionId: string): Promise<RoadmapResponse> {
    return apiJson<RoadmapResponse>(`/roadmap/from-session/${sessionId}`, {
      method: "POST",
    });
  },
};
