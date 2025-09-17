import React from 'react';
import './Inicio.scss';

const Inicio = () => {
  return (
    <div className="inicio-container">
      <header className="inicio-header">
        <h1>Bienvenido al Planner Universitario</h1>
        <p>Organiza tu vida académica de manera eficiente</p>
      </header>
      
      <main className="inicio-main">
        <section className="features-section">
          <div className="feature-card">
            <h3>Gestiona tus tareas</h3>
            <p>Organiza y planifica todas tus actividades académicas</p>
          </div>
          
          <div className="feature-card">
            <h3>Chat colaborativo</h3>
            <p>Comunícate con tus compañeros de estudio</p>
          </div>
          
          <div className="feature-card">
            <h3>Dashboard personalizado</h3>
            <p>Visualiza tu progreso académico en tiempo real</p>
          </div>
        </section>
        
        <section className="cta-section">
          <button className="cta-button">Comenzar ahora</button>
        </section>
      </main>
    </div>
  );
};

export default Inicio;
