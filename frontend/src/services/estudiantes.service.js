/**
 * Servicio de Estudiantes - Planner Universitario
 * 
 * Módulo para la gestión de perfiles de estudiantes.
 * Implementa los 15 endpoints del módulo de estudiantes del backend.
 * 
 * @module estudiantes.service
 * 
 * Un estudiante está vinculado a un usuario y a un programa académico.
 * Este servicio gestiona el perfil académico, inscripciones, notas y
 * toda la información relacionada con su progreso en el programa.
 * 
 * Endpoints implementados:
 * - CRUD de perfiles de estudiantes
 * - Historial académico
 * - Grupos actuales e históricos
 * - Resumen de notas y promedio
 * - Estadísticas de rendimiento
 * 
 * @requires Rol: Variable según operación
 */

import apiClient from './api.config';

const BASE_URL = '/estudiantes';

const estudiantesService = {
  /**
   * Obtener todos los estudiantes con filtros
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {Object} params - Parámetros de filtrado
   * @param {number} [params.skip=0] - Registros a saltar
   * @param {number} [params.limit=10] - Registros a retornar
   * @param {number} [params.programa_id] - Filtrar por programa
   * @param {string} [params.search] - Buscar por nombre o código
   * @param {string} [params.estado] - Filtrar por estado (Activo/Inactivo)
   * @returns {Promise<Array>} Lista de estudiantes
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener estudiante por ID
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Datos completos del estudiante
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear nuevo perfil de estudiante
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} estudianteData - Datos del estudiante
   * @param {number} estudianteData.usuario_id - ID del usuario asociado
   * @param {string} estudianteData.codigo - Código único del estudiante
   * @param {number} estudianteData.programa_id - ID del programa académico
   * @param {string} [estudianteData.semestre_ingreso] - Semestre de ingreso
   * @param {string} [estudianteData.estado='Activo'] - Estado inicial
   * @returns {Promise<Object>} Estudiante creado
   */
  async create(estudianteData) {
    const response = await apiClient.post(BASE_URL, estudianteData);
    return response.data;
  },

  /**
   * Actualizar perfil de estudiante
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del estudiante
   * @param {Object} estudianteData - Datos a actualizar
   * @returns {Promise<Object>} Estudiante actualizado
   */
  async update(id, estudianteData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, estudianteData);
    return response.data;
  },

  /**
   * Eliminar perfil de estudiante
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Mensaje de confirmación
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener estudiante por usuario
   * 
   * Útil para obtener el perfil de estudiante del usuario autenticado
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} usuarioId - ID del usuario
   * @returns {Promise<Object>} Perfil del estudiante
   */
  async getByUsuario(usuarioId) {
    const response = await apiClient.get(`${BASE_URL}/usuario/${usuarioId}`);
    return response.data;
  },

  /**
   * Obtener estudiantes por programa académico
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {number} programaId - ID del programa académico
   * @param {string} [estado] - Filtrar por estado (Activo/Inactivo/Graduado)
   * @returns {Promise<Array>} Lista de estudiantes del programa
   */
  async getByPrograma(programaId, estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(`${BASE_URL}/programa/${programaId}`, { params });
    return response.data;
  },

  /**
   * Obtener grupos actuales del estudiante
   * 
   * Retorna los grupos en los que el estudiante está inscrito
   * en el semestre actual
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante o Superadmin)
   * @param {number} id - ID del estudiante
   * @returns {Promise<Array>} Grupos actuales con información del curso y profesor
   */
  async getCurrentGroups(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/grupos-actuales`);
    return response.data;
  },

  /**
   * Obtener historial académico completo
   * 
   * Retorna todo el historial de cursos del estudiante con:
   * - Cursos aprobados y reprobados
   * - Notas finales
   * - Semestre cursado
   * - Créditos acumulados
   * - Promedio general
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante o Superadmin)
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Historial académico completo
   * @returns {Array} return.cursos - Lista de cursos cursados
   * @returns {number} return.promedio_general - Promedio acumulado
   * @returns {number} return.creditos_aprobados - Créditos aprobados
   * @returns {number} return.creditos_totales - Créditos del programa
   * @returns {string} return.estado_academico - Estado académico actual
   */
  async getAcademicHistory(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/historial-academico`);
    return response.data;
  },

  /**
   * Obtener resumen de notas del semestre actual
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante o Superadmin)
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Resumen de notas por curso
   */
  async getCurrentGrades(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/resumen-notas`);
    return response.data;
  },

  /**
   * Obtener estadísticas del estudiante
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante o Superadmin)
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Estadísticas generales
   * @returns {number} return.promedio_general - Promedio acumulado
   * @returns {number} return.cursos_aprobados - Total cursos aprobados
   * @returns {number} return.cursos_reprobados - Total cursos reprobados
   * @returns {number} return.porcentaje_asistencia - % asistencia general
   * @returns {number} return.creditos_cursados - Créditos cursados
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },

  /**
   * Cambiar estado del estudiante
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del estudiante
   * @param {string} estado - Nuevo estado (Activo/Inactivo/Graduado/Retirado)
   * @returns {Promise<Object>} Estudiante actualizado
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Buscar estudiantes
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {string} query - Término de búsqueda (nombre, código, email)
   * @returns {Promise<Array>} Estudiantes que coinciden
   */
  async search(query) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { q: query },
    });
    return response.data;
  },

  /**
   * Obtener grupos históricos del estudiante
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante o Superadmin)
   * @param {number} id - ID del estudiante
   * @param {string} [semestre] - Filtrar por semestre específico
   * @returns {Promise<Array>} Grupos cursados anteriormente
   */
  async getHistoricalGroups(id, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/${id}/grupos-historicos`, { params });
    return response.data;
  },

  /**
   * Verificar prerrequisitos para un curso
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante)
   * @param {number} id - ID del estudiante
   * @param {number} cursoId - ID del curso a verificar
   * @returns {Promise<Object>} Resultado de verificación
   * @returns {boolean} return.cumple_requisitos - Si cumple los requisitos
   * @returns {Array} return.requisitos_faltantes - Cursos pendientes
   */
  async checkPrerequisites(id, cursoId) {
    const response = await apiClient.get(`${BASE_URL}/${id}/verificar-requisitos/${cursoId}`);
    return response.data;
  },
};

export default estudiantesService;
