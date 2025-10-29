/**
 * Servicio de Profesores - Planner Universitario
 * 
 * Módulo para la gestión completa de perfiles de profesores.
 * Implementa los 14 endpoints del módulo de profesores del backend.
 * 
 * @module profesores.service
 * 
 * Un profesor está vinculado a un usuario y opcionalmente a una facultad.
 * Este servicio gestiona el perfil académico, carga docente, grupos asignados
 * y toda la información relacionada con su labor docente.
 * 
 * Funcionalidades principales:
 * - Gestión de perfiles de profesores (CRUD completo)
 * - Consulta de grupos asignados y carga académica
 * - Estadísticas y reportes docentes
 * - Búsqueda y filtrado de profesores
 * - Información de carga horaria por semestre
 * 
 * Endpoints implementados: 14
 * - Gestión CRUD: 5 endpoints
 * - Consultas: 6 endpoints  
 * - Carga académica: 3 endpoints
 * 
 * @requires Rol: Variable según operación (Ver documentación de cada método)
 */

import apiClient from './api.config';

const BASE_URL = '/profesores';

const profesoresService = {
  /**
   * Obtener todos los profesores con filtros y paginación
   * 
   * Lista profesores con múltiples opciones de filtrado.
   * Incluye información del usuario asociado y la facultad.
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} params - Parámetros de filtrado y paginación
   * @param {number} [params.skip=0] - Número de registros a saltar para paginación
   * @param {number} [params.limit=100] - Máximo de registros a retornar (máx: 500)
   * @param {number} [params.facultad_id] - Filtrar por ID de facultad específica
   * @param {string} [params.busqueda] - Buscar por nombre, apellido o documento
   * @param {boolean} [params.solo_activos=true] - Solo incluir profesores con usuario activo
   * @returns {Promise<Array<Object>>} Lista de profesores con información del usuario
   * 
   * @example
   * const profesores = await profesoresService.getAll({
   *   facultad_id: 1,
   *   solo_activos: true,
   *   limit: 50
   * });
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener profesor por ID
   * 
   * Recupera la información básica de un profesor específico.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del profesor
   * @returns {Promise<Object>} Datos básicos del profesor
   * @returns {number} return.id - ID del profesor
   * @returns {number} return.usuario_id - ID del usuario asociado
   * @returns {string} return.documento - Número de documento de identidad
   * @returns {string} return.tipo_documento - Tipo de documento (CC/CE/TI/etc)
   * @returns {number} return.facultad_id - ID de la facultad
   * @returns {string} return.titulo_academico - Título académico del profesor
   * 
   * @throws {Error} Profesor no encontrado (404)
   * 
   * @example
   * const profesor = await profesoresService.getById(5);
   * console.log(profesor.titulo_academico);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear nuevo perfil de profesor
   * 
   * Crea un perfil de profesor asociado a un usuario existente.
   * El usuario debe tener rol de Profesor.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} profesorData - Datos del nuevo profesor
   * @param {number} profesorData.usuario_id - ID del usuario a asociar (requerido)
   * @param {string} [profesorData.documento] - Número de documento de identidad
   * @param {string} [profesorData.tipo_documento] - Tipo de documento
   * @param {number} [profesorData.facultad_id] - ID de la facultad
   * @param {string} [profesorData.titulo_academico] - Título académico
   * @returns {Promise<Object>} Profesor creado
   * 
   * @throws {Error} Usuario no encontrado (404)
   * @throws {Error} Usuario ya tiene perfil de profesor (400)
   * @throws {Error} Usuario no tiene rol de Profesor (400)
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const nuevoProfesor = await profesoresService.create({
   *   usuario_id: 10,
   *   documento: '1234567890',
   *   tipo_documento: 'CC',
   *   facultad_id: 2,
   *   titulo_academico: 'Magíster en Ingeniería'
   * });
   */
  async create(profesorData) {
    const response = await apiClient.post(BASE_URL, profesorData);
    return response.data;
  },

  /**
   * Actualizar perfil de profesor
   * 
   * Actualiza los datos de un profesor existente.
   * Solo los campos proporcionados serán actualizados.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del profesor a actualizar
   * @param {Object} profesorData - Datos a actualizar (solo los campos a modificar)
   * @param {string} [profesorData.documento] - Nuevo número de documento
   * @param {string} [profesorData.tipo_documento] - Nuevo tipo de documento
   * @param {number} [profesorData.facultad_id] - Nueva facultad
   * @param {string} [profesorData.titulo_academico] - Nuevo título académico
   * @returns {Promise<Object>} Profesor actualizado
   * 
   * @throws {Error} Profesor no encontrado (404)
   * @throws {Error} Facultad no encontrada (404)
   * @throws {Error} Datos inválidos (400)
   * 
   * @example
   * const actualizado = await profesoresService.update(5, {
   *   facultad_id: 3,
   *   titulo_academico: 'Doctor en Ciencias'
   * });
   */
  async update(id, profesorData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, profesorData);
    return response.data;
  },

  /**
   * Eliminar perfil de profesor
   * 
   * Elimina el perfil de profesor del sistema.
   * NOTA: Esta operación NO elimina el usuario asociado, solo el perfil de profesor.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del profesor a eliminar
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Profesor no encontrado (404)
   * 
   * @example
   * await profesoresService.delete(5);
   * console.log('Perfil de profesor eliminado');
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener profesor por ID de usuario
   * 
   * Útil para obtener el perfil de profesor del usuario autenticado.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} usuarioId - ID del usuario
   * @returns {Promise<Object>} Perfil del profesor
   * 
   * @throws {Error} Usuario no tiene perfil de profesor (404)
   * 
   * @example
   * const currentUser = authService.getCurrentUser();
   * const miPerfil = await profesoresService.getByUsuario(currentUser.id);
   */
  async getByUsuario(usuarioId) {
    const response = await apiClient.get(`${BASE_URL}/usuario/${usuarioId}`);
    return response.data;
  },

  /**
   * Obtener perfil completo del profesor
   * 
   * Retorna información detallada incluyendo:
   * - Datos del profesor
   * - Información completa del usuario (nombre, email, teléfono)
   * - Información de la facultad
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del profesor
   * @returns {Promise<Object>} Perfil completo del profesor
   * @returns {Object} return.profesor - Datos básicos del profesor
   * @returns {Object} return.usuario - Información completa del usuario
   * @returns {string} return.usuario.nombre - Nombre del profesor
   * @returns {string} return.usuario.apellido - Apellido del profesor
   * @returns {string} return.usuario.email - Email del profesor
   * @returns {Object} return.facultad - Información de la facultad (si tiene)
   * 
   * @throws {Error} Profesor no encontrado (404)
   * 
   * @example
   * const perfilCompleto = await profesoresService.getProfileComplete(5);
   * console.log(`${perfilCompleto.usuario.nombre} - ${perfilCompleto.facultad.nombre}`);
   */
  async getProfileComplete(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/completo`);
    return response.data;
  },

  /**
   * Obtener profesores por facultad
   * 
   * Lista todos los profesores de una facultad específica.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} facultadId - ID de la facultad
   * @param {boolean} [soloActivos=true] - Solo incluir profesores con usuario activo
   * @returns {Promise<Array<Object>>} Lista de profesores de la facultad
   * 
   * @example
   * const profesoresFacultad = await profesoresService.getByFacultad(1);
   */
  async getByFacultad(facultadId, soloActivos = true) {
    const response = await apiClient.get(`${BASE_URL}/facultad/${facultadId}`, {
      params: { solo_activos: soloActivos },
    });
    return response.data;
  },

  /**
   * Buscar profesores
   * 
   * Búsqueda flexible por múltiples criterios.
   * No distingue mayúsculas/minúsculas y soporta coincidencias parciales.
   * 
   * @async
   * @requires Token JWT válido
   * @param {string} termino - Término de búsqueda
   * @param {number} [limit=10] - Máximo de resultados (máx: 100)
   * @returns {Promise<Array<Object>>} Profesores que coinciden con la búsqueda
   * 
   * @description
   * Busca en los siguientes campos:
   * - Nombre del usuario
   * - Apellido del usuario
   * - Número de documento
   * - Título académico
   * 
   * @example
   * const resultados = await profesoresService.search('garcía');
   * const resultados2 = await profesoresService.search('ingeniero');
   */
  async search(termino, limit = 10) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { termino, limit },
    });
    return response.data;
  },

  /**
   * Obtener grupos asignados al profesor
   * 
   * Retorna todos los grupos donde el profesor está asignado,
   * con información del curso, horarios y estudiantes inscritos.
   * 
   * @async
   * @requires Token JWT válido (Mismo profesor o Superadmin)
   * @param {number} id - ID del profesor
   * @param {string} [semestre] - Filtrar por semestre específico (ej: "2024-1")
   * @param {string} [estado] - Filtrar por estado del grupo
   * @returns {Promise<Array<Object>>} Lista de grupos asignados
   * @returns {Object[]} return[].curso - Información del curso
   * @returns {Object[]} return[].horarios - Horarios de clase
   * @returns {number} return[].estudiantes_inscritos - Cantidad de estudiantes
   * 
   * @description
   * Estados de grupo disponibles:
   * - Programado: Grupo creado pero no iniciado
   * - Activo: Grupo en curso
   * - Finalizado: Grupo terminado
   * 
   * @example
   * const grupos = await profesoresService.getAssignedGroups(5, '2024-2', 'Activo');
   * grupos.forEach(g => console.log(`${g.curso.nombre} - ${g.estudiantes_inscritos} estudiantes`));
   */
  async getAssignedGroups(id, semestre = null, estado = null) {
    const params = {};
    if (semestre) params.semestre = semestre;
    if (estado) params.estado = estado;
    
    const response = await apiClient.get(`${BASE_URL}/${id}/grupos`, { params });
    return response.data;
  },

  /**
   * Obtener grupos activos del profesor
   * 
   * Retorna solo los grupos que están actualmente en curso o abiertos.
   * Útil para ver los cursos actuales del profesor.
   * 
   * @async
   * @requires Token JWT válido (Mismo profesor o Superadmin)
   * @param {number} id - ID del profesor
   * @returns {Promise<Array<Object>>} Grupos activos (en curso o abiertos)
   * 
   * @description
   * Incluye grupos con estados:
   * - Abierto: Aceptando inscripciones
   * - En Curso: Clases en progreso
   * 
   * @example
   * const gruposActivos = await profesoresService.getActiveGroups(5);
   * console.log(`Dictando ${gruposActivos.length} grupos actualmente`);
   */
  async getActiveGroups(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/grupos-activos`);
    return response.data;
  },

  /**
   * Obtener carga académica del profesor en un semestre
   * 
   * Retorna un reporte completo de la carga docente del profesor,
   * incluyendo total de grupos, estudiantes y horas semanales.
   * 
   * @async
   * @requires Token JWT válido (Mismo profesor o Superadmin)
   * @param {number} id - ID del profesor
   * @param {string} semestre - Semestre a consultar (requerido, ej: "2024-2")
   * @returns {Promise<Object>} Reporte de carga académica
   * @returns {string} return.semestre - Periodo académico consultado
   * @returns {number} return.total_grupos - Número de grupos asignados
   * @returns {number} return.total_estudiantes - Suma de estudiantes en todos los grupos
   * @returns {number} return.total_horas_semanales - Total de horas de clase por semana
   * @returns {Array<Object>} return.grupos - Detalle de cada grupo
   * @returns {Object} return.grupos[].curso - Información del curso
   * @returns {Array} return.grupos[].horarios - Horarios de clase del grupo
   * @returns {number} return.grupos[].estudiantes_inscritos - Estudiantes en el grupo
   * 
   * @throws {Error} Profesor no encontrado (404)
   * 
   * @description
   * Útil para:
   * - Planificación académica
   * - Reportes de carga docente
   * - Evaluación de distribución de trabajo
   * - Verificación de límites de horas de trabajo
   * 
   * @example
   * const carga = await profesoresService.getAcademicLoad(5, '2024-2');
   * console.log(`Total grupos: ${carga.total_grupos}`);
   * console.log(`Total estudiantes: ${carga.total_estudiantes}`);
   * console.log(`Horas semanales: ${carga.total_horas_semanales}`);
   * 
   * carga.grupos.forEach(grupo => {
   *   console.log(`- ${grupo.curso.nombre}: ${grupo.estudiantes_inscritos} estudiantes`);
   * });
   */
  async getAcademicLoad(id, semestre) {
    const response = await apiClient.get(`${BASE_URL}/${id}/carga-academica`, {
      params: { semestre },
    });
    return response.data;
  },

  /**
   * Obtener estadísticas generales del profesor
   * 
   * Retorna métricas generales sobre la actividad docente del profesor.
   * 
   * @async
   * @requires Token JWT válido (Mismo profesor o Superadmin)
   * @param {number} id - ID del profesor
   * @returns {Promise<Object>} Estadísticas del profesor
   * @returns {number} return.total_grupos_dictados - Total histórico de grupos dictados
   * @returns {number} return.grupos_activos - Grupos actuales (abiertos o en curso)
   * @returns {number} return.total_estudiantes_actuales - Estudiantes en grupos activos
   * @returns {number} return.semestres_activo - Cantidad de semestres en que ha dictado
   * 
   * @description
   * Útil para:
   * - Perfil del profesor
   * - Evaluación docente
   * - Reportes de gestión
   * - Análisis de experiencia
   * 
   * @example
   * const stats = await profesoresService.getStatistics(5);
   * console.log(`Ha dictado ${stats.total_grupos_dictados} grupos en total`);
   * console.log(`Actualmente: ${stats.grupos_activos} grupos con ${stats.total_estudiantes_actuales} estudiantes`);
   * console.log(`Experiencia: ${stats.semestres_activo} semestres`);
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },
};

export default profesoresService;
