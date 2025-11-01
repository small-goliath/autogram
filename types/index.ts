// API Response Types

export interface Announcement {
  id: number;
  title: string;
  content: string;
  kakao_openchat_link?: string;
  kakao_qr_code_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RequestByWeek {
  id: number;
  sns_raise_user_id: number;
  username: string;
  instagram_link: string;
  week_start_date: string;
  created_at: string;
}

export interface UserActionVerification {
  id: number;
  sns_raise_user_id: number;
  username: string;
  instagram_link: string;
  link_owner_username: string;
  has_commented: boolean;
  created_at: string;
}

export interface SnsRaiseUser {
  id: number;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface Helper {
  id: number;
  instagram_username: string;
  is_active: boolean;
  last_used_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Consumer {
  id: number;
  instagram_username: string;
  created_at: string;
}

export interface Producer {
  id: number;
  instagram_username: string;
  created_at: string;
}

export interface UnfollowCheckResult {
  following: string[];
  followers: string[];
  not_following_back: string[];
  total_following: number;
  total_followers: number;
  total_unfollowers: number;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
}

export interface Admin {
  id: number;
  username: string;
  created_at: string;
  updated_at: string;
}

// Form Data Types

export interface ConsumerFormData {
  instagram_username: string;
}

export interface ProducerFormData {
  instagram_username: string;
  instagram_password: string;
  verification_code?: string;
}

export interface UnfollowCheckerFormData {
  instagram_username: string;
  instagram_password: string;
  verification_code?: string;
}

export interface AdminLoginFormData {
  username: string;
  password: string;
}

export interface SnsUserFormData {
  username: string;
}

export interface HelperFormData {
  instagram_username: string;
  instagram_password: string;
  verification_code?: string;
}

export interface AnnouncementFormData {
  title: string;
  content: string;
  kakao_openchat_link?: string;
  kakao_qr_code_url?: string;
  is_active: boolean;
}

// API Error Response
export interface APIError {
  detail: string;
}
