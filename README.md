# 📚 Planner Universitario - Dashboard del Profesor con IA

Sistema de gestión académica con dashboard inteligente para profesores que utiliza IA para analizar el desempeño estudiantil y generar retroalimentación personalizada.

## 🆕 Nueva Característica: Dashboard con IA

Se ha implementado un dashboard mejorado para profesores que:

- 📊 Muestra datos reales de entregas y calificaciones por grupo
- 🤖 Genera retroalimentación inteligente usando IA (OpenRouter API)
- 📈 Visualiza estadísticas y tendencias del grupo
- ⚠️ Identifica estudiantes en riesgo automáticamente
- 💡 Proporciona recomendaciones concretas

## 📖 Documentación

Toda la información está organizada en documentos específicos:

### 🚀 Para Empezar Rápido
- **[EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** - Resumen ejecutivo completo (5 min de lectura)

### 👨‍💻 Para Desarrolladores
- **[DASHBOARD_AI_README.md](./DASHBOARD_AI_README.md)** - Documentación técnica completa
  - APIs y funciones
  - Configuración detallada
  - Ejemplos de código

### 🧪 Para Testers/QA
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Guía completa de pruebas
  - 7 escenarios de prueba
  - Casos de error
  - Checklist de validación

### 🏗️ Para Arquitectos
- **[IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md)** - Notas de implementación
  - Estructura de datos
  - Decisiones técnicas
  - Mejoras futuras

### 📊 Para Visualización
- **[VISUAL_SUMMARY.md](./VISUAL_SUMMARY.md)** - Resumen visual
  - Diagramas de flujo
  - Arquitectura del sistema
  - Comparación antes/después

## ⚡ Quick Start

### 1. Instalación

```bash
cd frontend
npm install
```

### 2. Configuración

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Agregar:
```env
VITE_SUPABASE_URL=tu_url_de_supabase
VITE_SUPABASE_ANON_KEY=tu_anon_key

# Opcional - Para usar IA
VITE_OPENROUTER_API_KEY=tu_api_key
```

### 3. Ejecutar

```bash
npm run dev
```

## 🎯 Características Principales

### Dashboard por Grupo
- Acceso directo desde la lista de grupos
- Estadísticas en tiempo real
- Gráficos interactivos

### Alertas Inteligentes
- Análisis general del grupo con IA
- Identificación de estudiantes en riesgo
- Sugerencias personalizadas

### Estadísticas Automáticas
- Promedio general del grupo
- Tasa de entrega
- Distribución de calificaciones
- Progreso semanal

## 🛠️ Tecnologías

- **Frontend**: React 19 + Vite
- **Base de datos**: Supabase (PostgreSQL)
- **IA**: OpenRouter API (Claude 3.5 Sonnet)
- **Gráficos**: Recharts
- **Estilos**: SCSS

## 📁 Estructura del Proyecto

```
Planner-universitario/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard/          # Dashboard mejorado
│   │   ├── services/
│   │   │   ├── openrouter.service.js  # Integración IA (NUEVO)
│   │   │   └── api.js              # APIs del dashboard
│   │   └── ...
│   ├── .env.example                # Plantilla de configuración
│   └── package.json
│
├── DASHBOARD_AI_README.md          # Doc. técnica
├── TESTING_GUIDE.md                # Guía de pruebas
├── IMPLEMENTATION_NOTES.md         # Notas técnicas
├── VISUAL_SUMMARY.md               # Resumen visual
├── EXECUTIVE_SUMMARY.md            # Resumen ejecutivo
└── README.md                       # Este archivo
```

## 🔐 Seguridad

✅ **CodeQL Scan**: 0 vulnerabilidades encontradas  
✅ **Build**: Exitoso  
✅ **Linting**: Pasado  

- API keys en variables de entorno
- No hay datos sensibles en código
- Manejo robusto de errores

## 💰 Costos

### Con OpenRouter API (Opcional)
- ~$0.04 USD por carga de dashboard
- ~$40 USD/mes para 10 profesores (5 consultas/día)

### Sin OpenRouter (Gratis)
- Sistema funciona completamente sin IA
- Usa retroalimentación generada localmente
- Todas las características excepto análisis con IA

## 🎓 Uso

### Como Profesor:
1. Iniciar sesión
2. Ir a "Mis Cursos"
3. Seleccionar un curso
4. Ver lista de grupos
5. Clic en "Ver Dashboard del Grupo"
6. ¡Visualizar análisis completo con IA!

### Lo que verás:
- Estadísticas del grupo
- Gráficos de rendimiento
- Análisis generado por IA
- Alertas y recomendaciones

## 🤝 Contribuir

Este es un proyecto educativo. Para contribuir:

1. Fork el repositorio
2. Crear rama para tu feature
3. Hacer commit de cambios
4. Push a la rama
5. Abrir Pull Request

## 📞 Soporte

### Si algo no funciona:

1. Revisar documentación específica:
   - **Configuración** → EXECUTIVE_SUMMARY.md
   - **Pruebas** → TESTING_GUIDE.md
   - **Errores técnicos** → IMPLEMENTATION_NOTES.md

2. Verificar logs en consola del navegador

3. Revisar que `.env` esté configurado correctamente

## 🚀 Roadmap

### Implementado ✅
- Dashboard por grupo con datos reales
- Integración con OpenRouter API
- Alertas inteligentes con IA
- Estadísticas automáticas
- Visualizaciones interactivas

### Futuro 🔮
- Cache de respuestas de IA
- Exportación de reportes en PDF
- Notificaciones por email
- Análisis histórico
- Configuración personalizable

## 📜 Licencia

[Agregar licencia según corresponda]

## 👥 Autores

- Desarrollador principal: [Tu nombre]
- Contribuidores: Ver commits del repositorio

## 🙏 Agradecimientos

- OpenRouter por la API de IA
- Supabase por la infraestructura
- Comunidad de React

---

## 📊 Estado del Proyecto

**Versión**: 1.0.0 (Dashboard con IA)  
**Estado**: ✅ Producción Ready  
**Última actualización**: Noviembre 2025  

---

**Para comenzar, lee primero [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** 📖
