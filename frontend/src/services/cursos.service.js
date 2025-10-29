/**
 * Servicio de Cursos - Planner Universitario
 * 
 * Módulo para la gestión del catálogo de cursos académicos.
 * Implementa los 11 endpoints del módulo de cursos del backend.
 * 
 * @module cursos.service
 * 
 * Un curso es una materia o asignatura que se ofrece en el catálogo académico.
 * Los cursos se organizan por facultades y se imparten en grupos específicos.
 * Ejemplos: Cálculo I, Programación, Física Mecánica.
 * 
 * Estados de curso:
 * - Activo: Curso disponible para crear grupos
 * - Inactivo: Curso temporalmente suspendido
 * - En Revision: Curso en proceso de revisión curricular
 * 
 * Funcionalidades principales:
 * - Gestión CRUD de cursos
 * - Búsqueda por código o nombre
 * - Consulta de grupos del curso
 * - Filtrado por facultad y estado
 * - Estadísticas de cursos
 * 
 * @requires Rol: Variable según operación (Superadmin para modificaciones)
 */

import apiClient from './api.config';

const BASE_URL = '/cursos';

const cursosService = {
  /**
   * Crear un nuevo curso
   * 
   * Crea un curso en el catálogo académico.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} cursoData - Datos del curso
   * @param {string} cursoData.codigo - Código único del curso (ej: IS-101, MAT-201) (requerido)
   * @param {string} cursoData.nombre - Nombre del curso (requerido)
   * @param {number} cursoData.facultad_id - ID de la facultad (requerido)
   * @param {number} [cursoData.creditos] - Número de créditos
   * @param {number} [cursoData.horas_semanales] - Horas de clase por semana
   * @param {string} [cursoData.descripcion] - Descripción del curso
   * @param {string} [cursoData.estado='Activo'] - Estado inicial
   * @returns {Promise<Object>} Curso creado
   * @returns {number} return.id - ID del curso
   * @returns {string} return.codigo - Código único
   * @returns {string} return.nombre - Nombre del curso
   * @returns {number} return.facultad_id - ID de la facultad
   * @returns {string} return.estado - Estado del curso
   * 
   * @throws {Error} Facultad no encontrada (404)
   * @throws {Error} Código ya existe (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const curso = await cursosService.create({
   *   codigo: 'IS-101',
   *   nombre: 'Introducción a la Programación',
   *   facultad_id: 1,
   *   creditos: 3,
   *   horas_semanales: 4
   * });
   */
  async create(cursoData) {
    const response = await apiClient.post(BASE_URL, cursoData);
    return response.data;
  },

  /**
   * Obtener todos los cursos
   * 
   * Lista cursos con filtros opcionales múltiples.
   * 
   * @async
   * @param {Object} [filtros] - Filtros opcionales
   * @param {number} [filtros.facultad_id] - Filtrar por facultad
   * @param {string} [filtros.estado] - Filtrar por estado (Activo/Inactivo/En Revision)
   * @param {string} [filtros.codigo] - Buscar por código (parcial)
   * @param {string} [filtros.nombre] - Buscar por nombre (parcial)
   * @returns {Promise<Array<Object>>} Lista de cursos
   * 
   * @example
   * const todos = await cursosService.getAll();
   * const activos = await cursosService.getAll({ estado: 'Activo' });
   * const cursosFacultad = await cursosService.getAll({ facultad_id: 1 });
   * const filtrados = await cursosService.getAll({ 
   *   facultad_id: 1, 
   *   estado: 'Activo',
   *   codigo: 'IS'
   * });
   */
  async getAll(filtros = {}) {
    const response = await apiClient.get(BASE_URL, { params: filtros });
    return response.data;
  },

  /**
   * Obtener cursos de una facultad
   * 
   * Lista todos los cursos de una facultad específica.
   * 
   * @async
   * @param {number} facultadId - ID de la facultad
   * @param {boolean} [soloActivos=true] - Si es true, solo devuelve cursos activos
   * @returns {Promise<Array<Object>>} Lista de cursos de la facultad
   * 
   * @example
   * const cursos = await cursosService.getByFaculty(1);
   * const todosLosCursos = await cursosService.getByFaculty(1, false);
   */
  async getByFaculty(facultadId, soloActivos = true) {
    const response = await apiClient.get(`${BASE_URL}/facultad/${facultadId}`, {
      params: { solo_activos: soloActivos },
    });
    return response.data;
  },

  /**
   * Buscar cursos por término
   * 
   * Busca cursos por texto en código o nombre.
   * 
   * @async
   * @param {string} termino - Término de búsqueda (mínimo 1 carácter)
   * @param {number} [limit=20] - Máximo de resultados (1-100)
   * @returns {Promise<Array<Object>>} Lista de cursos que coinciden
   * 
   * @example
   * const resultados = await cursosService.search('programacion');
   * const limitados = await cursosService.search('IS', 10);
   */
  async search(termino, limit = 20) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { termino, limit },
    });
    return response.data;
  },

  /**
   * Obtener curso por código
   * 
   * Busca un curso específico por su código único.
   * 
   * @async
   * @param {string} codigo - Código del curso (ej: 'IS-101')
   * @returns {Promise<Object>} Curso encontrado
   * 
   * @throws {Error} Curso no encontrado (404)
   * 
   * @example
   * const curso = await cursosService.getByCode('IS-101');
   */
  async getByCode(codigo) {
    const response = await apiClient.get(`${BASE_URL}/codigo/${codigo}`);
    return response.data;
  },

  /**
   * Obtener curso por ID
   * 
   * Recupera un curso específico con todos sus detalles.
   * 
   * @async
   * @param {number} id - ID del curso
   * @returns {Promise<Object>} Curso encontrado
   * 
   * @throws {Error} Curso no encontrado (404)
   * 
   * @example
   * const curso = await cursosService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener grupos de un curso
   * 
   * Lista todos los grupos asociados a un curso.
   * 
   * @async
   * @param {number} id - ID del curso
   * @param {string} [semestre] - Filtrar por semestre (ej: '2025-1')
   * @returns {Promise<Array<Object>>} Lista de grupos del curso
   * @returns {number} return[].id - ID del grupo
   * @returns {string} return[].semestre - Semestre del grupo
   * @returns {number} return[].cupo_maximo - Cupo máximo
   * @returns {number} return[].cupo_actual - Cupo ocupado
   * @returns {string} return[].estado - Estado del grupo
   * @returns {number} return[].profesor_id - ID del profesor
   * 
   * @throws {Error} Curso no encontrado (404)
   * 
   * @example
   * const grupos = await cursosService.getGroups(1);
   * const gruposSemestre = await cursosService.getGroups(1, '2025-1');
   */
  async getGroups(id, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/${id}/grupos`, { params });
    return response.data;
  },

  /**
   * Obtener estadísticas de un curso
   * 
   * Retorna estadísticas generales del curso.
   * 
   * @async
   * @param {number} id - ID del curso
   * @returns {Promise<Object>} Estadísticas del curso
   * @returns {number} return.total_grupos - Total de grupos históricos
   * @returns {number} return.grupos_activos - Grupos actualmente activos
   * @returns {number} return.total_estudiantes - Total de estudiantes históricos
   * @returns {number} return.promedio_estudiantes - Promedio de estudiantes por grupo
   * 
   * @throws {Error} Curso no encontrado (404)
   * 
   * @example
   * const stats = await cursosService.getStatistics(1);
   * console.log(`Grupos activos: ${stats.grupos_activos}`);
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },

  /**
   * Actualizar un curso
   * 
   * Modifica los datos de un curso existente.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del curso
   * @param {Object} cursoData - Datos a actualizar (todos opcionales)
   * @param {string} [cursoData.codigo] - Nuevo código único
   * @param {string} [cursoData.nombre] - Nuevo nombre
   * @param {string} [cursoData.estado] - Nuevo estado
   * @param {number} [cursoData.facultad_id] - Nueva facultad
   * @param {number} [cursoData.creditos] - Nuevos créditos
   * @param {number} [cursoData.horas_semanales] - Nuevas horas semanales
   * @param {string} [cursoData.descripcion] - Nueva descripción
   * @returns {Promise<Object>} Curso actualizado
   * 
   * @throws {Error} Curso no encontrado (404)
   * @throws {Error} Código ya existe (400)
   * @throws {Error} Facultad inválida (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const actualizado = await cursosService.update(1, {
   *   nombre: 'Programación Avanzada I',
   *   creditos: 4
   * });
   */
  async update(id, cursoData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, cursoData);
    return response.data;
  },

  /**
   * Cambiar estado de un curso
   * 
   * Actualiza únicamente el estado del curso.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del curso
   * @param {string} estado - Nuevo estado (Activo/Inactivo/En Revision)
   * @returns {Promise<Object>} Curso actualizado
   * 
   * @throws {Error} Curso no encontrado (404)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const curso = await cursosService.changeStatus(1, 'Inactivo');
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Desactivar un curso
   * 
   * Cambia el estado del curso a Inactivo.
   * No se puede desactivar si tiene grupos activos.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del curso
   * @returns {Promise<Object>} Curso desactivado
   * 
   * @throws {Error} Curso no encontrado (404)
   * @throws {Error} Curso tiene grupos activos (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * await cursosService.deactivate(1);
   */
  async deactivate(id) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/desactivar`);
    return response.data;
  },

  /**
   * Activar un curso
   * 
   * Método auxiliar para cambiar el estado a Activo.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del curso
   * @returns {Promise<Object>} Curso activado
   * 
   * @example
   * await cursosService.activate(1);
   */
  async activate(id) {
    return this.changeStatus(id, 'Activo');
  },

  /**
   * Poner curso en revisión
   * 
   * Método auxiliar para cambiar el estado a En Revision.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del curso
   * @returns {Promise<Object>} Curso actualizado
   * 
   * @example
   * await cursosService.setInReview(id);
   */
  async setInReview(id) {
    return this.changeStatus(id, 'En Revision');
  },

  /**
   * Verificar si existe un curso por código
   * 
   * Método auxiliar para verificar la existencia de un curso.
   * 
   * @async
   * @param {string} codigo - Código del curso
   * @returns {Promise<boolean>} true si existe, false si no
   * 
   * @example
   * const existe = await cursosService.exists('IS-101');
   */
  async exists(codigo) {
    try {
      await this.getByCode(codigo);
      return true;
    } catch (error) {
      if (error.response?.status === 404) {
        return false;
      }
      throw error;
    }
  },

  /**
   * Obtener cursos activos
   * 
   * Método auxiliar para obtener solo los cursos con estado Activo.
   * 
   * @async
   * @param {number} [facultadId] - Filtrar por facultad
   * @returns {Promise<Array<Object>>} Lista de cursos activos
   * 
   * @example
   * const activos = await cursosService.getActive();
   * const activosFacultad = await cursosService.getActive(1);
   */
  async getActive(facultadId = null) {
    const filtros = { estado: 'Activo' };
    if (facultadId) filtros.facultad_id = facultadId;
    return this.getAll(filtros);
  },

  /**
   * Obtener cursos inactivos
   * 
   * Método auxiliar para obtener solo los cursos con estado Inactivo.
   * 
   * @async
   * @param {number} [facultadId] - Filtrar por facultad
   * @returns {Promise<Array<Object>>} Lista de cursos inactivos
   * 
   * @example
   * const inactivos = await cursosService.getInactive();
   */
  async getInactive(facultadId = null) {
    const filtros = { estado: 'Inactivo' };
    if (facultadId) filtros.facultad_id = facultadId;
    return this.getAll(filtros);
  },

  /**
   * Obtener cursos en revisión
   * 
   * Método auxiliar para obtener cursos con estado En Revision.
   * 
   * @async
   * @param {number} [facultadId] - Filtrar por facultad
   * @returns {Promise<Array<Object>>} Lista de cursos en revisión
   * 
   * @example
   * const enRevision = await cursosService.getInReview();
   */
  async getInReview(facultadId = null) {
    const filtros = { estado: 'En Revision' };
    if (facultadId) filtros.facultad_id = facultadId;
    return this.getAll(filtros);
  },

  /**
   * Obtener grupos activos de un curso
   * 
   * Método auxiliar para obtener solo los grupos con estado Activo.
   * 
   * @async
   * @param {number} id - ID del curso
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<Object>>} Lista de grupos activos
   * 
   * @example
   * const gruposActivos = await cursosService.getActiveGroups(1);
   */
  async getActiveGroups(id, semestre = null) {
    const grupos = await this.getGroups(id, semestre);
    return grupos.filter((g) => g.estado === 'Activo');
  },

  /**
   * Verificar si el curso tiene grupos activos
   * 
   * Método auxiliar para determinar si un curso tiene al menos un grupo activo.
   * 
   * @async
   * @param {number} id - ID del curso
   * @returns {Promise<boolean>} true si tiene grupos activos
   * 
   * @example
   * const tieneGrupos = await cursosService.hasActiveGroups(1);
   * if (!tieneGrupos) {
   *   await cursosService.deactivate(1);
   * }
   */
  async hasActiveGroups(id) {
    const stats = await this.getStatistics(id);
    return stats.grupos_activos > 0;
  },
};

export default cursosService;
