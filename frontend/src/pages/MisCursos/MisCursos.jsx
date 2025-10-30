import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { coursesApi } from '../../services/api';
import './MisCursos.scss';

const MisCursos = () => {
  const [cursos, setCursos] = useState([]);
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

  return (
    <div className="mis-cursos">
      <header className="mis-cursos-header">
        <h1>Mis Cursos</h1>
        <p>Selecciona un curso para ver sus grupos o el dashboard del curso.</p>
      </header>

      {loading ? (
        <p>Cargando cursos...</p>
      ) : (
        <div className="cursos-grid">
          {cursos.length === 0 && <p>No se encontraron cursos.</p>}
          {cursos.map(c => (
            <div key={c.id} className="curso-card">
              <h3>{c.name}</h3>
              <p className="curso-code">{c.code}</p>
              <p className="curso-grupos">Grupos: {c.grupos?.length || 0}</p>
              <div className="curso-actions">
                <Link to="/dashboard" className="btn btn-primary">Ir al Dashboard</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MisCursos;
