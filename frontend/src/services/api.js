// Minimal API aggregator used by pages. Provides small hooks and placeholder
// domain APIs so imports like `from '../../services/api'` resolve.
//
// This file intentionally keeps behaviour simple: it uses the browser fetch
// API to call conventional REST endpoints. Projects can replace these
// implementations with richer service clients (axios, supabase, etc.).

export function useApi(fetcher, deps = []) {
  // Very small hook-like contract (not a React hook to avoid forcing React import
  // in many files). Pages in this repo call useApi mainly as a convenience.
  // To keep things stable we return a function that runs the fetcher.
  return async (...args) => {
    if (typeof fetcher !== 'function') {
      throw new Error('useApi: fetcher must be a function');
    }
    return await fetcher(...args);
  };
}

export function useMutation(fn) {
  // Simple mutation helper that returns mutate() and loading state.
  let loading = false;

  const mutate = async (...args) => {
    loading = true;
    try {
      if (typeof fn === 'function') {
        const result = await fn(...args);
        loading = false;
        return result;
      }

      // If fn is not provided, try to use first arg as a function
      const maybeFn = args[0];
      if (typeof maybeFn === 'function') {
        const result = await maybeFn(...args.slice(1));
        loading = false;
        return result;
      }

      throw new Error('useMutation: no function provided to execute');
    } catch (err) {
      loading = false;
      throw err;
    }
  };

  return { mutate, get loading() { return loading; } };
}

const defaultHeaders = { 'Content-Type': 'application/json' };

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: defaultHeaders,
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  return res.json();
}

// Minimal activities API used by CrearActividad and Actividades pages.
export const activitiesApi = {
  create: async (data) => {
    // Try conventional backend route first; if it fails, store locally as fallback
    try {
      return await postJson('/api/actividades', data);
    } catch (err) {
      // Fallback: save draft locally so the UI can continue during development
      const drafts = JSON.parse(localStorage.getItem('local_actividades') || '[]');
      const item = { id: Date.now(), ...data };
      drafts.push(item);
      localStorage.setItem('local_actividades', JSON.stringify(drafts));
      return item;
    }
  },

  listLocal: () => {
    return JSON.parse(localStorage.getItem('local_actividades') || '[]');
  }
};

// Minimal students API placeholder
export const studentsApi = {
  getAll: async (grupoId = null) => {
    try {
      console.log('🔍 [studentsApi] Obteniendo lista de estudiantes desde matricula...');
      if (grupoId) {
        console.log('📌 [studentsApi] Filtrando por grupo:', grupoId);
      }
      
      const { supabase } = await import('../config/supabase');
      
      // Query basado en la estructura de matricula
      let query = supabase
        .from('matricula')
        .select(`
          id,
          estudiante_id,
          grupo_id,
          fecha_matricula,
          usuarios!estudiante_id (
            id,
            nombre,
            apellido,
            correo
          ),
          grupo!grupo_id (
            id,
            semestre,
            curso_id,
            curso!curso_id (
              nombre
            )
          )
        `);

      // Filtrar por grupo si se proporciona
      if (grupoId) {
        query = query.eq('grupo_id', grupoId);
      }

      const { data, error } = await query;

      if (error) {
        console.error('❌ Error al obtener estudiantes:', error);
        throw error;
      }

      console.log('✅ Estudiantes obtenidos desde matricula:', data);

      // Formatear los datos para la UI
      const estudiantes = (data || []).map(m => ({
        id: m.estudiante_id,
        name: `${m.usuarios.nombre} ${m.usuarios.apellido}`,
        email: m.usuarios.correo,
        career: m.grupo.curso?.nombre || 'Sin curso',
        semester: m.grupo.semestre,
        avatar: `${m.usuarios.nombre.charAt(0)}${m.usuarios.apellido.charAt(0)}`,
        status: 'active',
        matricula_id: m.id,
        grupo_id: m.grupo_id,
        fecha_matricula: m.fecha_matricula
      }));

      console.log('✅ Estudiantes formateados:', estudiantes);
      return estudiantes;
    } catch (err) {
      console.error('❌ Error en studentsApi.getAll:', err);
      return [];
    }
  },

  getByProfesor: async (correo) => {
    try {
      console.log('🔍 [studentsApi] Obteniendo estudiantes del profesor:', correo);
      
      const { supabase } = await import('../config/supabase');
      
      // Primero obtener el profesor
      const { data: usuario, error: userError } = await supabase
        .from('usuarios')
        .select('id')
        .eq('correo', correo)
        .single();

      if (userError || !usuario) {
        console.error('❌ Error al buscar usuario:', userError);
        return [];
      }

      const { data: profesor, error: profError } = await supabase
        .from('profesor')
        .select('id')
        .eq('usuario_id', usuario.id)
        .single();

      if (profError || !profesor) {
        console.error('❌ Error al buscar profesor:', profError);
        return [];
      }

      console.log('✅ Profesor ID:', profesor.id);

      // Obtener grupos del profesor
      const { data: grupos, error: gruposError } = await supabase
        .from('grupo')
        .select('id')
        .eq('profesor_id', profesor.id);

      if (gruposError) {
        console.error('❌ Error al obtener grupos:', gruposError);
        return [];
      }

      const grupoIds = (grupos || []).map(g => g.id);
      console.log('✅ Grupos del profesor:', grupoIds);

      if (grupoIds.length === 0) {
        console.warn('⚠️ El profesor no tiene grupos asignados');
        return [];
      }

      // Obtener estudiantes matriculados en esos grupos
      const { data: matriculas, error: matError } = await supabase
        .from('matricula')
        .select(`
          id,
          estudiante_id,
          grupo_id,
          fecha_matricula,
          usuarios!estudiante_id (
            id,
            nombre,
            apellido,
            correo
          ),
          grupo!grupo_id (
            id,
            semestre,
            curso_id,
            curso!curso_id (
              nombre
            )
          )
        `)
        .in('grupo_id', grupoIds);

      if (matError) {
        console.error('❌ Error al obtener matriculas:', matError);
        return [];
      }

      console.log('✅ Matriculas encontradas:', matriculas);

      // Formatear los datos
      const estudiantes = (matriculas || []).map(m => ({
        id: m.estudiante_id,
        name: `${m.usuarios.nombre} ${m.usuarios.apellido}`,
        email: m.usuarios.correo,
        career: m.grupo.curso?.nombre || 'Sin curso',
        semester: m.grupo.semestre,
        avatar: `${m.usuarios.nombre.charAt(0)}${m.usuarios.apellido.charAt(0)}`,
        status: 'active',
        matricula_id: m.id,
        grupo_id: m.grupo_id,
        fecha_matricula: m.fecha_matricula
      }));

      console.log('✅ Estudiantes del profesor formateados:', estudiantes);
      return estudiantes;
    } catch (err) {
      console.error('❌ Error en studentsApi.getByProfesor:', err);
      return [];
    }
  },

  delete: async (id) => {
    try {
      console.log('🗑️ [studentsApi] Eliminando estudiante:', id);
      
      const { supabase } = await import('../config/supabase');
      
      const { error } = await supabase
        .from('matricula')
        .delete()
        .eq('estudiante_id', id);

      if (error) {
        console.error('❌ Error al eliminar estudiante:', error);
        throw error;
      }

      console.log('✅ Estudiante eliminado correctamente');
      return true;
    } catch (err) {
      console.error('❌ Error en studentsApi.delete:', err);
      throw err;
    }
  }
};

// Minimal courses API to support professor flows (MisCursos -> Grupos -> Curso Dashboard)
import { 
  getProfesorByCorreo, 
  getCursosProfesor, 
  getGruposCurso, 
  getDashboardCurso 
} from './supabase-queries';

export const coursesApi = {
  listForProfesor: async (correo) => {
    try {
      console.log('🔍 [coursesApi] Buscando cursos para profesor con correo:', correo);
      
      // Obtener el perfil del profesor usando correo -> usuarios.id -> profesor.usuario_id
      const profesor = await getProfesorByCorreo(correo);
      const profesorId = profesor.profesor.id;
      
      console.log('✅ [coursesApi] Profesor ID:', profesorId);
      
      // Obtener cursos (todos) y grupos (filtrados por profesor_id)
      const cursos = await getCursosProfesor(profesorId);
      console.log('✅ [coursesApi] Cursos obtenidos:', cursos);
      
      return cursos;
    } catch (err) {
      console.error('❌ Error en listForProfesor:', err);
      // Fallback sample data for development
      return [
        { id: 'c1', name: 'Programación I', code: 'PROG101', grupos: [] },
        { id: 'c2', name: 'Cálculo I', code: 'CALC101', grupos: [] }
      ];
    }
  },

  groupsForCourse: async (courseId, correo) => {
    try {
      console.log('🔍 [coursesApi] Buscando grupos para curso:', courseId);
      
      const grupos = await getGruposCurso(courseId);
      console.log('✅ [coursesApi] Grupos obtenidos:', grupos);
      
      return grupos;
    } catch (err) {
      console.error('❌ Error en groupsForCourse:', err);
      // Fallback sample groups
      return [
        { id: `${courseId}-g1`, name: 'Grupo A', semestre: '2025-1', schedule: 'Lun 8:00-10:00', estudiantes: [] },
        { id: `${courseId}-g2`, name: 'Grupo B', semestre: '2025-1', schedule: 'Mie 10:00-12:00', estudiantes: [] }
      ];
    }
  },

  getDashboardData: async (courseId, correo) => {
    try {
      console.log('🔍 [coursesApi] Obteniendo dashboard para curso:', courseId);
      
      const dashboardData = await getDashboardCurso(courseId, correo);
      console.log('✅ [coursesApi] Dashboard obtenido:', dashboardData);
      
      return dashboardData;
    } catch (err) {
      console.error('❌ Error en getDashboardData:', err);
      return {
        curso_id: courseId,
        grupos: [],
        actividades: [],
        estadisticas: {
          totalGrupos: 0,
          totalEstudiantes: 0,
          totalActividades: 0,
          actividadesPendientes: 0
        }
      };
    }
  }
};

// Export a small default object for consumers that use default import
export default {
  useApi,
  useMutation,
  activitiesApi,
  studentsApi
};
