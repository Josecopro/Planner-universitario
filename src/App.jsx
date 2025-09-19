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
  return (
    <div className="app">
      <Navigation />
      
      <main className="app__main-content">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/estudiantes" element={<Estudiantes />} />
          <Route path="/actividades" element={<Actividades />} />
          <Route path="/crear-actividad" element={<CrearActividad />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/configuracion" element={<Configuracion />} />
          {/* Ruta 404 - página no encontrada */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
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
    padding: '2rem'
  }}>
    <h1 style={{ fontSize: '4rem', margin: '0', color: '#2d3748' }}>404</h1>
    <h2 style={{ color: '#4a5568', marginBottom: '1rem' }}>Página no encontrada</h2>
    <p style={{ color: '#718096', marginBottom: '2rem' }}>
      La página que buscas no existe o ha sido movida.
    </p>
    <a 
      href="#/" 
      style={{
        background: '#4299e1',
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
