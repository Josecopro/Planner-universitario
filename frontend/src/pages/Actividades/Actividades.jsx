import React, { useState, useEffect } from 'react';
import { activitiesApi } from '../../services/api';
import './Actividades.scss';
import { Link } from 'react-router-dom';
import CalificarEntregas from '../../components/CalificarEntregas/CalificarEntregas';

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
  
  // Estado para ver detalles de actividad
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [activeTab, setActiveTab] = useState('info'); // 'info' o 'entregas'
  
  // Estado para editar actividad
  const [editingActivity, setEditingActivity] = useState(null);
  const [editFormData, setEditFormData] = useState({
    titulo: '',
    descripcion: '',
    fecha_entrega: '',
    hora_entrega: '',
    tipo: 'Tarea',
    prioridad: 'Media',
    porcentaje: ''
  });
  const [editErrors, setEditErrors] = useState({});

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

  const handleViewActivity = (activity) => {
    setSelectedActivity(activity);
    setActiveTab('info');
  };

  const handleCloseDetails = () => {
    setSelectedActivity(null);
    setActiveTab('info');
  };

  const handleEditActivity = (activity) => {
    // Extraer fecha y hora si es timestamp completo
    const fechaObj = new Date(activity.fecha_entrega);
    const fecha = fechaObj.toISOString().split('T')[0];
    const hora = fechaObj.toTimeString().slice(0, 5);

    setEditFormData({
      titulo: activity.titulo,
      descripcion: activity.descripcion,
      fecha_entrega: fecha,
      hora_entrega: hora,
      tipo: activity.tipo,
      prioridad: activity.prioridad,
      porcentaje: activity.porcentaje || ''
    });
    setEditingActivity(activity);
    setEditErrors({});
  };

  const handleCloseEditModal = () => {
    setEditingActivity(null);
    setEditFormData({
      titulo: '',
      descripcion: '',
      fecha_entrega: '',
      hora_entrega: '',
      tipo: 'Tarea',
      prioridad: 'Media',
      porcentaje: ''
    });
    setEditErrors({});
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (editErrors[name]) {
      setEditErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateEditForm = () => {
    const newErrors = {};

    if (!editFormData.titulo.trim()) {
      newErrors.titulo = 'El título es obligatorio';
    }

    if (!editFormData.fecha_entrega) {
      newErrors.fecha_entrega = 'La fecha de entrega es obligatoria';
    }

    if (!editFormData.descripcion.trim()) {
      newErrors.descripcion = 'La descripción es obligatoria';
    }

    if (editFormData.porcentaje && (editFormData.porcentaje < 0 || editFormData.porcentaje > 100)) {
      newErrors.porcentaje = 'El porcentaje debe estar entre 0 y 100';
    }

    setEditErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmitEdit = async (e) => {
    e.preventDefault();
    
    if (!validateEditForm()) {
      return;
    }

    try {
      setMutationLoading(true);

      // Construir la fecha completa con hora
      let fechaCompleta = editFormData.fecha_entrega;
      if (editFormData.hora_entrega) {
        fechaCompleta = `${editFormData.fecha_entrega}T${editFormData.hora_entrega}:00`;
      } else {
        fechaCompleta = `${editFormData.fecha_entrega}T23:59:59`;
      }

      const updateData = {
        titulo: editFormData.titulo,
        descripcion: editFormData.descripcion,
        fecha_entrega: fechaCompleta,
        tipo: editFormData.tipo,
        prioridad: editFormData.prioridad,
        porcentaje: editFormData.porcentaje ? parseFloat(editFormData.porcentaje) : 0.0
      };

      await activitiesApi.update(editingActivity.id, updateData);
      
      alert('Actividad actualizada correctamente');
      handleCloseEditModal();
      await loadActivities(); // Recargar la lista
    } catch (err) {
      alert(`Error al actualizar actividad: ${err.message}`);
    } finally {
      setMutationLoading(false);
    }
  };

  // Si hay una actividad seleccionada, mostrar vista de detalles
  if (selectedActivity) {
    return (
      <div className="actividades-container">
        <div className="activity-details-view">
          <div className="details-header">
            <button className="back-button" onClick={handleCloseDetails}>
              ← Volver a Actividades
            </button>
            <h1>{selectedActivity.titulo}</h1>
          </div>

          <div className="tabs-container">
            <div className="tabs">
              <button 
                className={`tab ${activeTab === 'info' ? 'active' : ''}`}
                onClick={() => setActiveTab('info')}
              >
                📋 Información
              </button>
              <button 
                className={`tab ${activeTab === 'entregas' ? 'active' : ''}`}
                onClick={() => setActiveTab('entregas')}
              >
                📝 Entregas y Calificaciones
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'info' ? (
                <div className="info-tab">
                  <div className="info-section">
                    <h3>Detalles de la Actividad</h3>
                    
                    <div className="info-grid">
                      <div className="info-item">
                        <label>Curso:</label>
                        <span>{selectedActivity.grupo?.curso?.nombre || 'Sin curso'}</span>
                      </div>
                      
                      <div className="info-item">
                        <label>Código:</label>
                        <span>{selectedActivity.grupo?.curso?.codigo || 'N/A'}</span>
                      </div>
                      
                      <div className="info-item">
                        <label>Semestre:</label>
                        <span>{selectedActivity.grupo?.semestre || 'N/A'}</span>
                      </div>
                      
                      <div className="info-item">
                        <label>Tipo:</label>
                        <span>{selectedActivity.tipo}</span>
                      </div>
                      
                      <div className="info-item">
                        <label>Prioridad:</label>
                        <span className={`priority-badge-inline ${selectedActivity.prioridad.toLowerCase()}`}>
                          {selectedActivity.prioridad}
                        </span>
                      </div>
                      
                      <div className="info-item">
                        <label>Estado:</label>
                        <span className="status-badge-inline">
                          {selectedActivity.estado}
                        </span>
                      </div>
                      
                      <div className="info-item">
                        <label>Fecha de Entrega:</label>
                        <span>{formatDate(selectedActivity.fecha_entrega)}</span>
                      </div>
                      
                      <div className="info-item">
                        <label>Porcentaje:</label>
                        <span>{selectedActivity.porcentaje}% de la nota final</span>
                      </div>
                    </div>

                    <div className="description-section">
                      <h4>Descripción:</h4>
                      <p>{selectedActivity.descripcion}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <CalificarEntregas 
                  actividadId={selectedActivity.id}
                  actividadTitulo={selectedActivity.titulo}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

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
                  <button 
                    className="action-btn edit"
                    onClick={() => handleEditActivity(activity)}
                    title="Editar actividad"
                  >
                    ✏️
                  </button>
                  <button 
                    className="action-btn view"
                    onClick={() => handleViewActivity(activity)}
                    title="Ver detalles y calificar"
                  >
                    👁️
                  </button>
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

      {/* Modal de Edición */}
      {editingActivity && (
        <div className="modal-overlay" onClick={handleCloseEditModal}>
          <div className="modal-content edit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>✏️ Editar Actividad</h3>
              <button className="modal-close" onClick={handleCloseEditModal}>×</button>
            </div>

            <form onSubmit={handleSubmitEdit} className="edit-form">
              <div className="form-group">
                <label htmlFor="edit-titulo">Título *</label>
                <input
                  type="text"
                  id="edit-titulo"
                  name="titulo"
                  value={editFormData.titulo}
                  onChange={handleEditInputChange}
                  className={editErrors.titulo ? 'error' : ''}
                  placeholder="Título de la actividad"
                />
                {editErrors.titulo && <span className="error-message">{editErrors.titulo}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="edit-descripcion">Descripción *</label>
                <textarea
                  id="edit-descripcion"
                  name="descripcion"
                  value={editFormData.descripcion}
                  onChange={handleEditInputChange}
                  className={editErrors.descripcion ? 'error' : ''}
                  rows="4"
                  placeholder="Descripción de la actividad"
                />
                {editErrors.descripcion && <span className="error-message">{editErrors.descripcion}</span>}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-fecha">Fecha de Entrega *</label>
                  <input
                    type="date"
                    id="edit-fecha"
                    name="fecha_entrega"
                    value={editFormData.fecha_entrega}
                    onChange={handleEditInputChange}
                    className={editErrors.fecha_entrega ? 'error' : ''}
                  />
                  {editErrors.fecha_entrega && <span className="error-message">{editErrors.fecha_entrega}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="edit-hora">Hora</label>
                  <input
                    type="time"
                    id="edit-hora"
                    name="hora_entrega"
                    value={editFormData.hora_entrega}
                    onChange={handleEditInputChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit-tipo">Tipo</label>
                  <select
                    id="edit-tipo"
                    name="tipo"
                    value={editFormData.tipo}
                    onChange={handleEditInputChange}
                  >
                    <option value="Tarea">Tarea</option>
                    <option value="Examen">Examen</option>
                    <option value="Proyecto">Proyecto</option>
                    <option value="Presentacion">Presentación</option>
                    <option value="Laboratorio">Laboratorio</option>
                    <option value="Ensayo">Ensayo</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-prioridad">Prioridad</label>
                  <select
                    id="edit-prioridad"
                    name="prioridad"
                    value={editFormData.prioridad}
                    onChange={handleEditInputChange}
                  >
                    <option value="Baja">Baja</option>
                    <option value="Media">Media</option>
                    <option value="Alta">Alta</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="edit-porcentaje">Porcentaje (%)</label>
                  <input
                    type="number"
                    id="edit-porcentaje"
                    name="porcentaje"
                    value={editFormData.porcentaje}
                    onChange={handleEditInputChange}
                    min="0"
                    max="100"
                    step="0.01"
                    placeholder="0-100"
                    className={editErrors.porcentaje ? 'error' : ''}
                  />
                  {editErrors.porcentaje && <span className="error-message">{editErrors.porcentaje}</span>}
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={handleCloseEditModal}>
                  Cancelar
                </button>
                <button type="submit" className="btn-submit" disabled={mutationLoading}>
                  {mutationLoading ? '⏳ Guardando...' : '💾 Guardar Cambios'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Actividades;
