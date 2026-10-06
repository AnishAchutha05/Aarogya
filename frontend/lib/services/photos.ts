import { apiFetch, API_URL, getAccessToken } from "../api";
import { ApiError } from "../api";
import type { PhotoResponse } from "@/types";

export const photosService = {
  async listPhotos(): Promise<PhotoResponse[]> {
    const response = await apiFetch("/photos");
    if (!response.ok) throw new ApiError(response.status, "Failed to load photos");
    return response.json();
  },

  async uploadPhoto(file: File, photoDate?: string, notes?: string): Promise<PhotoResponse> {
    const formData = new FormData();
    formData.append("file", file);
    if (photoDate) formData.append("photo_date", photoDate);
    if (notes) formData.append("notes", notes);

    const response = await apiFetch("/photos", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      let msg = "Upload failed";
      try { const err = await response.json(); msg = err.detail || msg; } catch {}
      throw new ApiError(response.status, msg);
    }
    return response.json();
  },

  async deletePhoto(photoId: string): Promise<void> {
    const response = await apiFetch(`/photos/${photoId}`, { method: "DELETE" });
    if (!response.ok && response.status !== 204) {
      throw new ApiError(response.status, "Failed to delete photo");
    }
  },

  getPhotoUrl(photoId: string): string {
    const token = getAccessToken();
    return `${API_URL}/photos/${photoId}/file?token=${token}`;
  },

  // For actual file retrieval we need to fetch with auth header
  async getPhotoBlob(photoId: string): Promise<string> {
    const response = await apiFetch(`/photos/${photoId}/file`);
    if (!response.ok) throw new ApiError(response.status, "Failed to load photo");
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  },
};
