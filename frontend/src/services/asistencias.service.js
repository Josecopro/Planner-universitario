/**
 * Servicio de Asistencias - Planner Universitario
 * 
 * Módulo para la gestión de asistencias de estudiantes en grupos.
 * Implementa los 12 endpoints del módulo de asistencias del backend.
 * 
 * @module asistencias.service
 * 
 * Un registro de asistencia representa la presencia (o ausencia) de un estudiante
 * en una sesión de clase de un grupo en una fecha específica.
 * 
 * Estados de asistencia:
 * - Presente: Estudiante asistió a la clase
 * - Ausente: Estudiante no asistió
 * - Tardanza: Estudiante llegó tarde
 * - Justificado: Ausencia justificada
 * 
 * Funcionalidades principales:
 * - Registro individual y masivo de asistencias
 * - Consulta de asistencias por grupo, estudiante o fecha
 * - Estadísticas y resúmenes de asistencia
 * - Identificación de estudiantes ausentes
 * - Actualización de estados de asistencia
 * - Reportes de porcentaje de asistencia
 * 
 * @requires Rol: Variable según operación (Superadmin/Profesor para registrar)
 */

import apiClient from './api.config';

const BASE_URL = '/asistencias';

const asistenciasService = {
  /**
   * Registrar asistencia individual
   * 
   * Registra o actualiza la asistencia de un estudiante en una fecha específica.
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {Object} asistenciaData - Datos de la asistencia
   * @param {number} asistenciaData.inscripcion_id - ID de la inscripción del estudiante (requerido)
   * @param {number} asistenciaData.grupo_id - ID del grupo (requerido)
   * @param {string} asistenciaData.fecha - Fecha de la sesión (YYYY-MM-DD) (requerido)
   * @param {string} asistenciaData.estado - Estado (Presente/Ausente/Tardanza/Justificado) (requerido)
   * @returns {Promise<Object>} Registro de asistencia creado o actualizado
   * @returns {number} return.id - ID del registro
   * @returns {number} return.inscripcion_id - ID de la inscripción
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {string} return.fecha - Fecha de la sesión
   * @returns {string} return.estado - Estado de asistencia
   * 
   * @throws {Error} Inscripción no encontrada (404)
   * @throws {Error} Datos inválidos (400)
   * 
   * @example
   * const asistencia = await asistenciasService.create({
   *   inscripcion_id: 5,
   *   grupo_id: 1,
   *   fecha: '2024-10-28',
   *   estado: 'Presente'
   * });
   */
  async create(asistenciaData) {
    const response = await apiClient.post(BASE_URL, asistenciaData);
    return response.data;
  },

  /**
   * Registrar asistencia masiva
   * 
   * Registra la asistencia de múltiples estudiantes de un grupo en una fecha.
   * Útil para tomar asistencia de toda la clase de una vez.
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {Object} bulkData - Datos de la asistencia masiva
   * @param {number} bulkData.grupo_id - ID del grupo (requerido)
   * @param {string} bulkData.fecha - Fecha de la sesión (YYYY-MM-DD) (requerido)
   * @param {Array<Object>} bulkData.asistencias - Lista de asistencias (requerido)
   * @param {number} bulkData.asistencias[].inscripcion_id - ID de la inscripción
   * @param {string} bulkData.asistencias[].estado - Estado de asistencia
   * @returns {Promise<Object>} Resultado de la operación
   * @returns {string} return.message - Mensaje de éxito
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {string} return.fecha - Fecha registrada
   * @returns {number} return.total_registros - Cantidad de registros creados
   * 
   * @throws {Error} Grupo no encontrado (404)
   * @throws {Error} Datos inválidos (400)
   * 
   * @example
   * const resultado = await asistenciasService.createBulk({
   *   grupo_id: 1,
   *   fecha: '2024-10-28',
   *   asistencias: [
   *     { inscripcion_id: 1, estado: 'Presente' },
   *     { inscripcion_id: 2, estado: 'Ausente' },
   *     { inscripcion_id: 3, estado: 'Tardanza' }
   *   ]
   * });
   */
  async createBulk(bulkData) {
    const response = await apiClient.post(`${BASE_URL}/bulk`, bulkData);
    return response.data;
  },

  /**
   * Obtener asistencias de un grupo
   * 
   * Lista todos los registros de asistencia de un grupo con filtros opcionales por rango de fechas.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} [fechaInicio] - Fecha de inicio del rango (YYYY-MM-DD)
   * @param {string} [fechaFin] - Fecha de fin del rango (YYYY-MM-DD)
   * @returns {Promise<Array<Object>>} Lista de registros de asistencia
   * 
   * @example
   * const todas = await asistenciasService.getByGroup(1);
   * const octubre = await asistenciasService.getByGroup(1, '2024-10-01', '2024-10-31');
   */
  async getByGroup(grupoId, fechaInicio = null, fechaFin = null) {
    const params = {};
    if (fechaInicio) params.fecha_inicio = fechaInicio;
    if (fechaFin) params.fecha_fin = fechaFin;
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}`, { params });
    return response.data;
  },

  /**
   * Obtener asistencias por fecha
   * 
   * Lista los registros de asistencia de un grupo en una fecha específica.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión (YYYY-MM-DD)
   * @returns {Promise<Array<Object>>} Lista de registros de asistencia de esa fecha
   * 
   * @example
   * const asistenciasHoy = await asistenciasService.getByDate(1, '2024-10-28');
   */
  async getByDate(grupoId, fecha) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/fecha/${fecha}`);
    return response.data;
  },

  /**
   * Obtener asistencias de un estudiante
   * 
   * Lista todos los registros de asistencia de un estudiante con filtros opcionales.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción del estudiante
   * @param {string} [fechaInicio] - Fecha de inicio del rango
   * @param {string} [fechaFin] - Fecha de fin del rango
   * @returns {Promise<Array<Object>>} Lista de registros de asistencia del estudiante
   * 
   * @example
   * const asistencias = await asistenciasService.getByStudent(5);
   * const asistenciasOctubre = await asistenciasService.getByStudent(5, '2024-10-01', '2024-10-31');
   */
  async getByStudent(inscripcionId, fechaInicio = null, fechaFin = null) {
    const params = {};
    if (fechaInicio) params.fecha_inicio = fechaInicio;
    if (fechaFin) params.fecha_fin = fechaFin;
    const response = await apiClient.get(`${BASE_URL}/inscripcion/${inscripcionId}`, { params });
    return response.data;
  },

  /**
   * Obtener resumen de asistencia de un estudiante
   * 
   * Retorna estadísticas completas de asistencia de un estudiante en un grupo.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción del estudiante
   * @returns {Promise<Object>} Resumen de asistencia
   * @returns {number} return.inscripcion_id - ID de la inscripción
   * @returns {number} return.total_registros - Total de registros
   * @returns {number} return.porcentaje_asistencia - Porcentaje de asistencia
   * @returns {Object} return.conteo_estados - Conteo por cada estado
   * @returns {number} return.conteo_estados.Presente - Cantidad de presentes
   * @returns {number} return.conteo_estados.Ausente - Cantidad de ausentes
   * @returns {number} return.conteo_estados.Tardanza - Cantidad de tardanzas
   * @returns {number} return.conteo_estados.Justificado - Cantidad de justificados
   * @returns {Array} return.asistencias - Lista completa de asistencias
   * 
   * @throws {Error} Inscripción no encontrada (404)
   * 
   * @example
   * const resumen = await asistenciasService.getStudentSummary(5);
   * console.log(`Asistencia: ${resumen.porcentaje_asistencia}%`);
   * console.log(`Ausencias: ${resumen.conteo_estados.Ausente}`);
   */
  async getStudentSummary(inscripcionId) {
    const response = await apiClient.get(`${BASE_URL}/resumen/inscripcion/${inscripcionId}`);
    return response.data;
  },

  /**
   * Obtener estadísticas de asistencia de un grupo
   * 
   * Retorna estadísticas generales de asistencia de un grupo.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} [fecha] - Fecha específica (opcional)
   * @returns {Promise<Object>} Estadísticas del grupo
   * @returns {number} return.total_estudiantes - Total de estudiantes inscritos
   * @returns {number} return.total_registros - Total de registros de asistencia
   * @returns {number} return.presentes - Cantidad de presentes
   * @returns {number} return.ausentes - Cantidad de ausentes
   * @returns {number} return.justificados - Cantidad de justificados
   * @returns {number} return.tardanzas - Cantidad de tardanzas
   * @returns {number} return.porcentaje_asistencia - Porcentaje promedio de asistencia
   * 
   * @throws {Error} Grupo no encontrado (404)
   * 
   * @example
   * const stats = await asistenciasService.getGroupStatistics(1);
   * console.log(`Asistencia promedio: ${stats.porcentaje_asistencia}%`);
   * 
   * const statsHoy = await asistenciasService.getGroupStatistics(1, '2024-10-28');
   */
  async getGroupStatistics(grupoId, fecha = null) {
    const params = fecha ? { fecha } : {};
    const response = await apiClient.get(`${BASE_URL}/resumen/grupo/${grupoId}`, { params });
    return response.data;
  },

  /**
   * Obtener estudiantes ausentes
   * 
   * Lista los estudiantes ausentes en una fecha específica.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión (YYYY-MM-DD)
   * @returns {Promise<Array<Object>>} Lista de registros de asistencia con estado AUSENTE
   * 
   * @throws {Error} Grupo no encontrado (404)
   * 
   * @example
   * const ausentes = await asistenciasService.getAbsentStudents(1, '2024-10-28');
   * console.log(`${ausentes.length} estudiantes ausentes hoy`);
   */
  async getAbsentStudents(grupoId, fecha) {
    const response = await apiClient.get(`${BASE_URL}/ausentes/grupo/${grupoId}/fecha/${fecha}`);
    return response.data;
  },

  /**
   * Obtener fechas con asistencia registrada
   * 
   * Lista las fechas en las que se ha registrado asistencia para un grupo.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Array<string>>} Lista de fechas con asistencia registrada
   * 
   * @example
   * const fechas = await asistenciasService.getAttendanceDates(1);
   * console.log(`Asistencia registrada en ${fechas.length} fechas`);
   */
  async getAttendanceDates(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/fechas/grupo/${grupoId}`);
    return response.data;
  },

  /**
   * Obtener asistencia por ID
   * 
   * Recupera un registro de asistencia específico.
   * 
   * @async
   * @param {number} id - ID del registro de asistencia
   * @returns {Promise<Object>} Registro de asistencia
   * 
   * @throws {Error} Asistencia no encontrada (404)
   * 
   * @example
   * const asistencia = await asistenciasService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Actualizar estado de asistencia
   * 
   * Modifica el estado de un registro de asistencia existente.
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {number} id - ID del registro de asistencia
   * @param {string} estado - Nuevo estado (Presente/Ausente/Tardanza/Justificado)
   * @returns {Promise<Object>} Registro de asistencia actualizado
   * 
   * @throws {Error} Asistencia no encontrada (404)
   * @throws {Error} Estado inválido (400)
   * 
   * @example
   * const actualizada = await asistenciasService.update(1, 'Justificado');
   */
  async update(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}`, { estado });
    return response.data;
  },

  /**
   * Eliminar registro de asistencia
   * 
   * Elimina un registro de asistencia del sistema.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del registro a eliminar
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Asistencia no encontrada (404)
   * 
   * @example
   * await asistenciasService.delete(1);
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Marcar estudiante como presente
   * 
   * Método auxiliar para registrar asistencia con estado Presente.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @returns {Promise<Object>} Registro de asistencia
   * 
   * @example
   * await asistenciasService.markPresent(5, 1, '2024-10-28');
   */
  async markPresent(inscripcionId, grupoId, fecha) {
    return this.create({
      inscripcion_id: inscripcionId,
      grupo_id: grupoId,
      fecha,
      estado: 'Presente',
    });
  },

  /**
   * Marcar estudiante como ausente
   * 
   * Método auxiliar para registrar asistencia con estado Ausente.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @returns {Promise<Object>} Registro de asistencia
   * 
   * @example
   * await asistenciasService.markAbsent(5, 1, '2024-10-28');
   */
  async markAbsent(inscripcionId, grupoId, fecha) {
    return this.create({
      inscripcion_id: inscripcionId,
      grupo_id: grupoId,
      fecha,
      estado: 'Ausente',
    });
  },

  /**
   * Marcar estudiante con tardanza
   * 
   * Método auxiliar para registrar asistencia con estado Tardanza.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @returns {Promise<Object>} Registro de asistencia
   * 
   * @example
   * await asistenciasService.markLate(5, 1, '2024-10-28');
   */
  async markLate(inscripcionId, grupoId, fecha) {
    return this.create({
      inscripcion_id: inscripcionId,
      grupo_id: grupoId,
      fecha,
      estado: 'Tardanza',
    });
  },

  /**
   * Justificar ausencia
   * 
   * Método auxiliar para registrar o actualizar asistencia con estado Justificado.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @returns {Promise<Object>} Registro de asistencia
   * 
   * @example
   * await asistenciasService.justifyAbsence(5, 1, '2024-10-28');
   */
  async justifyAbsence(inscripcionId, grupoId, fecha) {
    return this.create({
      inscripcion_id: inscripcionId,
      grupo_id: grupoId,
      fecha,
      estado: 'Justificado',
    });
  },

  /**
   * Obtener estudiantes presentes
   * 
   * Método auxiliar para filtrar solo los estudiantes presentes en una fecha.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @returns {Promise<Array<Object>>} Lista de estudiantes presentes
   * 
   * @example
   * const presentes = await asistenciasService.getPresentStudents(1, '2024-10-28');
   */
  async getPresentStudents(grupoId, fecha) {
    const asistencias = await this.getByDate(grupoId, fecha);
    return asistencias.filter((a) => a.estado === 'Presente');
  },

  /**
   * Calcular porcentaje de asistencia
   * 
   * Método auxiliar para calcular el porcentaje de asistencia de un estudiante.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @returns {Promise<number>} Porcentaje de asistencia (0-100)
   * 
   * @example
   * const porcentaje = await asistenciasService.getAttendancePercentage(5);
   * console.log(`${porcentaje}% de asistencia`);
   */
  async getAttendancePercentage(inscripcionId) {
    const resumen = await this.getStudentSummary(inscripcionId);
    return resumen.porcentaje_asistencia;
  },

  /**
   * Verificar si estudiante tiene riesgo de perder por faltas
   * 
   * Método auxiliar para verificar si un estudiante está cerca del límite de faltas.
   * Considera que con menos del 80% de asistencia hay riesgo.
   * 
   * @async
   * @param {number} inscripcionId - ID de la inscripción
   * @returns {Promise<boolean>} true si tiene riesgo (< 80% asistencia)
   * 
   * @example
   * const enRiesgo = await asistenciasService.isAtRisk(5);
   * if (enRiesgo) {
   *   console.log('Alerta: Estudiante en riesgo de perder por faltas');
   * }
   */
  async isAtRisk(inscripcionId) {
    const porcentaje = await this.getAttendancePercentage(inscripcionId);
    return porcentaje < 80;
  },

  /**
   * Marcar toda la clase como presente
   * 
   * Método auxiliar para registrar asistencia de todos los estudiantes como presentes.
   * Útil para clases con asistencia completa.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @param {string} fecha - Fecha de la sesión
   * @param {Array<number>} inscripcionIds - Lista de IDs de inscripciones
   * @returns {Promise<Object>} Resultado de la operación
   * 
   * @example
   * const resultado = await asistenciasService.markAllPresent(1, '2024-10-28', [1, 2, 3, 4, 5]);
   */
  async markAllPresent(grupoId, fecha, inscripcionIds) {
    const asistencias = inscripcionIds.map((id) => ({
      inscripcion_id: id,
      estado: 'Presente',
    }));

    return this.createBulk({
      grupo_id: grupoId,
      fecha,
      asistencias,
    });
  },
};

export default asistenciasService;
