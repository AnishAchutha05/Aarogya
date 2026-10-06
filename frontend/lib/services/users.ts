import { apiJson } from "../api";
import type { UserResponse, ProfileResponse, ProfileUpdate } from "@/types";

export const usersService = {
  async getMe(): Promise<UserResponse> {
    return apiJson<UserResponse>("/users/me");
  },

  async getProfile(): Promise<ProfileResponse> {
    return apiJson<ProfileResponse>("/users/me/profile");
  },

  async updateProfile(data: ProfileUpdate): Promise<ProfileResponse> {
    return apiJson<ProfileResponse>("/users/me/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};
