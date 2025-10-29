/**
 * Servicio de Entregas - Planner Universitario
 * 
 * Módulo para la gestión de entregas de actividades evaluativas.
 * Implementa los 10 endpoints del módulo de entregas del backend.
 * 
 * @module entregas.service
 * 
 * Una entrega representa la sumisión de un estudiante para una actividad evaluativa.
 * Incluye contenido de texto, archivos adjuntos, fecha de entrega y estado.
 * 
 * Estados de entrega:
 * - Entregada: Entregada dentro del plazo
 * - Entregada Tarde: Entregada después de la fecha límite
 * - Calificada: Ya fue calificada por el profesor
 * 
 * Funcionalidades principales:
 * - Registro de entregas de estudiantes
 * - Consulta de entregas por actividad o estudiante
 * - Identificación de entregas tardías
 * - Estadísticas de entregas
 * - Actualización de entregas (solo si no están calificadas)
 * - Consulta de entregas pendientes de calificar
 * 
 * @requires Rol: Variable según operación (Estudiante para crear, Profesor para consultar)
 */

import apiClient from './api.config';

const BASE_URL = '/entregas';

const entregasService = {
  /**
   * Realizar una entrega
   * 
   * Registra la entrega de un estudiante para una actividad evaluativa.
   * El estado se asigna automáticamente según la fecha límite.
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} entregaData - Datos de la entrega
   * @param {number} entregaData.actividad_id - ID de la actividad (requerido)
   * @param {number} entregaData.inscripcion_id - ID de la inscripción del estudiante (requerido)
   * @param {string} [entregaData.texto_entrega] - Contenido de texto de la entrega
   * @param {Array<string>} [entregaData.archivos_adjuntos] - Lista de URLs de archivos
   * @returns {Promise<Object>} Entrega creada
   * @returns {number} return.id - ID de la entrega
   * @returns {number} return.actividad_id - ID de la actividad
   * @returns {number} return.inscripcion_id - ID de la inscripción
   * @returns {string} return.fecha_entrega - Fecha y hora de entrega
   * @returns {string} return.estado - Estado (Entregada/Entregada Tarde)
   * @returns {string} return.texto_entrega - Contenido de texto
   * @returns {Array} return.archivos_adjuntos - Archivos adjuntos
   * 
   * @throws {Error} Actividad o inscripción no encontrada (404)
   * @throws {Error} Ya existe una entrega para esta actividad (400)
   * 
   * @example
   * const entrega = await entregasService.create({
   *   actividad_id: 1,
   *   inscripcion_id: 5,
   *   texto_entrega: 'Mi respuesta al taller...',
   *   archivos_adjuntos: ['https://example.com/archivo1.pdf']
   * });
   */
  async create(entregaData) {
    const response = await apiClient.post(BASE_URL, entregaData);
    return response.data;
  },

  /**
   * Obtener entregas de una actividad
   * 
   * Lista todas las entregas de una actividad evaluativa,
   * opcionalmente filtradas por estado.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @param {string} [estado] - Filtrar por estado (Entregada/Entregada Tarde/Calificada)
   * @returns {Promise<Array<Object>>} Lista de entregas de la actividad
   * 
   * @example
   * const todas = await entregasService.getByActivity(1);
   * const calificadas = await entregasService.getByActivity(1, 'Calificada');
   */
  async getByActivity(actividadId, estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(`${BASE_URL}/actividad/${actividadId}`, { params });
    return response.data;
  },

  /**
   * Obtener entregas tardías de una actividad
   * 
   * Lista las entregas que fueron entregadas después de la fecha límite.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @returns {Promise<Array<Object>>} Lista de entregas tardías
   * 
   * @example
   * const tardias = await entregasService.getLateSubmissions(1);
   */
  async getLateSubmissions(actividadId) {
    const response = await apiClient.get(`${BASE_URL}/actividad/${actividadId}/tardias`);
    return response.data;
  },

  /**
   * Obtener entrega de un estudiante para una actividad
   * 
   * Recupera la entrega específica de un estudiante en una actividad.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @param {number} inscripcionId - ID de la inscripción del estudiante
   * @returns {Promise<Object|null>} Entrega del estudiante o null si no ha entregado
   * 
   * @example
   * const entrega = await entregasService.getStudentSubmission(1, 5);
   * if (entrega) {
   *   console.log('El estudiante ya entregó');
   * }
   */
  async getStudentSubmission(actividadId, inscripcionId) {
    const response = await apiClient.get(
      `${BASE_URL}/actividad/${actividadId}/estudiante/${inscripcionId}`
    );
    return response.data;
  },

  /**
   * Obtener entregas pendientes de calificar
   * 
   * Lista todas las entregas de un grupo que aún no han sido calificadas.
   * Útil para profesores.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Array<Object>>} Lista de entregas sin calificación
   * 
   * @example
   * const pendientes = await entregasService.getPendingToGrade(1);
   * console.log(`${pendientes.length} entregas por calificar`);
   */
  async getPendingToGrade(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/pendientes`);
    return response.data;
  },

  /**
   * Obtener entregas de un estudiante
   * 
   * Lista todas las entregas realizadas por un estudiante en un grupo.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción del estudiante
   * @returns {Promise<Array<Object>>} Lista de entregas del estudiante
   * 
   * @example
   * const entregas = await entregasService.getByStudent(5);
   * // Historial de entregas del estudiante
   */
  async getByStudent(inscripcionId) {
    const response = await apiClient.get(`${BASE_URL}/inscripcion/${inscripcionId}`);
    return response.data;
  },

  /**
   * Obtener estadísticas de entregas
   * 
   * Retorna estadísticas completas de las entregas de una actividad.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @returns {Promise<Object>} Estadísticas de entregas
   * @returns {number} return.total_estudiantes - Total de estudiantes inscritos
   * @returns {number} return.total_entregas - Entregas realizadas
   * @returns {number} return.pendientes - Estudiantes sin entregar
   * @returns {number} return.entregadas_tiempo - Entregas a tiempo
   * @returns {number} return.entregadas_tarde - Entregas tardías
   * @returns {number} return.calificadas - Entregas ya calificadas
   * @returns {number} return.porcentaje_entrega - % de estudiantes que entregaron
   * 
   * @throws {Error} Actividad no encontrada (404)
   * 
   * @example
   * const stats = await entregasService.getStatistics(1);
   * console.log(`${stats.porcentaje_entrega}% de entrega`);
   * console.log(`${stats.entregadas_tarde} entregas tardías`);
   */
  async getStatistics(actividadId) {
    const response = await apiClient.get(`${BASE_URL}/estadisticas/actividad/${actividadId}`);
    return response.data;
  },

  /**
   * Obtener entrega por ID
   * 
   * Recupera una entrega específica con todos sus detalles.
   * 
   * @async
   * @param {number} id - ID de la entrega
   * @returns {Promise<Object>} Entrega encontrada
   * 
   * @throws {Error} Entrega no encontrada (404)
   * 
   * @example
   * const entrega = await entregasService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Actualizar una entrega
   * 
   * Modifica una entrega existente.
   * Solo se pueden actualizar entregas que no han sido calificadas.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID de la entrega
   * @param {Object} entregaData - Datos a actualizar
   * @param {string} [entregaData.texto_entrega] - Nuevo texto
   * @param {Array<string>} [entregaData.archivos_adjuntos] - Nuevos archivos
   * @returns {Promise<Object>} Entrega actualizada
   * 
   * @throws {Error} Entrega no encontrada (404)
   * @throws {Error} No se puede actualizar (ya está calificada) (400)
   * 
   * @example
   * const actualizada = await entregasService.update(1, {
   *   texto_entrega: 'Corrección de mi respuesta...'
   * });
   */
  async update(id, entregaData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, entregaData);
    return response.data;
  },

  /**
   * Eliminar una entrega
   * 
   * Elimina una entrega del sistema.
   * Solo se pueden eliminar entregas que no han sido calificadas.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID de la entrega
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Entrega no encontrada (404)
   * @throws {Error} No se puede eliminar (ya está calificada) (400)
   * 
   * @example
   * await entregasService.delete(1);
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Verificar si un estudiante ha entregado
   * 
   * Método auxiliar para verificar si existe una entrega.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @param {number} inscripcionId - ID de la inscripción
   * @returns {Promise<boolean>} true si ya entregó, false si no
   * 
   * @example
   * const yaEntrego = await entregasService.hasSubmitted(1, 5);
   * if (yaEntrego) {
   *   console.log('El estudiante ya realizó su entrega');
   * }
   */
  async hasSubmitted(actividadId, inscripcionId) {
    const entrega = await this.getStudentSubmission(actividadId, inscripcionId);
    return entrega !== null;
  },

  /**
   * Obtener entregas a tiempo
   * 
   * Método auxiliar para obtener solo las entregas con estado "Entregada".
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @returns {Promise<Array<Object>>} Lista de entregas a tiempo
   * 
   * @example
   * const aTiempo = await entregasService.getOnTimeSubmissions(1);
   */
  async getOnTimeSubmissions(actividadId) {
    return this.getByActivity(actividadId, 'Entregada');
  },

  /**
   * Obtener entregas calificadas
   * 
   * Método auxiliar para obtener solo las entregas ya calificadas.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @returns {Promise<Array<Object>>} Lista de entregas calificadas
   * 
   * @example
   * const calificadas = await entregasService.getGradedSubmissions(1);
   */
  async getGradedSubmissions(actividadId) {
    return this.getByActivity(actividadId, 'Calificada');
  },

  /**
   * Obtener estudiantes que no han entregado
   * 
   * Método auxiliar que combina estadísticas para obtener
   * el número de estudiantes sin entrega.
   * 
   * @async
   * @param {number} actividadId - ID de la actividad
   * @returns {Promise<number>} Número de estudiantes sin entregar
   * 
   * @example
   * const sinEntregar = await entregasService.getMissingSubmissions(1);
   * console.log(`${sinEntregar} estudiantes no han entregado`);
   */
  async getMissingSubmissions(actividadId) {
    const stats = await this.getStatistics(actividadId);
    return stats.pendientes;
  },

  /**
   * Verificar si una entrega está tardía
   * 
   * Método auxiliar para verificar el estado de una entrega.
   * 
   * @async
   * @param {number} id - ID de la entrega
   * @returns {Promise<boolean>} true si está tardía
   * 
   * @example
   * const esTardia = await entregasService.isLate(1);
   */
  async isLate(id) {
    const entrega = await this.getById(id);
    return entrega.estado === 'Entregada Tarde';
  },

  /**
   * Verificar si una entrega está calificada
   * 
   * Método auxiliar para verificar si la entrega ya fue calificada.
   * 
   * @async
   * @param {number} id - ID de la entrega
   * @returns {Promise<boolean>} true si está calificada
   * 
   * @example
   * const estaCalificada = await entregasService.isGraded(1);
   */
  async isGraded(id) {
    const entrega = await this.getById(id);
    return entrega.estado === 'Calificada';
  },

  /**
   * Obtener resumen de entregas por grupo
   * 
   * Método auxiliar para obtener un resumen general de entregas de un grupo.
   * Combina información de múltiples actividades.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Resumen de entregas
   * @returns {number} return.total_actividades - Total de actividades
   * @returns {number} return.entregas_pendientes - Total de entregas por calificar
   * 
   * @example
   * const resumen = await entregasService.getGroupSummary(1);
   * console.log(`${resumen.entregas_pendientes} entregas pendientes en el grupo`);
   */
  async getGroupSummary(grupoId) {
    const pendientes = await this.getPendingToGrade(grupoId);
    
    // Contar actividades únicas
    const actividadesUnicas = new Set(pendientes.map((e) => e.actividad_id));
    
    return {
      total_actividades: actividadesUnicas.size,
      entregas_pendientes: pendientes.length,
    };
  },

  /**
   * Puede actualizar entrega
   * 
   * Método auxiliar para verificar si una entrega puede ser actualizada.
   * 
   * @async
   * @param {number} id - ID de la entrega
   * @returns {Promise<boolean>} true si puede actualizarse
   * 
   * @example
   * const puedeActualizar = await entregasService.canUpdate(1);
   * if (puedeActualizar) {
   *   await entregasService.update(1, { texto_entrega: '...' });
   * }
   */
  async canUpdate(id) {
    const entrega = await this.getById(id);
    return entrega.estado !== 'Calificada';
  },
};

export default entregasService;
