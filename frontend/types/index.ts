// API Response Types matching backend schemas

export interface UserResponse {
  id: string;
  email: string;
  name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProfileResponse {
  id: string;
  user_id: string;
  dob?: string;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  nationality?: string;
  region?: string;
  dietary_preferences?: string; // JSON string
  commonly_eaten_foods?: string; // JSON string
  lifestyle_info?: string; // JSON string
  activity_level?: string;
  timezone?: string;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdate {
  dob?: string;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  nationality?: string;
  region?: string;
  dietary_preferences?: string[];
  commonly_eaten_foods?: string[];
  lifestyle_info?: Record<string, unknown>;
  activity_level?: string;
  timezone?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

export interface GoalResponse {
  id: string;
  title: string;
  description?: string;
  category?: string;
  target_value?: number;
  target_unit?: string;
  current_value?: number;
  target_date?: string;
  is_active: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface GoalCreate {
  title: string;
  description?: string;
  category?: string;
  target_value?: number;
  target_unit?: string;
  target_date?: string;
}

export interface GoalUpdate {
  title?: string;
  description?: string;
  category?: string;
  target_value?: number;
  target_unit?: string;
  current_value?: number;
  target_date?: string;
  is_active?: boolean;
  is_completed?: boolean;
}

export interface ActivityResponse {
  id: string;
  name: string;
  description?: string;
  category?: string;
  duration_minutes?: number;
  is_active: boolean;
  created_at: string;
}

export interface ActivityCreate {
  name: string;
  description?: string;
  category?: string;
  duration_minutes?: number;
}

export interface ActivityLogResponse {
  id: string;
  activity_id: string;
  logged_date: string;
  duration_minutes?: number;
  notes?: string;
  intensity?: string;
  created_at: string;
}

export interface ActivityLogCreate {
  activity_id: string;
  logged_date: string;
  duration_minutes?: number;
  notes?: string;
  intensity?: string;
}

export interface CheckInCreate {
  check_in_date: string;
  mood_score?: number;
  energy_score?: number;
  sleep_hours?: number;
  water_intake_ml?: number;
  notes?: string;
  stress_score?: number;
}

export interface CheckInResponse {
  id: string;
  check_in_date: string;
  mood_score?: number;
  energy_score?: number;
  sleep_hours?: number;
  water_intake_ml?: number;
  notes?: string;
  stress_score?: number;
  created_at: string;
  updated_at: string;
}

export interface InsightResponse {
  id: string;
  category?: string;
  title: string;
  content: string;
  is_read: boolean;
  source?: string;
  created_at: string;
}

export interface PlanResponse {
  id: string;
  title: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  is_active: boolean;
  created_at: string;
  items: PlanItemResponse[];
}

export interface PlanItemResponse {
  id: string;
  plan_id: string;
  title: string;
  description?: string;
  item_type?: string;
  day_of_week?: number;
  duration_minutes?: number;
  is_completed: boolean;
  completed_at?: string;
  sort_order: number;
  created_at: string;
}

export interface ChatSessionResponse {
  id: string;
  title?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageResponse {
  id: string;
  session_id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface ProviderResponse {
  id: string;
  provider: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface PhotoResponse {
  id: string;
  photo_date?: string;
  notes?: string;
  file_path?: string;
  created_at: string;
}

export interface RoadmapResponse {
  markdown: string;
}
