import React, { useState } from 'react';
import './Configuracion.scss';

const Configuracion = () => {
  // Estado para los datos del perfil
  const [profileData, setProfileData] = useState({
    name: 'Laura Mejía',
    email: 'Laura.Mejia@udemedellin.edu.co',
    role: 'Coordinadora académica'
  });

  // Estado para las preferencias de notificaciones
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    platformAlerts: false,
    automaticReminders: true
  });

  // Manejadores de eventos
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleNotificationToggle = (key) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSaveProfile = (e) => {
    e.preventDefault();
    console.log('Guardando perfil:', profileData);
    alert('Perfil actualizado exitosamente');
  };

  return (
    <div className="configuracion">
      <div className="configuracion__container">
        
        {/* Sección de Perfil de Usuario */}
        <section className="configuracion__section">
          <h2 className="configuracion__section-title">Perfil de Usuario</h2>
          
          <div className="configuracion__profile-card">
            <div className="configuracion__profile-avatar">
              <div className="configuracion__avatar-placeholder">
                <span className="configuracion__avatar-icon">👤</span>
              </div>
              <button className="configuracion__change-photo">Cambiar foto</button>
            </div>

            <form className="configuracion__profile-form" onSubmit={handleSaveProfile}>
              <div className="configuracion__form-row">
                <div className="configuracion__form-field">
                  <label className="configuracion__form-label">Nombre completo</label>
                  <input
                    type="text"
                    name="name"
                    value={profileData.name}
                    onChange={handleProfileChange}
                    className="configuracion__form-input"
                  />
                </div>

                <div className="configuracion__form-field">
                  <label className="configuracion__form-label">Correo institucional</label>
                  <input
                    type="email"
                    name="email"
                    value={profileData.email}
                    onChange={handleProfileChange}
                    className="configuracion__form-input"
                  />
                </div>
              </div>

              <div className="configuracion__form-field">
                <label className="configuracion__form-label">Rol</label>
                <select
                  name="role"
                  value={profileData.role}
                  onChange={handleProfileChange}
                  className="configuracion__form-select"
                >
                  <option value="Profesor">Profesor</option>
                  <option value="Estudiante">Estudiante</option>
                  <option value="Administrativo">Administrativo</option>
                  <option value="Coordinadora académica">Coordinadora académica</option>
                </select>
              </div>

              <button type="submit" className="configuracion__btn configuracion__btn--primary">
                Editar perfil
              </button>
            </form>
          </div>
        </section>

        {/* Sección de Preferencias de Notificaciones */}
        <section className="configuracion__section">
          <h2 className="configuracion__section-title">Preferencias de Notificaciones</h2>
          
          <div className="configuracion__notifications-card">
            <div className="configuracion__notification-item">
              <div className="configuracion__notification-content">
                <h3 className="configuracion__notification-title">Notificaciones por correo</h3>
                <p className="configuracion__notification-description">Recibir actualizaciones por email</p>
              </div>
              <div className="configuracion__notification-toggle">
                <label className="configuracion__toggle-switch">
                  <input
                    type="checkbox"
                    checked={notifications.emailNotifications}
                    onChange={() => handleNotificationToggle('emailNotifications')}
                  />
                  <span className="configuracion__toggle-slider"></span>
                </label>
              </div>
            </div>

            <div className="configuracion__notification-item">
              <div className="configuracion__notification-content">
                <h3 className="configuracion__notification-title">Alertas dentro de la plataforma</h3>
                <p className="configuracion__notification-description">Notificaciones en tiempo real</p>
              </div>
              <div className="configuracion__notification-toggle">
                <label className="configuracion__toggle-switch">
                  <input
                    type="checkbox"
                    checked={notifications.platformAlerts}
                    onChange={() => handleNotificationToggle('platformAlerts')}
                  />
                  <span className="configuracion__toggle-slider"></span>
                </label>
              </div>
            </div>

            <div className="configuracion__notification-item">
              <div className="configuracion__notification-content">
                <h3 className="configuracion__notification-title">Recordatorios automáticos</h3>
                <p className="configuracion__notification-description">Alertas de entregas pendientes</p>
              </div>
              <div className="configuracion__notification-toggle">
                <label className="configuracion__toggle-switch">
                  <input
                    type="checkbox"
                    checked={notifications.automaticReminders}
                    onChange={() => handleNotificationToggle('automaticReminders')}
                  />
                  <span className="configuracion__toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </section>

        {/* Sección de Seguridad */}
        <section className="configuracion__section">
          <h2 className="configuracion__section-title">Seguridad</h2>
          
          <div className="configuracion__security-card">
            <div className="configuracion__security-item">
              <div className="configuracion__security-content">
                <h3 className="configuracion__security-title">Cambiar contraseña</h3>
                <p className="configuracion__security-description">Actualiza tu contraseña regularmente</p>
              </div>
              <button className="configuracion__btn configuracion__btn--secondary">Cambiar</button>
            </div>

            <div className="configuracion__security-item">
              <div className="configuracion__security-content">
                <h3 className="configuracion__security-title">Autenticación en dos pasos</h3>
                <p className="configuracion__security-description">Mayor seguridad para tu cuenta</p>
              </div>
              <button className="configuracion__btn configuracion__btn--secondary">Configurar</button>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default Configuracion;
