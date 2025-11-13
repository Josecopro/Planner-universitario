import React, { useState, useEffect } from 'react';
import { usuariosApi } from '../../services/api';
import './Usuarios.scss';

const Usuarios = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  
  // Estado para crear/editar usuario
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    correo: '',
    password: '',
    rol_id: '',
    activo: true
  });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadUsuarios();
    loadRoles();
  }, []);

  const loadUsuarios = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await usuariosApi.getAll();
      setUsuarios(data);
    } catch (err) {
      console.error('Error al cargar usuarios:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const data = await usuariosApi.getRoles();
      setRoles(data);
    } catch (err) {
      console.error('Error al cargar roles:', err);
    }
  };

  const handleOpenModal = (user = null) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        nombre: user.nombre,
        apellido: user.apellido,
        correo: user.correo,
        password: '', // No mostramos la contraseña
        rol_id: user.rol_id,
        activo: user.activo ?? true
      });
    } else {
      setEditingUser(null);
      setFormData({
        nombre: '',
        apellido: '',
        correo: '',
        password: '',
        rol_id: '',
        activo: true
      });
    }
    setFormErrors({});
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingUser(null);
    setFormData({
      nombre: '',
      apellido: '',
      correo: '',
      password: '',
      rol_id: '',
      activo: true
    });
    setFormErrors({});
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es obligatorio';
    }

    if (!formData.apellido.trim()) {
      errors.apellido = 'El apellido es obligatorio';
    }

    if (!formData.correo.trim()) {
      errors.correo = 'El correo es obligatorio';
    } else if (!/\S+@\S+\.\S+/.test(formData.correo)) {
      errors.correo = 'El correo no es válido';
    }

    if (!editingUser && !formData.password) {
      errors.password = 'La contraseña es obligatoria';
    }

    if (formData.password && formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    if (!formData.rol_id) {
      errors.rol_id = 'Debes seleccionar un rol';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);

      if (editingUser) {
        // Actualizar usuario
        const updateData = {
          nombre: formData.nombre,
          apellido: formData.apellido,
          correo: formData.correo,
          rol_id: parseInt(formData.rol_id)
        };

        // Solo incluir password si se proporcionó
        if (formData.password) {
          updateData.password = formData.password;
        }

        await usuariosApi.update(editingUser.id, updateData);
        alert('Usuario actualizado correctamente');
      } else {
        // Crear usuario
        const createData = {
          nombre: formData.nombre,
          apellido: formData.apellido,
          correo: formData.correo,
          password: formData.password,
          rol_id: parseInt(formData.rol_id)
        };

        await usuariosApi.create(createData);
        alert('Usuario creado correctamente');
      }

      handleCloseModal();
      await loadUsuarios();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (userId, nombre) => {
    if (!window.confirm(`¿Estás seguro de eliminar al usuario ${nombre}?`)) {
      return;
    }

    try {
      await usuariosApi.delete(userId);
      alert('Usuario eliminado correctamente');
      await loadUsuarios();
    } catch (err) {
      alert(`Error al eliminar: ${err.message}`);
    }
  };

  const filteredUsuarios = usuarios.filter(user => {
    const matchSearch = 
      user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.apellido.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.correo.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchRole = filterRole === 'all' || user.rol_id === parseInt(filterRole);

    return matchSearch && matchRole;
  });

  if (loading) {
    return (
      <div className="usuarios-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando usuarios...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="usuarios-container">
        <div className="error-state">
          <h2>Error al cargar usuarios</h2>
          <p>{error.message}</p>
          <button onClick={loadUsuarios} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="usuarios-container">
      <header className="usuarios-header">
        <div className="header-content">
          <h1>👥 Gestión de Usuarios</h1>
          <p>Administra todos los usuarios del sistema</p>
        </div>
        <button className="create-user-btn" onClick={() => handleOpenModal()}>
          + Crear Usuario
        </button>
      </header>

      <div className="controls-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="🔍 Buscar por nombre, apellido o correo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filters">
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos los roles</option>
            {roles.map(rol => (
              <option key={rol.id} value={rol.id}>{rol.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="users-stats">
        <div className="stat-card">
          <div className="stat-number">{usuarios.length}</div>
          <div className="stat-label">Total Usuarios</div>
        </div>
        {roles.map(rol => (
          <div key={rol.id} className="stat-card">
            <div className="stat-number">{usuarios.filter(u => u.rol_id === rol.id).length}</div>
            <div className="stat-label">{rol.nombre}s</div>
          </div>
        ))}
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Apellido</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsuarios.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.nombre}</td>
                <td>{user.apellido}</td>
                <td>{user.correo}</td>
                <td>
                  <span className={`role-badge role-${user.rol_nombre?.toLowerCase()}`}>
                    {user.rol_nombre}
                  </span>
                </td>
                <td className="actions-cell">
                  <button
                    className="action-btn edit"
                    onClick={() => handleOpenModal(user)}
                    title="Editar usuario"
                  >
                    ✏️
                  </button>
                  <button
                    className="action-btn delete"
                    onClick={() => handleDelete(user.id, `${user.nombre} ${user.apellido}`)}
                    title="Eliminar usuario"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredUsuarios.length === 0 && (
          <div className="no-results">
            <p>No se encontraron usuarios que coincidan con tu búsqueda</p>
          </div>
        )}
      </div>

      {/* Modal Crear/Editar Usuario */}
      {modalOpen && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingUser ? '✏️ Editar Usuario' : '➕ Crear Usuario'}</h3>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>

            <form onSubmit={handleSubmit} className="user-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="nombre">Nombre *</label>
                  <input
                    type="text"
                    id="nombre"
                    name="nombre"
                    value={formData.nombre}
                    onChange={handleInputChange}
                    className={formErrors.nombre ? 'error' : ''}
                    placeholder="Nombre"
                  />
                  {formErrors.nombre && <span className="error-message">{formErrors.nombre}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="apellido">Apellido *</label>
                  <input
                    type="text"
                    id="apellido"
                    name="apellido"
                    value={formData.apellido}
                    onChange={handleInputChange}
                    className={formErrors.apellido ? 'error' : ''}
                    placeholder="Apellido"
                  />
                  {formErrors.apellido && <span className="error-message">{formErrors.apellido}</span>}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="correo">Correo Electrónico *</label>
                <input
                  type="email"
                  id="correo"
                  name="correo"
                  value={formData.correo}
                  onChange={handleInputChange}
                  className={formErrors.correo ? 'error' : ''}
                  placeholder="usuario@ejemplo.com"
                />
                {formErrors.correo && <span className="error-message">{formErrors.correo}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  Contraseña {editingUser ? '(Dejar vacío para mantener actual)' : '*'}
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={formErrors.password ? 'error' : ''}
                  placeholder={editingUser ? 'Nueva contraseña (opcional)' : 'Mínimo 6 caracteres'}
                />
                {formErrors.password && <span className="error-message">{formErrors.password}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="rol_id">Rol *</label>
                <select
                  id="rol_id"
                  name="rol_id"
                  value={formData.rol_id}
                  onChange={handleInputChange}
                  className={formErrors.rol_id ? 'error' : ''}
                >
                  <option value="">Selecciona un rol</option>
                  {roles.map(rol => (
                    <option key={rol.id} value={rol.id}>{rol.nombre}</option>
                  ))}
                </select>
                {formErrors.rol_id && <span className="error-message">{formErrors.rol_id}</span>}
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={handleCloseModal}>
                  Cancelar
                </button>
                <button type="submit" className="btn-submit" disabled={submitting}>
                  {submitting ? '⏳ Guardando...' : editingUser ? '💾 Actualizar' : '➕ Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Usuarios;
