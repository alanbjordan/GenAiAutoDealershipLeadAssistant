// src/utils/api.js
import axios from 'axios';

// Default to the Heroku deployment URL
const DEFAULT_API_URL = process.env.REACT_APP_API_URL || 'https://student-success-15b4e9507355.herokuapp.com/api';

// Backup API URL (local development server)
const BACKUP_API_URL = 'http://localhost:5000/api';

// Create the axios instance with the default (deployment) base URL
const apiClient = axios.create({
  baseURL: DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add an interceptor to handle errors and retry with the backup URL if needed
apiClient.interceptors.response.use(
  response => response, // pass through successful responses
  async error => {
    // Check if error is network-related (server unreachable)
    if (
      error.code === 'ECONNABORTED' ||
      error.message === 'Network Error' ||
      (!error.response && error.config)
    ) {
      const originalConfig = error.config;
      // Prevent infinite loops by marking the config that it's been retried
      if (!originalConfig._retry) {
        originalConfig._retry = true;
        // Change the baseURL to the backup URL
        originalConfig.baseURL = BACKUP_API_URL;
        // Reattempt the request with the new configuration
        return apiClient(originalConfig);
      }
    }
    // If it still fails or the error isn't network-related, reject the promise
    return Promise.reject(error);
  }
);

// API calls
export const uploadFile = (formData) => {
  return apiClient.post('/test', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export default apiClient;
