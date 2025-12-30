import type {
  AdminLoginFormData,
  AdminLoginResponse,
  Announcement,
  AnnouncementFormData,
  APIError,
  Consumer,
  ConsumerFormData,
  Helper,
  HelperFormData,
  Producer,
  ProducerFormData,
  RequestByWeek,
  SnsRaiseUser,
  SnsUserFormData,
  UnfollowCheckerFormData,
  UnfollowCheckResult,
  UnfollowerServiceUserFormData,
  UnfollowerServiceUserResponse,
  UserActionVerification,
} from '@/types';
import axios, { AxiosError, AxiosInstance } from 'axios';

// API Base URL - use root-relative path to leverage Next.js rewrites
// Empty string or relative path causes issues on /admin/* routes
// Use window.location.origin for client-side, empty for server-side
const getApiBaseUrl = () => {
  // Server-side rendering: use empty string (relative to Next.js server)
  if (typeof window === 'undefined') {
    return '';
  }
  // Client-side: use root-relative path or window.location.origin
  return process.env.NEXT_PUBLIC_API_URL || window.location.origin;
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        if (window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
          window.location.href = '/admin/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Public API Functions

export const getAnnouncements = async (): Promise<Announcement[]> => {
  const response = await apiClient.get<Announcement[]>('/api/announcements');
  return response.data;
};

export const getRequestsByWeek = async (
  username?: string,
  limit: number = 100,
  offset: number = 0
): Promise<RequestByWeek[]> => {
  const params: any = { limit, offset };
  if (username) params.username = username;

  const response = await apiClient.get<RequestByWeek[]>('/api/request-by-week', { params });
  return response.data;
};

export const getUserActionVerification = async (
  username?: string,
  limit: number = 100,
  offset: number = 0
): Promise<UserActionVerification[]> => {
  const params: any = { limit, offset };
  if (username) params.username = username;

  const response = await apiClient.get<UserActionVerification[]>('/api/user-action-verification', { params });
  return response.data;
};

export const createConsumer = async (data: ConsumerFormData): Promise<Consumer> => {
  const response = await apiClient.post<Consumer>('/api/consumer', data);
  return response.data;
};

export const createProducer = async (data: ProducerFormData): Promise<Producer> => {
  const response = await apiClient.post<Producer>('/api/producer', data);
  return response.data;
};

export const checkUnfollowers = async (data: UnfollowCheckerFormData): Promise<UnfollowCheckResult> => {
  const response = await apiClient.post<UnfollowCheckResult>('/api/unfollow-checker', data);
  return response.data;
};

export const registerUnfollowerServiceUser = async (data: UnfollowerServiceUserFormData): Promise<UnfollowerServiceUserResponse> => {
  const response = await apiClient.post<UnfollowerServiceUserResponse>('/api/unfollower-service/register', data);
  return response.data;
};

// Admin API Functions

export const adminLogin = async (data: AdminLoginFormData): Promise<AdminLoginResponse> => {
  const response = await apiClient.post<AdminLoginResponse>('/api/admin/login', data);
  return response.data;
};

export const getSnsUsers = async (): Promise<SnsRaiseUser[]> => {
  const response = await apiClient.get<SnsRaiseUser[]>('/api/admin/sns-users');
  return response.data;
};

export const createSnsUser = async (data: SnsUserFormData): Promise<SnsRaiseUser> => {
  const response = await apiClient.post<SnsRaiseUser>('/api/admin/sns-users', data);
  return response.data;
};

export const updateSnsUser = async (id: number, data: SnsUserFormData): Promise<SnsRaiseUser> => {
  const response = await apiClient.put<SnsRaiseUser>(`/api/admin/sns-users/${id}`, data);
  return response.data;
};

export const deleteSnsUser = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/admin/sns-users/${id}`);
};

export const getHelpers = async (): Promise<Helper[]> => {
  const response = await apiClient.get<Helper[]>('/api/admin/helpers');
  return response.data;
};

export const createHelper = async (data: HelperFormData): Promise<Helper> => {
  const response = await apiClient.post<Helper>('/api/admin/helpers', data);
  return response.data;
};

export const deleteHelper = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/admin/helpers/${id}`);
};

export const getAdminAnnouncements = async (): Promise<Announcement[]> => {
  const response = await apiClient.get<Announcement[]>('/api/admin/announcements');
  return response.data;
};

export const createAnnouncement = async (data: AnnouncementFormData): Promise<Announcement> => {
  const response = await apiClient.post<Announcement>('/api/admin/announcements', data);
  return response.data;
};

export const updateAnnouncement = async (id: number, data: AnnouncementFormData): Promise<Announcement> => {
  const response = await apiClient.put<Announcement>(`/api/admin/announcements/${id}`, data);
  return response.data;
};

export const deleteAnnouncement = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/admin/announcements/${id}`);
};

// Export apiClient as api for direct use
export const api = apiClient;

// Helper function to handle API errors
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;
    return axiosError.response?.data?.detail || axiosError.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};

// Unfollowers API
export const getUnfollowers = async (owner: string) => {
  const response = await fetch(`${API_BASE_URL}/api/unfollowers/${owner}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch unfollowers');
  }
  return response.json();
};
