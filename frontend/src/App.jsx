import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Navigation from './components/Navigation/Navigation';
import NavBar from './components/NavBar';
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
import './styles/api-states.css';

function App() {
  const renderPage = (Component, { showNavigation = true } = {}) => (
    <>
      {showNavigation && <Navigation />}
      <main
        className={`app__main-content ${
          showNavigation ? '' : 'app__main-content--no-nav'
        }`}
      >
        <div className="app__main-wrapper">
          <NavBar />
          <div className="app__page-wrapper">
            <Component />
          </div>
        </div>
      </main>
    </>
  );

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={renderPage(Inicio, { showNavigation: false })} />
        <Route path="/dashboard" element={renderPage(Dashboard)} />
        <Route path="/estudiantes" element={renderPage(Estudiantes)} />
        <Route path="/actividades" element={renderPage(Actividades)} />
        <Route path="/crear-actividad" element={renderPage(CrearActividad)} />
        <Route path="/chat" element={renderPage(Chat)} />
        <Route path="/configuracion" element={renderPage(Configuracion)} />
        <Route path="*" element={<NotFound />} />
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
    <Link 
      to="/" 
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
    </Link>
  </div>
);

export default App;
