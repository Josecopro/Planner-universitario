/**
 * Servicio de Usuarios - Planner Universitario
 * 
 * Módulo para la gestión completa de usuarios del sistema.
 * Implementa los 22 endpoints del módulo de usuarios del backend.
 * 
 * @module usuarios.service
 * 
 * Endpoints implementados:
 * - Gestión CRUD de usuarios
 * - Búsqueda y filtrado
 * - Estadísticas y reportes
 * - Gestión de estado (activar/desactivar)
 * - Gestión de roles y permisos
 * 
 * @requires Rol: Superadmin para la mayoría de operaciones
 */

import apiClient from './api.config';

const BASE_URL = '/usuarios';

const usuariosService = {
  /**
   * Obtener lista de usuarios con filtros y paginación
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} params - Parámetros de filtrado y paginación
   * @param {number} [params.skip=0] - Número de registros a saltar
   * @param {number} [params.limit=10] - Número de registros a retornar
   * @param {string} [params.search] - Búsqueda por nombre, apellido o email
   * @param {number} [params.rol_id] - Filtrar por ID de rol
   * @param {string} [params.estado] - Filtrar por estado (Activo/Inactivo)
   * @returns {Promise<Array>} Lista de usuarios
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener usuario por ID
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del usuario
   * @returns {Promise<Object>} Datos del usuario
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear nuevo usuario
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} userData - Datos del nuevo usuario
   * @param {string} userData.email - Email único del usuario
   * @param {string} userData.password - Contraseña (mínimo 8 caracteres)
   * @param {string} userData.nombre - Nombre del usuario
   * @param {string} userData.apellido - Apellido del usuario
   * @param {number} userData.rol_id - ID del rol a asignar
   * @param {string} [userData.estado='Activo'] - Estado inicial
   * @returns {Promise<Object>} Usuario creado
   */
  async create(userData) {
    const response = await apiClient.post(BASE_URL, userData);
    return response.data;
  },

  /**
   * Actualizar usuario existente
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del usuario a actualizar
   * @param {Object} userData - Datos a actualizar
   * @returns {Promise<Object>} Usuario actualizado
   */
  async update(id, userData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, userData);
    return response.data;
  },

  /**
   * Eliminar usuario
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del usuario a eliminar
   * @returns {Promise<Object>} Mensaje de confirmación
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Cambiar estado del usuario (activar/desactivar)
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del usuario
   * @param {string} estado - Nuevo estado ('Activo' o 'Inactivo')
   * @returns {Promise<Object>} Usuario actualizado
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Obtener usuarios por rol
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} rolId - ID del rol
   * @returns {Promise<Array>} Lista de usuarios con ese rol
   */
  async getByRole(rolId) {
    const response = await apiClient.get(`${BASE_URL}/rol/${rolId}`);
    return response.data;
  },

  /**
   * Buscar usuarios
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {string} query - Término de búsqueda
   * @returns {Promise<Array>} Usuarios que coinciden con la búsqueda
   */
  async search(query) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { q: query },
    });
    return response.data;
  },

  /**
   * Obtener estadísticas de usuarios
   * 
   * @async
   * @requires Rol: Superadmin
   * @returns {Promise<Object>} Estadísticas generales
   * @returns {number} return.total - Total de usuarios
   * @returns {number} return.activos - Usuarios activos
   * @returns {number} return.inactivos - Usuarios inactivos
   * @returns {Object} return.por_rol - Conteo por rol
   */
  async getStatistics() {
    const response = await apiClient.get(`${BASE_URL}/estadisticas`);
    return response.data;
  },

  /**
   * Actualizar datos personales
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del usuario
   * @param {Object} personalData - Datos personales a actualizar
   * @param {string} [personalData.nombre] - Nuevo nombre
   * @param {string} [personalData.apellido] - Nuevo apellido
   * @returns {Promise<Object>} Usuario actualizado
   */
  async updatePersonalData(id, personalData) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/datos-personales`, personalData);
    return response.data;
  },
};

export default usuariosService;
