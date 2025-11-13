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
  EditarActividad,
  Configuracion,
  Login,
  ForgotPassword,
  MisCursos,
  VistaDetalladaCurso,
  Grupos,
  ActividadesEntregas,
  MisCalificaciones,
  Asistencias,
  Inscripciones,
  HorarioSemanal,
  MiPerfil,
  LandingPage,
  Usuarios
} from './pages';
import EntregasPage from './pages/Entregas/EntregasPage';
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

  const renderPageClean = (Component) => (
    <main className="app__main-content app__main-content--no-nav">
      <Component />
    </main>
  );

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={renderPageClean(Inicio)} />
        <Route path="/landing" element={renderPageClean(LandingPage)} />
        <Route path="/login" element={renderPageClean(Login)} />
        <Route path="/recuperar-password" element={renderPageClean(ForgotPassword)} />
        <Route path="/dashboard" element={renderPage(Dashboard)} />
        <Route path="/mis-cursos" element={renderPageClean(MisCursos)} />
        <Route path="/curso/:id" element={renderPageClean(VistaDetalladaCurso)} />
  <Route path="/curso/:id/grupos" element={renderPageClean(Grupos)} />
        <Route path="/actividades-entregas" element={renderPage(ActividadesEntregas)} />
        <Route path="/mis-calificaciones" element={renderPage(MisCalificaciones)} />
        <Route path="/asistencias" element={renderPage(Asistencias)} />
        <Route path="/inscripciones" element={renderPage(Inscripciones)} />
        <Route path="/horario-semanal" element={renderPage(HorarioSemanal)} />
        <Route path="/mi-perfil" element={renderPage(MiPerfil)} />
        <Route path="/estudiantes" element={renderPage(Estudiantes)} />
        <Route path="/usuarios" element={renderPage(Usuarios)} />
        <Route path="/actividades" element={renderPage(Actividades)} />
        <Route path="/crear-actividad" element={renderPage(CrearActividad)} />
        <Route path="/editar-actividad/:id" element={renderPage(EditarActividad)} />
        <Route path="/entregas" element={renderPage(EntregasPage)} />
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
