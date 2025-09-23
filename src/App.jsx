import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation/Navigation';
import {
  Inicio,
  Dashboard,
  Estudiantes,
  Chat,
  Actividades,
  CrearActividad,
  Configuracion
} from './pages';
import './App.css';

function App() {
  const pagesWithoutNav = [
    { path: '/', component: Inicio },
    { path: '*', component: NotFound }
  ];

  const pagesWithNav = [
    { path: '/dashboard', component: Dashboard },
    { path: '/estudiantes', component: Estudiantes },
    { path: '/actividades', component: Actividades },
    { path: '/crear-actividad', component: CrearActividad },
    { path: '/chat', component: Chat },
    { path: '/configuracion', component: Configuracion }
  ];

  const createRouteWithNav = (Component) => (
    <>
      <Navigation />
      <main className="app__main-content">
        <Component />
      </main>
    </>
  );

  return (
    <div className="app">
      <Routes>
        {pagesWithoutNav.map(({ path, component: Component }) => (
          <Route key={path} path={path} element={<Component />} />
        ))}
        
        {pagesWithNav.map(({ path, component: Component }) => (
          <Route key={path} path={path} element={createRouteWithNav(Component)} />
        ))}
      </Routes>
    </div>
  );
}

// Componente simple para páginas no encontradas
const NotFound = () => (
  <div style={{ 
    display: 'flex', 
    flexDirection: 'column', 
    alignItems: 'center', 
    justifyContent: 'center', 
    height: '100vh',
    textAlign: 'center',
    padding: '2rem',
    width: '100%',
  }}>
    <h1 style={{ fontSize: '4rem', margin: '0', color: '#2d3748' }}>404</h1>
    <h2 style={{ color: '#4a5568', marginBottom: '1rem' }}>Página no encontrada</h2>
    <p style={{ color: '#718096', marginBottom: '2rem' }}>
      La página que buscas no existe o ha sido movida.
    </p>
    <a 
      href="#/" 
      style={{
        background: '#932428',
        color: 'white',
        padding: '0.75rem 2rem',
        borderRadius: '8px',
        textDecoration: 'none',
        fontWeight: '600'
      }}
    >
      Volver al Inicio
    </a>
  </div>
);

export default App;
