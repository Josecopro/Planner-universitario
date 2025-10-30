import React, { useState, useEffect } from 'react';
import './CRUDForm.scss';

/**
 * Formulario CRUD genérico y reutilizable
 * 
 * @param {Object} props
 * @param {Array} fields - Configuración de los campos del formulario
 * @param {Object} initialData - Datos iniciales (para edición)
 * @param {Function} onSubmit - Callback al enviar el formulario
 * @param {Function} onCancel - Callback al cancelar
 * @param {boolean} loading - Estado de carga
 * @param {string} submitLabel - Texto del botón de envío
 */
const CRUDForm = ({ 
  fields = [], 
  initialData = {}, 
  onSubmit, 
  onCancel, 
  loading = false,
  submitLabel = 'Guardar' 
}) => {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});

  useEffect(() => {
    // Inicializar formulario con datos existentes o valores por defecto
    const initial = {};
    fields.forEach(field => {
      initial[field.name] = initialData[field.name] || field.defaultValue || '';
    });
    setFormData(initial);
  }, [initialData, fields]);

  const validateField = (field, value) => {
    // Validación requerida
    if (field.required && !value) {
      return `${field.label} es requerido`;
    }

    // Validación de email
    if (field.type === 'email' && value && !/\S+@\S+\.\S+/.test(value)) {
      return 'Email inválido';
    }

    // Validación personalizada
    if (field.validate) {
      const error = field.validate(value, formData);
      if (error) return error;
    }

    return null;
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field.name]: value
    }));

    // Validar en tiempo real
    const error = validateField(field, value);
    setErrors(prev => ({
      ...prev,
      [field.name]: error
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validar todos los campos
    const newErrors = {};
    let hasErrors = false;

    fields.forEach(field => {
      const error = validateField(field, formData[field.name]);
      if (error) {
        newErrors[field.name] = error;
        hasErrors = true;
      }
    });

    setErrors(newErrors);

    if (hasErrors) {
      return;
    }

    // Enviar datos
    if (onSubmit) {
      await onSubmit(formData);
    }
  };

  const renderField = (field) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];

    switch (field.type) {
      case 'text':
      case 'email':
      case 'number':
      case 'password':
      case 'date':
      case 'time':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              placeholder={field.placeholder}
              disabled={loading || field.disabled}
              min={field.min}
              max={field.max}
              step={field.step}
            />
            {error && <span className="error-message">{error}</span>}
            {field.help && <span className="help-text">{field.help}</span>}
          </div>
        );

      case 'textarea':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <textarea
              id={field.name}
              name={field.name}
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              placeholder={field.placeholder}
              disabled={loading || field.disabled}
              rows={field.rows || 4}
            />
            {error && <span className="error-message">{error}</span>}
            {field.help && <span className="help-text">{field.help}</span>}
          </div>
        );

      case 'select':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <select
              id={field.name}
              name={field.name}
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              disabled={loading || field.disabled}
            >
              <option value="">Seleccione una opción</option>
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {error && <span className="error-message">{error}</span>}
            {field.help && <span className="help-text">{field.help}</span>}
          </div>
        );

      case 'checkbox':
        return (
          <div key={field.name} className="form-group form-group-checkbox">
            <label>
              <input
                type="checkbox"
                name={field.name}
                checked={!!value}
                onChange={(e) => handleChange(field, e.target.checked)}
                disabled={loading || field.disabled}
              />
              <span>{field.label}</span>
            </label>
            {error && <span className="error-message">{error}</span>}
            {field.help && <span className="help-text">{field.help}</span>}
          </div>
        );

      case 'file':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="file"
              id={field.name}
              name={field.name}
              onChange={(e) => handleChange(field, e.target.files[0])}
              disabled={loading || field.disabled}
              accept={field.accept}
            />
            {error && <span className="error-message">{error}</span>}
            {field.help && <span className="help-text">{field.help}</span>}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="crud-form">
      <div className="form-fields">
        {fields.map(field => renderField(field))}
      </div>

      <div className="form-actions">
        {onCancel && (
          <button 
            type="button" 
            onClick={onCancel} 
            className="btn btn-secondary"
            disabled={loading}
          >
            Cancelar
          </button>
        )}
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Guardando...' : submitLabel}
        </button>
      </div>
    </form>
  );
};

export default CRUDForm;