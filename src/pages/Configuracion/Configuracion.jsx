import React, { useState } from 'react';
import './Configuracion.scss';

const Configuracion = () => {
  const [activeTab, setActiveTab] = useState('profile');
  
  const [profileData, setProfileData] = useState({
    name: 'José Coprolo',
    email: 'jose.coprolo@universidad.edu',
    career: 'Ingeniería en Sistemas',
    semester: 6,
    studentId: '2021-0123',
    phone: '+1 (555) 123-4567',
    bio: 'Estudiante de Ingeniería en Sistemas apasionado por el desarrollo web y la inteligencia artificial.'
  });

  const [preferences, setPreferences] = useState({
    theme: 'light',
    language: 'es',
    notifications: {
      email: true,
      push: true,
      reminders: true,
      deadlines: true,
      chat: false
    },
    privacy: {
      profileVisible: true,
      showEmail: false,
      showPhone: false
    }
  });

  const [security, setSecurity] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    twoFactorEnabled: false
  });

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreferenceChange = (section, key, value) => {
    setPreferences(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  const handleSecurityChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSecurity(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSaveProfile = (e) => {
    e.preventDefault();
    console.log('Guardando perfil:', profileData);
    alert('Perfil actualizado exitosamente');
  };

  const handleSavePreferences = () => {
    console.log('Guardando preferencias:', preferences);
    alert('Preferencias guardadas exitosamente');
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    if (security.newPassword !== security.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }
    console.log('Cambiando contraseña');
    alert('Contraseña actualizada exitosamente');
    setSecurity({
      ...security,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  const tabs = [
    { id: 'profile', label: '👤 Perfil', icon: '👤' },
    { id: 'preferences', label: '⚙️ Preferencias', icon: '⚙️' },
    { id: 'notifications', label: '🔔 Notificaciones', icon: '🔔' },
    { id: 'security', label: '🔒 Seguridad', icon: '🔒' },
    { id: 'data', label: '📊 Datos', icon: '📊' }
  ];

  return (
    <div className="configuracion-container">
      <header className="configuracion-header">
        <h1>Configuración</h1>
        <p>Personaliza tu experiencia en el planner universitario</p>
      </header>

      <div className="configuracion-content">
        <nav className="config-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label.replace(/^\S+\s/, '')}</span>
            </button>
          ))}
        </nav>

        <div className="config-content">
          {activeTab === 'profile' && (
            <div className="config-section">
              <h2>Información del Perfil</h2>
              <form onSubmit={handleSaveProfile} className="profile-form">
                <div className="profile-header">
                  <div className="avatar-section">
                    <div className="avatar">
                      {profileData.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </div>
                    <button type="button" className="change-avatar-btn">Cambiar Foto</button>
                  </div>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label htmlFor="name">Nombre Completo</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={profileData.name}
                      onChange={handleProfileChange}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="email">Correo Electrónico</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={profileData.email}
                      onChange={handleProfileChange}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="career">Carrera</label>
                    <input
                      type="text"
                      id="career"
                      name="career"
                      value={profileData.career}
                      onChange={handleProfileChange}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="semester">Semestre</label>
                    <select
                      id="semester"
                      name="semester"
                      value={profileData.semester}
                      onChange={handleProfileChange}
                    >
                      {[1,2,3,4,5,6,7,8,9,10].map(sem => (
                        <option key={sem} value={sem}>Semestre {sem}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="studentId">ID Estudiante</label>
                    <input
                      type="text"
                      id="studentId"
                      name="studentId"
                      value={profileData.studentId}
                      onChange={handleProfileChange}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="phone">Teléfono</label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      value={profileData.phone}
                      onChange={handleProfileChange}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="bio">Biografía</label>
                  <textarea
                    id="bio"
                    name="bio"
                    value={profileData.bio}
                    onChange={handleProfileChange}
                    rows="3"
                    placeholder="Cuéntanos sobre ti..."
                  />
                </div>

                <button type="submit" className="save-btn">Guardar Cambios</button>
              </form>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="config-section">
              <h2>Preferencias de la Aplicación</h2>
              
              <div className="preference-group">
                <h3>Apariencia</h3>
                <div className="preference-item">
                  <label>Tema</label>
                  <select
                    value={preferences.theme}
                    onChange={(e) => handlePreferenceChange('', 'theme', e.target.value)}
                  >
                    <option value="light">Claro</option>
                    <option value="dark">Oscuro</option>
                    <option value="auto">Automático</option>
                  </select>
                </div>
              </div>

              <div className="preference-group">
                <h3>Idioma</h3>
                <div className="preference-item">
                  <label>Idioma de la interfaz</label>
                  <select
                    value={preferences.language}
                    onChange={(e) => handlePreferenceChange('', 'language', e.target.value)}
                  >
                    <option value="es">Español</option>
                    <option value="en">English</option>
                    <option value="fr">Français</option>
                  </select>
                </div>
              </div>

              <div className="preference-group">
                <h3>Privacidad</h3>
                <div className="preference-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.privacy.profileVisible}
                      onChange={(e) => handlePreferenceChange('privacy', 'profileVisible', e.target.checked)}
                    />
                    Perfil visible para otros estudiantes
                  </label>
                </div>
                <div className="preference-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.privacy.showEmail}
                      onChange={(e) => handlePreferenceChange('privacy', 'showEmail', e.target.checked)}
                    />
                    Mostrar correo electrónico
                  </label>
                </div>
                <div className="preference-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.privacy.showPhone}
                      onChange={(e) => handlePreferenceChange('privacy', 'showPhone', e.target.checked)}
                    />
                    Mostrar número de teléfono
                  </label>
                </div>
              </div>

              <button onClick={handleSavePreferences} className="save-btn">
                Guardar Preferencias
              </button>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="config-section">
              <h2>Configuración de Notificaciones</h2>
              
              <div className="notification-group">
                <h3>Tipos de Notificación</h3>
                <div className="notification-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.notifications.email}
                      onChange={(e) => handlePreferenceChange('notifications', 'email', e.target.checked)}
                    />
                    <div className="notification-info">
                      <span className="notification-title">Notificaciones por Email</span>
                      <span className="notification-desc">Recibe actualizaciones importantes por correo</span>
                    </div>
                  </label>
                </div>

                <div className="notification-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.notifications.push}
                      onChange={(e) => handlePreferenceChange('notifications', 'push', e.target.checked)}
                    />
                    <div className="notification-info">
                      <span className="notification-title">Notificaciones Push</span>
                      <span className="notification-desc">Notificaciones instantáneas en el navegador</span>
                    </div>
                  </label>
                </div>

                <div className="notification-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.notifications.reminders}
                      onChange={(e) => handlePreferenceChange('notifications', 'reminders', e.target.checked)}
                    />
                    <div className="notification-info">
                      <span className="notification-title">Recordatorios de Tareas</span>
                      <span className="notification-desc">Alertas sobre tareas próximas a vencer</span>
                    </div>
                  </label>
                </div>

                <div className="notification-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.notifications.deadlines}
                      onChange={(e) => handlePreferenceChange('notifications', 'deadlines', e.target.checked)}
                    />
                    <div className="notification-info">
                      <span className="notification-title">Fechas Límite</span>
                      <span className="notification-desc">Avisos sobre fechas de entrega importantes</span>
                    </div>
                  </label>
                </div>

                <div className="notification-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={preferences.notifications.chat}
                      onChange={(e) => handlePreferenceChange('notifications', 'chat', e.target.checked)}
                    />
                    <div className="notification-info">
                      <span className="notification-title">Mensajes de Chat</span>
                      <span className="notification-desc">Notificaciones de nuevos mensajes</span>
                    </div>
                  </label>
                </div>
              </div>

              <button onClick={handleSavePreferences} className="save-btn">
                Guardar Configuración
              </button>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="config-section">
              <h2>Seguridad de la Cuenta</h2>
              
              <form onSubmit={handleChangePassword} className="security-form">
                <h3>Cambiar Contraseña</h3>
                <div className="form-group">
                  <label htmlFor="currentPassword">Contraseña Actual</label>
                  <input
                    type="password"
                    id="currentPassword"
                    name="currentPassword"
                    value={security.currentPassword}
                    onChange={handleSecurityChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="newPassword">Nueva Contraseña</label>
                  <input
                    type="password"
                    id="newPassword"
                    name="newPassword"
                    value={security.newPassword}
                    onChange={handleSecurityChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirmar Nueva Contraseña</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={security.confirmPassword}
                    onChange={handleSecurityChange}
                  />
                </div>

                <button type="submit" className="save-btn">Cambiar Contraseña</button>
              </form>

              <div className="security-options">
                <h3>Opciones de Seguridad</h3>
                <div className="security-item">
                  <label>
                    <input
                      type="checkbox"
                      name="twoFactorEnabled"
                      checked={security.twoFactorEnabled}
                      onChange={handleSecurityChange}
                    />
                    <div className="security-info">
                      <span className="security-title">Autenticación de dos factores</span>
                      <span className="security-desc">Añade una capa extra de seguridad a tu cuenta</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="config-section">
              <h2>Gestión de Datos</h2>
              
              <div className="data-section">
                <h3>Exportar Datos</h3>
                <p>Descarga una copia de todos tus datos del planner universitario.</p>
                <button className="export-btn">📄 Exportar Datos</button>
              </div>

              <div className="data-section danger-zone">
                <h3>Zona de Peligro</h3>
                <p>Las siguientes acciones son irreversibles. Procede con precaución.</p>
                
                <div className="danger-actions">
                  <button className="danger-btn">🗑️ Eliminar Todas las Actividades</button>
                  <button className="danger-btn">❌ Eliminar Cuenta</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Configuracion;
