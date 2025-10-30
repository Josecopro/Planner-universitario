// Funciones helper para consultas a Supabase relacionadas con el profesor
import { supabase } from '../config/supabase';

/**
 * Obtiene el perfil de profesor basado en el correo del usuario
 */
export const getProfesorByCorreo = async (correo) => {
  console.log('🔍 [supabase-queries] Buscando profesor con correo:', correo);
  
  // Primero buscar el usuario por correo
  const { data: usuario, error: userError } = await supabase
    .from('usuarios')
    .select('id, nombre, apellido, correo')
    .eq('correo', correo)
    .single();

  if (userError) {
    console.error('❌ Error al buscar usuario:', userError);
    throw userError;
  }

  console.log('✅ Usuario encontrado:', usuario);

  // Luego buscar el perfil de profesor con usuario_id
  const { data: profesor, error: profError } = await supabase
    .from('profesor')
    .select('id, facultad_id, titulo_academico')
    .eq('usuario_id', usuario.id)
    .single();

  if (profError) {
    console.error('❌ Error al buscar profesor:', profError);
    throw profError;
  }

  console.log('✅ Profesor encontrado:', profesor);
  
  return {
    ...usuario,
    profesor: profesor
  };
};

/**
 * Obtiene los cursos de un profesor incluyendo sus grupos
 */
export const getCursosProfesor = async (profesorId) => {
  console.log('🔍 [supabase-queries] Obteniendo cursos para profesor ID:', profesorId);
  
  // Primero obtener TODOS los cursos disponibles
  const { data: cursos, error: cursosError } = await supabase
    .from('curso')
    .select('id, codigo, nombre, facultad_id');

  if (cursosError) {
    console.error('❌ Error al obtener cursos:', cursosError);
    throw cursosError;
  }

  console.log('✅ Todos los cursos disponibles:', cursos);
  
  // Luego obtener los grupos que pertenecen a este profesor
  const { data: grupos, error: gruposError } = await supabase
    .from('grupo')
    .select('id, curso_id, semestre, cupo_maximo, cupo_actual, estado')
    .eq('profesor_id', profesorId);

  if (gruposError) {
    console.error('❌ Error al obtener grupos:', gruposError);
    throw gruposError;
  }

  console.log('✅ Grupos del profesor encontrados:', grupos);
  
  // Filtrar solo los cursos que tienen grupos del profesor
  const cursosConGrupos = (cursos || [])
    .map(curso => {
      const gruposDelCurso = (grupos || []).filter(g => g.curso_id === curso.id);
      
      if (gruposDelCurso.length === 0) return null;
      
      return {
        id: curso.id,
        code: curso.codigo,
        name: curso.nombre,
        facultad_id: curso.facultad_id,
        grupos: gruposDelCurso.map(g => ({
          id: g.id,
          semestre: g.semestre,
          cupo_maximo: g.cupo_maximo,
          cupo_actual: g.cupo_actual,
          estado: g.estado
        }))
      };
    })
    .filter(c => c !== null);

  console.log('✅ Cursos con grupos del profesor:', cursosConGrupos);
  
  return cursosConGrupos;
};

/**
 * Obtiene los grupos de un curso con información detallada
 */
export const getGruposCurso = async (cursoId) => {
  console.log('🔍 [supabase-queries] Obteniendo grupos para curso:', cursoId);
  
  const { data, error } = await supabase
    .from('grupo')
    .select(`
      id,
      semestre,
      cupo_maximo,
      cupo_actual,
      estado,
      horario(
        id,
        dia,
        hora_inicio,
        hora_fin,
        salon
      )
    `)
    .eq('curso_id', cursoId);

  if (error) {
    console.error('❌ Error al obtener grupos:', error);
    throw error;
  }

  console.log('✅ Grupos obtenidos:', data);

  // Obtener estudiantes matriculados para cada grupo
  const gruposConEstudiantes = await Promise.all(
    (data || []).map(async (g) => {
      // Buscar matriculas para este grupo
      const { data: matriculas, error: matError } = await supabase
        .from('matricula')
        .select(`
          id,
          estudiante_id,
          fecha_matricula,
          usuarios!estudiante_id (
            id,
            nombre,
            apellido,
            correo
          )
        `)
        .eq('grupo_id', g.id);

      if (matError) {
        console.error('❌ Error al obtener matriculas:', matError);
      }

      console.log(`✅ Matriculas para grupo ${g.id}:`, matriculas);

      return {
        id: g.id,
        name: `Grupo ${g.semestre}`,
        semestre: g.semestre,
        cupo_maximo: g.cupo_maximo,
        cupo_actual: g.cupo_actual,
        estado: g.estado,
        schedule: g.horario?.map(h => 
          `${h.dia} ${h.hora_inicio}-${h.hora_fin} (${h.salon || 'Sin asignar'})`
        ).join(', ') || 'Sin horario',
        estudiantes: (matriculas || []).map(m => ({
          id: m.estudiante_id,
          nombre: m.usuarios.nombre,
          apellido: m.usuarios.apellido,
          correo: m.usuarios.correo,
          fecha_matricula: m.fecha_matricula
        }))
      };
    })
  );

  console.log('✅ Grupos con estudiantes:', gruposConEstudiantes);
  
  return gruposConEstudiantes;
};

/**
 * Obtiene las actividades evaluativas de un grupo
 */
export const getActividadesGrupo = async (grupoIds) => {
  console.log('🔍 [supabase-queries] Obteniendo actividades para grupos:', grupoIds);
  
  const { data, error } = await supabase
    .from('actividadevaluativa')
    .select(`
      id,
      titulo,
      descripcion,
      estado,
      fecha_entrega,
      tipo,
      prioridad,
      porcentaje,
      grupo_id
    `)
    .in('grupo_id', grupoIds);

  if (error) {
    console.error('❌ Error al obtener actividades:', error);
    throw error;
  }

  console.log('✅ Actividades encontradas:', data);
  return data || [];
};

/**
 * Obtiene datos completos del dashboard de un curso
 */
export const getDashboardCurso = async (cursoId, correo) => {
  console.log('🔍 [supabase-queries] Obteniendo dashboard para curso:', cursoId);
  
  try {
    // Obtener grupos del curso
    const grupos = await getGruposCurso(cursoId);
    
    // Obtener actividades de todos los grupos
    const grupoIds = grupos.map(g => g.id);
    const actividades = grupoIds.length > 0 ? await getActividadesGrupo(grupoIds) : [];
    
    // Calcular estadísticas
    const totalEstudiantes = grupos.reduce((sum, g) => sum + g.cupo_actual, 0);
    const totalActividades = actividades.length;
    const actividadesPendientes = actividades.filter(a => a.estado === 'Abierta').length;

    const dashboardData = {
      curso_id: cursoId,
      grupos: grupos,
      actividades: actividades,
      estadisticas: {
        totalGrupos: grupos.length,
        totalEstudiantes,
        totalActividades,
        actividadesPendientes
      }
    };

    console.log('✅ Dashboard completo:', dashboardData);
    return dashboardData;
  } catch (error) {
    console.error('❌ Error al obtener dashboard:', error);
    throw error;
  }
};
