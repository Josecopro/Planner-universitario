import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { coursesApi } from '../../services/api';
import './VistaDetalladaCurso.scss';

const VistaDetalladaCurso = () => {
  const { id } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    
    // Obtener el correo del usuario logueado desde localStorage
    const userStr = localStorage.getItem('user');
    let correo = null;
    
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        correo = user.email || user.correo;
        console.log('📧 [VistaDetalladaCurso] Correo del usuario logueado:', correo);
      } catch (e) {
        console.error('❌ Error al parsear usuario de localStorage:', e);
      }
    }
    
    if (!correo) {
      console.warn('⚠️ No se encontró correo de usuario logueado');
      setLoading(false);
      return;
    }

    // Obtener datos completos del dashboard
    coursesApi.getDashboardData(id, correo).then(data => {
      if (!mounted) return;
      console.log('✅ [VistaDetalladaCurso] Dashboard data:', data);
      setDashboardData(data);
      setLoading(false);
    }).catch(err => {
      if (!mounted) return;
      console.error('❌ [VistaDetalladaCurso] Error al cargar dashboard:', err);
      setDashboardData(null);
      setLoading(false);
    });

    return () => { mounted = false; };
  }, [id]);

  if (loading) return <p>Cargando curso...</p>;
  if (!dashboardData) return <p>No se pudo cargar la información del curso.</p>;

  const { grupos, actividades, estadisticas } = dashboardData;

  return (
    <div className="vista-detallada-curso">
      <header className="curso-header">
        <h1>Dashboard del Curso</h1>
        <p>Curso ID: {id}</p>
      </header>

      <section className="curso-actions">
        <Link to={`/curso/${id}/grupos`} className="btn btn-secondary">Ver Grupos</Link>
      </section>

      <section className="curso-stats">
        <h2>Estadísticas Generales</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{estadisticas.totalGrupos}</h3>
            <p>Grupos Totales</p>
          </div>
          <div className="stat-card">
            <h3>{estadisticas.totalEstudiantes}</h3>
            <p>Estudiantes Inscritos</p>
          </div>
          <div className="stat-card">
            <h3>{estadisticas.totalActividades}</h3>
            <p>Actividades Creadas</p>
          </div>
          <div className="stat-card">
            <h3>{estadisticas.actividadesPendientes}</h3>
            <p>Actividades Abiertas</p>
          </div>
        </div>
      </section>

      <section className="curso-grupos">
        <h2>Grupos del Curso</h2>
        {grupos.length === 0 ? (
          <p>No hay grupos registrados para este curso.</p>
        ) : (
          <div className="grupos-summary">
            {grupos.map(g => (
              <div key={g.id} className="grupo-summary-card">
                <h4>{g.name}</h4>
                <p>Semestre: {g.semestre}</p>
                <p>Estudiantes: {g.cupo_actual}/{g.cupo_maximo}</p>
                <p>Estado: {g.estado}</p>
                <Link to={`/dashboard/grupo/${g.id}`} className="btn btn-sm">Ver Dashboard</Link>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="curso-actividades">
        <h2>Actividades Evaluativas</h2>
        {actividades.length === 0 ? (
          <p>No hay actividades registradas para este curso.</p>
        ) : (
          <div className="actividades-list">
            {actividades.slice(0, 10).map(a => (
              <div key={a.id} className="actividad-item">
                <h4>{a.titulo}</h4>
                <p>Tipo: {a.tipo} | Prioridad: {a.prioridad}</p>
                <p>Estado: {a.estado}</p>
                <p>Fecha de entrega: {new Date(a.fecha_entrega).toLocaleDateString('es-ES')}</p>
                <p>Porcentaje: {a.porcentaje}%</p>
              </div>
            ))}
            {actividades.length > 10 && (
              <p>...y {actividades.length - 10} actividades más</p>
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export default VistaDetalladaCurso;
