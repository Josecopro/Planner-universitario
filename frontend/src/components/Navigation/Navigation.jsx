import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { APP_PAGES } from '../../constants/navigation';
import './Navigation.scss';

const Navigation = () => {
  const location = useLocation();
  
  // Obtener el rol del usuario desde sessionStorage
  const userSession = JSON.parse(sessionStorage.getItem('user') || '{}');
  const userRole = userSession.rol_id;

  // Filtrar items basado en showInSidebar y roleRequired
  const navItems = APP_PAGES.filter((item) => {
    if (!item.showInSidebar) return false;
    
    // Si el item requiere un rol específico, verificar que el usuario tenga ese rol
    if (item.roleRequired !== undefined) {
      return userRole === item.roleRequired;
    }
    
    return true;
  });

  return (
    <nav className="navigation">
      <div className="navigation__header">
        <img className='navigation__logo' src="https://udemedellin.edu.co/wp-content/uploads/2022/10/logo_udemedellin2.png" alt="Universidad de Medellín" />
      </div>
  <hr />
      <ul className="navigation__menu">
        {navItems.map((item) => (
          <li key={item.path} className="navigation__item">
            <Link 
              to={item.path} 
              className={`navigation__link ${location.pathname === item.path ? 'navigation__link--active' : ''}`}
            >
              <span className="navigation__icon">{item.icon}</span>
              <span className="navigation__label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      
    </nav>
  );
};

export default Navigation;
