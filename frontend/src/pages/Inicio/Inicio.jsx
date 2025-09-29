import React, { useState } from 'react';
import CourseCard from '../../components/CourseCard';
import './Inicio.scss';
import { useNavigate } from 'react-router-dom';

const Inicio = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSemester, setSelectedSemester] = useState('all');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const cursos = [
    {
      id: 1,
      codigo: 'MAT-101',
      nombre: 'Cálculo Diferencial',
      semestre: '2025-1',
      programa: 'Ingeniería',
      grupo: 'A1',
      estudiantes: 30,
      icon: '📚',
      imagen: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=150&h=150&fit=crop&crop=center',
      color: 'red'
    },
    {
      id: 2,
      codigo: 'QUI-001',
      nombre: 'Química I',
      semestre: '2025-1',
      programa: 'Ingeniería',
      grupo: 'B2',
      estudiantes: 25,
      icon: '🧪',
      imagen: 'https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=150&h=150&fit=crop&crop=center',
      color: 'purple'
    },
    {
      id: 3,
      codigo: 'EST-001',
      nombre: 'Estadística I',
      
      semestre: '2025-1',
      programa: 'Computación',
      grupo: 'C1',
      estudiantes: 22,
      icon: '📊',
      imagen: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=150&h=150&fit=crop&crop=center',
      color: 'blue'
    },
    {
      id: 4,
      codigo: 'INF-402',
      nombre: 'Programación Web',
      
      semestre: '2025-1',
      programa: 'Ingeniería',
      grupo: 'A3',
      estudiantes: 29,
      icon: '💻',
      imagen: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=150&h=150&fit=crop&crop=center',
      color: 'green'
    },
    {
      id: 5,
      codigo: 'FIS-201',
      nombre: 'Física II',
      semestre: '2025-1',
      programa: 'Ingeniería',
      grupo: 'B1',
      estudiantes: 28,
      icon: '⚡',
      color: 'orange'
    },
    {
      id: 6,
      codigo: 'ING-301',
      nombre: 'Inglés Técnico',
      
      semestre: '2025-1',
      programa: 'Todos',
      grupo: 'D1',
      estudiantes: 35,
      icon: '🌐',
      imagen: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=150&h=150&fit=crop&crop=center',
      color: 'blue'
    }
  ];

  const filteredCursos = cursos.filter(curso => {
    const matchesSearch = curso.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         curso.codigo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSemester = selectedSemester === 'all' || curso.semestre === selectedSemester;
    const matchesProgram = selectedProgram === 'all' || curso.programa === selectedProgram;
    
    return matchesSearch && matchesSemester && matchesProgram;
  });

  // Importa useNavigate de react-router-dom

  const navigate = useNavigate();

  return (
    <div className="courses-page">
      <header className="courses-page__header">
        <h1 className="courses-page__title">Mis Cursos</h1>
      </header>
      
      <div className="courses-page__controls">
        <div className="search">
          <div className="search__wrapper">
            <input
              type="text"
              placeholder="Buscar por nombre o código del curso..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search__input"
            />
            <span className="search__icon">🔍</span>
          </div>
        </div>

        <div className="filters">
          <select
            value={selectedSemester}
            onChange={(e) => setSelectedSemester(e.target.value)}
            className="filters__select"
          >
            <option value="all">Todos los semestres</option>
            <option value="2025-1">2025-1</option>
            <option value="2024-2">2024-2</option>
            <option value="2024-1">2024-1</option>
          </select>

          <select
            value={selectedProgram}
            onChange={(e) => setSelectedProgram(e.target.value)}
            className="filters__select"
          >
            <option value="all">Todos los programas</option>
            <option value="Ingeniería">Ingeniería</option>
            <option value="Computación">Computación</option>
            <option value="Todos">Todos</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="filters__select"
          >
            <option value="all">Estado</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="completado">Completado</option>
          </select>
        </div>
      </div>

      <main className="courses-page__grid">
        {filteredCursos.map(curso => (
          <CourseCard
            key={curso.id}
            codigo={curso.codigo}
            nombre={curso.nombre}
            grupo={curso.grupo}
            estudiantes={curso.estudiantes}
            icon={curso.icon}
            imagen={curso.imagen}
            color={curso.color}
            onClick={() => navigate('/dashboard')}
          />
        ))}
      </main>

      {filteredCursos.length === 0 && (
        <div className="courses-page__empty">
          <p className="courses-page__empty-text">No se encontraron cursos que coincidan con tu búsqueda.</p>
        </div>
      )}
    </div>
  );
};

export default Inicio;
