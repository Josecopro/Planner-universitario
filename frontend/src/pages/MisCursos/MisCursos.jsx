import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { coursesApi } from '../../services/api';
import './MisCursos.scss';

const MisCursos = () => {
  const [cursos, setCursos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedCurso, setExpandedCurso] = useState(null);

  useEffect(() => {
    let mounted = true;
    
    // Obtener el correo del usuario logueado desde localStorage
    const userStr = localStorage.getItem('user');
    let correo = null;
    
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        correo = user.email || user.correo;
        console.log('📧 [MisCursos] Correo del usuario logueado:', correo);
      } catch (e) {
        console.error('❌ Error al parsear usuario de localStorage:', e);
      }
    }
    
    if (!correo) {
      console.warn('⚠️ No se encontró correo de usuario logueado');
      setLoading(false);
      return;
    }

    coursesApi.listForProfesor(correo).then((data) => {
      if (!mounted) return;
      console.log('✅ [MisCursos] Cursos recibidos:', data);
      setCursos(data || []);
      setLoading(false);
    }).catch((err) => {
      if (!mounted) return;
      console.error('❌ [MisCursos] Error al cargar cursos:', err);
      setCursos([]);
      setLoading(false);
    });

    return () => { mounted = false; };
  }, []);

  const handleGrupoClic = (grupoId, cursoName, semestre) => {
    // Guardar información del grupo en localStorage para que esté disponible
    const grupoInfo = {
      grupoId,
      cursoName,
      semestre,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('selectedGrupo', JSON.stringify(grupoInfo));
    console.log('💾 [MisCursos] Guardado grupoId en localStorage:', grupoInfo);
  };

  const toggleCurso = (cursoId) => {
    setExpandedCurso(expandedCurso === cursoId ? null : cursoId);
  };

  return (
    <div className="mis-cursos">
      <header className="mis-cursos-header">
        <h1>Mis Cursos</h1>
        <p>Selecciona un grupo para ver el dashboard del curso.</p>
      </header>

      {loading ? (
        <p>Cargando cursos...</p>
      ) : (
        <div className="cursos-grid">
          {cursos.length === 0 && <p>No se encontraron cursos.</p>}
          {cursos.map(c => (
            <div key={c.id} className="curso-card">
              <div className="curso-card-header" onClick={() => toggleCurso(c.id)}>
                <div>
                  <h3>{c.name}</h3>
                  <p className="curso-code">{c.code}</p>
                  <p className="curso-grupos">Grupos: {c.grupos?.length || 0}</p>
                </div>
                <span className={`expand-icon ${expandedCurso === c.id ? 'expanded' : ''}`}>
                  {expandedCurso === c.id ? '▼' : '▶'}
                </span>
              </div>
              
              {expandedCurso === c.id && c.grupos && c.grupos.length > 0 && (
                <div className="grupos-list">
                  {c.grupos.map(grupo => (
                    <Link 
                      key={grupo.id}
                      to={`/dashboard/grupo/${grupo.id}`}
                      className="grupo-item"
                      onClick={() => handleGrupoClic(grupo.id, c.name, grupo.semestre)}
                    >
                      <div className="grupo-info">
                        <span className="grupo-semestre">Semestre: {grupo.semestre}</span>
                        <span className="grupo-year">Año: {grupo.year}</span>
                      </div>
                      <span className="btn-dashboard">Ver Dashboard →</span>
                    </Link>
                  ))}
                </div>
              )}
              
              {expandedCurso === c.id && (!c.grupos || c.grupos.length === 0) && (
                <p className="no-grupos">No hay grupos disponibles para este curso.</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MisCursos;
