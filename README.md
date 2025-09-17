# 📚 Planner Universitario

Una aplicación web moderna para la gestión académica de estudiantes universitarios, desarrollada con React, React Router y Sass.

## 🚀 Características

### 📄 Páginas Principales

- **🏠 Inicio**: Página de bienvenida con información general
- **📊 Dashboard**: Panel principal con estadísticas y resumen de actividades
- **👥 Estudiantes**: Gestión de información de estudiantes
- **📝 Actividades**: Lista y gestión de tareas académicas
- **➕ Crear Actividad**: Formulario completo para crear nuevas actividades
- **💬 Chat**: Sistema de chat grupal para colaboración
- **⚙️ Configuración**: Panel de configuración de usuario y aplicación

### 🎨 Características de Diseño

- **Diseño Responsivo**: Se adapta perfectamente a todos los dispositivos
- **Navegación Intuitiva**: Sidebar con navegación clara y estados activos
- **Tema Moderno**: Paleta de colores profesional y consistente
- **Animaciones Suaves**: Transiciones y efectos hover elegantes
- **Componentes Reutilizables**: Arquitectura modular y escalable

## 🛠️ Tecnologías Utilizadas

- **React 19.1.1**: Framework principal
- **React Router DOM 7.9.1**: Enrutamiento con HashRouter
- **Sass**: Preprocesador CSS para estilos avanzados
- **Vite**: Herramienta de desarrollo rápida
- **React Hook Form**: Gestión de formularios

## 📁 Estructura del Proyecto

```
src/
├── components/
│   └── Navigation/
│       ├── Navigation.jsx
│       ├── Navigation.scss
│       └── index.js
├── pages/
│   ├── Inicio/
│   ├── Dashboard/
│   ├── Estudiantes/
│   ├── Chat/
│   ├── Actividades/
│   ├── CrearActividad/
│   ├── Configuracion/
│   └── index.js
├── App.jsx
├── App.css
├── main.jsx
└── index.css
```

## 🚀 Instalación y Uso

### Prerrequisitos
- Node.js (versión 16 o superior)
- npm o yarn

### Instalación
1. Clona o descarga el proyecto
2. Instala las dependencias:
   ```bash
   npm install
   ```

### Desarrollo
Para iniciar el servidor de desarrollo:
```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173` (o el siguiente puerto disponible).

### Construcción para Producción
```bash
npm run build
```

### Vista Previa de Producción
```bash
npm run preview
```

## 🌐 Navegación

La aplicación utiliza HashRouter, lo que significa que todas las rutas son accesibles directamente:

- `/#/` - Página de inicio
- `/#/dashboard` - Dashboard principal
- `/#/estudiantes` - Gestión de estudiantes
- `/#/actividades` - Lista de actividades
- `/#/crear-actividad` - Crear nueva actividad
- `/#/chat` - Chat grupal
- `/#/configuracion` - Configuración

## 📱 Responsividad

La aplicación se adapta a diferentes tamaños de pantalla:

- **Desktop (>1024px)**: Sidebar completo con labels
- **Tablet (768px-1024px)**: Sidebar compacto solo con iconos
- **Mobile (<768px)**: Sidebar oculto por defecto
