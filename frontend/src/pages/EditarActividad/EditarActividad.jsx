import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { activitiesApi } from '../../services/api';
import './EditarActividad.scss';

const EditarActividad = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  
  const [formData, setFormData] = useState({
    grupo_id: '',
    titulo: '',
    descripcion: '',
    fecha_entrega: '',
    hora_entrega: '',
    tipo: 'Tarea',
    prioridad: 'Media',
    estado: 'Programada',
    porcentaje: ''
  });

  const [gruposDisponibles, setGruposDisponibles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadActivityAndGroups();
  }, [id]);

  const loadActivityAndGroups = async () => {
    try {
      // Obtener la actividad
      const { supabase } = await import('../../config/supabase');
      
      const { data: activity, error: actError } = await supabase
        .from('actividadevaluativa')
        .select('*')
        .eq('id', id)
        .single();

      if (actError || !activity) {
        throw new Error('No se pudo cargar la actividad');
      }

      // Formatear la fecha para el input
      const dateStr = activity.fecha_entrega?.split('T')[0] || '';

      setFormData({
        grupo_id: activity.grupo_id,
        titulo: activity.titulo,
        descripcion: activity.descripcion,
        fecha_entrega: dateStr,
        hora_entrega: activity.hora_entrega || '',
        tipo: activity.tipo || 'Tarea',
        prioridad: activity.prioridad || 'Media',
        estado: activity.estado || 'Programada',
        porcentaje: activity.porcentaje || ''
      });

      // Obtener grupos del profesor
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.warn('No se encontró información del usuario');
        return;
      }

      const user = JSON.parse(userStr);
      const correo = user.correo;

      const { data: usuario } = await supabase
        .from('usuarios')
        .select('id')
        .eq('correo', correo)
        .single();

      if (!usuario) return;

      const { data: profesor } = await supabase
        .from('profesor')
        .select('id')
        .eq('usuario_id', usuario.id)
        .single();

      if (!profesor) return;

      const { data: grupos } = await supabase
        .from('grupo')
        .select(`
          id,
          semestre,
          curso:curso_id (
            codigo,
            nombre
          )
        `)
        .eq('profesor_id', profesor.id);

      setGruposDisponibles(grupos || []);
    } catch (err) {
      console.error('❌ Error al cargar datos:', err);
      setErrors({ general: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Limpiar error del campo
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.titulo.trim()) {
      newErrors.titulo = 'El título es obligatorio';
    }
    if (!formData.descripcion.trim()) {
      newErrors.descripcion = 'La descripción es obligatoria';
    }
    if (!formData.fecha_entrega) {
      newErrors.fecha_entrega = 'La fecha de entrega es obligatoria';
    }
    if (!formData.grupo_id) {
      newErrors.grupo_id = 'Debes seleccionar un grupo';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setIsSaving(true);
      
      const dataToSave = {
        ...formData,
        fecha_entrega: `${formData.fecha_entrega}T00:00:00`,
        porcentaje: parseFloat(formData.porcentaje) || 0
      };

      await activitiesApi.update(id, dataToSave);
      alert('Actividad actualizada correctamente');
      navigate('/actividades');
    } catch (error) {
      setErrors({ general: error.message });
      alert(`Error al actualizar actividad: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (window.confirm('¿Descartar cambios?')) {
      navigate('/actividades');
    }
  };

  if (isLoading) {
    return (
      <div className="editar-actividad-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando actividad...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="editar-actividad-container">
      <header className="editar-header">
        <h1>Editar Actividad</h1>
        <p>Actualiza los detalles de tu actividad evaluativa</p>
      </header>

      <form className="editar-form" onSubmit={handleSubmit}>
        {errors.general && (
          <div className="error-alert">
            {errors.general}
          </div>
        )}

        <div className="form-section">
          <h2>Información Básica</h2>

          <div className="form-group">
            <label htmlFor="grupo">Grupo *</label>
            <select
              id="grupo"
              value={formData.grupo_id}
              onChange={(e) => handleChange('grupo_id', parseInt(e.target.value))}
              className={errors.grupo_id ? 'error' : ''}
            >
              <option value="">Selecciona un grupo</option>
              {gruposDisponibles.map(grupo => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.curso?.nombre} - Grupo {grupo.semestre}
                </option>
              ))}
            </select>
            {errors.grupo_id && <span className="error-message">{errors.grupo_id}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="titulo">Título *</label>
            <input
              id="titulo"
              type="text"
              value={formData.titulo}
              onChange={(e) => handleChange('titulo', e.target.value)}
              placeholder="Ej: Ensayo sobre la Revolución Francesa"
              className={errors.titulo ? 'error' : ''}
            />
            {errors.titulo && <span className="error-message">{errors.titulo}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="descripcion">Descripción *</label>
            <textarea
              id="descripcion"
              value={formData.descripcion}
              onChange={(e) => handleChange('descripcion', e.target.value)}
              placeholder="Describe la actividad en detalle..."
              rows="5"
              className={errors.descripcion ? 'error' : ''}
            />
            {errors.descripcion && <span className="error-message">{errors.descripcion}</span>}
          </div>
        </div>

        <div className="form-section">
          <h2>Detalles de Entrega</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="fecha">Fecha de Entrega *</label>
              <input
                id="fecha"
                type="date"
                value={formData.fecha_entrega}
                onChange={(e) => handleChange('fecha_entrega', e.target.value)}
                className={errors.fecha_entrega ? 'error' : ''}
              />
              {errors.fecha_entrega && <span className="error-message">{errors.fecha_entrega}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="hora">Hora de Entrega</label>
              <input
                id="hora"
                type="time"
                value={formData.hora_entrega}
                onChange={(e) => handleChange('hora_entrega', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h2>Categorización</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tipo">Tipo de Actividad</label>
              <select
                id="tipo"
                value={formData.tipo}
                onChange={(e) => handleChange('tipo', e.target.value)}
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
              <label htmlFor="prioridad">Prioridad</label>
              <select
                id="prioridad"
                value={formData.prioridad}
                onChange={(e) => handleChange('prioridad', e.target.value)}
              >
                <option value="Baja">Baja</option>
                <option value="Media">Media</option>
                <option value="Alta">Alta</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="estado">Estado</label>
              <select
                id="estado"
                value={formData.estado}
                onChange={(e) => handleChange('estado', e.target.value)}
              >
                <option value="Programada">Programada</option>
                <option value="Publicada">Publicada</option>
                <option value="Abierta">Abierta</option>
                <option value="Cerrada">Cerrada</option>
                <option value="Cancelada">Cancelada</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="porcentaje">Porcentaje de Calificación (%)</label>
            <input
              id="porcentaje"
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.porcentaje}
              onChange={(e) => handleChange('porcentaje', e.target.value)}
              placeholder="Ej: 10.5"
            />
            <small>Porcentaje de la calificación final que representa esta actividad</small>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-cancel"
            onClick={handleCancel}
            disabled={isSaving}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn-save"
            disabled={isSaving}
          >
            {isSaving ? '⏳ Guardando...' : '💾 Guardar Cambios'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditarActividad;
