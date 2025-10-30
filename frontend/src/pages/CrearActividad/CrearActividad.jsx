import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { activitiesApi } from '../../services/api';
import './CrearActividad.scss';

const CrearActividad = () => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    grupo_id: '',
    titulo: '',
    descripcion: '',
    fecha_entrega: '',
    hora_entrega: '',
    tipo: 'Tarea',
    prioridad: 'Media',
    porcentaje: ''
  });

  const [gruposDisponibles, setGruposDisponibles] = useState([]);
  const [isCreating, setIsCreating] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadGruposProfesor();
  }, []);

  const loadGruposProfesor = async () => {
    try {
      // Obtener correo del profesor desde localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        console.warn('No se encontró información del usuario');
        return;
      }

      const user = JSON.parse(userStr);
      const correo = user.correo;

      console.log('📧 Cargando grupos del profesor:', correo);

      const { supabase } = await import('../../config/supabase');

      // Obtener el usuario
      const { data: usuario, error: userError } = await supabase
        .from('usuarios')
        .select('id')
        .eq('correo', correo)
        .single();

      if (userError || !usuario) {
        console.error('❌ Error al buscar usuario:', userError);
        return;
      }

      // Obtener el profesor
      const { data: profesor, error: profError } = await supabase
        .from('profesor')
        .select('id')
        .eq('usuario_id', usuario.id)
        .single();

      if (profError || !profesor) {
        console.error('❌ Error al buscar profesor:', profError);
        return;
      }

      // Obtener grupos del profesor con información del curso
      const { data: grupos, error: gruposError } = await supabase
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

      if (gruposError) {
        console.error('❌ Error al obtener grupos:', gruposError);
        return;
      }

      console.log('✅ Grupos cargados:', grupos);
      setGruposDisponibles(grupos || []);
    } catch (err) {
      console.error('❌ Error al cargar grupos:', err);
    }
  };

  const tiposActividad = [
    { value: 'Tarea', label: 'Tarea' },
    { value: 'Examen', label: 'Examen' },
    { value: 'Proyecto', label: 'Proyecto' },
    { value: 'Presentacion', label: 'Presentación' },
    { value: 'Laboratorio', label: 'Laboratorio' },
    { value: 'Ensayo', label: 'Ensayo' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.grupo_id) {
      newErrors.grupo_id = 'Debes seleccionar un grupo';
    }

    if (!formData.titulo.trim()) {
      newErrors.titulo = 'El título es obligatorio';
    }

    if (!formData.fecha_entrega) {
      newErrors.fecha_entrega = 'La fecha de entrega es obligatoria';
    } else {
      const selectedDate = new Date(formData.fecha_entrega);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        newErrors.fecha_entrega = 'La fecha de entrega no puede ser en el pasado';
      }
    }

    if (!formData.descripcion.trim()) {
      newErrors.descripcion = 'La descripción es obligatoria';
    }

    if (formData.porcentaje && (formData.porcentaje < 0 || formData.porcentaje > 100)) {
      newErrors.porcentaje = 'El porcentaje debe estar entre 0 y 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      try {
        setIsCreating(true);

        // Construir la fecha completa con hora si se proporciona
        let fechaCompleta = formData.fecha_entrega;
        if (formData.hora_entrega) {
          fechaCompleta = `${formData.fecha_entrega}T${formData.hora_entrega}:00`;
        } else {
          fechaCompleta = `${formData.fecha_entrega}T23:59:59`;
        }

        const activityData = {
          grupo_id: parseInt(formData.grupo_id),
          titulo: formData.titulo,
          descripcion: formData.descripcion,
          fecha_entrega: fechaCompleta,
          tipo: formData.tipo,
          prioridad: formData.prioridad,
          porcentaje: formData.porcentaje ? parseFloat(formData.porcentaje) : 0.0
        };

        console.log('📝 Enviando actividad:', activityData);

        await activitiesApi.create(activityData);
        
        alert('¡Actividad creada exitosamente!');
        
        // Limpiar formulario
        setFormData({
          grupo_id: '',
          titulo: '',
          descripcion: '',
          fecha_entrega: '',
          hora_entrega: '',
          tipo: 'Tarea',
          prioridad: 'Media',
          porcentaje: ''
        });

        navigate('/actividades');
        
      } catch (error) {
        console.error('Error al crear actividad:', error);
        alert(`Error al crear la actividad: ${error.message}`);
      } finally {
        setIsCreating(false);
      }
    }
  };

  const handleDraft = () => {
    localStorage.setItem('activityDraft', JSON.stringify(formData));
    alert('Borrador guardado');
  };

  return (
    <div className="crear-actividad-container">
      <header className="crear-actividad-header">
        <h1>Crear Nueva Actividad</h1>
        <p>Organiza tu trabajo académico de manera eficiente</p>
      </header>

      <div className="form-container">
        <form onSubmit={handleSubmit} className="activity-form">
          <div className="form-section">
            <h2>Información Básica</h2>
            
            <div className="form-group">
              <label htmlFor="grupo_id">Grupo / Curso *</label>
              <select
                id="grupo_id"
                name="grupo_id"
                value={formData.grupo_id}
                onChange={handleInputChange}
                className={errors.grupo_id ? 'error' : ''}
              >
                <option value="">Selecciona un grupo</option>
                {gruposDisponibles.map(grupo => (
                  <option key={grupo.id} value={grupo.id}>
                    {grupo.curso?.nombre || 'Sin nombre'} - {grupo.curso?.codigo || ''} (Semestre: {grupo.semestre})
                  </option>
                ))}
              </select>
              {errors.grupo_id && <span className="error-message">{errors.grupo_id}</span>}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="titulo">Título de la Actividad *</label>
                <input
                  type="text"
                  id="titulo"
                  name="titulo"
                  value={formData.titulo}
                  onChange={handleInputChange}
                  placeholder="Ej: Tarea de Cálculo Capítulo 3"
                  className={errors.titulo ? 'error' : ''}
                />
                {errors.titulo && <span className="error-message">{errors.titulo}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="tipo">Tipo de Actividad</label>
                <select
                  id="tipo"
                  name="tipo"
                  value={formData.tipo}
                  onChange={handleInputChange}
                >
                  {tiposActividad.map(tipo => (
                    <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="descripcion">Descripción *</label>
              <textarea
                id="descripcion"
                name="descripcion"
                value={formData.descripcion}
                onChange={handleInputChange}
                placeholder="Describe los detalles de la actividad..."
                rows="4"
                className={errors.descripcion ? 'error' : ''}
              />
              {errors.descripcion && <span className="error-message">{errors.descripcion}</span>}
            </div>
          </div>

          <div className="form-section">
            <h2>Fecha y Prioridad</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="fecha_entrega">Fecha de Entrega *</label>
                <input
                  type="date"
                  id="fecha_entrega"
                  name="fecha_entrega"
                  value={formData.fecha_entrega}
                  onChange={handleInputChange}
                  className={errors.fecha_entrega ? 'error' : ''}
                />
                {errors.fecha_entrega && <span className="error-message">{errors.fecha_entrega}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="hora_entrega">Hora de Entrega</label>
                <input
                  type="time"
                  id="hora_entrega"
                  name="hora_entrega"
                  value={formData.hora_entrega}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="prioridad">Prioridad</label>
                <select
                  id="prioridad"
                  name="prioridad"
                  value={formData.prioridad}
                  onChange={handleInputChange}
                >
                  <option value="Baja">Baja</option>
                  <option value="Media">Media</option>
                  <option value="Alta">Alta</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="porcentaje">Porcentaje de Calificación (%)</label>
              <input
                type="number"
                id="porcentaje"
                name="porcentaje"
                value={formData.porcentaje}
                onChange={handleInputChange}
                placeholder="Ej: 20"
                min="0"
                max="100"
                step="0.01"
                className={errors.porcentaje ? 'error' : ''}
              />
              {errors.porcentaje && <span className="error-message">{errors.porcentaje}</span>}
              <small>Peso de esta actividad en la nota final (0-100)</small>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={handleDraft} className="draft-btn">
              💾 Guardar Borrador
            </button>
            <button type="button" className="cancel-btn" onClick={() => navigate('/actividades')}>
              ❌ Cancelar
            </button>
            <button type="submit" className="submit-btn" disabled={isCreating}>
              {isCreating ? '⏳ Creando...' : '✅ Crear Actividad'}
            </button>
          </div>
        </form>

        <div className="form-sidebar">
          <div className="preview-card">
            <h3>Vista Previa</h3>
            <div className="activity-preview">
              <h4>{formData.titulo || 'Título de la actividad'}</h4>
              <p className="preview-subject">
                {gruposDisponibles.find(g => g.id === parseInt(formData.grupo_id))?.curso?.nombre || 'Selecciona un grupo'}
              </p>
              <p className="preview-description">{formData.descripcion || 'Descripción de la actividad'}</p>
              <div className="preview-badges">
                <span className={`priority-badge ${formData.prioridad.toLowerCase()}`}>
                  {formData.prioridad}
                </span>
                <span className="category-badge">{formData.tipo}</span>
              </div>
              <p className="preview-date">
                {formData.fecha_entrega ? new Date(formData.fecha_entrega).toLocaleDateString('es-ES') : 'Fecha de entrega'}
                {formData.hora_entrega && ` a las ${formData.hora_entrega}`}
              </p>
              {formData.porcentaje && (
                <p className="preview-percentage">
                  📊 Peso: {formData.porcentaje}% de la nota final
                </p>
              )}
            </div>
          </div>

          <div className="tips-card">
            <h3>💡 Consejos</h3>
            <ul>
              <li>Usa títulos descriptivos y claros</li>
              <li>Establece fechas realistas</li>
              <li>Asigna el porcentaje correcto</li>
              <li>Selecciona el tipo de actividad apropiado</li>
              <li>Proporciona una descripción detallada</li>
            </ul>
          </div>

          {gruposDisponibles.length === 0 && (
            <div className="warning-card">
              <h3>⚠️ Aviso</h3>
              <p>No tienes grupos asignados. Contacta al administrador para que te asignen grupos.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CrearActividad;
