/**
 * Servicio de Grupos - Planner Universitario
 * 
 * Módulo para la gestión de grupos (secciones) de cursos.
 * Implementa los 13 endpoints del módulo de grupos del backend.
 * 
 * @module grupos.service
 * 
 * Un grupo representa una sección específica de un curso en un semestre,
 * con un profesor asignado, horarios definidos y estudiantes inscritos.
 * 
 * Endpoints implementados:
 * - CRUD de grupos
 * - Asignación de profesores
 * - Gestión de cupos
 * - Consulta de grupos por semestre/curso
 * - Dashboard de grupo con estadísticas
 * 
 * @requires Rol: Variable según operación (Ver documentación de cada método)
 */

import apiClient from './api.config';

const BASE_URL = '/grupos';

const gruposService = {
  /**
   * Obtener todos los grupos con filtros
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} params - Parámetros de filtrado
   * @param {number} [params.skip=0] - Registros a saltar
   * @param {number} [params.limit=10] - Registros a retornar
   * @param {number} [params.curso_id] - Filtrar por curso
   * @param {string} [params.semestre] - Filtrar por semestre (ej: "2024-1")
   * @param {string} [params.estado] - Filtrar por estado (Programado/Activo/Finalizado)
   * @returns {Promise<Array>} Lista de grupos
   */
  async getAll(params = {}) {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener grupo por ID
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del grupo
   * @returns {Promise<Object>} Datos completos del grupo
   * @returns {Object} return.curso - Información del curso
   * @returns {Object} return.profesor - Información del profesor
   * @returns {number} return.cupos_totales - Cupos totales
   * @returns {number} return.cupos_disponibles - Cupos disponibles
   * @returns {number} return.inscritos - Estudiantes inscritos
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Crear nuevo grupo
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} grupoData - Datos del grupo
   * @param {number} grupoData.curso_id - ID del curso
   * @param {string} grupoData.codigo - Código único del grupo (ej: "G01")
   * @param {string} grupoData.semestre - Semestre (ej: "2024-1")
   * @param {number} [grupoData.profesor_id] - ID del profesor (opcional)
   * @param {number} [grupoData.cupos_totales=30] - Cupos máximos
   * @param {string} [grupoData.estado='Programado'] - Estado inicial
   * @returns {Promise<Object>} Grupo creado
   */
  async create(grupoData) {
    const response = await apiClient.post(BASE_URL, grupoData);
    return response.data;
  },

  /**
   * Actualizar grupo existente
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del grupo
   * @param {Object} grupoData - Datos a actualizar
   * @returns {Promise<Object>} Grupo actualizado
   */
  async update(id, grupoData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, grupoData);
    return response.data;
  },

  /**
   * Eliminar grupo
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del grupo
   * @returns {Promise<Object>} Mensaje de confirmación
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener grupos de un curso
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} cursoId - ID del curso
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array>} Grupos del curso
   */
  async getByCurso(cursoId, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/curso/${cursoId}`, { params });
    return response.data;
  },

  /**
   * Obtener grupos de un semestre
   * 
   * @async
   * @requires Token JWT válido
   * @param {string} semestre - Código del semestre (ej: "2024-1")
   * @returns {Promise<Array>} Grupos del semestre
   */
  async getBySemestre(semestre) {
    const response = await apiClient.get(`${BASE_URL}/semestre/${semestre}`);
    return response.data;
  },

  /**
   * Asignar o cambiar profesor del grupo
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del grupo
   * @param {number} profesorId - ID del profesor a asignar
   * @returns {Promise<Object>} Grupo actualizado
   */
  async assignProfesor(id, profesorId) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/profesor`, {
      profesor_id: profesorId,
    });
    return response.data;
  },

  /**
   * Cambiar estado del grupo
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del grupo
   * @param {string} estado - Nuevo estado (Programado/Activo/Finalizado)
   * @returns {Promise<Object>} Grupo actualizado
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Obtener dashboard del grupo con estadísticas
   * 
   * Retorna información completa del grupo incluyendo:
   * - Información del curso y profesor
   * - Estadísticas de inscripciones
   * - Total de actividades
   * - Promedio general del grupo
   * - Horarios de clase
   * 
   * @async
   * @requires Token JWT válido (Profesor del grupo o Superadmin)
   * @param {number} id - ID del grupo
   * @returns {Promise<Object>} Dashboard completo del grupo
   */
  async getDashboard(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/dashboard`);
    return response.data;
  },

  /**
   * Obtener estudiantes inscritos en el grupo
   * 
   * @async
   * @requires Token JWT válido (Profesor del grupo o Superadmin)
   * @param {number} id - ID del grupo
   * @returns {Promise<Array>} Lista de estudiantes inscritos
   */
  async getStudents(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estudiantes`);
    return response.data;
  },

  /**
   * Verificar si un estudiante puede inscribirse
   * 
   * Verifica:
   * - Cupos disponibles
   * - Prerrequisitos cumplidos
   * - No tener cruce de horarios
   * - Estado del grupo (debe estar Activo)
   * 
   * @async
   * @requires Rol: Estudiante
   * @param {number} id - ID del grupo
   * @returns {Promise<Object>} Resultado de la verificación
   * @returns {boolean} return.puede_inscribirse - Si puede inscribirse
   * @returns {string} return.razon - Razón si no puede inscribirse
   */
  async canEnroll(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/puede-inscribirse`);
    return response.data;
  },

  /**
   * Verificar cupos disponibles
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID del grupo
   * @returns {Promise<Object>} Información de cupos
   * @returns {number} return.cupos_totales - Cupos totales
   * @returns {number} return.cupos_ocupados - Cupos ocupados
   * @returns {number} return.cupos_disponibles - Cupos disponibles
   * @returns {boolean} return.tiene_cupos - Si hay cupos disponibles
   */
  async checkCapacity(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/cupos`);
    return response.data;
  },
};

export default gruposService;
