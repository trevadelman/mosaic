import axios, { type AxiosInstance } from 'axios';

// Create axios instance with default config
export const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use((config) => {
  // You can add auth headers or other request modifications here
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle API errors here
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API request/response types
export interface XetoConvertRequest {
  json_path: string;
  manufacturer: string;
  model: string;
}

export interface XetoCompileRequest {
  lib_content: string;
  specs_content: string;
  manufacturer: string;
  model: string;
}

export interface XetoSaveRequest {
  lib_content: string;
  specs_content: string;
  manufacturer: string;
  model: string;
}

export interface XetoResponse {
  success: boolean;
  lib_content?: string;
  specs_content?: string;
  output?: string;
  error?: string;
  paths?: {
    lib: string;
    specs: string;
  };
}

// API endpoints for Xeto operations
export const xetoApi = {
  convertToXeto: (data: XetoConvertRequest) => 
    api.post<XetoResponse>('/apps/pdf-ingestion/convert-to-xeto', data),

  compileXeto: (data: XetoCompileRequest) => 
    api.post<XetoResponse>('/apps/pdf-ingestion/compile-xeto', data),

  saveXeto: (data: XetoSaveRequest) => 
    api.post<XetoResponse>('/apps/pdf-ingestion/save-xeto', data),
};
