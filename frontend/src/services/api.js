const API_BASE_URL = 'http://localhost:8001';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }
  return response.json();
};

const makeRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    return await handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(`Error de conexión: ${error.message}`, 0, error);
  }
};

// ============ SERVICIOS DE ESTUDIANTES ============
export const studentsApi = {
  getAll: (filters = {}) => {
    const params = new URLSearchParams(filters);
    const queryString = params.toString();
    return makeRequest(`/students${queryString ? `?${queryString}` : ''}`);
  },

  getById: (id) => makeRequest(`/students/${id}`),

  create: (studentData) => makeRequest('/students', {
    method: 'POST',
    body: JSON.stringify(studentData),
  }),

  update: (id, studentData) => makeRequest(`/students/${id}`, {
    method: 'PUT',
    body: JSON.stringify(studentData),
  }),

  delete: (id) => makeRequest(`/students/${id}`, {
    method: 'DELETE',
  }),
};

// ============ SERVICIOS DE ACTIVIDADES ============
export const activitiesApi = {
  getAll: (filters = {}) => {
    const params = new URLSearchParams(filters);
    const queryString = params.toString();
    return makeRequest(`/activities${queryString ? `?${queryString}` : ''}`);
  },

  getById: (id) => makeRequest(`/activities/${id}`),

  create: (activityData) => makeRequest('/activities', {
    method: 'POST',
    body: JSON.stringify(activityData),
  }),

  update: (id, activityData) => makeRequest(`/activities/${id}`, {
    method: 'PUT',
    body: JSON.stringify(activityData),
  }),

  delete: (id) => makeRequest(`/activities/${id}`, {
    method: 'DELETE',
  }),
};

// ============ SERVICIOS DEL DASHBOARD ============
export const dashboardApi = {
  getData: () => makeRequest('/dashboard'),
};

// ============ SERVICIOS DEL CHAT ============
export const chatApi = {
  getMessages: () => makeRequest('/chat/messages'),

  sendMessage: (messageData) => makeRequest('/chat/messages', {
    method: 'POST',
    body: JSON.stringify(messageData),
  }),

  getActiveUsers: () => makeRequest('/chat/users'),
};

// ============ SERVICIOS AUXILIARES ============
export const utilsApi = {
  getSubjects: () => makeRequest('/subjects'),

  healthCheck: () => makeRequest('/health'),
};

// ============ HOOK PERSONALIZADO PARA REACT ============
import { useState, useEffect, useCallback } from 'react';

export const useApi = (apiFunction, deps = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const memoizedApiFunction = useCallback(apiFunction, deps);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await memoizedApiFunction();
        setData(result);
      } catch (err) {
        setError(err);
        console.error('Error en API:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [memoizedApiFunction]);

  const refetch = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await memoizedApiFunction();
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch };
};

export const useMutation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const mutate = async (apiFunction) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { mutate, loading, error };
};

export { API_BASE_URL, ApiError };

const apiService = {
  students: studentsApi,
  activities: activitiesApi,
  dashboard: dashboardApi,
  chat: chatApi,
  utils: utilsApi,
};

export default apiService;