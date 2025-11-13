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
    try {
      console.log('📝 [activitiesApi] Creando nueva actividad:', data);
      
      const { supabase } = await import('../config/supabase');
      
      // Mapear campos del frontend a la estructura de la BD
      const actividadData = {
        grupo_id: data.grupo_id,
        titulo: data.titulo,
        descripcion: data.descripcion,
        fecha_entrega: data.fecha_entrega,
        tipo: data.tipo || 'Tarea',
        prioridad: data.prioridad || 'Media',
        estado: 'Programada',
        porcentaje: data.porcentaje || 0.0
      };

      const { data: actividad, error } = await supabase
        .from('actividadevaluativa')
        .insert([actividadData])
        .select()
        .single();

      if (error) {
        console.error('❌ Error al crear actividad:', error);
        throw error;
      }

      console.log('✅ Actividad creada:', actividad);
      return actividad;
    } catch (err) {
      console.error('❌ Error en activitiesApi.create:', err);
      throw err;
    }
  },

  getAll: async (grupoId = null) => {
    try {
      console.log('🔍 [activitiesApi] Obteniendo actividades...');
      
      const { supabase } = await import('../config/supabase');
      
      let query = supabase
        .from('actividadevaluativa')
        .select(`
          *,
          grupo:grupo_id (
            id,
            semestre,
            curso:curso_id (
              codigo,
              nombre
            )
          )
        `)
        .order('fecha_entrega', { ascending: true });

      if (grupoId) {
        query = query.eq('grupo_id', grupoId);
      }

      const { data, error } = await query;

      if (error) {
        console.error('❌ Error al obtener actividades:', error);
        throw error;
      }

      console.log('✅ Actividades obtenidas:', data);
      return data || [];
    } catch (err) {
      console.error('❌ Error en activitiesApi.getAll:', err);
      return [];
    }
  },

  getByProfesor: async (correo) => {
    try {
      console.log('🔍 [activitiesApi] Obteniendo actividades del profesor:', correo);
      
      const { supabase } = await import('../config/supabase');
      
      // Obtener el usuario
      const { data: usuario, error: userError } = await supabase
        .from('usuarios')
        .select('id')
        .eq('correo', correo)
        .single();

      if (userError || !usuario) {
        console.error('❌ Error al buscar usuario:', userError);
        return [];
      }

      // Obtener el profesor
      const { data: profesor, error: profError } = await supabase
        .from('profesor')
        .select('id')
        .eq('usuario_id', usuario.id)
        .single();

      if (profError || !profesor) {
        console.error('❌ Error al buscar profesor:', profError);
        return [];
      }

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
        return [];
      }

      // Obtener actividades de esos grupos
      const { data: actividades, error: actError } = await supabase
        .from('actividadevaluativa')
        .select(`
          *,
          grupo:grupo_id (
            id,
            semestre,
            curso:curso_id (
              codigo,
              nombre
            )
          )
        `)
        .in('grupo_id', grupoIds)
        .order('fecha_entrega', { ascending: true });

      if (actError) {
        console.error('❌ Error al obtener actividades:', actError);
        return [];
      }

      console.log('✅ Actividades del profesor:', actividades);
      return actividades || [];
    } catch (err) {
      console.error('❌ Error en activitiesApi.getByProfesor:', err);
      return [];
    }
  },

  update: async (id, data) => {
    try {
      console.log('✏️ [activitiesApi] Actualizando actividad:', id, data);
      
      const { supabase } = await import('../config/supabase');
      
      // Mapear campos del frontend a la estructura de la BD
      const actividadData = {
        grupo_id: data.grupo_id,
        titulo: data.titulo,
        descripcion: data.descripcion,
        fecha_entrega: data.fecha_entrega,
        tipo: data.tipo || 'Tarea',
        prioridad: data.prioridad || 'Media',
        estado: data.estado || 'Programada',
        porcentaje: data.porcentaje || 0.0
      };

      const { data: actividad, error } = await supabase
        .from('actividadevaluativa')
        .update(actividadData)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('❌ Error al actualizar actividad:', error);
        throw error;
      }

      console.log('✅ Actividad actualizada:', actividad);
      return actividad;
    } catch (err) {
      console.error('❌ Error en activitiesApi.update:', err);
      throw err;
    }
  },

  delete: async (id) => {
    try {
      console.log('🗑️ [activitiesApi] Eliminando actividad:', id);
      
      const { supabase } = await import('../config/supabase');
      
      const { error } = await supabase
        .from('actividadevaluativa')
        .delete()
        .eq('id', id);

      if (error) {
        console.error('❌ Error al eliminar actividad:', error);
        throw error;
      }

      console.log('✅ Actividad eliminada correctamente');
      return true;
    } catch (err) {
      console.error('❌ Error en activitiesApi.delete:', err);
      throw err;
    }
  },

  update: async (id, data) => {
    try {
      console.log('✏️ [activitiesApi] Actualizando actividad:', id, data);
      
      const { supabase } = await import('../config/supabase');
      
      // Construir objeto de actualización
      const updateData = {
        titulo: data.titulo,
        descripcion: data.descripcion,
        fecha_entrega: data.fecha_entrega,
        tipo: data.tipo,
        prioridad: data.prioridad,
        porcentaje: data.porcentaje
      };

      // Solo incluir grupo_id si se proporciona
      if (data.grupo_id !== undefined) {
        updateData.grupo_id = data.grupo_id;
      }

      const { data: actividad, error } = await supabase
        .from('actividadevaluativa')
        .update(updateData)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('❌ Error al actualizar actividad:', error);
        throw error;
      }

      console.log('✅ Actividad actualizada:', actividad);
      return actividad;
    } catch (err) {
      console.error('❌ Error en activitiesApi.update:', err);
      throw err;
    }
  },

  listLocal: () => {
    return JSON.parse(localStorage.getItem('local_actividades') || '[]');
  }
};

// API para manejar entregas de actividades
export const entregasApi = {
  getByActividad: async (actividadId) => {
    try {
      console.log('🔍 [entregasApi] Obteniendo entregas para actividad:', actividadId);
      
      const { supabase } = await import('../config/supabase');
      
      const { data, error } = await supabase
        .from('entrega')
        .select(`
          id,
          actividad_id,
          estudiante_id,
          grupo_id,
          fecha_entrega,
          estado,
          texto_entrega,
          archivos_adjuntos,
          estudiante:usuarios!entrega_estudiante_id_fkey (
            id,
            nombre,
            apellido,
            correo
          ),
          actividad:actividadevaluativa!fk_actividad_entrega (
            id,
            titulo
          ),
          grupo:grupo!entrega_grupo_id_fkey (
            id,
            semestre,
            curso:curso!fk_curso_grupo (
              codigo,
              nombre
            )
          )
        `)
        .eq('actividad_id', actividadId)
        .order('fecha_entrega', { ascending: false });

      if (error) {
        console.error('❌ Error al obtener entregas:', error);
        throw error;
      }

      console.log('✅ Entregas obtenidas desde BD:', data);
      
      // Obtener calificaciones para estas entregas
      const entregaIds = (data || []).map(e => e.id);
      let calificaciones = [];
      
      if (entregaIds.length > 0) {
        const { data: cals, error: calError } = await supabase
          .from('calificacion')
          .select('*')
          .in('entrega_id', entregaIds);
        
        if (!calError) {
          calificaciones = cals || [];
        }
      }

      console.log('✅ Calificaciones obtenidas:', calificaciones);
      
      // Formatear datos
      const entregas = (data || []).map(e => {
        const cal = calificaciones.find(c => c.entrega_id === e.id);
        
        return {
          id: e.id,
          actividad_id: e.actividad_id,
          estudiante_id: e.estudiante_id,
          grupo_id: e.grupo_id,
          fecha_entrega: e.fecha_entrega,
          estado: e.estado,
          texto_entrega: e.texto_entrega,
          archivos_adjuntos: e.archivos_adjuntos,
          estudiante: {
            id: e.estudiante.id,
            nombre: e.estudiante.nombre,
            apellido: e.estudiante.apellido,
            correo: e.estudiante.correo,
            nombre_completo: `${e.estudiante.nombre} ${e.estudiante.apellido}`
          },
          actividad: {
            id: e.actividad.id,
            titulo: e.actividad.titulo
          },
          grupo: e.grupo ? {
            id: e.grupo.id,
            semestre: e.grupo.semestre,
            curso: e.grupo.curso?.nombre || 'Sin curso'
          } : null,
          calificacion: cal ? {
            id: cal.id,
            nota: cal.nota,
            retroalimentacion: cal.retroalimentacion,
            fecha_calificacion: cal.fecha_calificacion
          } : null
        };
      });

      console.log('✅ Entregas formateadas:', entregas);
      return entregas;
    } catch (err) {
      console.error('❌ Error en entregasApi.getByActividad:', err);
      return [];
    }
  },

  calificar: async (entregaId, nota, retroalimentacion) => {
    try {
      console.log('📝 [entregasApi] Calificando entrega:', entregaId, nota);
      
      const { supabase } = await import('../config/supabase');
      
      // Verificar si ya existe una calificación
      const { data: existing, error: checkError } = await supabase
        .from('calificacion')
        .select('id')
        .eq('entrega_id', entregaId)
        .maybeSingle();

      if (checkError && checkError.code !== 'PGRST116') {
        console.error('❌ Error al verificar calificación:', checkError);
        throw checkError;
      }

      let result;
      
      if (existing) {
        // Actualizar calificación existente
        const { data, error } = await supabase
          .from('calificacion')
          .update({
            nota: nota,
            retroalimentacion: retroalimentacion,
            fecha_calificacion: new Date().toISOString()
          })
          .eq('entrega_id', entregaId)
          .select()
          .single();

        if (error) {
          console.error('❌ Error al actualizar calificación:', error);
          throw error;
        }
        
        result = data;
      } else {
        // Crear nueva calificación
        const { data, error } = await supabase
          .from('calificacion')
          .insert([{
            entrega_id: entregaId,
            nota: nota,
            retroalimentacion: retroalimentacion,
            fecha_calificacion: new Date().toISOString()
          }])
          .select()
          .single();

        if (error) {
          console.error('❌ Error al crear calificación:', error);
          throw error;
        }
        
        result = data;
      }

      console.log('✅ Calificación guardada:', result);
      return result;
    } catch (err) {
      console.error('❌ Error en entregasApi.calificar:', err);
      throw err;
    }
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

// API para gestión de usuarios (superadmin)
export const usuariosApi = {
  getAll: async () => {
    try {
      console.log('🔍 [usuariosApi] Obteniendo todos los usuarios...');
      
      const { supabase } = await import('../config/supabase');
      
      const { data, error } = await supabase
        .from('usuarios')
        .select(`
          id,
          nombre,
          apellido,
          correo,
          rol_id,
          activo,
          rol:rol_id (
            id,
            nombre
          )
        `)
        .order('id', { ascending: true });

      if (error) {
        console.error('❌ Error al obtener usuarios:', error);
        throw error;
      }

      // Formatear datos
      const usuarios = (data || []).map(u => ({
        id: u.id,
        nombre: u.nombre,
        apellido: u.apellido,
        correo: u.correo,
        rol_id: u.rol_id,
        rol_nombre: u.rol?.nombre || 'Sin rol',
        activo: u.activo
      }));

      console.log('✅ Usuarios obtenidos:', usuarios);
      return usuarios;
    } catch (err) {
      console.error('❌ Error en usuariosApi.getAll:', err);
      throw err;
    }
  },

  getRoles: async () => {
    try {
      console.log('🔍 [usuariosApi] Obteniendo roles...');
      
      const { supabase } = await import('../config/supabase');
      
      const { data, error } = await supabase
        .from('rol')
        .select('*')
        .order('id', { ascending: true });

      if (error) {
        console.error('❌ Error al obtener roles:', error);
        throw error;
      }

      console.log('✅ Roles obtenidos:', data);
      return data || [];
    } catch (err) {
      console.error('❌ Error en usuariosApi.getRoles:', err);
      throw err;
    }
  },

  create: async (userData) => {
    try {
      console.log('📝 [usuariosApi] Creando nuevo usuario:', userData);
      
      const { supabase } = await import('../config/supabase');
      
      const { data, error } = await supabase
        .from('usuarios')
        .insert([{
          nombre: userData.nombre,
          apellido: userData.apellido,
          correo: userData.correo,
          password: userData.password, // En producción, deberías hashear esto
          rol_id: userData.rol_id
        }])
        .select()
        .single();

      if (error) {
        console.error('❌ Error al crear usuario:', error);
        throw error;
      }

      console.log('✅ Usuario creado:', data);
      return data;
    } catch (err) {
      console.error('❌ Error en usuariosApi.create:', err);
      throw err;
    }
  },

  update: async (id, userData) => {
    try {
      console.log('✏️ [usuariosApi] Actualizando usuario:', id, userData);
      
      const { supabase } = await import('../config/supabase');
      
      const updateData = {
        nombre: userData.nombre,
        apellido: userData.apellido,
        correo: userData.correo,
        rol_id: userData.rol_id
      };

      // Solo incluir password si se proporciona
      if (userData.password) {
        updateData.password = userData.password;
      }

      const { data, error } = await supabase
        .from('usuarios')
        .update(updateData)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('❌ Error al actualizar usuario:', error);
        throw error;
      }

      console.log('✅ Usuario actualizado:', data);
      return data;
    } catch (err) {
      console.error('❌ Error en usuariosApi.update:', err);
      throw err;
    }
  },

  delete: async (id) => {
    try {
      console.log('🗑️ [usuariosApi] Eliminando usuario:', id);
      
      const { supabase } = await import('../config/supabase');
      
      const { error } = await supabase
        .from('usuarios')
        .delete()
        .eq('id', id);

      if (error) {
        console.error('❌ Error al eliminar usuario:', error);
        throw error;
      }

      console.log('✅ Usuario eliminado correctamente');
      return true;
    } catch (err) {
      console.error('❌ Error en usuariosApi.delete:', err);
      throw err;
    }
  }
};

// Export a small default object for consumers that use default import
export default {
  useApi,
  useMutation,
  activitiesApi,
  studentsApi,
  entregasApi,
  usuariosApi
};
