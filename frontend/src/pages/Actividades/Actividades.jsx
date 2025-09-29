import React, { useState } from 'react';
import { useApi, useMutation, activitiesApi } from '../../services/api';
import './Actividades.scss';
import { Link } from 'react-router-dom';

const Actividades = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterSubject, setFilterSubject] = useState('all');
  const [sortBy, setSortBy] = useState('dueDate');

  const { data: activities, loading, error, refetch } = useApi(() => activitiesApi.getAll());
  const { mutate, loading: mutationLoading } = useMutation();

  // Asegurar que activities sea un array antes de usar filter
  const activitiesArray = activities || [];

  const filteredAndSortedActivities = activitiesArray
    .filter(activity => {
      const statusMatch = filterStatus === 'all' || activity.status === filterStatus;
      const priorityMatch = filterPriority === 'all' || activity.priority === filterPriority;
      return statusMatch && priorityMatch;
    })
    .sort((a, b) => {
      if (sortBy === 'dueDate') return new Date(a.due_date || a.dueDate) - new Date(b.due_date || b.dueDate);
      if (sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }
      if (sortBy === 'status') return a.status.localeCompare(b.status);
      return 0;
    });

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#48bb78';
      case 'in-progress': return '#ed8936';
      case 'pending': return '#f56565';
      default: return '#a0aec0';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#f56565';
      case 'medium': return '#ed8936';
      case 'low': return '#48bb78';
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

  const handleDeleteActivity = async (id, title) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar "${title}"?`)) {
      try {
        await mutate(() => activitiesApi.delete(id));
        await refetch(); // Actualizar la lista
        alert('Actividad eliminada correctamente');
      } catch (error) {
        alert(`Error al eliminar actividad: ${error.message}`);
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
          <button onClick={refetch} className="retry-button">
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
          <div className="stat-number">{activities.filter(a => a.status === 'pending').length}</div>
          <div className="stat-label">Pendientes</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => a.status === 'in-progress').length}</div>
          <div className="stat-label">En Progreso</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => a.status === 'completed').length}</div>
          <div className="stat-label">Completadas</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{activities.filter(a => getDaysUntilDue(a.dueDate) <= 3 && a.status !== 'completed').length}</div>
          <div className="stat-label">Urgentes</div>
        </div>
      </div>

      <div className="activities-list">
        {filteredAndSortedActivities.map(activity => {
          const daysUntilDue = getDaysUntilDue(activity.due_date || activity.dueDate);
          const isOverdue = daysUntilDue < 0 && activity.status !== 'completed';
          const isUrgent = daysUntilDue <= 3 && daysUntilDue >= 0 && activity.status !== 'completed';

          return (
            <div key={activity.id} className={`activity-card ${activity.status} ${isOverdue ? 'overdue' : ''} ${isUrgent ? 'urgent' : ''}`}>
              <div className="activity-header">
                <div className="activity-title-section">
                  <h3 className="activity-title">{activity.title}</h3>
                  <span className="activity-subject">{activity.subject}</span>
                </div>
                <div className="activity-badges">
                  <span 
                    className="priority-badge" 
                    style={{ backgroundColor: getPriorityColor(activity.priority) }}
                  >
                    {activity.priority === 'high' ? 'Alta' : activity.priority === 'medium' ? 'Media' : 'Baja'}
                  </span>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(activity.status) }}
                  >
                    {activity.status === 'completed' ? 'Completada' : 
                     activity.status === 'in-progress' ? 'En Progreso' : 'Pendiente'}
                  </span>
                </div>
              </div>

              <p className="activity-description">{activity.description}</p>

              <div className="activity-footer">
                <div className="activity-dates">
                  <div className="due-date">
                    <span className="date-label">Vence:</span>
                    <span className={`date-value ${isOverdue ? 'overdue' : isUrgent ? 'urgent' : ''}`}>
                      {formatDate(activity.due_date || activity.dueDate)}
                      {isOverdue && ` (${Math.abs(daysUntilDue)} días atrasado)`}
                      {isUrgent && ` (${daysUntilDue} días restantes)`}
                    </span>
                  </div>
                </div>

                <div className="activity-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn view">👁️</button>
                  <button 
                    className="action-btn delete"
                    onClick={() => handleDeleteActivity(activity.id, activity.title)}
                    disabled={mutationLoading}
                  >
                    🗑️
                  </button>
                  {activity.status !== 'completed' && (
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
