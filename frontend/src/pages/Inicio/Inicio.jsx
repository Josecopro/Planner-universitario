import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Inicio.scss';

const Inicio = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <div className="inicio-page">
      <div className="inicio-page__container">
        <div className="inicio-page__content">
          <div className="inicio-page__brand">
            <h1 className="inicio-page__title">
              📚 Planner Universitario
            </h1>
            <p className="inicio-page__subtitle">
              Tu herramienta de gestión académica
            </p>
          </div>
          
          <div className="inicio-page__description">
            <p className="inicio-page__text">
              Organiza tus cursos, gestiona estudiantes y mantén un seguimiento 
              completo de tu vida académica en un solo lugar.
            </p>
          </div>
          
          <div className="inicio-page__actions">
            <button 
              className="inicio-page__login-btn"
              onClick={handleLoginClick}
            >
              Iniciar Sesión
            </button>
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default Inicio;
