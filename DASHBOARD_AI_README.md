# Dashboard del Profesor con Retroalimentación de IA

## Descripción

Esta actualización mejora el dashboard del profesor con las siguientes funcionalidades:

1. **Dashboard por Grupo**: El dashboard ahora muestra datos específicos de un grupo particular, incluyendo:
   - Estadísticas de estudiantes activos
   - Promedio general de calificaciones
   - Entregas pendientes
   - Tasa de entrega del grupo

2. **Visualización de Datos Reales**: 
   - Gráficos de progreso semanal basados en calificaciones
   - Distribución de calificaciones del grupo
   - Todos los datos provienen de entregas y calificaciones reales

3. **Alertas y Notificaciones con IA**:
   - Análisis general del grupo generado por IA
   - Alertas automáticas para estudiantes con bajo rendimiento
   - Retroalimentación personalizada usando OpenRouter API
   - Sugerencias y recomendaciones para el profesor

## Configuración

### Variables de Entorno

Crear un archivo `.env` en el directorio `frontend/` basado en `.env.example`:

```env
# OpenRouter API Configuration
VITE_OPENROUTER_API_KEY=tu_api_key_de_openrouter

# Supabase Configuration
VITE_SUPABASE_URL=tu_url_de_supabase
VITE_SUPABASE_ANON_KEY=tu_anon_key_de_supabase
```

### Obtener API Key de OpenRouter

1. Visitar [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Crear una cuenta o iniciar sesión
3. Generar una nueva API key
4. Copiar la key y agregarla al archivo `.env`

**Nota**: Si no se configura la API key de OpenRouter, el sistema utilizará retroalimentación generada localmente sin IA.

## Estructura de Archivos

```
frontend/src/
├── services/
│   ├── openrouter.service.js    # Servicio de integración con OpenRouter
│   └── api.js                    # Actualizado con dashboardApi
└── pages/
    └── Dashboard/
        ├── Dashboard.jsx         # Componente actualizado con IA
        └── Dashboard.scss        # Estilos actualizados
```

## Uso

### Navegar al Dashboard de un Grupo

1. Desde **Mis Cursos**, seleccionar un curso
2. Ver los grupos disponibles
3. Hacer clic en "Ver Dashboard del Grupo" para cualquier grupo
4. El dashboard mostrará:
   - Estadísticas del grupo
   - Gráficos de rendimiento
   - Alertas y notificaciones con análisis de IA

### Funcionalidades de IA

El sistema de IA analiza automáticamente:

- **Desempeño del grupo**: Analiza el promedio general, tasa de entrega y tendencias
- **Estudiantes con bajo rendimiento**: Identifica estudiantes que necesitan atención especial
- **Retroalimentación personalizada**: Genera comentarios específicos para cada situación
- **Recomendaciones para el profesor**: Sugiere acciones concretas

## API del Dashboard

### `dashboardApi.getDataByGroup(grupoId)`

Obtiene todos los datos del dashboard para un grupo específico:

```javascript
const data = await dashboardApi.getDataByGroup(grupoId);

// Retorna:
{
  grupo: { id, semestre, curso, ... },
  estudiantes: [...],
  actividades: [...],
  entregas: [...],
  calificaciones: [...],
  stats: {
    active_students: number,
    general_average: number,
    pending_submissions: number,
    submission_rate: number,
    weekly_progress: [...],
    grade_distribution: [...]
  }
}
```

## Servicios de IA

### `generatePerformanceFeedback(data)`

Genera retroalimentación para el desempeño de un estudiante:

```javascript
const feedback = await generatePerformanceFeedback({
  estudiante: "Juan Pérez",
  actividad: "Tarea 1",
  calificacion: 3.5,
  promedio_grupo: 4.2
});
```

### `generateGroupInsights(groupData)`

Genera análisis general del grupo:

```javascript
const insights = await generateGroupInsights({
  nombre_grupo: "Programación I - 2025-1",
  total_estudiantes: 25,
  promedio_general: 4.1,
  tasa_entrega: 85,
  actividades_completadas: 8,
  actividades_totales: 10
});
```

## Estadísticas Calculadas

- **Promedio General**: Promedio de todas las calificaciones del grupo
- **Tasa de Entrega**: Porcentaje de entregas realizadas vs esperadas
- **Entregas Pendientes**: Número de entregas que faltan
- **Progreso Semanal**: Promedio de calificaciones por semana (últimas 4 semanas)
- **Distribución de Calificaciones**: Cantidad de estudiantes en cada rango (Excelente, Bueno, Aceptable, Bajo)

## Consideraciones de Seguridad

- La API key de OpenRouter nunca se expone en el código del cliente
- Todas las consultas a la base de datos usan los permisos configurados en Supabase
- Los datos personales de estudiantes solo son visibles para profesores autorizados

## Mejoras Futuras

- Cache de respuestas de IA para reducir costos
- Configuración de umbrales de alerta personalizables
- Exportación de reportes en PDF
- Integración con sistema de notificaciones por email
- Análisis de tendencias a largo plazo
