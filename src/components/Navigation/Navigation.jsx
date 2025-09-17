import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.scss';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Inicio', icon: '🏠' },
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/estudiantes', label: 'Estudiantes', icon: '👥' },
    { path: '/actividades', label: 'Actividades', icon: '📝' },
    { path: '/crear-actividad', label: 'Nueva Actividad', icon: '➕' },
    { path: '/chat', label: 'Chat', icon: '💬' },
    { path: '/configuracion', label: 'Configuración', icon: '⚙️' }
  ];

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h2>📚 Planner Universitario</h2>
      </div>
      
      <ul className="nav-menu">
        {navItems.map((item) => (
          <li key={item.path} className="nav-item">
            <Link 
              to={item.path} 
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      
      <div className="nav-footer">
        <p>Versión 1.0.0</p>
      </div>
    </nav>
  );
};

export default Navigation;
