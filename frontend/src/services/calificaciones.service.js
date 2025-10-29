/**
 * Servicio de Calificaciones - Planner Universitario
 * 
 * Módulo para la gestión de calificaciones de estudiantes.
 * Implementa los 11 endpoints del módulo de calificaciones del backend.
 * 
 * @module calificaciones.service
 * 
 * Las calificaciones se asocian a entregas de actividades evaluativas.
 * Incluye gestión de notas, retroalimentación y estadísticas.
 * 
 * Endpoints implementados:
 * - CRUD de calificaciones
 * - Calificación individual y masiva
 * - Estadísticas por grupo y estudiante
 * - Historial de cambios
 * - Exportación de notas
 * 
 * @requires Rol: Principalmente Profesor y Superadmin
 */

import apiClient from './api.config';

const BASE_URL = '/calificaciones';

const calificacionesService = {
  /**
   * Obtener todas las calificaciones con filtros
   * 
   * @async
   * @requires Rol: Profesor o Superadmin
   * @param {Object} params - Parámetros de filtrado
   * @param {number} [params.skip=0] - Registros a saltar
   * @param {number} [params.limit=10] - Registros a retornar
   * @param {number} [params.grupo_id] - Filtrar por grupo
   * @param {number} [params.estudiante_id] - Filtrar por estudiante
   * @returns {Promise<Array>} Lista de calificaciones
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener calificación por ID
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID de la calificación
   * @returns {Promise<Object>} Datos de la calificación
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear calificación individual
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {Object} calificacionData - Datos de la calificación
   * @param {number} calificacionData.entrega_id - ID de la entrega
   * @param {number} calificacionData.nota - Nota (0-100 o según escala)
   * @param {string} [calificacionData.retroalimentacion] - Comentarios
   * @param {string} [calificacionData.observaciones] - Observaciones adicionales
   * @returns {Promise<Object>} Calificación creada
   */
  async create(calificacionData) {
    const response = await apiClient.post(BASE_URL, calificacionData);
    return response.data;
  },

  /**
   * Calificación masiva de entregas
   * 
   * Permite calificar múltiples entregas en una sola operación
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {Array<Object>} calificaciones - Array de calificaciones
   * @param {number} calificaciones[].entrega_id - ID de la entrega
   * @param {number} calificaciones[].nota - Nota asignada
   * @param {string} [calificaciones[].retroalimentacion] - Comentarios
   * @returns {Promise<Object>} Resultado de la operación masiva
   * @returns {number} return.exitosas - Calificaciones creadas exitosamente
   * @returns {number} return.fallidas - Calificaciones que fallaron
   * @returns {Array} return.errores - Detalles de errores
   */
  async bulkCreate(calificaciones) {
    const response = await apiClient.post(`${BASE_URL}/bulk`, { calificaciones });
    return response.data;
  },

  /**
   * Actualizar calificación existente
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la calificación
   * @param {Object} calificacionData - Datos a actualizar
   * @param {number} [calificacionData.nota] - Nueva nota
   * @param {string} [calificacionData.retroalimentacion] - Nueva retroalimentación
   * @returns {Promise<Object>} Calificación actualizada
   */
  async update(id, calificacionData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, calificacionData);
    return response.data;
  },

  /**
   * Eliminar calificación
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la calificación
   * @returns {Promise<Object>} Mensaje de confirmación
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener calificaciones de un grupo
   * 
   * Retorna todas las calificaciones de un grupo con detalles
   * de estudiantes y actividades
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Array>} Calificaciones del grupo
   */
  async getByGrupo(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}`);
    return response.data;
  },

  /**
   * Obtener calificaciones de un estudiante en un grupo
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante, su profesor o Superadmin)
   * @param {number} grupoId - ID del grupo
   * @param {number} estudianteId - ID del estudiante
   * @returns {Promise<Array>} Calificaciones del estudiante
   */
  async getByGrupoAndEstudiante(grupoId, estudianteId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/estudiante/${estudianteId}`);
    return response.data;
  },

  /**
   * Obtener estadísticas de calificaciones de un grupo
   * 
   * Incluye:
   * - Promedio general del grupo
   * - Distribución de notas
   * - Estudiantes aprobados/reprobados
   * - Estadísticas por actividad
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Estadísticas del grupo
   * @returns {number} return.promedio_grupo - Promedio general
   * @returns {number} return.aprobados - Estudiantes aprobados
   * @returns {number} return.reprobados - Estudiantes reprobados
   * @returns {Object} return.distribucion - Distribución de notas
   * @returns {Array} return.por_actividad - Estadísticas por actividad
   */
  async getGroupStatistics(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/estadisticas`);
    return response.data;
  },

  /**
   * Obtener matriz de calificaciones del grupo
   * 
   * Retorna una tabla con estudiantes (filas) y actividades (columnas)
   * Útil para mostrar en una tabla o exportar
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Matriz de calificaciones
   * @returns {Array} return.estudiantes - Lista de estudiantes
   * @returns {Array} return.actividades - Lista de actividades
   * @returns {Array} return.notas - Matriz de notas [estudiante][actividad]
   */
  async getGradesMatrix(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/matriz`);
    return response.data;
  },

  /**
   * Exportar calificaciones del grupo
   * 
   * Genera un archivo Excel o CSV con todas las calificaciones
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} grupoId - ID del grupo
   * @param {string} [format='excel'] - Formato de exportación (excel/csv)
   * @returns {Promise<Blob>} Archivo para descargar
   */
  async exportGrades(grupoId, format = 'excel') {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/exportar`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },
};

export default calificacionesService;
