import React, { useState } from 'react';
import './Estudiantes.scss';

const Estudiantes = () => {
  const [students, setStudents] = useState([
    {
      id: 1,
      name: 'María González',
      email: 'maria.gonzalez@universidad.edu',
      career: 'Ingeniería en Sistemas',
      semester: 6,
      status: 'active',
      avatar: 'M'
    },
    {
      id: 2,
      name: 'Carlos Rodríguez',
      email: 'carlos.rodriguez@universidad.edu',
      career: 'Administración de Empresas',
      semester: 4,
      status: 'active',
      avatar: 'C'
    },
    {
      id: 3,
      name: 'Ana López',
      email: 'ana.lopez@universidad.edu',
      career: 'Psicología',
      semester: 8,
      status: 'inactive',
      avatar: 'A'
    },
    {
      id: 4,
      name: 'Diego Martínez',
      email: 'diego.martinez@universidad.edu',
      career: 'Medicina',
      semester: 10,
      status: 'active',
      avatar: 'D'
    }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.career.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || student.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="students-page">
      <header className="students-page__header">
        <h1 className="students-page__title">Gestión de Estudiantes</h1>
        <p>Administra la información de los estudiantes registrados</p>
      </header>

      <div className="controls-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Buscar estudiante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <span className="search-icon">🔍</span>
        </div>

        <div className="filters">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>
        </div>

        <button className="add-student-btn">
          + Agregar Estudiante
        </button>
      </div>

      <div className="students-stats">
        <div className="stat-item">
          <span className="stat-number">{students.length}</span>
          <span className="stat-label">Total</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{students.filter(s => s.status === 'active').length}</span>
          <span className="stat-label">Activos</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{students.filter(s => s.status === 'inactive').length}</span>
          <span className="stat-label">Inactivos</span>
        </div>
      </div>

      <div className="students-grid">
        {filteredStudents.map(student => (
          <div key={student.id} className={`student-card ${student.status}`}>
            <div className="student-avatar">
              {student.avatar}
            </div>
            
            <div className="student-info">
              <h3 className="student-name">{student.name}</h3>
              <p className="student-email">{student.email}</p>
              <p className="student-career">{student.career}</p>
              <p className="student-semester">Semestre {student.semester}</p>
            </div>

            <div className={`status-indicator ${student.status}`}>
              {student.status === 'active' ? 'Activo' : 'Inactivo'}
            </div>

            <div className="student-actions">
              <button className="action-btn edit">✏️</button>
              <button className="action-btn view">👁️</button>
              <button className="action-btn delete">🗑️</button>
            </div>
          </div>
        ))}
      </div>

      {filteredStudents.length === 0 && (
        <div className="no-results">
          <p>No se encontraron estudiantes que coincidan con tu búsqueda.</p>
        </div>
      )}
    </div>
  );
};

export default Estudiantes;
