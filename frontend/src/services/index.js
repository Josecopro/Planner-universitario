/**
 * Índice de Servicios - Planner Universitario
 * 
 * Archivo central que exporta todos los servicios de la aplicación.
 * Facilita la importación de servicios en los componentes.
 * 
 * @module services/index
 * 
 * Uso:
 * ```javascript
 * import { authService, estudiantesService } from '@/services';
 * 
 * // O importar todo
 * import * as services from '@/services';
 * ```
 * 
 * Servicios disponibles:
 * 
 * 1. authService - Autenticación y autorización (7 endpoints)
 * 2. usuariosService - Gestión de usuarios (22 endpoints)
 * 3. rolesService - Gestión de roles (10 endpoints)
 * 4. facultadesService - Gestión de facultades (11 endpoints)
 * 5. programasAcademicosService - Gestión de programas (14 endpoints)
 * 6. cursosService - Gestión de cursos (11 endpoints)
 * 7. profesoresService - Gestión de profesores (14 endpoints)
 * 8. estudiantesService - Gestión de estudiantes (15 endpoints)
 * 9. gruposService - Gestión de grupos (13 endpoints)
 * 10. horariosService - Gestión de horarios (13 endpoints)
 * 11. inscripcionesService - Gestión de inscripciones (17 endpoints)
 * 12. actividadesEvaluativasService - Actividades evaluativas (9 endpoints)
 * 13. entregasService - Gestión de entregas (10 endpoints)
 * 14. calificacionesService - Gestión de calificaciones (11 endpoints)
 * 15. asistenciasService - Control de asistencia (12 endpoints)
 * 
 * Total: 179 endpoints REST
 * 
 * Configuración:
 * - apiClient: Cliente Axios configurado
 * - tokenManager: Gestión de tokens JWT
 * - userManager: Gestión de datos del usuario
 * - apiConfig: Configuración general de la API
 */

export { default as apiClient, tokenManager, userManager, apiConfig } from './api.config';

export { default as authService } from './auth.service';

export { default as usuariosService } from './usuarios.service';

export { default as estudiantesService } from './estudiantes.service';

export { default as profesoresService } from './profesores.service';

export { default as gruposService } from './grupos.service';

export { default as actividadesEvaluativasService } from './actividades-evaluativas.service';

export { default as calificacionesService } from './calificaciones.service';

export { default as inscripcionesService } from './inscripciones.service';

export { default as rolesService } from './roles.service';

export { default as facultadesService } from './facultades.service';

export { default as programasAcademicosService } from './programas-academicos.service';

export { default as cursosService } from './cursos.service';

export { default as horariosService } from './horarios.service';

export { default as entregasService } from './entregas.service';

export { default as asistenciasService } from './asistencias.service';
