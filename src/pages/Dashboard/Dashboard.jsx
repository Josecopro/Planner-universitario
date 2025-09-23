import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './Dashboard.scss';

const Dashboard = () => {
  // Datos de estadísticas principales
  const [stats] = useState({
    activeStudents: 18,
    generalAverage: 4.2,
    pendingSubmissions: 12,
    attendance: 78
  });

  // Datos para el gráfico de progreso semanal
  const weeklyProgressData = [
    { week: 'Sem 1', value: 2.5 },
    { week: 'Sem 2', value: 3.2 },
    { week: 'Sem 3', value: 2.8 },
    { week: 'Sem 4', value: 3.8 },
    { week: 'Sem 5', value: 4.1 },
    { week: 'Sem 6', value: 3.9 },
    { week: 'Sem 7', value: 4.2 }
  ];

  // Datos para el gráfico de distribución de calificaciones
  const gradeDistributionData = [
    { name: 'Excelente', value: 25, color: '#10B981' },
    { name: 'Bueno', value: 35, color: '#932428' },
    { name: 'Regular', value: 25, color: '#F59E0B' },
    { name: 'Deficiente', value: 15, color: '#EF4444' }
  ];

  // Alertas y notificaciones
  const [alerts] = useState([
    {
      id: 1,
      type: 'warning',
      title: 'Estudiante en Riesgo',
      description: 'María González - Bajo rendimiento en últimas 3 actividades',
      action: 'Ver detalles'
    },
    {
      id: 2,
      type: 'info',
      title: 'Entregas Vencidas',
      description: '5 estudiantes no han entregado la tarea de la semana pasada',
      action: 'Enviar recordatorio'
    }
  ]);

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
        </div>
      </header>

      <main className="dashboard__main">
        {/* Stats Cards */}
        <section className="dashboard__stats">
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Estudiantes Activos</div>
              <div className="stat-card__number">{stats.activeStudents}</div>
            </div>
            <div className="stat-card__icon">👥</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Promedio General</div>
              <div className="stat-card__number">{stats.generalAverage}</div>
            </div>
            <div className="stat-card__icon">📊</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Entregas Pendientes</div>
              <div className="stat-card__number">{stats.pendingSubmissions}</div>
            </div>
            <div className="stat-card__icon">⏰</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Asistencia</div>
              <div className="stat-card__number">{stats.attendance}%</div>
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
