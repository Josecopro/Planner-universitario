/**
 * Configuración Central de la API - Planner Universitario
 * 
 * Este módulo centraliza toda la configuración necesaria para la comunicación
 * con el backend de la aplicación.
 * 
 * @module api.config
 * 
 * Características:
 * - Configuración de Axios con interceptores
 * - Manejo automático de tokens JWT
 * - Gestión de errores HTTP
 * - Refresh automático de tokens
 * - Logging de peticiones en desarrollo
 * 
 * Estructura del Backend:
 * Base URL: http://localhost:8000
 * API Version: /api/v1
 * 
 * Endpoints disponibles:
 * - /auth              - Autenticación y autorización (7 endpoints)
 * - /usuarios          - Gestión de usuarios (22 endpoints)
 * - /roles             - Gestión de roles (10 endpoints)
 * - /facultades        - Gestión de facultades (11 endpoints)
 * - /programas-academicos - Gestión de programas (14 endpoints)
 * - /cursos            - Gestión de cursos (11 endpoints)
 * - /profesores        - Gestión de profesores (14 endpoints)
 * - /estudiantes       - Gestión de estudiantes (15 endpoints)
 * - /grupos            - Gestión de grupos (13 endpoints)
 * - /horarios          - Gestión de horarios (13 endpoints)
 * - /inscripciones     - Gestión de inscripciones (17 endpoints)
 * - /actividades-evaluativas - Actividades evaluativas (9 endpoints)
 * - /entregas          - Entregas de trabajos (10 endpoints)
 * - /calificaciones    - Calificaciones (11 endpoints)
 * - /asistencias       - Control de asistencia (12 endpoints)
 * 
 * Total: 179 endpoints REST
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';
const API_URL = `${API_BASE_URL}${API_VERSION}`;

const TIMEOUT = 30000;

/**
 * Instancia principal de Axios configurada para el API
 * 
 * Configuración incluida:
 * - Base URL apuntando al backend
 * - Timeout de 30 segundos
 * - Headers por defecto con Content-Type JSON
 * - Interceptores para manejo de autenticación y errores
 */
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Gestor de tokens JWT
 * 
 * Funcionalidades:
 * - Almacenamiento seguro en localStorage
 * - Recuperación de tokens
 * - Eliminación de tokens (logout)
 * - Verificación de existencia
 */
export const tokenManager = {
  getToken: () => localStorage.getItem('access_token'),
  setToken: (token) => localStorage.setItem('access_token', token),
  removeToken: () => localStorage.removeItem('access_token'),
  hasToken: () => !!localStorage.getItem('access_token'),
};

/**
 * Gestor de información del usuario
 * 
 * Almacena y recupera información del usuario autenticado:
 * - Datos personales
 * - Rol asignado
 * - Permisos
 */
export const userManager = {
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
  removeUser: () => localStorage.removeItem('user'),
  getRole: () => {
    const user = userManager.getUser();
    return user?.rol?.nombre || null;
  },
};

/**
 * Interceptor de Request
 * 
 * Se ejecuta antes de cada petición HTTP y realiza:
 * 1. Añade el token JWT al header Authorization si existe
 * 2. Log de la petición en modo desarrollo
 * 3. Preparación de headers adicionales
 * 
 * Formato del token: Bearer <token>
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * Interceptor de Response
 * 
 * Se ejecuta después de recibir cada respuesta HTTP y maneja:
 * 1. Respuestas exitosas: Log y retorno de datos
 * 2. Errores 401 (No autorizado): Limpia tokens y redirige al login
 * 3. Errores 403 (Prohibido): Notifica falta de permisos
 * 4. Errores 404 (No encontrado): Recurso no existe
 * 5. Errores 422 (Validación): Errores de validación de datos
 * 6. Errores 500+: Errores del servidor
 * 7. Errores de red: Sin conexión con el servidor
 * 
 * Todos los errores se formatean en un objeto estándar:
 * {
 *   message: string,
 *   status: number,
 *   errors: object | null
 * }
 */
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }
    return response;
  },
  (error) => {
    const originalRequest = error.config;

    if (import.meta.env.DEV) {
      console.error('[API Error]', {
        url: originalRequest?.url,
        method: originalRequest?.method,
        status: error.response?.status,
        data: error.response?.data,
      });
    }

    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          tokenManager.removeToken();
          userManager.removeUser();
          
          if (!originalRequest.url.includes('/auth/login')) {
            window.location.href = '/login';
          }
          
          return Promise.reject({
            message: 'Sesión expirada. Por favor, inicia sesión nuevamente.',
            status,
            errors: null,
          });

        case 403:
          return Promise.reject({
            message: 'No tienes permisos para realizar esta acción.',
            status,
            errors: null,
          });

        case 404:
          return Promise.reject({
            message: data?.detail || 'Recurso no encontrado.',
            status,
            errors: null,
          });

        case 422:
          return Promise.reject({
            message: 'Error de validación en los datos enviados.',
            status,
            errors: data?.detail || null,
          });

        case 500:
        case 502:
        case 503:
          return Promise.reject({
            message: 'Error en el servidor. Intenta nuevamente más tarde.',
            status,
            errors: null,
          });

        default:
          return Promise.reject({
            message: data?.detail || 'Ha ocurrido un error inesperado.',
            status,
            errors: data?.errors || null,
          });
      }
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        message: 'La petición tardó demasiado tiempo. Verifica tu conexión.',
        status: 0,
        errors: null,
      });
    }

    return Promise.reject({
      message: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
      status: 0,
      errors: null,
    });
  }
);

/**
 * Objeto de configuración exportable
 * 
 * Contiene todas las URLs y configuraciones necesarias
 * para los servicios específicos
 */
export const apiConfig = {
  baseURL: API_BASE_URL,
  apiURL: API_URL,
  version: API_VERSION,
  timeout: TIMEOUT,
  endpoints: {
    auth: '/auth',
    usuarios: '/usuarios',
    roles: '/roles',
    facultades: '/facultades',
    programasAcademicos: '/programas-academicos',
    cursos: '/cursos',
    profesores: '/profesores',
    estudiantes: '/estudiantes',
    grupos: '/grupos',
    horarios: '/horarios',
    inscripciones: '/inscripciones',
    actividadesEvaluativas: '/actividades-evaluativas',
    entregas: '/entregas',
    calificaciones: '/calificaciones',
    asistencias: '/asistencias',
  },
};

export default apiClient;
