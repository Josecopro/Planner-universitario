import React, { useState, useEffect } from 'react';
import { activitiesApi } from '../../services/api';
import './Actividades.scss';
import { Link } from 'react-router-dom';

const Actividades = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterSubject, setFilterSubject] = useState('all');
  const [sortBy, setSortBy] = useState('dueDate');
  
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mutationLoading, setMutationLoading] = useState(false);

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      setLoading(true);
      setError(null);

      // Obtener correo del profesor desde localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        throw new Error('No se encontró información del usuario');
      }

      const user = JSON.parse(userStr);
      const correo = user.correo;

      console.log('📧 Correo del profesor:', correo);

      // Cargar actividades del profesor
      const data = await activitiesApi.getByProfesor(correo);
      setActivities(data);
      
      console.log('✅ Actividades cargadas:', data);
    } catch (err) {
      console.error('❌ Error al cargar actividades:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // Asegurar que activities sea un array antes de usar filter
  const activitiesArray = activities || [];

  const filteredAndSortedActivities = activitiesArray
    .filter(activity => {
      // Mapear estados de BD a estados del filtro
      const estadoMap = {
        'Programada': 'pending',
        'En Progreso': 'in-progress',
        'Completada': 'completed',
        'Cancelada': 'cancelled'
      };
      
      const prioridadMap = {
        'Alta': 'high',
        'Media': 'medium',
        'Baja': 'low'
      };

      const activityStatus = estadoMap[activity.estado] || 'pending';
      const activityPriority = prioridadMap[activity.prioridad] || 'medium';

      const statusMatch = filterStatus === 'all' || activityStatus === filterStatus;
      const priorityMatch = filterPriority === 'all' || activityPriority === filterPriority;
      
      return statusMatch && priorityMatch;
    })
    .sort((a, b) => {
      if (sortBy === 'dueDate') return new Date(a.fecha_entrega) - new Date(b.fecha_entrega);
      if (sortBy === 'priority') {
        const priorityOrder = { Alta: 3, Media: 2, Baja: 1 };
        return priorityOrder[b.prioridad] - priorityOrder[a.prioridad];
      }
      if (sortBy === 'status') return a.estado.localeCompare(b.estado);
      return 0;
    });

  const getStatusColor = (estado) => {
    switch (estado) {
      case 'Completada': return '#48bb78';
      case 'En Progreso': return '#ed8936';
      case 'Programada': return '#4299e1';
      case 'Cancelada': return '#a0aec0';
      default: return '#a0aec0';
    }
  };

  const getPriorityColor = (prioridad) => {
    switch (prioridad) {
      case 'Alta': return '#f56565';
      case 'Media': return '#ed8936';
      case 'Baja': return '#48bb78';
      default: return '#a0aec0';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getDaysUntilDue = (dueDate) => {
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleDeleteActivity = async (id, titulo) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar "${titulo}"?`)) {
      try {
        setMutationLoading(true);
        await activitiesApi.delete(id);
        await loadActivities(); // Recargar la lista
        alert('Actividad eliminada correctamente');
      } catch (error) {
        alert(`Error al eliminar actividad: ${error.message}`);
      } finally {
        setMutationLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="actividades-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando actividades...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="actividades-container">
        <div className="error-state">
          <h2>Error al cargar actividades</h2>
          <p>{error.message}</p>
          <button onClick={loadActivities} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="actividades-container">
      <header className="actividades-header">
        <div className="header-content">
          <h1>Mis Actividades</h1>
          <p>Gestiona y organiza todas tus tareas académicas</p>
        </div>
        <Link
          to="/crear-actividad"
          className="create-activity-btn"
        >
          + Nueva Actividad
        </Link>
      </header>

      <div className="controls-section">
        <div className="filters">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos los estados</option>
            <option value="pending">Pendientes</option>
            <option value="in-progress">En progreso</option>
            <option value="completed">Completadas</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todas las prioridades</option>
            <option value="high">Alta prioridad</option>
            <option value="medium">Prioridad media</option>
            <option value="low">Baja prioridad</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="dueDate">Ordenar por fecha</option>
            <option value="priority">Ordenar por prioridad</option>
            <option value="status">Ordenar por estado</option>
          </select>
        </div>

        <div className="view-options">
          <button className="view-btn active">📋 Lista</button>
          <button className="view-btn">📅 Calendario</button>
          <button className="view-btn">📊 Kanban</button>
        </div>
      </div>

      <div className="activities-stats">
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => a.estado === 'Programada').length}</div>
          <div className="stat-label">Pendientes</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => a.estado === 'En Progreso').length}</div>
          <div className="stat-label">En Progreso</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => a.estado === 'Completada').length}</div>
          <div className="stat-label">Completadas</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => getDaysUntilDue(a.fecha_entrega) <= 3 && a.estado !== 'Completada').length}</div>
          <div className="stat-label">Urgentes</div>
        </div>
      </div>

      <div className="activities-list">
        {filteredAndSortedActivities.map(activity => {
          const daysUntilDue = getDaysUntilDue(activity.fecha_entrega);
          const isOverdue = daysUntilDue < 0 && activity.estado !== 'Completada';
          const isUrgent = daysUntilDue <= 3 && daysUntilDue >= 0 && activity.estado !== 'Completada';

          return (
            <div key={activity.id} className={`activity-card ${activity.estado.toLowerCase().replace(' ', '-')} ${isOverdue ? 'overdue' : ''} ${isUrgent ? 'urgent' : ''}`}>
              <div className="activity-header">
                <div className="activity-title-section">
                  <h3 className="activity-title">{activity.titulo}</h3>
                  <span className="activity-subject">{activity.grupo?.curso?.nombre || 'Sin curso'}</span>
                </div>
                <div className="activity-badges">
                  <span 
                    className="priority-badge" 
                    style={{ backgroundColor: getPriorityColor(activity.prioridad) }}
                  >
                    {activity.prioridad}
                  </span>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(activity.estado) }}
                  >
                    {activity.estado}
                  </span>
                </div>
              </div>

              <p className="activity-description">{activity.descripcion}</p>

              <div className="activity-footer">
                <div className="activity-dates">
                  <div className="due-date">
                    <span className="date-label">Vence:</span>
                    <span className={`date-value ${isOverdue ? 'overdue' : isUrgent ? 'urgent' : ''}`}>
                      {formatDate(activity.fecha_entrega)}
                      {isOverdue && ` (${Math.abs(daysUntilDue)} días atrasado)`}
                      {isUrgent && ` (${daysUntilDue} días restantes)`}
                    </span>
                  </div>
                  {activity.tipo && (
                    <div className="activity-type">
                      <span className="type-badge">{activity.tipo}</span>
                    </div>
                  )}
                </div>

                <div className="activity-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn view">👁️</button>
                  <button 
                    className="action-btn delete"
                    onClick={() => handleDeleteActivity(activity.id, activity.titulo)}
                    disabled={mutationLoading}
                  >
                    🗑️
                  </button>
                  {activity.estado !== 'Completada' && (
                    <button className="action-btn complete">✅</button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredAndSortedActivities.length === 0 && (
        <div className="no-activities">
          <div className="no-activities-icon">📝</div>
          <h3>No hay actividades que mostrar</h3>
          <p>Ajusta los filtros o crea una nueva actividad para comenzar.</p>
        </div>
      )}
    </div>
  );
};

export default Actividades;
