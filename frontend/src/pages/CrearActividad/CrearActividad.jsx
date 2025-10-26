import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, activitiesApi } from '../../services/api';
import './CrearActividad.scss';

const CrearActividad = () => {
  const navigate = useNavigate();
  const { mutate, loading: isCreating } = useMutation();
  
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    description: '',
    dueDate: '',
    dueTime: '',
    priority: 'medium',
    category: 'tarea',
    estimatedHours: '',
    tags: [],
    reminders: [],
    attachments: []
  });

  const [newTag, setNewTag] = useState('');
  const [errors, setErrors] = useState({});

  const subjects = [
    'Cálculo I',
    'Historia Universal',
    'Química Orgánica',
    'Programación',
    'Marketing Digital',
    'Física',
    'Literatura',
    'Inglés',
    'Estadística',
    'Otra'
  ];

  const categories = [
    { value: 'tarea', label: 'Tarea' },
    { value: 'examen', label: 'Examen' },
    { value: 'proyecto', label: 'Proyecto' },
    { value: 'presentacion', label: 'Presentación' },
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'ensayo', label: 'Ensayo' },
    { value: 'investigacion', label: 'Investigación' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleAddTag = (e) => {
    if (e) e.preventDefault();
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const addReminder = () => {
    const newReminder = {
      id: Date.now(),
      type: 'email',
      time: '1-day',
      message: 'Recordatorio de actividad pendiente'
    };
    setFormData(prev => ({
      ...prev,
      reminders: [...prev.reminders, newReminder]
    }));
  };

  const removeReminder = (id) => {
    setFormData(prev => ({
      ...prev,
      reminders: prev.reminders.filter(reminder => reminder.id !== id)
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'El título es obligatorio';
    }

    if (!formData.subject.trim()) {
      newErrors.subject = 'La materia es obligatoria';
    }

    if (!formData.dueDate) {
      newErrors.dueDate = 'La fecha de entrega es obligatoria';
    } else {
      const selectedDate = new Date(formData.dueDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        newErrors.dueDate = 'La fecha de entrega no puede ser en el pasado';
      }
    }

    if (!formData.description.trim()) {
      newErrors.description = 'La descripción es obligatoria';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      try {
        const activityData = {
          title: formData.title,
          subject: formData.subject,
          description: formData.description,
          due_date: formData.dueDate,
          priority: formData.priority,
          status: 'pending',
          category: formData.category,
          estimated_hours: formData.estimatedHours ? parseInt(formData.estimatedHours) : null,
          tags: formData.tags
        };

        await mutate(() => activitiesApi.create(activityData));
        
        alert('¡Actividad creada exitosamente!');
        
        setFormData({
          title: '',
          subject: '',
          description: '',
          dueDate: '',
          dueTime: '',
          priority: 'medium',
          category: 'tarea',
          estimatedHours: '',
          tags: [],
          reminders: [],
          attachments: []
        });

        navigate('/actividades');
        
      } catch (error) {
        console.error('Error al crear actividad:', error);
        alert(`Error al crear la actividad: ${error.message}`);
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
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title">Título de la Actividad *</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Ej: Tarea de Cálculo Capítulo 3"
                  className={errors.title ? 'error' : ''}
                />
                {errors.title && <span className="error-message">{errors.title}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="subject">Materia *</label>
                <select
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  className={errors.subject ? 'error' : ''}
                >
                  <option value="">Selecciona una materia</option>
                  {subjects.map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
                {errors.subject && <span className="error-message">{errors.subject}</span>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="description">Descripción *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe los detalles de la actividad..."
                rows="4"
                className={errors.description ? 'error' : ''}
              />
              {errors.description && <span className="error-message">{errors.description}</span>}
            </div>
          </div>

          <div className="form-section">
            <h2>Fecha y Prioridad</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="dueDate">Fecha de Entrega *</label>
                <input
                  type="date"
                  id="dueDate"
                  name="dueDate"
                  value={formData.dueDate}
                  onChange={handleInputChange}
                  className={errors.dueDate ? 'error' : ''}
                />
                {errors.dueDate && <span className="error-message">{errors.dueDate}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="dueTime">Hora de Entrega</label>
                <input
                  type="time"
                  id="dueTime"
                  name="dueTime"
                  value={formData.dueTime}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="priority">Prioridad</label>
                <select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                >
                  <option value="low">Baja</option>
                  <option value="medium">Media</option>
                  <option value="high">Alta</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Categorización</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category">Tipo de Actividad</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="estimatedHours">Horas Estimadas</label>
                <input
                  type="number"
                  id="estimatedHours"
                  name="estimatedHours"
                  value={formData.estimatedHours}
                  onChange={handleInputChange}
                  placeholder="Ej: 3"
                  min="0.5"
                  step="0.5"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Etiquetas</label>
              <div className="tags-input">
                <div className="tags-display">
                  {formData.tags.map(tag => (
                    <span key={tag} className="tag">
                      {tag}
                      <button type="button" onClick={() => handleRemoveTag(tag)}>×</button>
                    </span>
                  ))}
                </div>
                <div className="add-tag-form">
                  <input
                    type="text"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Agregar etiqueta..."
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddTag(e);
                      }
                    }}
                  />
                  <button type="button" onClick={handleAddTag}>+</button>
                </div>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Recordatorios</h2>
            
            <div className="reminders-section">
              {formData.reminders.map(reminder => (
                <div key={reminder.id} className="reminder-item">
                  <span>Recordatorio por email 1 día antes</span>
                  <button type="button" onClick={() => removeReminder(reminder.id)}>×</button>
                </div>
              ))}
              <button type="button" onClick={addReminder} className="add-reminder-btn">
                + Agregar Recordatorio
              </button>
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
              <h4>{formData.title || 'Título de la actividad'}</h4>
              <p className="preview-subject">{formData.subject || 'Materia'}</p>
              <p className="preview-description">{formData.description || 'Descripción de la actividad'}</p>
              <div className="preview-badges">
                <span className={`priority-badge ${formData.priority}`}>
                  {formData.priority === 'high' ? 'Alta' : formData.priority === 'medium' ? 'Media' : 'Baja'}
                </span>
                <span className="category-badge">{categories.find(c => c.value === formData.category)?.label}</span>
              </div>
              <p className="preview-date">
                {formData.dueDate ? new Date(formData.dueDate).toLocaleDateString('es-ES') : 'Fecha de entrega'}
              </p>
            </div>
          </div>

          <div className="tips-card">
            <h3>💡 Consejos</h3>
            <ul>
              <li>Usa títulos descriptivos y claros</li>
              <li>Establece fechas realistas</li>
              <li>Agrega etiquetas para organizar mejor</li>
              <li>Estima el tiempo necesario</li>
              <li>Configura recordatorios útiles</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrearActividad;
