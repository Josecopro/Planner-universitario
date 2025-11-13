import React, { useState, useEffect } from 'react';
import { entregasApi } from '../../services/api';
import './CalificarEntregas.scss';

const CalificarEntregas = ({ actividadId, actividadTitulo }) => {
  const [entregas, setEntregas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [calificandoId, setCalificandoId] = useState(null);
  const [modalData, setModalData] = useState({
    entregaId: null,
    nota: '',
    retroalimentacion: '',
    notaActual: null
  });

  useEffect(() => {
    if (actividadId) {
      loadEntregas();
    }
  }, [actividadId]);

  const loadEntregas = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await entregasApi.getByActividad(actividadId);
      setEntregas(data);
    } catch (err) {
      console.error('Error al cargar entregas:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const openCalificarModal = (entrega) => {
    setModalData({
      entregaId: entrega.id,
      nota: entrega.calificacion?.nota_obtenida ?? '',
      retroalimentacion: entrega.calificacion?.retroalimentacion ?? '',
      notaActual: entrega.calificacion?.nota_obtenida ?? null
    });
    setCalificandoId(entrega.id);
  };

  const closeModal = () => {
    setCalificandoId(null);
    setModalData({
      entregaId: null,
      nota: '',
      retroalimentacion: '',
      notaActual: null
    });
  };

  const handleCalificar = async (e) => {
    e.preventDefault();
    
    if (!modalData.nota || modalData.nota < 0 || modalData.nota > 5) {
      alert('La nota debe estar entre 0 y 5');
      return;
    }

    try {
      await entregasApi.calificar(
        modalData.entregaId,
        parseFloat(modalData.nota),
        modalData.retroalimentacion
      );

      alert('Calificación guardada correctamente');
      closeModal();
      await loadEntregas(); // Recargar entregas
    } catch (err) {
      alert(`Error al calificar: ${err.message}`);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Sin fecha';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'Entregada': return '#4299e1';
      case 'Revisada': return '#48bb78';
      case 'Tardia': return '#ed8936';
      default: return '#a0aec0';
    }
  };

  if (loading) {
    return (
      <div className="calificar-entregas-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando entregas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="calificar-entregas-container">
        <div className="error-state">
          <h3>Error al cargar entregas</h3>
          <p>{error.message}</p>
          <button onClick={loadEntregas} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="calificar-entregas-container">
      <div className="entregas-header">
        <h2>Entregas: {actividadTitulo}</h2>
        <div className="entregas-stats">
          <span className="stat">
            Total: <strong>{entregas.length}</strong>
          </span>
          <span className="stat">
            Calificadas: <strong>{entregas.filter(e => e.calificacion && e.calificacion.nota_obtenida != null).length}</strong>
          </span>
          <span className="stat">
            Pendientes: <strong>{entregas.filter(e => !e.calificacion || e.calificacion.nota_obtenida == null).length}</strong>
          </span>
        </div>
      </div>

      {entregas.length === 0 ? (
        <div className="no-entregas">
          <div className="no-entregas-icon">📭</div>
          <h3>No hay entregas aún</h3>
          <p>Los estudiantes aún no han realizado entregas para esta actividad.</p>
        </div>
      ) : (
        <div className="entregas-list">
          {entregas.map((entrega) => (
            <div key={entrega.id} className="entrega-card">
              <div className="entrega-header">
                <div className="estudiante-info">
                  <div className="estudiante-avatar">
                    {entrega.estudiante?.nombre?.charAt(0) || 'E'}
                    {entrega.estudiante?.apellido?.charAt(0) || 'S'}
                  </div>
                  <div className="estudiante-datos">
                    <h3>{entrega.estudiante?.nombre_completo || 'Estudiante'}</h3>
                    <p className="estudiante-email">{entrega.estudiante?.correo || 'Sin correo'}</p>
                  </div>
                </div>
                <div className="entrega-badges">
                  <span 
                    className="estado-badge" 
                    style={{ backgroundColor: getEstadoColor(entrega.estado) }}
                  >
                    {entrega.estado}
                  </span>
                  {entrega.calificacion && entrega.calificacion.nota_obtenida != null ? (
                    <span className="nota-badge calificada">
                      ✅ {Number(entrega.calificacion.nota_obtenida).toFixed(1)}
                    </span>
                  ) : (
                    <span className="nota-badge sin-calificar">
                      ⏳ Sin calificar
                    </span>
                  )}
                </div>
              </div>

              <div className="entrega-body">
                <div className="entrega-info-row">
                  <span className="info-label">📅 Fecha de entrega:</span>
                  <span className="info-value">{formatDate(entrega.fecha_entrega)}</span>
                </div>

                {entrega.grupo && (
                  <div className="entrega-info-row">
                    <span className="info-label">👥 Grupo:</span>
                    <span className="info-value">
                      {entrega.grupo.curso} - Semestre {entrega.grupo.semestre}
                    </span>
                  </div>
                )}

                {entrega.texto_entrega && (
                  <div className="entrega-texto">
                    <h4>Comentarios del estudiante:</h4>
                    <p>{entrega.texto_entrega}</p>
                  </div>
                )}

                {entrega.archivos_adjuntos && entrega.archivos_adjuntos.length > 0 && (
                  <div className="entrega-archivos">
                    <h4>Archivos adjuntos ({entrega.archivos_adjuntos.length}):</h4>
                    <ul>
                      {entrega.archivos_adjuntos.map((archivo, idx) => (
                        <li key={idx}>
                          <a href={archivo} target="_blank" rel="noopener noreferrer">
                            📎 {archivo.split('/').pop()}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {entrega.calificacion && entrega.calificacion.nota_obtenida != null && (
                  <div className="calificacion-actual">
                    <h4>Calificación actual:</h4>
                    <div className="calificacion-details">
                      <p className="nota-display">
                        Nota: <strong>{Number(entrega.calificacion.nota_obtenida).toFixed(1)} / 5.0</strong>
                      </p>
                      {entrega.calificacion.retroalimentacion && (
                        <p className="retroalimentacion">
                          <strong>Retroalimentación:</strong> {entrega.calificacion.retroalimentacion}
                        </p>
                      )}
                      <p className="fecha-calificacion">
                        Calificada el: {formatDate(entrega.calificacion.fecha_calificacion)}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="entrega-actions">
                <button 
                  className="btn-calificar"
                  onClick={() => openCalificarModal(entrega)}
                >
                  {entrega.calificacion ? '✏️ Editar Calificación' : '📝 Calificar'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal para calificar */}
      {calificandoId && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {modalData.notaActual !== null ? 'Editar Calificación' : 'Calificar Entrega'}
              </h3>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>

            <form onSubmit={handleCalificar} className="calificar-form">
              <div className="form-group">
                <label htmlFor="nota">Nota (0.0 - 5.0) *</label>
                <input
                  type="number"
                  id="nota"
                  value={modalData.nota}
                  onChange={(e) => setModalData({ ...modalData, nota: e.target.value })}
                  min="0"
                  max="5"
                  step="0.1"
                  required
                  placeholder="Ej: 4.5"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="retroalimentacion">Retroalimentación</label>
                <textarea
                  id="retroalimentacion"
                  value={modalData.retroalimentacion}
                  onChange={(e) => setModalData({ ...modalData, retroalimentacion: e.target.value })}
                  rows="5"
                  placeholder="Escribe aquí tus comentarios sobre la entrega..."
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={closeModal}>
                  Cancelar
                </button>
                <button type="submit" className="btn-submit">
                  {modalData.notaActual !== null ? 'Actualizar Calificación' : 'Guardar Calificación'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalificarEntregas;
