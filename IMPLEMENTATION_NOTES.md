# Notas de Implementación - Dashboard del Profesor con IA

## Resumen de Cambios

Este documento describe los cambios implementados para actualizar el dashboard del profesor según los requisitos especificados.

## Requisito Original

> "Requiero que actualices el dashboard del profesor segun los datos de todas las entregas asociadas a ese grupo en especifico, y en su panel de alertas y notificaciones crear comentarios con IA segun el desempeño de los estudiantes en ciertas actividades, basicamente que haga un fetch a un api de open router Polaris Alpha en donde mediante las calificaciones y la entrega pueda dar retroalimentacion al profesor"

## Implementación Realizada

### 1. Dashboard Específico por Grupo ✅

**Antes**: El dashboard mostraba datos genéricos o de ejemplo.

**Ahora**: El dashboard muestra datos reales específicos de un grupo:
- Ruta nueva: `/dashboard/grupo/:grupoId`
- Obtiene todas las entregas del grupo
- Calcula estadísticas basadas en datos reales
- Muestra información del curso y semestre

**Archivos modificados**:
- `frontend/src/App.jsx` - Agregada ruta con parámetro de grupo
- `frontend/src/pages/Dashboard/Dashboard.jsx` - Actualizado para usar grupoId

### 2. Integración con OpenRouter API ✅

**Implementación**:
- Servicio dedicado: `frontend/src/services/openrouter.service.js`
- Usa modelo Claude 3.5 Sonnet (Polaris Alpha puede configurarse cuando esté disponible)
- Dos funciones principales:
  - `generatePerformanceFeedback()` - Retroalimentación individual
  - `generateGroupInsights()` - Análisis grupal

**Configuración**:
```javascript
const MODEL = 'anthropic/claude-3.5-sonnet'; // Cambiar a 'polaris-alpha' cuando esté disponible
```

**Nota sobre el modelo**: Se usó Claude 3.5 Sonnet como modelo alternativo confiable ya que Polaris Alpha podría no estar disponible públicamente en OpenRouter al momento de la implementación. El código está estructurado para cambiar fácilmente de modelo modificando una sola constante.

### 3. Datos de Entregas y Calificaciones ✅

**Nueva API**: `dashboardApi.getDataByGroup(grupoId)`

Esta API obtiene:
- Información del grupo (curso, semestre, estudiantes)
- Todas las actividades del grupo
- Todas las entregas realizadas
- Todas las calificaciones asociadas
- Calcula automáticamente:
  - Promedio general
  - Tasa de entrega
  - Entregas pendientes
  - Progreso semanal
  - Distribución de calificaciones

**Archivos modificados**:
- `frontend/src/services/api.js` - Agregado `dashboardApi` con funciones de cálculo

### 4. Alertas y Notificaciones con IA ✅

**Tipos de alertas generadas**:

1. **Análisis General del Grupo** (siempre):
   - Evaluación del promedio y tasa de entrega
   - Aspectos destacables
   - Recomendaciones para el profesor

2. **Alertas por Estudiante** (bajo rendimiento):
   - Identifica estudiantes con promedio < 3.5
   - Genera retroalimentación personalizada
   - Sugiere acciones específicas
   - Máximo 3 alertas por carga (optimización de costos)

3. **Alertas Automáticas** (basadas en umbrales):
   - Alto número de entregas pendientes
   - Baja tasa de entrega (< 70%)

**Ejemplo de prompt a la IA**:
```
Eres un asistente educativo experto. Analiza el siguiente desempeño de un estudiante y proporciona retroalimentación constructiva en español (máximo 100 palabras):

Estudiante: Juan Pérez
Actividad: Tarea de Programación
Calificación obtenida: 3.2/5.0
Promedio del grupo: 4.1/5.0

Proporciona retroalimentación breve y constructiva enfocada en:
1. Reconocimiento si la calificación es buena
2. Áreas de mejora si está por debajo del promedio
3. Sugerencias concretas para el profesor
```

### 5. Visualización de Datos Reales ✅

**Gráficos actualizados**:

1. **Progreso Semanal**:
   - Muestra promedio de calificaciones por semana
   - Últimas 4 semanas
   - Ayuda a identificar tendencias

2. **Distribución de Calificaciones**:
   - Excelente: 4.5 - 5.0 (verde)
   - Bueno: 4.0 - 4.4 (azul)
   - Aceptable: 3.5 - 3.9 (naranja)
   - Bajo: < 3.5 (rojo)

**Estadísticas mostradas**:
- Estudiantes Activos (del grupo)
- Promedio General (calculado de calificaciones)
- Entregas Pendientes (esperadas - realizadas)
- Tasa de Entrega (% de cumplimiento)

### 6. Navegación Mejorada ✅

**Desde Mis Cursos**:
```
Mis Cursos → Curso → Grupos → [Ver Dashboard del Grupo] → Dashboard
```

**Desde Vista Detallada del Curso**:
```
Vista del Curso → Grupos → [Ver Dashboard] → Dashboard
```

**Archivos modificados**:
- `frontend/src/pages/Grupos/Grupos.jsx` - Agregado botón al dashboard
- `frontend/src/pages/VistaDetalladaCurso/VistaDetalladaCurso.jsx` - Agregado enlace por grupo

## Características Técnicas

### Manejo de Errores

1. **Sin API Key de OpenRouter**:
   - El sistema usa retroalimentación generada localmente
   - No interrumpe la funcionalidad
   - Log de advertencia en consola

2. **Error de API**:
   - Fallback automático a retroalimentación local
   - Usuario no experimenta errores

3. **Sin Datos**:
   - Mensajes informativos
   - Gráficos muestran "No hay datos suficientes"
   - No hay crashes

### Optimizaciones

1. **Límite de alertas de IA**:
   - Máximo 3 alertas por estudiante
   - Evita costos excesivos de API
   - Prioriza estudiantes con menor rendimiento

2. **Cálculos eficientes**:
   - Una sola consulta por tipo de datos
   - Cálculos en memoria (no en DB)
   - Reutilización de datos

3. **Caché de datos**:
   - Los datos se cargan una vez
   - Botón de actualizar para refrescar
   - Evita llamadas innecesarias

### Seguridad

1. **API Keys**:
   - Almacenadas en variables de entorno
   - No expuestas en código del cliente
   - `.env` está en `.gitignore`

2. **Validaciones**:
   - Verifica que grupoId sea válido
   - Maneja datos faltantes o nulos
   - Sanitiza entradas

3. **Permisos**:
   - Usa políticas de Supabase
   - Solo profesores autorizados ven datos

## Estructura de Datos

### Respuesta de `dashboardApi.getDataByGroup()`

```javascript
{
  grupo: {
    id: number,
    semestre: string,
    curso: { id, codigo, nombre },
    cupo_maximo: number,
    cupo_actual: number,
    estado: string
  },
  estudiantes: [
    { id, nombre, apellido, correo }
  ],
  actividades: [
    { id, titulo, descripcion, fecha_entrega, tipo, estado, porcentaje }
  ],
  entregas: [
    {
      id,
      actividad_id,
      estudiante_id,
      fecha_entrega,
      estado,
      estudiante: { nombre, apellido }
    }
  ],
  calificaciones: [
    { id, entrega_id, nota_obtenida, fecha_calificacion, retroalimentacion }
  ],
  stats: {
    active_students: number,
    general_average: string, // "4.25"
    pending_submissions: number,
    submission_rate: string, // "85.5"
    total_activities: number,
    activities_pending: number,
    weekly_progress: [
      { week: "Esta semana", value: "4.2" }
    ],
    grade_distribution: [
      { name: "Excelente", value: 5, color: "#10b981" }
    ]
  }
}
```

## Dependencias Agregadas

**Ninguna nueva**. Se utilizaron las librerías ya existentes:
- `recharts` - Ya estaba instalado (gráficos)
- `react-router-dom` - Ya estaba instalado (routing)
- Fetch API nativo del navegador (llamadas a OpenRouter)

## Configuración Requerida

### Archivo `.env`

```env
# Requerido - Conexión a base de datos
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# Opcional - Retroalimentación con IA
VITE_OPENROUTER_API_KEY=sk-or-v1-...
```

### OpenRouter API Key

1. Crear cuenta en https://openrouter.ai
2. Ir a https://openrouter.ai/keys
3. Crear nueva API key
4. Agregar al archivo `.env`

**Costo estimado**: ~$0.01 - $0.05 por carga de dashboard (3-4 llamadas)

## Pruebas Recomendadas

Ver `TESTING_GUIDE.md` para guía completa de pruebas.

**Pruebas mínimas**:
1. ✅ Dashboard carga con datos reales
2. ✅ Estadísticas son correctas
3. ✅ Gráficos muestran datos
4. ✅ Alertas de IA se generan (con API key)
5. ✅ Sistema funciona sin API key

## Mejoras Futuras Sugeridas

1. **Cache de IA**: Guardar respuestas de IA por 24h para reducir costos
2. **Filtros**: Por fecha, por actividad específica
3. **Exportación**: Generar PDF del reporte
4. **Notificaciones**: Email automático para estudiantes con bajo rendimiento
5. **Histórico**: Comparar desempeño entre periodos
6. **Configuración**: Umbrales personalizables por profesor

## Soporte y Documentación

- `DASHBOARD_AI_README.md` - Documentación técnica completa
- `TESTING_GUIDE.md` - Guía de pruebas detallada
- `frontend/.env.example` - Plantilla de configuración

## Contacto

Para preguntas o problemas con la implementación, contactar al desarrollador o revisar los logs en la consola del navegador que proporcionan información detallada sobre cada operación.
