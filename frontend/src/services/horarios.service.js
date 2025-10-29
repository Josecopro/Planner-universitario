/**
 * Servicio de Horarios - Planner Universitario
 * 
 * Módulo para la gestión de horarios de grupos (bloques de clase).
 * Implementa los 13 endpoints del módulo de horarios del backend.
 * 
 * @module horarios.service
 * 
 * Un horario define cuándo y dónde se imparte una clase de un grupo específico.
 * Incluye día de la semana, hora de inicio, hora de fin y salón.
 * 
 * Validaciones importantes:
 * - Día de semana válido (Lunes-Domingo)
 * - Hora de fin posterior a hora de inicio
 * - Duración entre 30 minutos y 4 horas
 * - Horario entre 6:00 AM y 10:00 PM
 * - Sin conflictos de salón
 * - Sin conflictos de horario del profesor
 * 
 * Funcionalidades principales:
 * - Gestión CRUD de horarios
 * - Consulta por grupo, día o salón
 * - Verificación de conflictos (salón y profesor)
 * - Consulta de disponibilidad de salones
 * - Eliminación masiva por grupo
 * 
 * @requires Rol: Variable según operación (Superadmin/Profesor para crear/modificar)
 */

import apiClient from './api.config';

const BASE_URL = '/horarios';

const horariosService = {
  /**
   * Crear un nuevo horario
   * 
   * Crea un bloque de horario para un grupo con validaciones completas.
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {Object} horarioData - Datos del horario
   * @param {number} horarioData.grupo_id - ID del grupo (requerido)
   * @param {string} horarioData.dia - Día de la semana (Lunes-Domingo) (requerido)
   * @param {string} horarioData.hora_inicio - Hora de inicio (HH:MM:SS) (requerido)
   * @param {string} horarioData.hora_fin - Hora de fin (HH:MM:SS) (requerido)
   * @param {string} [horarioData.salon] - Salón o ubicación
   * @returns {Promise<Object>} Horario creado
   * @returns {number} return.id - ID del horario
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {string} return.dia - Día de la semana
   * @returns {string} return.hora_inicio - Hora de inicio
   * @returns {string} return.hora_fin - Hora de fin
   * @returns {string} return.salon - Salón asignado
   * 
   * @throws {Error} Grupo no encontrado (404)
   * @throws {Error} Día inválido (400)
   * @throws {Error} Hora de fin debe ser posterior a hora de inicio (400)
   * @throws {Error} Duración fuera de rango (30 min - 4 hrs) (400)
   * @throws {Error} Horario fuera del rango permitido (6AM-10PM) (400)
   * @throws {Error} Conflicto de salón (400)
   * @throws {Error} Conflicto de horario del profesor (400)
   * 
   * @example
   * const horario = await horariosService.create({
   *   grupo_id: 1,
   *   dia: 'Lunes',
   *   hora_inicio: '08:00:00',
   *   hora_fin: '10:00:00',
   *   salon: 'Bloque 5 - 101'
   * });
   */
  async create(horarioData) {
    const response = await apiClient.post(BASE_URL, horarioData);
    return response.data;
  },

  /**
   * Obtener horarios por grupo
   * 
   * Lista todos los horarios de un grupo ordenados por día y hora.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Array<Object>>} Lista de horarios del grupo
   * 
   * @example
   * const horarios = await horariosService.getByGroup(1);
   * // Retorna todos los bloques de clase del grupo
   */
  async getByGroup(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}`);
    return response.data;
  },

  /**
   * Obtener horarios por día
   * 
   * Lista todos los horarios de un día específico.
   * 
   * @async
   * @param {string} dia - Día de la semana (Lunes, Martes, etc.)
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<Object>>} Lista de horarios del día ordenados por hora
   * 
   * @example
   * const horarios = await horariosService.getByDay('Lunes');
   * const horariosLunes2024 = await horariosService.getByDay('Lunes', '2024-1');
   */
  async getByDay(dia, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/dia/${dia}`, { params });
    return response.data;
  },

  /**
   * Obtener horarios por salón
   * 
   * Lista todos los horarios que usan un salón específico.
   * 
   * @async
   * @param {string} salon - Nombre del salón
   * @param {string} [dia] - Filtrar por día de la semana
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<Object>>} Lista de horarios que usan el salón
   * 
   * @example
   * const ocupacion = await horariosService.getByRoom('Bloque 5 - 101');
   * const ocupacionLunes = await horariosService.getByRoom('Bloque 5 - 101', 'Lunes');
   */
  async getByRoom(salon, dia = null, semestre = null) {
    const params = {};
    if (dia) params.dia = dia;
    if (semestre) params.semestre = semestre;
    const response = await apiClient.get(`${BASE_URL}/salon/${salon}`, { params });
    return response.data;
  },

  /**
   * Obtener disponibilidad de un salón
   * 
   * Retorna los bloques ocupados de un salón en un día específico.
   * Útil para encontrar horas libres.
   * 
   * @async
   * @param {string} salon - Nombre del salón
   * @param {string} dia - Día de la semana (requerido)
   * @param {string} semestre - Semestre (requerido)
   * @returns {Promise<Array<Object>>} Lista de bloques ocupados con información de curso y profesor
   * @returns {string} return[].hora_inicio - Hora de inicio del bloque ocupado
   * @returns {string} return[].hora_fin - Hora de fin del bloque ocupado
   * @returns {Object} return[].curso - Información del curso
   * @returns {Object} return[].profesor - Información del profesor
   * @returns {number} return[].grupo_id - ID del grupo
   * 
   * @example
   * const ocupados = await horariosService.getRoomAvailability(
   *   'Bloque 5 - 101',
   *   'Lunes',
   *   '2024-1'
   * );
   * // Retorna los bloques ocupados, las horas libres son las que faltan
   */
  async getRoomAvailability(salon, dia, semestre) {
    const response = await apiClient.get(`${BASE_URL}/salon/${salon}/disponibilidad`, {
      params: { dia, semestre },
    });
    return response.data;
  },

  /**
   * Obtener horario por ID
   * 
   * Recupera un horario específico por su identificador.
   * 
   * @async
   * @param {number} id - ID del horario
   * @returns {Promise<Object>} Horario encontrado
   * 
   * @throws {Error} Horario no encontrado (404)
   * 
   * @example
   * const horario = await horariosService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Verificar conflicto de salón
   * 
   * Verifica si hay conflictos de uso de salón en un horario específico.
   * 
   * @async
   * @param {Object} params - Parámetros de verificación
   * @param {string} params.salon - Nombre del salón
   * @param {string} params.dia - Día de la semana
   * @param {string} params.hora_inicio - Hora de inicio (HH:MM:SS)
   * @param {string} params.hora_fin - Hora de fin (HH:MM:SS)
   * @param {string} params.semestre - Semestre
   * @param {number} [params.excluir_horario_id] - ID de horario a excluir (útil al actualizar)
   * @returns {Promise<Object>} Resultado de verificación
   * @returns {boolean} return.hay_conflicto - Si hay conflicto
   * @returns {Array<Object>} return.conflictos - Lista de horarios que entran en conflicto
   * 
   * @example
   * const resultado = await horariosService.checkRoomConflict({
   *   salon: 'Bloque 5 - 101',
   *   dia: 'Lunes',
   *   hora_inicio: '08:00:00',
   *   hora_fin: '10:00:00',
   *   semestre: '2024-1'
   * });
   * 
   * if (resultado.hay_conflicto) {
   *   console.log('Conflictos:', resultado.conflictos);
   * }
   */
  async checkRoomConflict({ salon, dia, hora_inicio, hora_fin, semestre, excluir_horario_id = null }) {
    const params = {
      salon,
      dia,
      hora_inicio,
      hora_fin,
      semestre,
    };
    if (excluir_horario_id) params.excluir_horario_id = excluir_horario_id;

    const response = await apiClient.get(`${BASE_URL}/verificar-conflicto/salon`, { params });
    return response.data;
  },

  /**
   * Verificar conflicto de profesor
   * 
   * Verifica si un profesor tiene conflictos de horario (dos clases al mismo tiempo).
   * 
   * @async
   * @param {Object} params - Parámetros de verificación
   * @param {number} params.profesor_id - ID del profesor
   * @param {string} params.dia - Día de la semana
   * @param {string} params.hora_inicio - Hora de inicio (HH:MM:SS)
   * @param {string} params.hora_fin - Hora de fin (HH:MM:SS)
   * @param {string} params.semestre - Semestre
   * @param {number} [params.excluir_grupo_id] - ID de grupo a excluir (útil al actualizar)
   * @returns {Promise<Object>} Resultado de verificación
   * @returns {boolean} return.hay_conflicto - Si hay conflicto
   * @returns {Array<Object>} return.conflictos - Lista de horarios que entran en conflicto
   * 
   * @example
   * const resultado = await horariosService.checkProfessorConflict({
   *   profesor_id: 5,
   *   dia: 'Lunes',
   *   hora_inicio: '08:00:00',
   *   hora_fin: '10:00:00',
   *   semestre: '2024-1'
   * });
   * 
   * if (!resultado.hay_conflicto) {
   *   // El profesor está disponible en ese horario
   * }
   */
  async checkProfessorConflict({ profesor_id, dia, hora_inicio, hora_fin, semestre, excluir_grupo_id = null }) {
    const params = {
      profesor_id,
      dia,
      hora_inicio,
      hora_fin,
      semestre,
    };
    if (excluir_grupo_id) params.excluir_grupo_id = excluir_grupo_id;

    const response = await apiClient.get(`${BASE_URL}/verificar-conflicto/profesor`, { params });
    return response.data;
  },

  /**
   * Actualizar un horario
   * 
   * Modifica un horario existente con validaciones completas.
   * 
   * @async
   * @requires Rol: Superadmin o Profesor
   * @param {number} id - ID del horario
   * @param {Object} horarioData - Datos a actualizar (todos opcionales)
   * @param {string} [horarioData.dia] - Nuevo día de la semana
   * @param {string} [horarioData.hora_inicio] - Nueva hora de inicio
   * @param {string} [horarioData.hora_fin] - Nueva hora de fin
   * @param {string} [horarioData.salon] - Nuevo salón
   * @returns {Promise<Object>} Horario actualizado
   * 
   * @throws {Error} Horario no encontrado (404)
   * @throws {Error} Datos inválidos o conflictos (400)
   * 
   * @example
   * const actualizado = await horariosService.update(1, {
   *   hora_inicio: '09:00:00',
   *   hora_fin: '11:00:00'
   * });
   */
  async update(id, horarioData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, horarioData);
    return response.data;
  },

  /**
   * Eliminar un horario
   * 
   * Elimina un bloque de horario específico.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del horario
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Horario no encontrado (404)
   * 
   * @example
   * await horariosService.delete(1);
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Eliminar todos los horarios de un grupo
   * 
   * Elimina masivamente todos los bloques de horario de un grupo.
   * Útil para limpiar horarios antes de recrearlos o al cancelar un grupo.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Resultado de la operación
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {number} return.horarios_eliminados - Cantidad de horarios eliminados
   * 
   * @example
   * const resultado = await horariosService.deleteAllByGroup(1);
   * console.log(`Eliminados ${resultado.horarios_eliminados} horarios`);
   */
  async deleteAllByGroup(grupoId) {
    const response = await apiClient.delete(`${BASE_URL}/grupo/${grupoId}/todos`);
    return response.data;
  },

  /**
   * Obtener horario semanal de un grupo
   * 
   * Método auxiliar que organiza los horarios por día de la semana.
   * 
   * @async
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Horarios organizados por día
   * @returns {Array} return.Lunes - Horarios del lunes
   * @returns {Array} return.Martes - Horarios del martes
   * @returns {Array} return.Miércoles - Horarios del miércoles
   * @returns {Array} return.Jueves - Horarios del jueves
   * @returns {Array} return.Viernes - Horarios del viernes
   * @returns {Array} return.Sábado - Horarios del sábado
   * @returns {Array} return.Domingo - Horarios del domingo
   * 
   * @example
   * const semana = await horariosService.getWeeklySchedule(1);
   * console.log('Clases del lunes:', semana.Lunes);
   */
  async getWeeklySchedule(grupoId) {
    const horarios = await this.getByGroup(grupoId);
    const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    
    const horarioSemanal = {};
    diasSemana.forEach((dia) => {
      horarioSemanal[dia] = horarios.filter((h) => h.dia === dia);
    });
    
    return horarioSemanal;
  },

  /**
   * Verificar si un horario está libre (sin conflictos)
   * 
   * Método auxiliar que verifica tanto conflictos de salón como de profesor.
   * 
   * @async
   * @param {Object} params - Parámetros de verificación
   * @param {string} params.salon - Nombre del salón
   * @param {number} params.profesor_id - ID del profesor
   * @param {string} params.dia - Día de la semana
   * @param {string} params.hora_inicio - Hora de inicio
   * @param {string} params.hora_fin - Hora de fin
   * @param {string} params.semestre - Semestre
   * @returns {Promise<Object>} Resultado de verificación completa
   * @returns {boolean} return.disponible - Si el horario está completamente libre
   * @returns {boolean} return.conflicto_salon - Si hay conflicto de salón
   * @returns {boolean} return.conflicto_profesor - Si hay conflicto de profesor
   * @returns {Array} return.conflictos_salon - Lista de conflictos de salón
   * @returns {Array} return.conflictos_profesor - Lista de conflictos de profesor
   * 
   * @example
   * const verificacion = await horariosService.isScheduleFree({
   *   salon: 'Bloque 5 - 101',
   *   profesor_id: 5,
   *   dia: 'Lunes',
   *   hora_inicio: '08:00:00',
   *   hora_fin: '10:00:00',
   *   semestre: '2024-1'
   * });
   * 
   * if (verificacion.disponible) {
   *   // Se puede crear el horario
   * }
   */
  async isScheduleFree({ salon, profesor_id, dia, hora_inicio, hora_fin, semestre }) {
    const [resultadoSalon, resultadoProfesor] = await Promise.all([
      this.checkRoomConflict({ salon, dia, hora_inicio, hora_fin, semestre }),
      this.checkProfessorConflict({ profesor_id, dia, hora_inicio, hora_fin, semestre }),
    ]);

    return {
      disponible: !resultadoSalon.hay_conflicto && !resultadoProfesor.hay_conflicto,
      conflicto_salon: resultadoSalon.hay_conflicto,
      conflicto_profesor: resultadoProfesor.hay_conflicto,
      conflictos_salon: resultadoSalon.conflictos,
      conflictos_profesor: resultadoProfesor.conflictos,
    };
  },

  /**
   * Obtener salones disponibles
   * 
   * Método auxiliar para obtener lista de salones únicos en uso.
   * 
   * @async
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<string>>} Lista de salones únicos
   * 
   * @example
   * const salones = await horariosService.getUsedRooms('2024-1');
   */
  async getUsedRooms(semestre = null) {
    const horarios = await this.getByDay('Lunes', semestre);
    const salones = [...new Set(horarios.map((h) => h.salon).filter((s) => s))];
    return salones.sort();
  },

  /**
   * Clonar horarios de un grupo a otro
   * 
   * Método auxiliar para copiar todos los horarios de un grupo a otro.
   * Útil para crear grupos similares.
   * 
   * @async
   * @param {number} grupoOrigenId - ID del grupo origen
   * @param {number} grupoDestinoId - ID del grupo destino
   * @returns {Promise<Array<Object>>} Horarios creados
   * 
   * @example
   * const horariosCopiados = await horariosService.cloneSchedule(1, 2);
   */
  async cloneSchedule(grupoOrigenId, grupoDestinoId) {
    const horariosOrigen = await this.getByGroup(grupoOrigenId);
    
    const promesas = horariosOrigen.map((horario) =>
      this.create({
        grupo_id: grupoDestinoId,
        dia: horario.dia,
        hora_inicio: horario.hora_inicio,
        hora_fin: horario.hora_fin,
        salon: horario.salon,
      })
    );
    
    return Promise.all(promesas);
  },
};

export default horariosService;
