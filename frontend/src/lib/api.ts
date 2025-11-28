import axios from 'axios';
import { Task, VoiceCommandRequest, VoiceCommandResponse } from '@/types/task';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  // Register new user
  register: async (email: string, password: string, displayName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      display_name: displayName,
    });
    return response.data;
  },

  // Login user
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Get current user info
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Logout
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Chat API
export const chatApi = {
  // Get chat history
  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get('/chat/history', {
      params: { limit, offset },
    });
    return response.data;
  },

  // Clear chat history
  clearHistory: async () => {
    const response = await api.delete('/chat/history');
    return response.data;
  },
};

// Task API
export const taskApi = {
  // Get all tasks
  getTasks: async (): Promise<Task[]> => {
    const response = await api.get('/tasks');
    return response.data.tasks;
  },

  // Get single task
  getTask: async (id: string): Promise<Task> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  // Create task
  createTask: async (task: Partial<Task>): Promise<Task> => {
    const response = await api.post('/tasks', task);
    return response.data;
  },

  // Update task
  updateTask: async (id: string, updates: Partial<Task>): Promise<Task> => {
    const response = await api.put(`/tasks/${id}`, updates);
    return response.data;
  },

  // Delete task
  deleteTask: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  // Quick transcribe only (returns immediately with transcript)
  transcribeOnly: async (request: VoiceCommandRequest): Promise<{ success: boolean; transcript: string }> => {
    const response = await api.post('/voice/transcribe', request);
    return response.data;
  },

  // Process voice command (full processing)
  processVoiceCommand: async (
    request: VoiceCommandRequest
  ): Promise<VoiceCommandResponse> => {
    const response = await api.post('/voice/process', request);
    return response.data;
  },
};

export default api;

