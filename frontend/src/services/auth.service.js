/**
 * Servicio de Autenticación - Planner Universitario
 * 
 * Módulo encargado de todas las operaciones de autenticación y autorización.
 * Implementa los 7 endpoints del módulo de autenticación del backend.
 * 
 * @module auth.service
 * 
 * Endpoints implementados:
 * 1. POST /auth/login                - Iniciar sesión y obtener token JWT
 * 2. GET /auth/me                    - Obtener información del usuario actual
 * 3. POST /auth/change-password      - Cambiar contraseña del usuario
 * 4. POST /auth/verify-token         - Verificar validez del token
 * 5. POST /auth/logout               - Cerrar sesión (invalidar token)
 * 6. GET /auth/check-permissions     - Verificar permisos del usuario
 * 7. GET /auth/session-info          - Información de la sesión actual
 * 
 * Seguridad implementada:
 * - JWT Bearer Token con expiración de 24 horas
 * - Rate limiting en login (máximo 5 intentos)
 * - Bloqueo de cuenta tras intentos fallidos
 * - Validación de estado de usuario (Activo/Inactivo)
 * 
 * Roles disponibles:
 * - Superadmin: Acceso completo al sistema
 * - Profesor: Gestión de grupos, notas, asistencias
 * - Estudiante: Acceso a cursos inscritos, entregas, notas
 */

import apiClient, { tokenManager, userManager } from './api.config';

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  ME: '/auth/me',
  CHANGE_PASSWORD: '/auth/change-password',
  VERIFY_TOKEN: '/auth/verify-token',
  LOGOUT: '/auth/logout',
  CHECK_PERMISSIONS: '/auth/check-permissions',
  SESSION_INFO: '/auth/session-info',
};

/**
 * Servicio de Autenticación
 * 
 * Proporciona métodos para todas las operaciones de autenticación
 * y gestión de sesiones de usuario
 */
const authService = {
  /**
   * Iniciar sesión en el sistema
   * 
   * Autentica al usuario con email y contraseña, obtiene un token JWT
   * y almacena la información del usuario en localStorage
   * 
   * @async
   * @param {Object} credentials - Credenciales del usuario
   * @param {string} credentials.email - Email del usuario
   * @param {string} credentials.password - Contraseña del usuario
   * @returns {Promise<Object>} Objeto con token y datos del usuario
   * @returns {string} return.access_token - Token JWT para autenticación
   * @returns {string} return.token_type - Tipo de token (Bearer)
   * @returns {Object} return.usuario - Información del usuario autenticado
   * @returns {number} return.usuario.id - ID del usuario
   * @returns {string} return.usuario.email - Email del usuario
   * @returns {string} return.usuario.nombre - Nombre del usuario
   * @returns {string} return.usuario.apellido - Apellido del usuario
   * @returns {Object} return.usuario.rol - Rol del usuario
   * @returns {string} return.usuario.rol.nombre - Nombre del rol
   * 
   * @throws {Error} Credenciales inválidas (401)
   * @throws {Error} Usuario inactivo o bloqueado (403)
   * @throws {Error} Demasiados intentos de login (429)
   * 
   * @example
   * const result = await authService.login({
   *   email: 'admin@universidad.edu',
   *   password: 'Admin123!'
   * });
   * console.log(result.usuario.nombre); // "Super"
   */
  async login(credentials) {
    const response = await apiClient.post(AUTH_ENDPOINTS.LOGIN, credentials);
    const { access_token, usuario } = response.data;
    
    tokenManager.setToken(access_token);
    userManager.setUser(usuario);
    
    return response.data;
  },

  /**
   * Obtener información del usuario actual
   * 
   * Recupera los datos completos del usuario autenticado actualmente
   * 
   * @async
   * @requires Token JWT válido
   * @returns {Promise<Object>} Información completa del usuario
   * @returns {number} return.id - ID del usuario
   * @returns {string} return.email - Email del usuario
   * @returns {string} return.nombre - Nombre del usuario
   * @returns {string} return.apellido - Apellido del usuario
   * @returns {string} return.estado - Estado del usuario (Activo/Inactivo)
   * @returns {Object} return.rol - Información del rol
   * @returns {string} return.rol.nombre - Nombre del rol
   * @returns {string} return.rol.descripcion - Descripción del rol
   * @returns {string|null} return.ultimo_acceso - Fecha del último acceso
   * 
   * @throws {Error} No autorizado - Token inválido o expirado (401)
   * 
   * @example
   * const currentUser = await authService.getCurrentUser();
   * console.log(`${currentUser.nombre} - ${currentUser.rol.nombre}`);
   */
  async getCurrentUser() {
    const response = await apiClient.get(AUTH_ENDPOINTS.ME);
    userManager.setUser(response.data);
    return response.data;
  },

  /**
   * Cambiar contraseña del usuario
   * 
   * Permite al usuario autenticado cambiar su contraseña actual
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} passwordData - Datos para cambio de contraseña
   * @param {string} passwordData.current_password - Contraseña actual
   * @param {string} passwordData.new_password - Nueva contraseña
   * @param {string} passwordData.confirm_password - Confirmación de nueva contraseña
   * @returns {Promise<Object>} Mensaje de confirmación
   * @returns {string} return.message - Mensaje de éxito
   * 
   * @throws {Error} Contraseña actual incorrecta (400)
   * @throws {Error} Las contraseñas no coinciden (400)
   * @throws {Error} No autorizado (401)
   * 
   * @example
   * await authService.changePassword({
   *   current_password: 'OldPass123!',
   *   new_password: 'NewPass123!',
   *   confirm_password: 'NewPass123!'
   * });
   */
  async changePassword(passwordData) {
    const response = await apiClient.post(AUTH_ENDPOINTS.CHANGE_PASSWORD, passwordData);
    return response.data;
  },

  /**
   * Verificar validez del token JWT
   * 
   * Comprueba si el token actual es válido y no ha expirado
   * 
   * @async
   * @requires Token JWT
   * @returns {Promise<Object>} Estado del token
   * @returns {boolean} return.valid - Indica si el token es válido
   * @returns {Object} return.token_data - Datos decodificados del token
   * @returns {number} return.token_data.user_id - ID del usuario
   * @returns {string} return.token_data.email - Email del usuario
   * @returns {number} return.token_data.exp - Timestamp de expiración
   * 
   * @throws {Error} Token inválido o expirado (401)
   * 
   * @example
   * const tokenStatus = await authService.verifyToken();
   * if (tokenStatus.valid) {
   *   console.log('Token válido hasta:', new Date(tokenStatus.token_data.exp * 1000));
   * }
   */
  async verifyToken() {
    const response = await apiClient.post(AUTH_ENDPOINTS.VERIFY_TOKEN);
    return response.data;
  },

  /**
   * Cerrar sesión del usuario
   * 
   * Invalida el token actual y limpia los datos de sesión del localStorage
   * 
   * @async
   * @requires Token JWT válido
   * @returns {Promise<Object>} Mensaje de confirmación
   * @returns {string} return.message - Mensaje de éxito
   * 
   * @example
   * await authService.logout();
   * // Usuario será redirigido al login
   */
  async logout() {
    try {
      const response = await apiClient.post(AUTH_ENDPOINTS.LOGOUT);
      return response.data;
    } finally {
      tokenManager.removeToken();
      userManager.removeUser();
    }
  },

  /**
   * Verificar permisos del usuario actual
   * 
   * Obtiene la lista de permisos asignados al rol del usuario
   * 
   * @async
   * @requires Token JWT válido
   * @returns {Promise<Object>} Información de permisos
   * @returns {string} return.rol - Nombre del rol
   * @returns {Array<string>} return.permisos - Lista de permisos
   * @returns {Object} return.puede - Objeto con flags de permisos
   * @returns {boolean} return.puede.crear_usuarios - Puede crear usuarios
   * @returns {boolean} return.puede.editar_grupos - Puede editar grupos
   * @returns {boolean} return.puede.calificar - Puede calificar
   * 
   * @throws {Error} No autorizado (401)
   * 
   * @example
   * const permissions = await authService.checkPermissions();
   * if (permissions.puede.calificar) {
   *   // Mostrar opciones de calificación
   * }
   */
  async checkPermissions() {
    const response = await apiClient.get(AUTH_ENDPOINTS.CHECK_PERMISSIONS);
    return response.data;
  },

  /**
   * Obtener información de la sesión actual
   * 
   * Recupera datos detallados sobre la sesión activa
   * 
   * @async
   * @requires Token JWT válido
   * @returns {Promise<Object>} Información de sesión
   * @returns {Object} return.usuario - Datos del usuario
   * @returns {string} return.token_expires_at - Fecha de expiración del token
   * @returns {number} return.tiempo_restante_minutos - Minutos hasta expiración
   * @returns {string} return.ip_address - Dirección IP de la sesión
   * @returns {string} return.user_agent - User agent del navegador
   * 
   * @throws {Error} No autorizado (401)
   * 
   * @example
   * const sessionInfo = await authService.getSessionInfo();
   * console.log(`Sesión expira en ${sessionInfo.tiempo_restante_minutos} minutos`);
   */
  async getSessionInfo() {
    const response = await apiClient.get(AUTH_ENDPOINTS.SESSION_INFO);
    return response.data;
  },

  /**
   * Verificar si el usuario está autenticado
   * 
   * Comprueba si existe un token en localStorage
   * 
   * @returns {boolean} True si existe token, false en caso contrario
   * 
   * @example
   * if (!authService.isAuthenticated()) {
   *   router.push('/login');
   * }
   */
  isAuthenticated() {
    return tokenManager.hasToken();
  },

  /**
   * Obtener el rol del usuario actual
   * 
   * Recupera el nombre del rol desde los datos almacenados del usuario
   * 
   * @returns {string|null} Nombre del rol o null si no hay usuario
   * 
   * @example
   * const userRole = authService.getUserRole();
   * if (userRole === 'Superadmin') {
   *   // Mostrar panel de administración
   * }
   */
  getUserRole() {
    return userManager.getRole();
  },

  /**
   * Verificar si el usuario tiene un rol específico
   * 
   * @param {string} role - Nombre del rol a verificar
   * @returns {boolean} True si el usuario tiene el rol, false en caso contrario
   * 
   * @example
   * if (authService.hasRole('Profesor')) {
   *   // Mostrar opciones de profesor
   * }
   */
  hasRole(role) {
    return userManager.getRole() === role;
  },

  /**
   * Verificar si el usuario es Superadmin
   * 
   * @returns {boolean} True si es Superadmin, false en caso contrario
   * 
   * @example
   * if (authService.isSuperadmin()) {
   *   // Mostrar gestión de usuarios
   * }
   */
  isSuperadmin() {
    return this.hasRole('Superadmin');
  },

  /**
   * Verificar si el usuario es Profesor
   * 
   * @returns {boolean} True si es Profesor, false en caso contrario
   * 
   * @example
   * if (authService.isProfesor()) {
   *   // Mostrar mis grupos
   * }
   */
  isProfesor() {
    return this.hasRole('Profesor');
  },

  /**
   * Verificar si el usuario es Estudiante
   * 
   * @returns {boolean} True si es Estudiante, false en caso contrario
   * 
   * @example
   * if (authService.isEstudiante()) {
   *   // Mostrar mis cursos
   * }
   */
  isEstudiante() {
    return this.hasRole('Estudiante');
  },
};

export default authService;
