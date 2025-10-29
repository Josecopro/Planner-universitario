/**
 * Servicio de Actividades Evaluativas - Planner Universitario
 * 
 * Módulo para la gestión de actividades evaluativas (tareas, quizzes, parciales, etc).
 * Implementa los 9 endpoints del módulo de actividades evaluativas del backend.
 * 
 * @module actividades-evaluativas.service
 * 
 * Las actividades evaluativas son las tareas, talleres, quizzes, parciales y
 * cualquier otra forma de evaluación que un profesor asigna a un grupo.
 * 
 * Tipos de actividades soportadas:
 * - Taller
 * - Quiz
 * - Parcial
 * - Proyecto
 * - Exposición
 * - Otro
 * 
 * Estados de actividades:
 * - Programada: Creada pero aún no disponible
 * - Activa: Disponible para entregas
 * - Cerrada: Ya no acepta entregas
 * 
 * @requires Rol: Principalmente Profesor y Estudiante
 */

import apiClient from './api.config';

const BASE_URL = '/actividades-evaluativas';

const actividadesEvaluativasService = {
  /**
   * Obtener todas las actividades con filtros
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} params - Parámetros de filtrado
   * @param {number} [params.skip=0] - Registros a saltar
   * @param {number} [params.limit=10] - Registros a retornar
   * @param {number} [params.grupo_id] - Filtrar por grupo
   * @param {string} [params.tipo] - Filtrar por tipo
   * @param {string} [params.estado] - Filtrar por estado
   * @returns {Promise<Array>} Lista de actividades
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener actividad por ID
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Datos completos de la actividad
   * @returns {string} return.titulo - Título de la actividad
   * @returns {string} return.descripcion - Descripción detallada
   * @returns {string} return.tipo - Tipo (Taller/Quiz/Parcial/etc)
   * @returns {number} return.porcentaje - Porcentaje de la nota final
   * @returns {string} return.fecha_limite - Fecha límite de entrega
   * @returns {string} return.estado - Estado actual
   * @returns {number} return.entregas_totales - Total de entregas
   * @returns {number} return.entregas_pendientes - Entregas pendientes
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear nueva actividad evaluativa
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {Object} actividadData - Datos de la actividad
   * @param {number} actividadData.grupo_id - ID del grupo
   * @param {string} actividadData.titulo - Título (max 200 caracteres)
   * @param {string} actividadData.descripcion - Descripción detallada
   * @param {string} actividadData.tipo - Tipo de actividad
   * @param {number} actividadData.porcentaje - Porcentaje (0-100)
   * @param {string} actividadData.fecha_limite - Fecha límite ISO
   * @param {string} [actividadData.estado='Programada'] - Estado inicial
   * @param {boolean} [actividadData.permite_entrega_tardia=false] - Permite entregas tardías
   * @returns {Promise<Object>} Actividad creada
   */
  async create(actividadData) {
    const response = await apiClient.post(BASE_URL, actividadData);
    return response.data;
  },

  /**
   * Actualizar actividad existente
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la actividad
   * @param {Object} actividadData - Datos a actualizar
   * @returns {Promise<Object>} Actividad actualizada
   */
  async update(id, actividadData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, actividadData);
    return response.data;
  },

  /**
   * Eliminar actividad
   * 
   * Solo se puede eliminar si no tiene entregas asociadas
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Mensaje de confirmación
   * @throws {Error} No se puede eliminar si tiene entregas (400)
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener actividades de un grupo
   * 
   * Retorna todas las actividades del grupo ordenadas por fecha límite
   * 
   * @async
   * @requires Token JWT válido (Profesor, estudiante inscrito o Superadmin)
   * @param {number} grupoId - ID del grupo
   * @param {string} [estado] - Filtrar por estado (Programada/Activa/Cerrada)
   * @returns {Promise<Array>} Actividades del grupo
   */
  async getByGrupo(grupoId, estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}`, { params });
    return response.data;
  },

  /**
   * Cambiar estado de la actividad
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la actividad
   * @param {string} estado - Nuevo estado (Programada/Activa/Cerrada)
   * @returns {Promise<Object>} Actividad actualizada
   * 
   * @example
   * // Activar una actividad para que los estudiantes puedan entregar
   * await actividadesService.changeStatus(1, 'Activa');
   * 
   * // Cerrar una actividad para no aceptar más entregas
   * await actividadesService.changeStatus(1, 'Cerrada');
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Obtener estadísticas de una actividad
   * 
   * Incluye:
   * - Total de entregas recibidas
   * - Entregas pendientes
   * - Promedio de calificaciones
   * - Entregas a tiempo vs tardías
   * - Distribución de notas
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Estadísticas de la actividad
   * @returns {number} return.total_entregas - Total de entregas
   * @returns {number} return.entregas_calificadas - Entregas calificadas
   * @returns {number} return.entregas_pendientes - Sin entregar
   * @returns {number} return.promedio - Promedio de calificaciones
   * @returns {number} return.entregas_a_tiempo - Entregas a tiempo
   * @returns {number} return.entregas_tardias - Entregas tardías
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },

  /**
   * Verificar si un estudiante puede entregar
   * 
   * Verifica:
   * - Si la actividad está activa
   * - Si ya realizó una entrega
   * - Si está dentro de la fecha límite
   * - Si se permiten entregas tardías
   * 
   * @async
   * @requires Rol: Estudiante (inscrito en el grupo)
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Resultado de la verificación
   * @returns {boolean} return.puede_entregar - Si puede entregar
   * @returns {string} return.razon - Razón si no puede entregar
   * @returns {boolean} return.es_tardia - Si sería una entrega tardía
   */
  async canSubmit(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/puede-entregar`);
    return response.data;
  },
};

export default actividadesEvaluativasService;
