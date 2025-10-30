import React, { useState, useEffect } from 'react';
import { studentsApi } from '../../services/api';
import './Estudiantes.scss';

const Estudiantes = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mutationLoading, setMutationLoading] = useState(false);

  // Cargar estudiantes del profesor al montar el componente
  useEffect(() => {
    const loadStudents = async () => {
      try {
        setLoading(true);
        setError(null);

        // Obtener el correo del usuario logueado
        const userStr = localStorage.getItem('user');
        let correo = null;
        
        if (userStr) {
          try {
            const user = JSON.parse(userStr);
            correo = user.email || user.correo;
            console.log('📧 [Estudiantes] Correo del profesor:', correo);
          } catch (e) {
            console.error('❌ Error al parsear usuario:', e);
          }
        }

        if (!correo) {
          console.warn('⚠️ No se encontró correo de usuario logueado');
          setStudents([]);
          setLoading(false);
          return;
        }

        // Cargar estudiantes del profesor
        console.log('🔍 [Estudiantes] Cargando estudiantes del profesor...');
        const data = await studentsApi.getByProfesor(correo);
        setStudents(data || []);
        console.log('✅ [Estudiantes] Estudiantes cargados:', data);
      } catch (err) {
        console.error('❌ [Estudiantes] Error al cargar estudiantes:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadStudents();
  }, []);

  const refetch = async () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      const correo = user.email || user.correo;
      if (correo) {
        const data = await studentsApi.getByProfesor(correo);
        setStudents(data || []);
      }
    }
  };

  const studentsArray = students || [];
  
  const filteredStudents = studentsArray.filter(student => {
    const matchesSearch = student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.career?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || student.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  const handleDeleteStudent = async (id, name) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar a ${name}?`)) {
      try {
        setMutationLoading(true);
        await studentsApi.delete(id);
        await refetch();
        alert('Estudiante eliminado correctamente');
      } catch (error) {
        alert(`Error al eliminar estudiante: ${error.message}`);
      } finally {
        setMutationLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="students-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando estudiantes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="students-page">
        <div className="error-state">
          <h2>Error al cargar estudiantes</h2>
          <p>{error.message}</p>
          <button onClick={refetch} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

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
          <span className="stat-number">{studentsArray.length}</span>
          <span className="stat-label">Total</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{studentsArray.filter(s => s.status === 'active').length}</span>
          <span className="stat-label">Activos</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{studentsArray.filter(s => s.status === 'inactive').length}</span>
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
              <button 
                className="action-btn delete"
                onClick={() => handleDeleteStudent(student.id, student.name)}
                disabled={mutationLoading}
              >
                🗑️
              </button>
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
