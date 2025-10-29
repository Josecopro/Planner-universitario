/**
 * Servicio de Programas Académicos - Planner Universitario
 * 
 * Módulo para la gestión de programas académicos de la universidad.
 * Implementa los 14 endpoints del módulo de programas académicos del backend.
 * 
 * @module programas-academicos.service
 * 
 * Un programa académico es una carrera o plan de estudios ofrecido por una facultad.
 * Ejemplos: Ingeniería de Sistemas, Medicina, Administración de Empresas.
 * 
 * Estados de programa:
 * - Activo: Programa que acepta nuevas inscripciones
 * - Inactivo: Programa temporalmente suspendido
 * - Cerrado: Programa cerrado permanentemente
 * 
 * Funcionalidades principales:
 * - Gestión CRUD de programas académicos
 * - Consulta de estudiantes por programa
 * - Búsqueda por código o nombre
 * - Estadísticas de programas
 * - Gestión de estados
 * 
 * @requires Rol: Variable según operación (Superadmin para modificaciones)
 */

import apiClient from './api.config';

const BASE_URL = '/programas-academicos';

const programasAcademicosService = {
  /**
   * Crear un nuevo programa académico
   * 
   * Crea un programa académico asociado a una facultad.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} programaData - Datos del programa
   * @param {string} programaData.codigo - Código único del programa (requerido)
   * @param {string} programaData.nombre - Nombre completo del programa (requerido)
   * @param {number} programaData.facultad_id - ID de la facultad (requerido)
   * @param {string} [programaData.duracion_semestres] - Duración en semestres
   * @param {string} [programaData.titulo_otorgado] - Título que otorga
   * @param {string} [programaData.estado='Activo'] - Estado inicial
   * @returns {Promise<Object>} Programa creado
   * @returns {number} return.id - ID del programa
   * @returns {string} return.codigo - Código único
   * @returns {string} return.nombre - Nombre completo
   * @returns {number} return.facultad_id - ID de la facultad
   * @returns {string} return.estado - Estado del programa
   * 
   * @throws {Error} Facultad no existe (400)
   * @throws {Error} Código ya registrado (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const programa = await programasAcademicosService.create({
   *   codigo: 'ING-SIST',
   *   nombre: 'Ingeniería de Sistemas',
   *   facultad_id: 1,
   *   duracion_semestres: '10',
   *   titulo_otorgado: 'Ingeniero de Sistemas'
   * });
   */
  async create(programaData) {
    const response = await apiClient.post(BASE_URL, programaData);
    return response.data;
  },

  /**
   * Obtener todos los programas académicos
   * 
   * Lista todos los programas, opcionalmente filtrados por estado.
   * 
   * @async
   * @param {string} [estado] - Filtrar por estado (Activo/Inactivo/Cerrado)
   * @returns {Promise<Array<Object>>} Lista de programas
   * 
   * @example
   * const todos = await programasAcademicosService.getAll();
   * const activos = await programasAcademicosService.getAll('Activo');
   */
  async getAll(estado = null) {
    const params = estado ? { estado } : {};
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  /**
   * Obtener programas académicos activos
   * 
   * Lista solo los programas con estado Activo, opcionalmente filtrados por facultad.
   * 
   * @async
   * @param {number} [facultadId] - Filtrar por facultad
   * @returns {Promise<Array<Object>>} Lista de programas activos
   * 
   * @example
   * const activos = await programasAcademicosService.getActive();
   * const activosFacultad = await programasAcademicosService.getActive(1);
   */
  async getActive(facultadId = null) {
    const params = facultadId ? { facultad_id: facultadId } : {};
    const response = await apiClient.get(`${BASE_URL}/activos`, { params });
    return response.data;
  },

  /**
   * Obtener programas por facultad
   * 
   * Lista todos los programas de una facultad específica.
   * 
   * @async
   * @param {number} facultadId - ID de la facultad
   * @returns {Promise<Array<Object>>} Lista de programas de la facultad
   * 
   * @example
   * const programas = await programasAcademicosService.getByFaculty(1);
   */
  async getByFaculty(facultadId) {
    const response = await apiClient.get(`${BASE_URL}/facultad/${facultadId}`);
    return response.data;
  },

  /**
   * Obtener programas con conteo de estudiantes
   * 
   * Lista programas con el número total de estudiantes en cada uno.
   * Útil para reportes y dashboards.
   * 
   * @async
   * @param {number} [facultadId] - Filtrar por facultad
   * @returns {Promise<Array<Object>>} Lista de programas con contadores
   * @returns {Object} return[].programa - Datos del programa
   * @returns {number} return[].total_estudiantes - Total de estudiantes
   * 
   * @example
   * const programasConConteo = await programasAcademicosService.getWithStudentCount();
   */
  async getWithStudentCount(facultadId = null) {
    const params = facultadId ? { facultad_id: facultadId } : {};
    const response = await apiClient.get(`${BASE_URL}/con-conteo`, { params });
    return response.data;
  },

  /**
   * Buscar programas académicos
   * 
   * Busca programas por nombre o código con filtros opcionales.
   * La búsqueda es case-insensitive y soporta búsqueda parcial.
   * 
   * @async
   * @param {string} termino - Término de búsqueda (mínimo 1 carácter)
   * @param {number} [facultadId] - Filtrar por facultad
   * @param {string} [estado] - Filtrar por estado
   * @returns {Promise<Array<Object>>} Lista de programas que coinciden
   * 
   * @example
   * const resultados = await programasAcademicosService.search('ingenieria');
   * const resultadosFiltrados = await programasAcademicosService.search('ing', 1, 'Activo');
   */
  async search(termino, facultadId = null, estado = null) {
    const params = { termino_busqueda: termino };
    if (facultadId) params.facultad_id = facultadId;
    if (estado) params.estado = estado;
    const response = await apiClient.get(`${BASE_URL}/buscar`, { params });
    return response.data;
  },

  /**
   * Obtener programa por código
   * 
   * Busca un programa específico por su código único.
   * 
   * @async
   * @param {string} codigo - Código del programa
   * @returns {Promise<Object>} Programa encontrado
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const programa = await programasAcademicosService.getByCode('ING-SIST');
   */
  async getByCode(codigo) {
    const response = await apiClient.get(`${BASE_URL}/codigo/${codigo}`);
    return response.data;
  },

  /**
   * Obtener programa por ID
   * 
   * Recupera un programa específico por su identificador.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Programa encontrado
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const programa = await programasAcademicosService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener estudiantes de un programa
   * 
   * Lista todos los estudiantes inscritos en un programa académico.
   * 
   * @async
   * @param {number} id - ID del programa
   * @param {string} [semestre] - Filtrar por semestre
   * @returns {Promise<Array<Object>>} Lista de estudiantes
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const estudiantes = await programasAcademicosService.getStudents(1);
   * const estudiantesSemestre = await programasAcademicosService.getStudents(1, '2024-1');
   */
  async getStudents(id, semestre = null) {
    const params = semestre ? { semestre } : {};
    const response = await apiClient.get(`${BASE_URL}/${id}/estudiantes`, { params });
    return response.data;
  },

  /**
   * Contar estudiantes de un programa
   * 
   * Obtiene el número total de estudiantes en un programa.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Conteo de estudiantes
   * @returns {number} return.total_estudiantes - Total de estudiantes
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const { total_estudiantes } = await programasAcademicosService.countStudents(1);
   */
  async countStudents(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/conteo-estudiantes`);
    return response.data;
  },

  /**
   * Obtener estadísticas de un programa
   * 
   * Retorna estadísticas completas del programa académico.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Estadísticas del programa
   * @returns {Object} return.programa - Datos del programa
   * @returns {number} return.total_estudiantes - Total de estudiantes
   * @returns {number} return.total_cursos - Total de cursos del programa
   * @returns {Object} return.estudiantes_por_semestre - Distribución por semestre
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const stats = await programasAcademicosService.getStatistics(1);
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },

  /**
   * Actualizar un programa académico
   * 
   * Modifica los datos de un programa existente.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del programa
   * @param {Object} programaData - Datos a actualizar
   * @param {string} [programaData.codigo] - Nuevo código único
   * @param {string} [programaData.nombre] - Nuevo nombre
   * @param {number} [programaData.facultad_id] - Nueva facultad
   * @param {string} [programaData.duracion_semestres] - Nueva duración
   * @param {string} [programaData.titulo_otorgado] - Nuevo título
   * @param {string} [programaData.estado] - Nuevo estado
   * @returns {Promise<Object>} Programa actualizado
   * 
   * @throws {Error} Programa no encontrado (404)
   * @throws {Error} Código ya en uso (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const actualizado = await programasAcademicosService.update(1, {
   *   nombre: 'Ingeniería de Sistemas y Computación'
   * });
   */
  async update(id, programaData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, programaData);
    return response.data;
  },

  /**
   * Cambiar estado de un programa
   * 
   * Actualiza únicamente el estado del programa.
   * 
   * @async
   * @param {number} id - ID del programa
   * @param {string} estado - Nuevo estado (Activo/Inactivo/Cerrado)
   * @returns {Promise<Object>} Programa actualizado
   * 
   * @throws {Error} Programa no encontrado (404)
   * 
   * @example
   * const programa = await programasAcademicosService.changeStatus(1, 'Inactivo');
   */
  async changeStatus(id, estado) {
    const response = await apiClient.patch(`${BASE_URL}/${id}/estado`, { estado });
    return response.data;
  },

  /**
   * Eliminar un programa académico
   * 
   * Elimina un programa del sistema.
   * No se puede eliminar si tiene estudiantes registrados.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID del programa
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Programa no encontrado (404)
   * @throws {Error} Programa tiene estudiantes registrados (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @description
   * ADVERTENCIA: Esta operación elimina permanentemente el programa.
   * Considere cambiar el estado a "Cerrado" en su lugar.
   * 
   * @example
   * await programasAcademicosService.delete(5);
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Activar un programa
   * 
   * Método auxiliar para cambiar el estado a Activo.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Programa actualizado
   * 
   * @example
   * await programasAcademicosService.activate(1);
   */
  async activate(id) {
    return this.changeStatus(id, 'Activo');
  },

  /**
   * Desactivar un programa
   * 
   * Método auxiliar para cambiar el estado a Inactivo.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Programa actualizado
   * 
   * @example
   * await programasAcademicosService.deactivate(1);
   */
  async deactivate(id) {
    return this.changeStatus(id, 'Inactivo');
  },

  /**
   * Cerrar un programa
   * 
   * Método auxiliar para cambiar el estado a Cerrado.
   * 
   * @async
   * @param {number} id - ID del programa
   * @returns {Promise<Object>} Programa actualizado
   * 
   * @example
   * await programasAcademicosService.close(1);
   */
  async close(id) {
    return this.changeStatus(id, 'Cerrado');
  },

  /**
   * Verificar si existe un programa por código
   * 
   * Método auxiliar para verificar la existencia de un programa.
   * 
   * @async
   * @param {string} codigo - Código del programa
   * @returns {Promise<boolean>} true si existe, false si no
   * 
   * @example
   * const existe = await programasAcademicosService.exists('ING-SIST');
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
   * Obtener programas con estadísticas completas
   * 
   * Método auxiliar que combina múltiples llamadas para obtener
   * información detallada de todos los programas.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Programas con estadísticas
   * 
   * @example
   * const programasDetallados = await programasAcademicosService.getAllWithStats();
   */
  async getAllWithStats() {
    return this.getWithStudentCount();
  },

  /**
   * Obtener programas por estado con conteo
   * 
   * Método auxiliar para obtener programas de un estado específico con su conteo de estudiantes.
   * 
   * @async
   * @param {string} estado - Estado del programa
   * @returns {Promise<Array<Object>>} Programas del estado especificado con estadísticas
   * 
   * @example
   * const programasActivos = await programasAcademicosService.getByStatusWithCount('Activo');
   */
  async getByStatusWithCount(estado) {
    const programas = await this.getAll(estado);
    const programasConConteo = await this.getWithStudentCount();
    
    return programas.map((programa) => {
      const conteo = programasConConteo.find((p) => p.programa?.id === programa.id);
      return {
        ...programa,
        total_estudiantes: conteo?.total_estudiantes || 0,
      };
    });
  },
};

export default programasAcademicosService;
