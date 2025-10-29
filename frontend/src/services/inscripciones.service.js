/**
 * Servicio de Inscripciones - Planner Universitario
 * 
 * Módulo para la gestión de inscripciones de estudiantes en grupos (matrícula de cursos).
 * Implementa los 17 endpoints del módulo de inscripciones del backend.
 * 
 * @module inscripciones.service
 * 
 * Una inscripción representa la matrícula de un estudiante en un grupo específico.
 * Gestiona el ciclo completo desde la inscripción inicial hasta la finalización
 * del curso con nota definitiva y estado final (aprobado/reprobado).
 * 
 * Estados de inscripción:
 * - Inscrito: Estudiante actualmente cursando
 * - Retirado: Estudiante se retiró del curso
 * - Aprobado: Estudiante aprobó el curso
 * - Reprobado: Estudiante reprobó el curso
 * - Cancelado: Inscripción cancelada
 * 
 * Funcionalidades principales:
 * - Inscripción de estudiantes en grupos
 * - Gestión de estados y retiros
 * - Consulta de inscripciones por estudiante o grupo
 * - Actualización de notas definitivas
 * - Estadísticas y reportes de inscripciones
 * - Verificación de inscripciones activas
 * 
 * @requires Rol: Variable según operación
 */

import apiClient from './api.config';

const BASE_URL = '/inscripciones';

const inscripcionesService = {
  /**
   * Inscribir estudiante en un grupo
   * 
   * Crea una nueva inscripción (matrícula) de un estudiante en un grupo.
   * Valida cupos disponibles, estado del grupo y que no esté ya inscrito.
   * 
   * @async
   * @requires Token JWT válido
   * @param {Object} inscripcionData - Datos de la inscripción
   * @param {number} inscripcionData.estudiante_id - ID del estudiante (requerido)
   * @param {number} inscripcionData.grupo_id - ID del grupo (requerido)
   * @returns {Promise<Object>} Inscripción creada
   * @returns {number} return.id - ID de la inscripción
   * @returns {number} return.estudiante_id - ID del estudiante
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {string} return.estado - Estado inicial (Inscrito)
   * @returns {string} return.fecha_inscripcion - Fecha de inscripción
   * 
   * @throws {Error} Estudiante ya inscrito en el grupo (400)
   * @throws {Error} Grupo sin cupos disponibles (400)
   * @throws {Error} Grupo no acepta inscripciones (400)
   * @throws {Error} Estudiante o grupo no encontrado (404)
   */
  async create(inscripcionData) {
    const response = await apiClient.post(BASE_URL, inscripcionData);
    return response.data;
  },

  /**
   * Obtener inscripciones de un estudiante
   * 
   * Lista todas las inscripciones (historial académico) de un estudiante,
   * opcionalmente filtradas por semestre.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} estudianteId - ID del estudiante
   * @param {string} [semestre] - Filtrar por semestre (ej: "2024-1")
   * @returns {Promise<Array<Object>>} Lista de inscripciones con información de grupos
   */
  async getByEstudiante(estudianteId, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/estudiante/${estudianteId}`, { params });
    return response.data;
  },

  /**
   * Obtener inscripciones de un grupo
   * 
   * Lista todas las inscripciones (estudiantes) de un grupo específico,
   * con opción de filtrar por estado.
   * 
   * @async
   * @requires Token JWT válido (Profesor del grupo o Superadmin)
   * @param {number} grupoId - ID del grupo
   * @param {string} [estado] - Filtrar por estado (Inscrito/Retirado/Aprobado/Reprobado/Cancelado)
   * @returns {Promise<Array<Object>>} Lista de inscripciones con datos de estudiantes
   */
  async getByGrupo(grupoId, estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}`, { params });
    return response.data;
  },

  /**
   * Obtener grupos inscritos de un estudiante
   * 
   * Retorna los grupos en los que el estudiante está inscrito,
   * con información completa del curso, profesor y horarios.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} estudianteId - ID del estudiante
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<Object>>} Lista de grupos con información completa
   * @returns {Object[]} return[].grupo - Información del grupo
   * @returns {Object[]} return[].curso - Información del curso
   * @returns {Object[]} return[].profesor - Información del profesor
   * @returns {Array} return[].horarios - Horarios de clase
   */
  async getGruposInscritos(estudianteId, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/estudiante/${estudianteId}/grupos`, { params });
    return response.data;
  },

  /**
   * Obtener inscripción específica de estudiante en grupo
   * 
   * Recupera la inscripción de un estudiante en un grupo particular.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} estudianteId - ID del estudiante
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Inscripción del estudiante en el grupo
   * 
   * @throws {Error} Inscripción no encontrada (404)
   */
  async getByEstudianteAndGrupo(estudianteId, grupoId) {
    const response = await apiClient.get(`${BASE_URL}/estudiante/${estudianteId}/grupo/${grupoId}`);
    return response.data;
  },

  /**
   * Obtener inscripción por ID
   * 
   * Recupera una inscripción específica con todas sus relaciones.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} id - ID de la inscripción
   * @returns {Promise<Object>} Datos completos de la inscripción
   * 
   * @throws {Error} Inscripción no encontrada (404)
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener estadísticas de inscripciones de un grupo
   * 
   * Retorna un resumen estadístico de las inscripciones del grupo.
   * 
   * @async
   * @requires Token JWT válido (Profesor del grupo o Superadmin)
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Estadísticas de inscripciones
   * @returns {number} return.total_inscripciones - Total histórico de inscripciones
   * @returns {number} return.inscritos - Estudiantes actualmente inscritos
   * @returns {number} return.retirados - Estudiantes retirados
   * @returns {number} return.aprobados - Estudiantes que aprobaron
   * @returns {number} return.reprobados - Estudiantes que reprobaron
   * @returns {number} return.cancelados - Inscripciones canceladas
   * @returns {number} return.cupos_disponibles - Cupos libres en el grupo
   */
  async getStatistics(grupoId) {
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/estadisticas`);
    return response.data;
  },

  /**
   * Contar inscripciones de un grupo
   * 
   * Cuenta el número de inscripciones de un grupo, opcionalmente por estado.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} grupoId - ID del grupo
   * @param {string} [estado] - Filtrar por estado
   * @returns {Promise<Object>} Conteo de inscripciones
   * @returns {number} return.grupo_id - ID del grupo
   * @returns {number} return.total_inscripciones - Número de inscripciones
   */
  async count(grupoId, estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(`${BASE_URL}/grupo/${grupoId}/contar`, { params });
    return response.data;
  },

  /**
   * Verificar si estudiante está inscrito en grupo
   * 
   * Verifica si un estudiante tiene una inscripción activa en un grupo.
   * Solo considera inscripciones con estado "Inscrito".
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} estudianteId - ID del estudiante
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Resultado de verificación
   * @returns {boolean} return.esta_inscrito - Si está inscrito activamente
   * @returns {string} return.mensaje - Mensaje descriptivo
   */
  async isEnrolled(estudianteId, grupoId) {
    const response = await apiClient.get(
      `${BASE_URL}/verificar/estudiante/${estudianteId}/grupo/${grupoId}`
    );
    return response.data;
  },

  /**
   * Actualizar inscripción
   * 
   * Actualiza los datos de una inscripción existente.
   * Puede cambiar estado y/o nota definitiva.
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la inscripción
   * @param {Object} inscripcionData - Datos a actualizar
   * @param {string} [inscripcionData.estado] - Nuevo estado
   * @param {number} [inscripcionData.nota_definitiva] - Nota final (0.0 - 5.0)
   * @returns {Promise<Object>} Inscripción actualizada
   * 
   * @throws {Error} Inscripción no encontrada (404)
   */
  async update(id, inscripcionData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, inscripcionData);
    return response.data;
  },

  /**
   * Cambiar estado de inscripción
   * 
   * Actualiza el estado de una inscripción.
   * Puede afectar los cupos del grupo según el cambio de estado.
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la inscripción
   * @param {string} estado - Nuevo estado (Inscrito/Retirado/Aprobado/Reprobado/Cancelado)
   * @returns {Promise<Object>} Inscripción actualizada
   * 
   * @description
   * Efectos según estado:
   * - Retirado/Cancelado: Libera 1 cupo del grupo
   * - Inscrito (desde retirado): Ocupa 1 cupo del grupo
   * - Aprobado/Reprobado: No afecta cupos
   * 
   * @throws {Error} Inscripción no encontrada (404)
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Actualizar nota definitiva
   * 
   * Asigna la nota final del estudiante en el curso.
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la inscripción
   * @param {number} notaDefinitiva - Nota final (0.0 - 5.0)
   * @returns {Promise<Object>} Inscripción actualizada
   * 
   * @description
   * Criterio de aprobación:
   * - Nota >= 3.0: Se considera aprobado
   * - Nota < 3.0: Se considera reprobado
   * 
   * @throws {Error} Inscripción no encontrada (404)
   * @throws {Error} Nota fuera de rango (400)
   */
  async updateGrade(id, notaDefinitiva) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/nota`, null, {
      params: { nota_definitiva: notaDefinitiva },
    });
    return response.data;
  },

  /**
   * Retirar estudiante de un grupo
   * 
   * Retira un estudiante del grupo cambiando el estado a "Retirado"
   * y liberando el cupo ocupado.
   * 
   * @async
   * @requires Token JWT válido (Mismo estudiante, Profesor del grupo o Superadmin)
   * @param {number} id - ID de la inscripción
   * @returns {Promise<Object>} Inscripción actualizada con estado Retirado
   * 
   * @throws {Error} Ya está retirado o cancelado (400)
   * @throws {Error} Inscripción no encontrada (404)
   * 
   * @description
   * Efectos:
   * - Cambia estado a "Retirado"
   * - Libera 1 cupo en el grupo
   * - Mantiene historial (no elimina el registro)
   */
  async withdraw(id) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/retirar`);
    return response.data;
  },

  /**
   * Eliminar inscripción
   * 
   * Elimina físicamente una inscripción del sistema.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID de la inscripción
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Inscripción no encontrada (404)
   * 
   * @description
   * ADVERTENCIA: Esta operación elimina permanentemente el registro.
   * Para mantener historial, use withdraw() en su lugar.
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Inscribir estudiante (alias de create)
   * 
   * Método alternativo más semántico para inscribir un estudiante.
   * 
   * @async
   * @param {number} estudianteId - ID del estudiante
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Object>} Inscripción creada
   */
  async enroll(estudianteId, grupoId) {
    return this.create({
      estudiante_id: estudianteId,
      grupo_id: grupoId,
    });
  },

  /**
   * Aprobar inscripción
   * 
   * Marca una inscripción como aprobada con una nota.
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la inscripción
   * @param {number} nota - Nota definitiva (>= 3.0)
   * @returns {Promise<Object>} Inscripción actualizada
   */
  async approve(id, nota) {
    await this.updateGrade(id, nota);
    return this.changeStatus(id, 'Aprobado');
  },

  /**
   * Reprobar inscripción
   * 
   * Marca una inscripción como reprobada con una nota.
   * 
   * @async
   * @requires Rol: Profesor (del grupo) o Superadmin
   * @param {number} id - ID de la inscripción
   * @param {number} nota - Nota definitiva (< 3.0)
   * @returns {Promise<Object>} Inscripción actualizada
   */
  async fail(id, nota) {
    await this.updateGrade(id, nota);
    return this.changeStatus(id, 'Reprobado');
  },

  /**
   * Obtener inscripciones activas de un grupo
   * 
   * Obtiene solo las inscripciones con estado "Inscrito".
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} grupoId - ID del grupo
   * @returns {Promise<Array<Object>>} Lista de inscripciones activas
   */
  async getActiveEnrollments(grupoId) {
    return this.getByGrupo(grupoId, 'Inscrito');
  },

  /**
   * Obtener cursos actuales del estudiante
   * 
   * Obtiene los grupos en los que el estudiante está inscrito actualmente.
   * 
   * @async
   * @requires Token JWT válido
   * @param {number} estudianteId - ID del estudiante
   * @returns {Promise<Array<Object>>} Lista de grupos actuales
   */
  async getCurrentCourses(estudianteId) {
    const inscripciones = await this.getByEstudiante(estudianteId);
    return inscripciones.filter((insc) => insc.estado === 'Inscrito');
  },
};

export default inscripcionesService;
