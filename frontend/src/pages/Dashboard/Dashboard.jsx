import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useApi } from '../../services/api';
import { dashboardApi } from '../../services/api';
import './Dashboard.scss';

const Dashboard = () => {
  // Usar el hook personalizado para obtener datos del dashboard
  const { data: dashboardData, loading, error, refetch } = useApi(() => dashboardApi.getData());

  // Mostrar estado de carga
  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard__loading">
          <div className="spinner"></div>
          <p>Cargando datos del dashboard...</p>
        </div>
      </div>
    );
  }

  // Mostrar error si ocurre
  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard__error">
          <h2>Error al cargar datos</h2>
          <p>{error.message}</p>
          <button onClick={refetch} className="retry-button">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  // Extraer datos de la respuesta de la API
  const stats = dashboardData?.stats || {};
  const weeklyProgressData = dashboardData?.weekly_progress || [];
  const gradeDistributionData = dashboardData?.grade_distribution || [];
  const alerts = dashboardData?.alerts || [];

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1 className="dashboard__title">Dashboard de Desempeño</h1>
        <div className="dashboard__period-selector">
          <select className="dashboard__select">
            <option>Último mes</option>
            <option>Últimos 3 meses</option>
            <option>Último semestre</option>
          </select>
          <button onClick={refetch} className="refresh-button" title="Actualizar datos">
            🔄
          </button>
        </div>
      </header>

      <main className="dashboard__main">
        {/* Stats Cards */}
        <section className="dashboard__stats">
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Estudiantes Activos</div>
              <div className="stat-card__number">{stats.active_students || 0}</div>
            </div>
            <div className="stat-card__icon">👥</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Promedio General</div>
              <div className="stat-card__number">{stats.general_average || 0}</div>
            </div>
            <div className="stat-card__icon">📊</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Entregas Pendientes</div>
              <div className="stat-card__number">{stats.pending_submissions || 0}</div>
            </div>
            <div className="stat-card__icon">⏰</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Asistencia</div>
              <div className="stat-card__number">{stats.attendance || 0}%</div>
            </div>
            <div className="stat-card__icon">📋</div>
          </div>
        </section>

        {/* Charts Section */}
        <section className="dashboard__charts">
          <div className="chart-container">
            <h3 className="chart-container__title">Progreso Semanal</h3>
            <div className="chart-container__content">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyProgressData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="week" stroke="#718096" />
                  <YAxis stroke="#718096" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#932428" 
                    strokeWidth={3}
                    dot={{ fill: '#932428', strokeWidth: 2, r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-container">
            <h3 className="chart-container__title">Distribución de Calificaciones</h3>
            <div className="chart-container__content">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={gradeDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {gradeDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* Alerts Section */}
        <section className="dashboard__alerts">
          <h3 className="dashboard__alerts-title">Alertas y Notificaciones</h3>
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-item alert-item--${alert.type}`}>
                <div className="alert-item__icon">
                  {alert.type === 'warning' ? '⚠️' : 'ℹ️'}
                </div>
                <div className="alert-item__content">
                  <h4 className="alert-item__title">{alert.title}</h4>
                  <p className="alert-item__description">{alert.description}</p>
                  <button className="alert-item__action">{alert.action}</button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
