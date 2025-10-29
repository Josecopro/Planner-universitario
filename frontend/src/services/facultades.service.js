/**
 * Servicio de Facultades - Planner Universitario
 * 
 * Módulo para la gestión de facultades de la universidad.
 * Implementa los 11 endpoints del módulo de facultades del backend.
 * 
 * @module facultades.service
 * 
 * Una facultad es una división académica de la universidad que agrupa
 * programas académicos, cursos y profesores relacionados.
 * Ejemplos: Facultad de Ingeniería, Facultad de Ciencias, Facultad de Administración.
 * 
 * Funcionalidades principales:
 * - Gestión CRUD de facultades
 * - Búsqueda por código o nombre
 * - Consulta de profesores adscritos
 * - Consulta de cursos ofrecidos
 * - Estadísticas y resúmenes
 * 
 * @requires Rol: Variable según operación (Superadmin para modificaciones)
 */

import apiClient from './api.config';

const BASE_URL = '/facultades';

const facultadesService = {
  /**
   * Crear una nueva facultad
   * 
   * Crea una facultad en el sistema con código y nombre únicos.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {Object} facultadData - Datos de la facultad
   * @param {string} facultadData.codigo - Código único de la facultad (ej: ING, CIEN, ADMIN) (requerido)
   * @param {string} facultadData.nombre - Nombre completo de la facultad (requerido)
   * @returns {Promise<Object>} Facultad creada
   * @returns {number} return.id - ID de la facultad
   * @returns {string} return.codigo - Código único
   * @returns {string} return.nombre - Nombre completo
   * 
   * @throws {Error} Código o nombre duplicado (400)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const facultad = await facultadesService.create({
   *   codigo: 'ING',
   *   nombre: 'Facultad de Ingeniería'
   * });
   */
  async create(facultadData) {
    const response = await apiClient.post(BASE_URL, facultadData);
    return response.data;
  },

  /**
   * Obtener todas las facultades
   * 
   * Lista todas las facultades del sistema ordenadas por nombre.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Lista de facultades
   * @returns {number} return[].id - ID de la facultad
   * @returns {string} return[].codigo - Código único
   * @returns {string} return[].nombre - Nombre completo
   * 
   * @example
   * const facultades = await facultadesService.getAll();
   * // [{ id: 1, codigo: 'ING', nombre: 'Facultad de Ingeniería' }, ...]
   */
  async getAll() {
    const response = await apiClient.get(BASE_URL);
    return response.data;
  },

  /**
   * Obtener resumen de facultades con estadísticas
   * 
   * Retorna todas las facultades con contadores de programas, cursos y profesores.
   * Útil para dashboards y reportes administrativos.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Lista de facultades con estadísticas
   * @returns {number} return[].id - ID de la facultad
   * @returns {string} return[].codigo - Código único
   * @returns {string} return[].nombre - Nombre completo
   * @returns {number} return[].total_programas - Total de programas académicos
   * @returns {number} return[].total_cursos - Total de cursos ofrecidos
   * @returns {number} return[].total_profesores - Total de profesores adscritos
   * 
   * @example
   * const resumen = await facultadesService.getSummary();
   * // [{ id: 1, codigo: 'ING', nombre: '...', total_programas: 5, total_cursos: 80, total_profesores: 25 }]
   */
  async getSummary() {
    const response = await apiClient.get(`${BASE_URL}/resumen`);
    return response.data;
  },

  /**
   * Buscar facultades por término
   * 
   * Busca facultades cuyo código o nombre contenga el término especificado.
   * La búsqueda es case-insensitive y soporta búsqueda parcial.
   * 
   * @async
   * @param {string} termino - Término de búsqueda (mínimo 1 carácter)
   * @returns {Promise<Array<Object>>} Lista de facultades que coinciden
   * 
   * @example
   * const resultados = await facultadesService.search('ing');
   * // Encuentra 'Facultad de Ingeniería'
   * 
   * const resultados2 = await facultadesService.search('ciencias');
   * // Encuentra 'Facultad de Ciencias'
   */
  async search(termino) {
    const response = await apiClient.get(`${BASE_URL}/buscar`, {
      params: { termino },
    });
    return response.data;
  },

  /**
   * Obtener facultad por código
   * 
   * Busca una facultad específica por su código único.
   * 
   * @async
   * @param {string} codigo - Código de la facultad (ej: 'ING', 'CIEN')
   * @returns {Promise<Object>} Facultad encontrada
   * 
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const facultad = await facultadesService.getByCode('ING');
   */
  async getByCode(codigo) {
    const response = await apiClient.get(`${BASE_URL}/codigo/${codigo}`);
    return response.data;
  },

  /**
   * Obtener facultad por ID
   * 
   * Recupera una facultad específica por su identificador.
   * 
   * @async
   * @param {number} id - ID de la facultad
   * @returns {Promise<Object>} Facultad encontrada
   * 
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const facultad = await facultadesService.getById(1);
   */
  async getById(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Obtener estadísticas de una facultad
   * 
   * Retorna información completa de la facultad con contadores detallados.
   * 
   * @async
   * @param {number} id - ID de la facultad
   * @returns {Promise<Object>} Estadísticas de la facultad
   * @returns {number} return.id - ID de la facultad
   * @returns {string} return.codigo - Código único
   * @returns {string} return.nombre - Nombre completo
   * @returns {number} return.total_programas - Número de programas académicos
   * @returns {number} return.total_cursos - Número de cursos ofrecidos
   * @returns {number} return.total_profesores - Número de profesores adscritos
   * 
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const stats = await facultadesService.getStatistics(1);
   * console.log(`${stats.nombre} tiene ${stats.total_programas} programas`);
   */
  async getStatistics(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/estadisticas`);
    return response.data;
  },

  /**
   * Obtener profesores de una facultad
   * 
   * Lista todos los profesores adscritos a una facultad específica.
   * 
   * @async
   * @param {number} id - ID de la facultad
   * @returns {Promise<Array<Object>>} Lista de profesores
   * @returns {number} return[].id - ID del profesor
   * @returns {Object} return[].usuario - Información del usuario asociado
   * @returns {number} return[].facultad_id - ID de la facultad
   * 
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const profesores = await facultadesService.getProfessors(1);
   * // Lista de todos los profesores de la facultad
   */
  async getProfessors(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/profesores`);
    return response.data;
  },

  /**
   * Obtener cursos de una facultad
   * 
   * Lista todos los cursos que pertenecen a una facultad.
   * 
   * @async
   * @param {number} id - ID de la facultad
   * @returns {Promise<Array<Object>>} Lista de cursos
   * @returns {number} return[].id - ID del curso
   * @returns {string} return[].codigo - Código del curso
   * @returns {string} return[].nombre - Nombre del curso
   * @returns {number} return[].creditos - Créditos del curso
   * @returns {number} return[].horas_semanales - Horas semanales
   * @returns {string} return[].estado - Estado del curso (Activo/Inactivo)
   * 
   * @throws {Error} Facultad no encontrada (404)
   * 
   * @example
   * const cursos = await facultadesService.getCourses(1);
   * // Lista de todos los cursos ofrecidos por la facultad
   */
  async getCourses(id) {
    const response = await apiClient.get(`${BASE_URL}/${id}/cursos`);
    return response.data;
  },

  /**
   * Actualizar una facultad
   * 
   * Modifica los datos de una facultad existente.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID de la facultad
   * @param {Object} facultadData - Datos a actualizar
   * @param {string} [facultadData.codigo] - Nuevo código único
   * @param {string} [facultadData.nombre] - Nuevo nombre
   * @returns {Promise<Object>} Facultad actualizada
   * 
   * @throws {Error} Código o nombre duplicado (400)
   * @throws {Error} Facultad no encontrada (404)
   * @throws {Error} Usuario no es Superadmin (403)
   * 
   * @example
   * const facultadActualizada = await facultadesService.update(1, {
   *   nombre: 'Facultad de Ingeniería y Arquitectura'
   * });
   */
  async update(id, facultadData) {
    const response = await apiClient.put(`${BASE_URL}/${id}`, facultadData);
    return response.data;
  },

  /**
   * Eliminar una facultad
   * 
   * NOTA: Este endpoint no está implementado en el backend actual.
   * Típicamente no se eliminan facultades por integridad referencial.
   * 
   * @async
   * @requires Rol: Superadmin
   * @param {number} id - ID de la facultad
   * @returns {Promise<void>} Sin contenido (204)
   * 
   * @throws {Error} Endpoint no implementado (501)
   */
  async delete(id) {
    const response = await apiClient.delete(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Verificar si existe una facultad por código
   * 
   * Método auxiliar para verificar la existencia de una facultad.
   * 
   * @async
   * @param {string} codigo - Código de la facultad
   * @returns {Promise<boolean>} true si existe, false si no
   * 
   * @example
   * const existe = await facultadesService.exists('ING');
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
   * Obtener facultades con sus programas académicos
   * 
   * Método auxiliar que combina información de facultades con sus programas.
   * 
   * @async
   * @returns {Promise<Array<Object>>} Facultades con información de programas
   * 
   * @example
   * const facultadesConProgramas = await facultadesService.getAllWithPrograms();
   */
  async getAllWithPrograms() {
    const resumen = await this.getSummary();
    return resumen.filter((f) => f.total_programas > 0);
  },

  /**
   * Obtener facultades activas
   * 
   * Método auxiliar para obtener facultades que tienen actividad
   * (con al menos un curso o profesor).
   * 
   * @async
   * @returns {Promise<Array<Object>>} Facultades activas
   * 
   * @example
   * const activas = await facultadesService.getActive();
   */
  async getActive() {
    const resumen = await this.getSummary();
    return resumen.filter((f) => f.total_cursos > 0 || f.total_profesores > 0);
  },

  /**
   * Obtener estadísticas globales de facultades
   * 
   * Calcula estadísticas agregadas de todas las facultades.
   * 
   * @async
   * @returns {Promise<Object>} Estadísticas globales
   * @returns {number} return.total_facultades - Total de facultades
   * @returns {number} return.total_programas - Suma de todos los programas
   * @returns {number} return.total_cursos - Suma de todos los cursos
   * @returns {number} return.total_profesores - Suma de todos los profesores
   * @returns {number} return.promedio_cursos_por_facultad - Promedio de cursos
   * @returns {number} return.promedio_profesores_por_facultad - Promedio de profesores
   * 
   * @example
   * const stats = await facultadesService.getGlobalStatistics();
   * console.log(`Total de facultades: ${stats.total_facultades}`);
   */
  async getGlobalStatistics() {
    const resumen = await this.getSummary();
    const total_facultades = resumen.length;
    const total_programas = resumen.reduce((sum, f) => sum + f.total_programas, 0);
    const total_cursos = resumen.reduce((sum, f) => sum + f.total_cursos, 0);
    const total_profesores = resumen.reduce((sum, f) => sum + f.total_profesores, 0);

    return {
      total_facultades,
      total_programas,
      total_cursos,
      total_profesores,
      promedio_cursos_por_facultad: total_facultades > 0 ? Math.round(total_cursos / total_facultades) : 0,
      promedio_profesores_por_facultad:
        total_facultades > 0 ? Math.round(total_profesores / total_facultades) : 0,
    };
  },
};

export default facultadesService;
