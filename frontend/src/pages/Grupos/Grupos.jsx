import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { coursesApi } from '../../services/api';
import './Grupos.scss';

const Grupos = () => {
  const { id: courseId } = useParams();
  const [grupos, setGrupos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    
    coursesApi.groupsForCourse(courseId).then(data => {
      if (!mounted) return;
      console.log('✅ [Grupos] Grupos recibidos:', data);
      setGrupos(data || []);
      setLoading(false);
    }).catch((err) => {
      if (!mounted) return;
      console.error('❌ [Grupos] Error al cargar grupos:', err);
      setGrupos([]);
      setLoading(false);
    });

    return () => { mounted = false; };
  }, [courseId]);

  return (
    <div className="grupos-page">
      <header className="grupos-header">
        <h1>Grupos del Curso</h1>
        <p>Curso: {courseId}</p>
      </header>

      {loading ? (
        <p>Cargando grupos...</p>
      ) : (
        <div className="grupos-list">
          {grupos.length === 0 && <p>No se encontraron grupos para este curso.</p>}
          {grupos.map(g => (
            <div key={g.id} className="grupo-card">
              <h3>{g.name}</h3>
              <p className="grupo-semestre">Semestre: {g.semestre}</p>
              <p className="grupo-schedule">{g.schedule}</p>
              <p className="grupo-cupo">Cupo: {g.cupo_actual}/{g.cupo_maximo}</p>
              <p className="grupo-estado">Estado: {g.estado}</p>
              {g.estudiantes && g.estudiantes.length > 0 && (
                <div className="grupo-estudiantes">
                  <h4>Estudiantes inscritos ({g.estudiantes.length}):</h4>
                  <ul>
                    {g.estudiantes.slice(0, 5).map(est => (
                      <li key={est.id}>{est.nombre} {est.apellido}</li>
                    ))}
                    {g.estudiantes.length > 5 && <li>...y {g.estudiantes.length - 5} más</li>}
                  </ul>
                </div>
              )}
              <div className="grupo-actions">
                <Link to={`/dashboard/grupo/${g.id}`} className="btn btn-primary">Ver Dashboard del Grupo</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Grupos;
