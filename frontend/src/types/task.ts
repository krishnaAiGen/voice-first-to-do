export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  category?: string;
  priority: number;
  status: 'pending' | 'in_progress' | 'completed';
  scheduled_time?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  display_order?: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  category?: string;
  priority?: number;
  status?: string;
  scheduled_time?: string;
}

export interface VoiceCommandRequest {
  audio_base64: string;
  transcript?: string;  // Optional: Skip STT if provided
  user_id?: string;
}

export interface VoiceCommandResponse {
  success: boolean;
  transcript: string;
  result: any;
  natural_response: string;
  latency_ms?: number;
}

