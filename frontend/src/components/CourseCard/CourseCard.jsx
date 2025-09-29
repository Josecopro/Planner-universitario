import React from 'react';
import './CourseCard.scss';

const CourseCard = ({ 
  codigo, 
  nombre, 
  grupo, 
  estudiantes, 
  icon, 
  imagen, 
  color,
  onClick 
}) => {
  return (
    <div className={`course-card course-card--${color}`} onClick={onClick}>
      <div className="course-card__header">
        {imagen ? (
          <img 
            src={imagen} 
            alt={`Logo de ${nombre}`} 
            className="course-card__image"
          />
        ) : (
          <div className="course-card__icon">
            {icon}
          </div>
        )}
      </div>

      <div className="course-card__content">
        <h3 className="course-card__title">{nombre}</h3>
        <p className="course-card__code">{codigo}</p>
        {grupo && <p className="course-card__group">Grupo: {grupo}</p>}
      </div>

      <div className="course-card__stats">
        <div className="course-card__students">
          <span className="course-card__students-icon">👥</span>
          <span className="course-card__students-count">{estudiantes} estudiantes</span>
        </div>
      </div>

      <button className="course-card__button">
        Ver Curso
      </button>
    </div>
  );
};

export default CourseCard;
