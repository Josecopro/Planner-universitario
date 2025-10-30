import React, { useEffect, useState } from 'react';
import useSupabaseCRUD from '../../hooks/useSupabaseCRUD';
import CRUDForm from '../../components/CRUDForm/CRUDForm';
import './EntregasPage.scss';

const EntregasPage = () => {
  const {
    data: entregas,
    loading,
    error,
    fetchAll,
    create,
    update,
    remove
  } = useSupabaseCRUD('entregas');

  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [actividades, setActividades] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);

  const actividadesCRUD = useSupabaseCRUD('actividades_evaluativas');
  const estudiantesCRUD = useSupabaseCRUD('estudiantes');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      await fetchAll({
        select: '*, actividades_evaluativas(titulo), estudiantes(nombre, apellido)',
        orderBy: { column: 'fecha_entrega', ascending: false }
      });

      // Cargar actividades y estudiantes para los selects
      const actividadesData = await actividadesCRUD.fetchAll();
      const estudiantesData = await estudiantesCRUD.fetchAll();
      
      setActividades(actividadesData || []);
      setEstudiantes(estudiantesData || []);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const formFields = [
    {
      name: 'actividad_evaluativa_id',
      label: 'Actividad Evaluativa',
      type: 'select',
      required: true,
      options: actividades.map(a => ({
        value: a.id,
        label: a.titulo
      }))
    },
    {
      name: 'estudiante_id',
      label: 'Estudiante',
      type: 'select',
      required: true,
      options: estudiantes.map(e => ({
        value: e.id,
        label: `${e.nombre} ${e.apellido}`
      }))
    },
    {
      name: 'fecha_entrega',
      label: 'Fecha de Entrega',
      type: 'date',
      required: true
    },
    {
      name: 'hora_entrega',
      label: 'Hora de Entrega',
      type: 'time',
      required: false
    },
    {
      name: 'archivo_url',
      label: 'URL del Archivo',
      type: 'text',
      placeholder: 'https://...',
      help: 'URL del archivo entregado (Google Drive, OneDrive, etc.)'
    },
    {
      name: 'comentarios',
      label: 'Comentarios',
      type: 'textarea',
      rows: 4,
      placeholder: 'Comentarios adicionales sobre la entrega...'
    },
    {
      name: 'calificacion',
      label: 'Calificación',
      type: 'number',
      min: 0,
      max: 5,
      step: 0.1,
      placeholder: '0.0 - 5.0'
    },
    {
      name: 'retroalimentacion',
      label: 'Retroalimentación',
      type: 'textarea',
      rows: 3,
      placeholder: 'Retroalimentación del profesor...'
    },
    {
      name: 'entregado_tarde',
      label: 'Entregado Tarde',
      type: 'checkbox',
      defaultValue: false
    }
  ];

  const handleSubmit = async (formData) => {
    try {
      if (editingItem) {
        await update(editingItem.id, formData);
        alert('Entrega actualizada exitosamente');
      } else {
        await create(formData);
        alert('Entrega creada exitosamente');
      }
      
      setShowForm(false);
      setEditingItem(null);
      loadData();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar esta entrega?')) {
      try {
        await remove(id);
        alert('Entrega eliminada exitosamente');
        loadData();
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  if (loading && !entregas.length) {
    return <div className="loading">Cargando entregas...</div>;
  }

  return (
    <div className="entregas-page">
      <div className="page-header">
        <h1>Gestión de Entregas</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(true)}
        >
          + Nueva Entrega
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          Error: {error}
        </div>
      )}

      {showForm && (
        <div className="form-modal">
          <div className="form-container">
            <h2>{editingItem ? 'Editar Entrega' : 'Nueva Entrega'}</h2>
            <CRUDForm
              fields={formFields}
              initialData={editingItem || {}}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              loading={loading}
              submitLabel={editingItem ? 'Actualizar' : 'Crear'}
            />
          </div>
        </div>
      )}

      <div className="entregas-list">
        {entregas.length === 0 ? (
          <div className="empty-state">
            <p>No hay entregas registradas</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowForm(true)}
            >
              Crear primera entrega
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Actividad</th>
                  <th>Estudiante</th>
                  <th>Fecha</th>
                  <th>Calificación</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {entregas.map(entrega => (
                  <tr key={entrega.id}>
                    <td>{entrega.actividades_evaluativas?.titulo || 'N/A'}</td>
                    <td>
                      {entrega.estudiantes 
                        ? `${entrega.estudiantes.nombre} ${entrega.estudiantes.apellido}`
                        : 'N/A'}
                    </td>
                    <td>
                      {new Date(entrega.fecha_entrega).toLocaleDateString('es-ES')}
                      {entrega.hora_entrega && ` - ${entrega.hora_entrega}`}
                    </td>
                    <td>
                      {entrega.calificacion 
                        ? <span className="calificacion">{entrega.calificacion.toFixed(1)}</span>
                        : <span className="sin-calificar">Sin calificar</span>
                      }
                    </td>
                    <td>
                      {entrega.entregado_tarde 
                        ? <span className="badge badge-warning">Tarde</span>
                        : <span className="badge badge-success">A tiempo</span>
                      }
                    </td>
                    <td className="actions">
                      <button 
                        className="btn-icon btn-edit"
                        onClick={() => handleEdit(entrega)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button 
                        className="btn-icon btn-delete"
                        onClick={() => handleDelete(entrega.id)}
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                      {entrega.archivo_url && (
                        <a 
                          href={entrega.archivo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-icon btn-view"
                          title="Ver archivo"
                        >
                          📄
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default EntregasPage;