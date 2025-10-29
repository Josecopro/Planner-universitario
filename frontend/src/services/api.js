/**
 * API y hooks principales - Planner Universitario
 * 
 * Exporta los principales servicios y hooks utilizados por los componentes.
 * Sirve como punto de entrada unificado para la lógica de API.
 */

import { useState, useEffect } from 'react';
import actividadesEvaluativasService from './actividades-evaluativas.service';
import estudiantesService from './estudiantes.service';
import cursosService from './cursos.service';
import gruposService from './grupos.service';

/**
 * Hook personalizado para consultas (data fetching)
 * Proporciona funcionalidad similar a React Query para operaciones de lectura
 * 
 * @param {Function} queryFn - Función que realiza la consulta
 * @param {Object} options - Opciones adicionales
 * @returns {Object} Estado de la consulta
 */
export const useApi = (queryFn, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    if (!queryFn) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await queryFn();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const refetch = () => {
    fetchData();
  };

  return {
    data,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook personalizado para mutaciones
 * Proporciona funcionalidad similar a React Query para operaciones de escritura
 * 
 * @param {Function} mutationFn - Función que realiza la mutación
 * @returns {Object} Estado y función de mutación
 */
export const useMutation = (mutationFn) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const mutate = async (variables) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await mutationFn(variables);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    mutate,
    loading,
    error,
    data,
  };
};

/**
 * API para actividades (alias para actividades evaluativas)
 * Mantiene compatibilidad con el componente CrearActividad
 */
export const activitiesApi = {
  /**
   * Crear nueva actividad
   * @param {Object} activityData - Datos de la actividad
   * @returns {Promise<Object>} Actividad creada
   */
  create: (activityData) => actividadesEvaluativasService.create(activityData),
  
  /**
   * Obtener todas las actividades
   * @param {Object} params - Parámetros de filtrado
   * @returns {Promise<Array>} Lista de actividades
   */
  getAll: (params) => actividadesEvaluativasService.getAll(params),
  
  /**
   * Obtener actividad por ID
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Datos de la actividad
   */
  getById: (id) => actividadesEvaluativasService.getById(id),
  
  /**
   * Actualizar actividad
   * @param {number} id - ID de la actividad
   * @param {Object} activityData - Datos a actualizar
   * @returns {Promise<Object>} Actividad actualizada
   */
  update: (id, activityData) => actividadesEvaluativasService.update(id, activityData),
  
  /**
   * Eliminar actividad
   * @param {number} id - ID de la actividad
   * @returns {Promise<Object>} Confirmación
   */
  delete: (id) => actividadesEvaluativasService.delete(id),
  
  /**
   * Obtener actividades por grupo
   * @param {number} grupoId - ID del grupo
   * @param {string} estado - Estado a filtrar
   * @returns {Promise<Array>} Actividades del grupo
   */
  getByGrupo: (grupoId, estado) => actividadesEvaluativasService.getByGrupo(grupoId, estado),
};

/**
 * API para estudiantes
 */
export const studentsApi = {
  /**
   * Obtener todos los estudiantes
   * @param {Object} params - Parámetros de filtrado
   * @returns {Promise<Array>} Lista de estudiantes
   */
  getAll: (params) => estudiantesService.getAll(params),
  
  /**
   * Crear nuevo estudiante
   * @param {Object} studentData - Datos del estudiante
   * @returns {Promise<Object>} Estudiante creado
   */
  create: (studentData) => estudiantesService.create(studentData),
  
  /**
   * Obtener estudiante por ID
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Datos del estudiante
   */
  getById: (id) => estudiantesService.getById(id),
  
  /**
   * Actualizar estudiante
   * @param {number} id - ID del estudiante
   * @param {Object} studentData - Datos a actualizar
   * @returns {Promise<Object>} Estudiante actualizado
   */
  update: (id, studentData) => estudiantesService.update(id, studentData),
  
  /**
   * Eliminar estudiante
   * @param {number} id - ID del estudiante
   * @returns {Promise<Object>} Confirmación
   */
  delete: (id) => estudiantesService.delete(id),
};

/**
 * API para dashboard
 */
export const dashboardApi = {
  /**
   * Obtener datos del dashboard
   * @returns {Promise<Object>} Datos del dashboard
   */
  getData: async () => {
    // Simular llamada de datos del dashboard combinando diferentes servicios
    try {
      const [activities, students, courses] = await Promise.all([
        actividadesEvaluativasService.getAll(),
        estudiantesService.getAll(),
        cursosService.getAll(),
      ]);
      
      return {
        activities: activities || [],
        students: students || [],
        courses: courses || [],
        stats: {
          totalActivities: activities?.length || 0,
          totalStudents: students?.length || 0,
          totalCourses: courses?.length || 0,
        }
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  },
};

// Exportar por defecto el objeto completo
export default {
  useApi,
  useMutation,
  activitiesApi,
  studentsApi,
  dashboardApi,
};