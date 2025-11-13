export const APP_PAGES = [
  { path: '/', label: 'Inicio', icon: '🏠', showInSidebar: false },
  { path: '/dashboard', label: 'Dashboard', icon: '📊', showInSidebar: true },
  { path: '/estudiantes', label: 'Estudiantes', icon: '👥', showInSidebar: true },
  { path: '/actividades', label: 'Actividades', icon: '📝', showInSidebar: true },
  { path: '/crear-actividad', label: 'Crear actividad', icon: '➕', showInSidebar: false },
  { path: '/usuarios', label: 'Usuarios', icon: '👤', showInSidebar: true, roleRequired: 1 },
  { path: '/chat', label: 'Chat', icon: '💬', showInSidebar: false },
  { path: '/configuracion', label: 'Configuración', icon: '⚙️', showInSidebar: false }
];

/**
 * Busca la página correspondiente a una ruta.
 * Intenta coincidir primero rutas exactas y luego rutas que comiencen igual.
 * pura confianza en dios :blessd:
 */
export const findPageByPath = (pathname) => {
  if (!pathname) {
    return null;
  }

  const exactMatch = APP_PAGES.find((page) => page.path === pathname);
  if (exactMatch) {
    return exactMatch;
  }

  return APP_PAGES.find((page) => pathname.startsWith(page.path));
};
