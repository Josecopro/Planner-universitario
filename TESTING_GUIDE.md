# Guía de Prueba - Dashboard del Profesor con IA

## Requisitos Previos

1. **Base de datos con datos de prueba**:
   - Al menos un profesor registrado
   - Al menos un curso con grupos asignados
   - Actividades evaluativas creadas para los grupos
   - Entregas de estudiantes con calificaciones

2. **Configuración del entorno**:
   ```bash
   cd frontend
   cp .env.example .env
   # Editar .env con las credenciales reales
   npm install
   ```

3. **Variables de entorno** (en `frontend/.env`):
   ```env
   VITE_SUPABASE_URL=tu_url_de_supabase
   VITE_SUPABASE_ANON_KEY=tu_anon_key_de_supabase
   VITE_OPENROUTER_API_KEY=tu_api_key_de_openrouter  # Opcional
   ```

## Escenarios de Prueba

### Escenario 1: Ver Dashboard de un Grupo

**Objetivo**: Verificar que el dashboard muestra datos correctos de un grupo específico.

**Pasos**:
1. Iniciar sesión como profesor
2. Navegar a "Mis Cursos"
3. Seleccionar un curso
4. Ver la lista de grupos
5. Hacer clic en "Ver Dashboard del Grupo"

**Resultados esperados**:
- ✅ Se muestra el nombre del curso y semestre
- ✅ Las estadísticas muestran:
  - Número correcto de estudiantes activos
  - Promedio general calculado de calificaciones
  - Cantidad de entregas pendientes
  - Tasa de entrega en porcentaje
- ✅ Gráfico de progreso semanal muestra promedios de las últimas semanas
- ✅ Gráfico de distribución muestra categorías de calificaciones

### Escenario 2: Alertas con IA (Con API Key Configurada)

**Objetivo**: Verificar que se generan alertas con retroalimentación de IA.

**Prerequisitos**:
- API key de OpenRouter configurada en `.env`
- Grupo con al menos 3 estudiantes
- Al menos 2 actividades con calificaciones variadas

**Pasos**:
1. Navegar al dashboard de un grupo
2. Esperar a que aparezca "🤖 Generando análisis con IA..."
3. Observar las alertas generadas

**Resultados esperados**:
- ✅ Se muestra un análisis general del grupo generado por IA
- ✅ Se muestran alertas para estudiantes con bajo rendimiento (si existen)
- ✅ Las alertas contienen retroalimentación personalizada y constructiva
- ✅ Las alertas sugieren acciones concretas para el profesor

**Ejemplo de alerta esperada**:
```
🤖 Análisis General del Grupo (IA)
El grupo muestra un desempeño satisfactorio con un promedio de 4.1...
[Análisis detallado generado por IA]
```

### Escenario 3: Alertas sin IA (Sin API Key)

**Objetivo**: Verificar que el sistema funciona con retroalimentación de respaldo.

**Prerequisitos**:
- NO configurar VITE_OPENROUTER_API_KEY o dejarlo vacío

**Pasos**:
1. Navegar al dashboard de un grupo
2. Observar las alertas generadas

**Resultados esperados**:
- ✅ El dashboard carga normalmente
- ✅ Se muestran alertas con retroalimentación generada localmente
- ✅ Las alertas son coherentes y útiles
- ✅ No hay errores en la consola

### Escenario 4: Grupo sin Datos

**Objetivo**: Verificar el manejo de grupos sin actividades o entregas.

**Prerequisitos**:
- Grupo sin actividades evaluativas creadas

**Pasos**:
1. Navegar al dashboard de un grupo vacío

**Resultados esperados**:
- ✅ El dashboard carga sin errores
- ✅ Las estadísticas muestran valores en cero
- ✅ Los gráficos muestran mensaje de "No hay datos suficientes"
- ✅ Se muestra alerta: "No hay alertas - El grupo está funcionando bien"

### Escenario 5: Actualización de Datos

**Objetivo**: Verificar que el botón de actualizar recarga los datos.

**Pasos**:
1. Navegar al dashboard de un grupo
2. Hacer clic en el botón "🔄 Actualizar"
3. Observar que se vuelve a cargar la información

**Resultados esperados**:
- ✅ Aparece indicador de carga
- ✅ Los datos se actualizan
- ✅ Las alertas de IA se regeneran
- ✅ No hay errores en la consola

### Escenario 6: Cálculos de Estadísticas

**Objetivo**: Verificar la precisión de los cálculos estadísticos.

**Datos de prueba**:
- Grupo con 5 estudiantes
- 2 actividades creadas
- Total entregas esperadas: 5 × 2 = 10
- Entregas realizadas: 8
- Calificaciones: [4.5, 3.8, 4.2, 3.5, 4.0, 3.9, 4.3, 3.7]

**Cálculos esperados**:
- Promedio general: (4.5 + 3.8 + 4.2 + 3.5 + 4.0 + 3.9 + 4.3 + 3.7) / 8 = 4.0
- Tasa de entrega: (8 / 10) × 100 = 80%
- Entregas pendientes: 10 - 8 = 2

**Pasos**:
1. Crear el escenario de datos de prueba en la base de datos
2. Navegar al dashboard del grupo
3. Verificar las estadísticas mostradas

**Resultados esperados**:
- ✅ Promedio general: 4.0
- ✅ Tasa de entrega: 80%
- ✅ Entregas pendientes: 2

### Escenario 7: Distribución de Calificaciones

**Objetivo**: Verificar que el gráfico de distribución categoriza correctamente.

**Datos de prueba**:
- Calificaciones: [5.0, 4.7, 4.3, 3.8, 3.2, 4.9, 4.1, 3.6, 4.5, 3.0]

**Distribución esperada**:
- Excelente (4.5-5.0): 4 estudiantes (5.0, 4.7, 4.9, 4.5)
- Bueno (4.0-4.4): 2 estudiantes (4.3, 4.1)
- Aceptable (3.5-3.9): 3 estudiantes (3.8, 3.6, 3.6)
- Bajo (<3.5): 1 estudiante (3.2, 3.0)

**Pasos**:
1. Crear calificaciones de prueba
2. Ver el gráfico de distribución en el dashboard

**Resultados esperados**:
- ✅ El gráfico muestra las 4 categorías
- ✅ Los números coinciden con el cálculo manual
- ✅ Los colores son apropiados (verde para excelente, rojo para bajo)

## Pruebas de Integración

### Integración con OpenRouter API

**Verificar en consola del navegador**:
```javascript
// Debe mostrar:
✅ AI feedback generated successfully
// O en caso de error:
⚠️ OpenRouter API key not configured
```

### Verificar Llamadas a Supabase

**En la consola del navegador, debe mostrar**:
```
🔍 [dashboardApi] Obteniendo datos del dashboard para grupo: [ID]
✅ Grupo obtenido: {...}
✅ Actividades obtenidas: [...]
✅ Entregas obtenidas: [...]
✅ Calificaciones obtenidas: [...]
✅ Estudiantes obtenidos: [...]
✅ Estadísticas calculadas: {...}
```

## Casos de Error

### Error 1: Grupo No Existe

**Pasos**:
1. Navegar manualmente a `/dashboard/grupo/99999`

**Resultado esperado**:
- ✅ Mensaje de error claro
- ✅ Botón para reintentar
- ✅ No se rompe la aplicación

### Error 2: Error de Red

**Pasos**:
1. Desconectar la red mientras se carga el dashboard
2. Observar el comportamiento

**Resultado esperado**:
- ✅ Mensaje de error de red
- ✅ Opción para reintentar
- ✅ No hay excepciones no manejadas

### Error 3: API de OpenRouter Falla

**Pasos**:
1. Configurar un API key inválido
2. Observar el comportamiento

**Resultado esperado**:
- ✅ Se utiliza retroalimentación de respaldo
- ✅ No se rompe la funcionalidad
- ✅ Log de advertencia en consola

## Pruebas de Rendimiento

### Tiempo de Carga

**Objetivo**: El dashboard debe cargar en menos de 3 segundos.

**Medición**:
1. Abrir DevTools → Network
2. Navegar al dashboard
3. Medir tiempo hasta que aparece el contenido

**Resultado esperado**:
- ✅ Datos del grupo: < 1s
- ✅ Generación de alertas de IA: < 5s (depende de la API)
- ✅ Renderizado completo: < 3s (sin IA)

### Múltiples Alertas de IA

**Objetivo**: Verificar que no se hacen demasiadas llamadas a la API.

**Pasos**:
1. Abrir DevTools → Network
2. Navegar al dashboard
3. Contar llamadas a openrouter.ai

**Resultado esperado**:
- ✅ Máximo 4 llamadas por carga (1 análisis grupal + 3 estudiantes máx)
- ✅ No hay llamadas repetidas innecesarias

## Checklist de Validación Final

- [ ] Dashboard carga sin errores
- [ ] Todas las estadísticas son correctas
- [ ] Los gráficos muestran datos reales
- [ ] Las alertas de IA son útiles y coherentes
- [ ] El sistema funciona sin API key de OpenRouter
- [ ] Los enlaces de navegación funcionan correctamente
- [ ] No hay warnings críticos en la consola
- [ ] El diseño es responsive
- [ ] Los mensajes de error son claros
- [ ] La documentación es completa

## Notas para el Revisor

1. **Costos de API**: OpenRouter cobra por uso. Con los límites implementados (máx 3 alertas por estudiante), el costo es mínimo.

2. **Fallbacks**: El sistema está diseñado para funcionar completamente sin IA, usando retroalimentación generada localmente.

3. **Seguridad**: La API key nunca se expone en el código del cliente, solo se usa a través de variables de entorno.

4. **Performance**: Las consultas a Supabase están optimizadas para traer solo los datos necesarios.

## Solución de Problemas

### Problema: "No se especificó un grupo"
**Solución**: Navegar al dashboard desde la lista de grupos, no directamente.

### Problema: Estadísticas muestran 0
**Solución**: Verificar que el grupo tiene actividades y entregas en la base de datos.

### Problema: IA no genera feedback
**Solución**: Verificar que VITE_OPENROUTER_API_KEY está configurado correctamente en `.env`.

### Problema: Error 401 de OpenRouter
**Solución**: Verificar que la API key es válida y tiene créditos disponibles.
