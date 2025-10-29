/**
 * Servicio de Roles - Planner Universitario
 * 
 * Módulo para la gestión de roles y permisos del sistema.
 * Implementa los 10 endpoints del módulo de roles del backend.
 * 
 * @module roles.service
 * 
 * Un rol define el tipo de acceso y permisos que tiene un usuario en el sistema.
 * Los roles básicos del sistema son:
 * - Superadmin: Acceso completo al sistema
 * - Profesor: Gestión de grupos, actividades y calificaciones
 * - Estudiante: Acceso a inscripciones, actividades y calificaciones
 * 
 * Funcionalidades principales:
 * - Gestión CRUD de roles
 * - Inicialización de roles del sistema
 * - Consulta de usuarios por rol
 * - Búsqueda de roles
 * - Conteo de usuarios por rol
 * 
 * @requires Rol: Variable según operación (generalmente Superadmin para modificaciones)
 */

import apiClient from './api.config';

const BASE_URL = '/roles';

const rolesService = {
  /**
   * Crear un nuevo rol
   * 
   * Crea un rol personalizado en el sistema.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} rolData - Datos del rol
   * @param {string} rolData.nombre - Nombre único del rol (requerido)
   * @param {string} [rolData.descripcion] - Descripción del rol
   * @returns {Promise<Object>} Rol creado
   * @returns {number} return.id - ID del rol
   * @returns {string} return.nombre - Nombre del rol
   * @returns {string} return.descripcion - Descripción del rol
   * 
   * @throws {Error} El nombre del rol ya existe (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const nuevoRol = await rolesService.create({
   *   nombre: 'Coordinador',
   *   descripcion: 'Coordinador de programa académico'
   * });
   */
  async create(rolData) {
    const response = await apiClient.post(BASE_URL, rolData);
    return response.data;
  },

  /**
   * Obtener todos los roles
   * 
   * Lista todos los roles disponibles en el sistema ordenados por nombre.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Lista de roles
   * @returns {number} return[].id - ID del rol
   * @returns {string} return[].nombre - Nombre del rol
   * @returns {string} return[].descripcion - Descripción del rol
   * 
   * @example
   * const roles = await rolesService.getAll();
   * // [{ id: 1, nombre: 'Superadmin', descripcion: '...' }, ...]
   */
  async getAll() {
    const response = await apiClient.get(BASE_URL);
    return response.data;
  },

  /**
   * Inicializar roles del sistema
   * 
   * Crea los roles básicos del sistema si no existen:
   * - Superadmin
   * - Profesor
   * - Estudiante
   * 
   * Es idempotente: si los roles ya existen, simplemente los retorna.
   * Útil para inicializar el sistema en primera instalación.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Lista de roles creados o existentes
   * 
   * @example
   * const rolesBasicos = await rolesService.initialize();
   * // Retorna los 3 roles básicos del sistema
   */
  async initialize() {
    const response = await apiClient.get(`${BASE_URL}/inicializar`);
    return response.data;
  },

  /**
   * Buscar roles por término
   * 
   * Busca roles cuyo nombre o descripción contenga el término especificado.
   * La búsqueda es case-insensitive.
   * 
   * @async
   * @param {string} termino - Término de búsqueda (mínimo 1 carácter)
   * @returns {Promise<Array<Object>>} Lista de roles que coinciden
   * 
   * @example
   * const roles = await rolesService.search('admin');
   * // Encuentra 'Superadmin' y cualquier rol con 'admin' en nombre o descripción
   */
  async search(termino) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { termino },
    });
    return response.data;
  },

  /**
   * Obtener rol por nombre
   * 
   * Busca un rol específico por su nombre exacto.
   * 
   * @async
   * @param {string} nombre - Nombre del rol
   * @returns {Promise<Object>} Rol encontrado
   * 
   * @throws {Error} Rol no encontrado (404)
   * 
   * @example
   * const rolProfesor = await rolesService.getByName('Profesor');
   */
  async getByName(nombre) {
    const response = await apiClient.get(`${BASE_URL}/nombre/${nombre}`);
    return response.data;
  },

  /**
   * Obtener rol por ID
   * 
   * Recupera un rol específico por su identificador.
   * 
   * @async
   * @param {number} id - ID del rol
   * @returns {Promise<Object>} Rol encontrado
   * 
   * @throws {Error} Rol no encontrado (404)
   * 
   * @example
   * const rol = await rolesService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener usuarios de un rol
   * 
   * Lista todos los usuarios que tienen asignado un rol específico.
   * 
   * @async
   * @param {number} rolId - ID del rol
   * @returns {Promise<Array<Object>>} Lista de usuarios con ese rol
   * @returns {number} return[].id - ID del usuario
   * @returns {string} return[].email - Email del usuario
   * @returns {string} return[].nombre_completo - Nombre completo
   * @returns {boolean} return[].activo - Si el usuario está activo
   * 
   * @throws {Error} Rol no encontrado (404)
   * 
   * @example
   * const profesores = await rolesService.getUsers(2);
   * // Lista de todos los usuarios con rol de Profesor
   */
  async getUsers(rolId) {
    const response = await apiClient.get(`${BASE_URL}/${rolId}/usuarios`);
    return response.data;
  },

  /**
   * Contar usuarios de un rol
   * 
   * Obtiene el número total de usuarios que tienen un rol específico.
   * 
   * @async
   * @param {number} rolId - ID del rol
   * @returns {Promise<Object>} Conteo de usuarios
   * @returns {number} return.total_usuarios - Cantidad de usuarios con ese rol
   * 
   * @throws {Error} Rol no encontrado (404)
   * 
   * @example
   * const { total_usuarios } = await rolesService.countUsers(3);
   * console.log(`Hay ${total_usuarios} estudiantes en el sistema`);
   */
  async countUsers(rolId) {
    const response = await apiClient.get(`${BASE_URL}/${rolId}/conteo-usuarios`);
    return response.data;
  },

  /**
   * Actualizar descripción de un rol
   * 
   * Modifica únicamente la descripción de un rol existente.
   * El nombre del rol no puede ser modificado por restricciones del sistema.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del rol
   * @param {string} nuevaDescripcion - Nueva descripción del rol
   * @returns {Promise<Object>} Rol actualizado
   * 
   * @throws {Error} Rol no encontrado (404)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const rolActualizado = await rolesService.updateDescription(
   *   2,
   *   'Profesor a cargo de grupos académicos'
   * );
   */
  async updateDescription(id, nuevaDescripcion) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/descripcion`, null, {
      params: { nueva_descripcion: nuevaDescripcion },
    });
    return response.data;
  },

  /**
   * Eliminar un rol
   * 
   * Elimina un rol del sistema.
   * No se puede eliminar un rol que tenga usuarios asociados.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del rol a eliminar
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Rol no encontrado (404)
   * @throws {Error} Rol tiene usuarios asociados (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @description
   * ADVERTENCIA: No se pueden eliminar los roles básicos del sistema
   * (Superadmin, Profesor, Estudiante) si tienen usuarios activos.
   * 
   * @example
   * await rolesService.delete(5);
   * // Elimina el rol con ID 5 si no tiene usuarios
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Verificar si existe un rol por nombre
   * 
   * Método auxiliar para verificar la existencia de un rol.
   * 
   * @async
   * @param {string} nombre - Nombre del rol a verificar
   * @returns {Promise<boolean>} true si existe, false si no
   * 
   * @example
   * const existe = await rolesService.exists('Coordinador');
   */
  async exists(nombre) {
    try {
      await this.getByName(nombre);
      return true;
    } catch (error) {
      if (error.response?.status === 404) {
        return false;
      }
      throw error;
    }
  },

  /**
   * Obtener roles básicos del sistema
   * 
   * Retorna los tres roles fundamentales del sistema.
   * 
   * @async
   * @returns {Promise<Object>} Objeto con los roles básicos
   * @returns {Object} return.superadmin - Rol de Superadmin
   * @returns {Object} return.profesor - Rol de Profesor
   * @returns {Object} return.estudiante - Rol de Estudiante
   * 
   * @example
   * const { superadmin, profesor, estudiante } = await rolesService.getBasicRoles();
   */
  async getBasicRoles() {
    const roles = await this.getAll();
    return {
      superadmin: roles.find((r) => r.nombre === 'Superadmin'),
      profesor: roles.find((r) => r.nombre === 'Profesor'),
      estudiante: roles.find((r) => r.nombre === 'Estudiante'),
    };
  },

  /**
   * Obtener estadísticas de roles
   * 
   * Método auxiliar que combina información de todos los roles con su conteo de usuarios.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Lista de roles con estadísticas
   * @returns {number} return[].id - ID del rol
   * @returns {string} return[].nombre - Nombre del rol
   * @returns {string} return[].descripcion - Descripción
   * @returns {number} return[].total_usuarios - Cantidad de usuarios
   * 
   * @example
   * const estadisticas = await rolesService.getStatistics();
   * // [{ id: 1, nombre: 'Superadmin', total_usuarios: 2 }, ...]
   */
  async getStatistics() {
    const roles = await this.getAll();
    const estadisticas = await Promise.all(
      roles.map(async (rol) => {
        const { total_usuarios } = await this.countUsers(rol.id);
        return {
          ...rol,
          total_usuarios,
        };
      })
    );
    return estadisticas;
  },
};

export default rolesService;
