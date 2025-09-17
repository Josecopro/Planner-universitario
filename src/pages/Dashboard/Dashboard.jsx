import React, { useState, useEffect } from 'react';
import './Dashboard.scss';

const Dashboard = () => {
  const [stats, setStats] = useState({
    pendingTasks: 5,
    completedTasks: 12,
    totalSubjects: 6,
    upcomingDeadlines: 3
  });

  const [recentActivities, setRecentActivities] = useState([
    { id: 1, title: 'Tarea de Matemáticas', subject: 'Cálculo I', dueDate: '2025-09-20', status: 'pending' },
    { id: 2, title: 'Ensayo de Historia', subject: 'Historia Universal', dueDate: '2025-09-22', status: 'in-progress' },
    { id: 3, title: 'Práctica de Química', subject: 'Química Orgánica', dueDate: '2025-09-18', status: 'completed' }
  ]);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Resumen de tu progreso académico</p>
      </header>

      <main className="dashboard-main">
        <section className="stats-section">
          <div className="stat-card pending">
            <div className="stat-number">{stats.pendingTasks}</div>
            <div className="stat-label">Tareas Pendientes</div>
          </div>
          
          <div className="stat-card completed">
            <div className="stat-number">{stats.completedTasks}</div>
            <div className="stat-label">Tareas Completadas</div>
          </div>
          
          <div className="stat-card subjects">
            <div className="stat-number">{stats.totalSubjects}</div>
            <div className="stat-label">Materias Activas</div>
          </div>
          
          <div className="stat-card deadlines">
            <div className="stat-number">{stats.upcomingDeadlines}</div>
            <div className="stat-label">Fechas Próximas</div>
          </div>
        </section>

        <section className="content-section">
          <div className="recent-activities">
            <h2>Actividades Recientes</h2>
            <div className="activities-list">
              {recentActivities.map(activity => (
                <div key={activity.id} className={`activity-item ${activity.status}`}>
                  <div className="activity-info">
                    <h3>{activity.title}</h3>
                    <p>{activity.subject}</p>
                    <span className="due-date">Vence: {activity.dueDate}</span>
                  </div>
                  <div className={`status-badge ${activity.status}`}>
                    {activity.status === 'completed' ? 'Completada' : 
                     activity.status === 'in-progress' ? 'En Progreso' : 'Pendiente'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="quick-actions">
            <h2>Acciones Rápidas</h2>
            <div className="actions-grid">
              <button className="action-btn create-task">
                <span className="action-icon">📝</span>
                Nueva Actividad
              </button>
              <button className="action-btn view-calendar">
                <span className="action-icon">📅</span>
                Ver Calendario
              </button>
              <button className="action-btn chat">
                <span className="action-icon">💬</span>
                Abrir Chat
              </button>
              <button className="action-btn settings">
                <span className="action-icon">⚙️</span>
                Configuración
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
