import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { dashboardApi } from '../../services/api';
import { generatePerformanceFeedback, generateGroupInsights } from '../../services/openrouter.service';
import './Dashboard.scss';

const Dashboard = () => {
  const { grupoId } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loadingAI, setLoadingAI] = useState(false);

  // Cargar datos del dashboard
  useEffect(() => {
    if (!grupoId) {
      setError(new Error('No se especificó un grupo'));
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await dashboardApi.getDataByGroup(grupoId);
        setDashboardData(data);
        setLoading(false);
        
        // Generar alertas con IA después de cargar datos
        generateAIAlerts(data);
      } catch (err) {
        console.error('❌ Error al cargar dashboard:', err);
        setError(err);
        setLoading(false);
      }
    };

    loadData();
  }, [grupoId]);

  const refetch = () => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await dashboardApi.getDataByGroup(grupoId);
        setDashboardData(data);
        setLoading(false);
        
        // Generar alertas con IA después de cargar datos
        generateAIAlerts(data);
      } catch (err) {
        console.error('❌ Error al cargar dashboard:', err);
        setError(err);
        setLoading(false);
      }
    };

    loadData();
  };

  // Generar alertas con retroalimentación de IA
  const generateAIAlerts = async (data) => {
    if (!data || loadingAI) return;
    
    setLoadingAI(true);
    const generatedAlerts = [];

    try {
      const { grupo, actividades, entregas, calificaciones, stats } = data;

      // 1. Generar insight general del grupo con IA
      try {
        const groupInsight = await generateGroupInsights({
          nombre_grupo: `${grupo.curso.nombre} - ${grupo.semestre}`,
          total_estudiantes: stats.active_students,
          promedio_general: stats.general_average,
          tasa_entrega: stats.submission_rate,
          actividades_completadas: stats.total_activities - stats.activities_pending,
          actividades_totales: stats.total_activities
        });

        generatedAlerts.push({
          id: 'ai-group-insight',
          type: 'info',
          title: '🤖 Análisis General del Grupo (IA)',
          description: groupInsight,
          action: 'Ver detalles'
        });
      } catch (err) {
        console.error('Error generando insight grupal:', err);
      }

      // 2. Identificar estudiantes con bajo desempeño y generar alertas con IA
      const calificacionesPorEstudiante = {};
      
      calificaciones.forEach(cal => {
        const entrega = entregas.find(e => e.id === cal.entrega_id);
        if (!entrega) return;
        
        const estudianteId = entrega.estudiante_id;
        if (!calificacionesPorEstudiante[estudianteId]) {
          calificacionesPorEstudiante[estudianteId] = {
            estudiante: entrega.estudiante,
            notas: []
          };
        }
        
        calificacionesPorEstudiante[estudianteId].notas.push(parseFloat(cal.nota_obtenida || 0));
      });

      // Calcular promedio por estudiante y generar alertas para bajo rendimiento
      const promedioGeneral = parseFloat(stats.general_average);
      let alertasGeneradas = 0;
      const maxAlertas = 3; // Limitar alertas para no saturar

      for (const [estudianteId, data] of Object.entries(calificacionesPorEstudiante)) {
        if (alertasGeneradas >= maxAlertas) break;
        
        const promedio = data.notas.reduce((a, b) => a + b, 0) / data.notas.length;
        
        // Solo generar alerta si está por debajo del promedio y tiene calificaciones bajas
        if (promedio < promedioGeneral && promedio < 3.5) {
          try {
            // Encontrar la actividad con la calificación más reciente
            const ultimaEntrega = entregas
              .filter(e => e.estudiante_id === estudianteId)
              .sort((a, b) => new Date(b.fecha_entrega) - new Date(a.fecha_entrega))[0];
            
            if (ultimaEntrega) {
              const ultimaCalificacion = calificaciones.find(c => c.entrega_id === ultimaEntrega.id);
              const actividad = actividades.find(a => a.id === ultimaEntrega.actividad_id);
              
              if (ultimaCalificacion && actividad) {
                const feedback = await generatePerformanceFeedback({
                  estudiante: `${data.estudiante.nombre} ${data.estudiante.apellido}`,
                  actividad: actividad.titulo,
                  calificacion: parseFloat(ultimaCalificacion.nota_obtenida || 0).toFixed(2),
                  promedio_grupo: promedioGeneral.toFixed(2)
                });

                generatedAlerts.push({
                  id: `ai-student-${estudianteId}`,
                  type: 'warning',
                  title: `⚠️ Atención requerida: ${data.estudiante.nombre} ${data.estudiante.apellido}`,
                  description: feedback,
                  action: 'Contactar estudiante'
                });
                
                alertasGeneradas++;
              }
            }
          } catch (err) {
            console.error(`Error generando feedback para estudiante ${estudianteId}:`, err);
          }
        }
      }

      // 3. Alerta si hay muchas entregas pendientes
      if (stats.pending_submissions > stats.active_students * 2) {
        generatedAlerts.push({
          id: 'pending-submissions',
          type: 'warning',
          title: '⏰ Alto número de entregas pendientes',
          description: `Hay ${stats.pending_submissions} entregas pendientes. Considere enviar recordatorios a los estudiantes o revisar las fechas límite.`,
          action: 'Ver entregas'
        });
      }

      // 4. Alerta si la tasa de entrega es baja
      if (parseFloat(stats.submission_rate) < 70) {
        generatedAlerts.push({
          id: 'low-submission-rate',
          type: 'warning',
          title: '📉 Baja tasa de entrega',
          description: `La tasa de entrega del grupo es del ${stats.submission_rate}%. Recomendación: Verificar si los estudiantes tienen dificultades con las actividades o el acceso a la plataforma.`,
          action: 'Analizar causas'
        });
      }

      setAlerts(generatedAlerts);
    } catch (err) {
      console.error('Error generando alertas:', err);
    } finally {
      setLoadingAI(false);
    }
  };

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

  if (!dashboardData) {
    return (
      <div className="dashboard">
        <div className="dashboard__error">
          <h2>No hay datos disponibles</h2>
          <p>No se encontró información para este grupo</p>
        </div>
      </div>
    );
  }

  const { grupo, stats } = dashboardData;
  const weeklyProgressData = stats?.weekly_progress || [];
  const gradeDistributionData = stats?.grade_distribution || [];

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Dashboard del Profesor</h1>
          <p className="dashboard__subtitle">
            {grupo?.curso?.nombre || 'Curso'} - {grupo?.semestre || 'Semestre'}
          </p>
        </div>
        <div className="dashboard__period-selector">
          <button onClick={refetch} className="refresh-button" title="Actualizar datos">
            🔄 Actualizar
          </button>
        </div>
      </header>

      <main className="dashboard__main">
        {/* Stats Cards */}
        <section className="dashboard__stats">
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Estudiantes Activos</div>
              <div className="stat-card__number">{stats?.active_students || 0}</div>
            </div>
            <div className="stat-card__icon">👥</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Promedio General</div>
              <div className="stat-card__number">{stats?.general_average || 0}</div>
            </div>
            <div className="stat-card__icon">📊</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Entregas Pendientes</div>
              <div className="stat-card__number">{stats?.pending_submissions || 0}</div>
            </div>
            <div className="stat-card__icon">⏰</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-card__content">
              <div className="stat-card__label">Tasa de Entrega</div>
              <div className="stat-card__number">{stats?.submission_rate || 0}%</div>
            </div>
            <div className="stat-card__icon">📋</div>
          </div>
        </section>

        {/* Charts Section */}
        <section className="dashboard__charts">
          <div className="chart-container">
            <h3 className="chart-container__title">Progreso Semanal (Promedio de Calificaciones)</h3>
            <div className="chart-container__content">
              {weeklyProgressData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={weeklyProgressData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="week" stroke="#718096" />
                    <YAxis stroke="#718096" domain={[0, 5]} />
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
                      name="Promedio"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p>No hay suficientes datos para mostrar el progreso semanal</p>
              )}
            </div>
          </div>

          <div className="chart-container">
            <h3 className="chart-container__title">Distribución de Calificaciones</h3>
            <div className="chart-container__content">
              {gradeDistributionData.some(d => d.value > 0) ? (
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
                      label={({ name, value }) => value > 0 ? `${name}: ${value}` : ''}
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
              ) : (
                <p>No hay calificaciones disponibles para mostrar la distribución</p>
              )}
            </div>
          </div>
        </section>

        {/* Alerts Section with AI-powered feedback */}
        <section className="dashboard__alerts">
          <div className="dashboard__alerts-header">
            <h3 className="dashboard__alerts-title">Alertas y Notificaciones con IA</h3>
            {loadingAI && <span className="loading-ai">🤖 Generando análisis con IA...</span>}
          </div>
          <div className="alerts-list">
            {alerts.length === 0 && !loadingAI && (
              <div className="alert-item alert-item--info">
                <div className="alert-item__icon">ℹ️</div>
                <div className="alert-item__content">
                  <h4 className="alert-item__title">No hay alertas</h4>
                  <p className="alert-item__description">
                    El grupo está funcionando bien. No hay problemas que requieran atención inmediata.
                  </p>
                </div>
              </div>
            )}
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-item alert-item--${alert.type}`}>
                <div className="alert-item__icon">
                  {alert.type === 'warning' ? '⚠️' : 'ℹ️'}
                </div>
                <div className="alert-item__content">
                  <h4 className="alert-item__title">{alert.title}</h4>
                  <p className="alert-item__description">{alert.description}</p>
                  {alert.action && (
                    <button className="alert-item__action">{alert.action}</button>
                  )}
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
