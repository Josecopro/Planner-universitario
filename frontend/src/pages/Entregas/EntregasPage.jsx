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
  } = useSupabaseCRUD('Entrega');

  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [actividades, setActividades] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);

  const actividadesCRUD = useSupabaseCRUD('ActividadEvaluativa');
  const estudiantesCRUD = useSupabaseCRUD('Estudiante');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      await fetchAll({
        select: `
          id,
          actividad_id,
          inscripcion_id,
          fecha_entrega,
          estado,
          texto_entrega,
          archivos_adjuntos,
          ActividadEvaluativa(id, titulo, descripcion),
          Inscripcion(
            id,
            estudiante_id,
            Estudiante(id, usuario_id, Usuarios(nombre, apellido))
          )
        `,
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
      name: 'actividad_id',
      label: 'Actividad Evaluativa',
      type: 'select',
      required: true,
      options: actividades.map(a => ({
        value: a.id,
        label: a.titulo
      }))
    },
    {
      name: 'inscripcion_id',
      label: 'Estudiante (Inscripción)',
      type: 'select',
      required: true,
      options: estudiantes.map(e => {
        const usuario = e.Usuarios || {};
        return {
          value: e.id,
          label: `${usuario.nombre || ''} ${usuario.apellido || ''}`
        };
      })
    },
    {
      name: 'fecha_entrega',
      label: 'Fecha de Entrega',
      type: 'datetime-local',
      required: true
    },
    {
      name: 'estado',
      label: 'Estado',
      type: 'select',
      required: true,
      options: [
        { value: 'Entregada', label: 'Entregada' },
        { value: 'Pendiente', label: 'Pendiente' },
        { value: 'Revisada', label: 'Revisada' }
      ],
      defaultValue: 'Entregada'
    },
    {
      name: 'texto_entrega',
      label: 'Texto/Descripción de la Entrega',
      type: 'textarea',
      rows: 4,
      placeholder: 'Escribe aquí el contenido de la entrega...'
    },
    {
      name: 'archivos_adjuntos',
      label: 'URLs de Archivos Adjuntos',
      type: 'textarea',
      rows: 3,
      placeholder: 'Una URL por línea (https://...)',
      help: 'Puedes agregar múltiples URLs de archivos separadas por líneas'
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
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {entregas.map(entrega => {
                  const actividad = entrega.ActividadEvaluativa || {};
                  const inscripcion = entrega.Inscripcion || {};
                  const estudiante = inscripcion.Estudiante || {};
                  const usuario = estudiante.Usuarios || {};
                  
                  return (
                    <tr key={entrega.id}>
                      <td>{actividad.titulo || 'N/A'}</td>
                      <td>
                        {usuario.nombre && usuario.apellido
                          ? `${usuario.nombre} ${usuario.apellido}`
                          : 'N/A'}
                      </td>
                      <td>
                        {new Date(entrega.fecha_entrega).toLocaleDateString('es-ES', { timeZone: 'UTC' })}
                      </td>
                      <td>
                        <span className={`estado estado-${entrega.estado?.toLowerCase() || 'pendiente'}`}>
                          {entrega.estado || 'Pendiente'}
                        </span>
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
                        {entrega.archivos_adjuntos && entrega.archivos_adjuntos.length > 0 && (
                          <button 
                            className="btn-icon btn-view"
                            onClick={() => alert(`Archivos:\n${entrega.archivos_adjuntos.join('\n')}`)}
                            title="Ver archivos"
                          >
                            📄
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default EntregasPage;