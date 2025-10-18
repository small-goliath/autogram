import { axiosInstance } from './axios';

// Types
export interface SnsUser {
  id: number;
  username: string;
  instagram_id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RequestByWeek {
  id: number;
  user_id: number;
  username: string;
  instagram_link: string;
  request_date: string;
  week_start_date: string;
  week_end_date: string;
  status: string;
  comment_count: number;
}

export interface UserActionVerification {
  id: number;
  user_id: number;
  username: string;
  instagram_link: string;
  link_owner_username: string;
  is_commented: boolean;
  verified_at: string;
}

export interface Notice {
  id: number;
  title: string;
  content: string;
  is_pinned: boolean;
  is_important: boolean;
  view_count: number;
  created_at: string;
}

export interface NoticesResponse {
  kakaotalk_open_chat_link: string;
  kakaotalk_qr_code_path: string;
  notices: Notice[];
}

export interface Admin {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_superadmin: boolean;
  last_login_at: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UnfollowerCheckRequest {
  instagram_id: string;
  instagram_password: string;
}

export interface UnfollowerCheckResponse {
  unfollowers: string[];
  total_count: number;
}

// Public API
export const publicApi = {
  // Get notices
  getNotices: () =>
    axiosInstance.get<NoticesResponse>('/api/py/notices'),

  // Get weekly requests (with optional username filter)
  getRequestsByWeek: (username?: string) =>
    axiosInstance.get<RequestByWeek[]>('/api/py/requests-by-week', {
      params: username ? { username } : undefined,
    }),

  // Get user action verification (with optional username filter)
  getUserActionVerification: (username?: string) =>
    axiosInstance.get<UserActionVerification[]>('/api/py/user-action-verification', {
      params: username ? { username } : undefined,
    }),

  // Register as consumer
  registerConsumer: (data: {
    instagram_id: string;
    comment_tone: string;
    special_requests?: string;
  }) =>
    axiosInstance.post('/api/py/consumer', data),

  // Register as producer
  registerProducer: (data: {
    instagram_id: string;
    instagram_password: string;
  }) =>
    axiosInstance.post('/api/py/producer', data),

  // Check unfollowers
  checkUnfollowers: (data: UnfollowerCheckRequest) =>
    axiosInstance.post<UnfollowerCheckResponse>('/api/py/unfollow-checker', data),
};

// Admin API
export const adminApi = {
  // Login
  login: (username: string, password: string) =>
    axiosInstance.post<LoginResponse>('/api/py/admin/login',
      new URLSearchParams({ username, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ),

  // Get current admin info
  getMe: () =>
    axiosInstance.get<Admin>('/api/py/admin/me'),

  // SNS Users
  getSnsUsers: () =>
    axiosInstance.get<SnsUser[]>('/api/py/admin/sns-users'),

  getSnsUser: (id: number) =>
    axiosInstance.get<SnsUser>(`/api/py/admin/sns-users/${id}`),

  createSnsUser: (data: {
    username: string;
    instagram_id: string;
    email: string;
    is_active?: boolean;
  }) =>
    axiosInstance.post<SnsUser>('/api/py/admin/sns-users', data),

  updateSnsUser: (id: number, data: {
    username?: string;
    instagram_id?: string;
    email?: string;
    is_active?: boolean;
  }) =>
    axiosInstance.put<SnsUser>(`/api/py/admin/sns-users/${id}`, data),

  deleteSnsUser: (id: number) =>
    axiosInstance.delete(`/api/py/admin/sns-users/${id}`),

  // Helpers
  getHelpers: () =>
    axiosInstance.get('/api/py/admin/helpers'),

  registerHelper: (data: {
    instagram_id: string;
    instagram_password: string;
  }) =>
    axiosInstance.post('/api/py/admin/helpers', data),

  deleteHelper: (id: number) =>
    axiosInstance.delete(`/api/py/admin/helpers/${id}`),
};
