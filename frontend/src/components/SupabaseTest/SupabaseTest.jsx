import React, { useState, useEffect } from 'react';
import supabaseService from '../../services/supabase.service';

/**
 * Componente de Prueba de Supabase
 * 
 * Este componente verifica la conexión y muestra el estado de Supabase
 */
const SupabaseTest = () => {
  const [status, setStatus] = useState('checking');
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkSupabase();
  }, []);

  const checkSupabase = async () => {
    try {
      setStatus('checking');
      setError(null);

      // Verificar conexión
      const isConnected = await supabaseService.checkConnection();
      
      if (isConnected) {
        setStatus('connected');
        
        // Intentar obtener usuario actual
        try {
          const currentUser = await supabaseService.getCurrentUser();
          setUser(currentUser);
        } catch (err) {
          console.log('No hay usuario autenticado');
        }
      } else {
        setStatus('disconnected');
        setError('No se pudo conectar con Supabase');
      }
    } catch (err) {
      console.error('Error al verificar Supabase:', err);
      setStatus('error');
      setError(err.message);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return '#48bb78';
      case 'disconnected':
        return '#ed8936';
      case 'error':
        return '#f56565';
      default:
        return '#718096';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'checking':
        return 'Verificando conexión...';
      case 'connected':
        return 'Conectado ✅';
      case 'disconnected':
        return 'Desconectado ⚠️';
      case 'error':
        return 'Error ❌';
      default:
        return 'Desconocido';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>🔌 Estado de Supabase</h2>
        
        <div style={{ ...styles.status, backgroundColor: getStatusColor() }}>
          {getStatusText()}
        </div>

        {error && (
          <div style={styles.error}>
            <strong>Error:</strong> {error}
          </div>
        )}

        <div style={styles.info}>
          <h3 style={styles.subtitle}>Configuración:</h3>
          <div style={styles.configItem}>
            <strong>URL:</strong> {import.meta.env.VITE_SUPABASE_URL}
          </div>
          <div style={styles.configItem}>
            <strong>Key:</strong> {import.meta.env.VITE_SUPABASE_ANON_KEY?.substring(0, 20)}...
          </div>
        </div>

        {user && (
          <div style={styles.info}>
            <h3 style={styles.subtitle}>Usuario Actual:</h3>
            <div style={styles.configItem}>
              <strong>Email:</strong> {user.email}
            </div>
            <div style={styles.configItem}>
              <strong>ID:</strong> {user.id}
            </div>
          </div>
        )}

        <button onClick={checkSupabase} style={styles.button}>
          🔄 Verificar Nuevamente
        </button>

        <div style={styles.note}>
          <strong>💡 Nota:</strong> Para usar Supabase, ejecuta el proyecto con:
          <code style={styles.code}>npm run dev</code>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '2rem',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f7fafc',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '2rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    maxWidth: '600px',
    width: '100%',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    marginBottom: '1.5rem',
    color: '#2d3748',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: '1rem',
    fontWeight: '600',
    marginBottom: '0.5rem',
    color: '#4a5568',
  },
  status: {
    padding: '1rem',
    borderRadius: '8px',
    color: 'white',
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: '1rem',
  },
  error: {
    padding: '1rem',
    backgroundColor: '#fed7d7',
    border: '1px solid #feb2b2',
    borderRadius: '8px',
    color: '#c53030',
    marginBottom: '1rem',
    fontSize: '0.875rem',
  },
  info: {
    backgroundColor: '#edf2f7',
    padding: '1rem',
    borderRadius: '8px',
    marginBottom: '1rem',
  },
  configItem: {
    fontSize: '0.875rem',
    color: '#4a5568',
    marginBottom: '0.5rem',
    wordBreak: 'break-all',
  },
  button: {
    width: '100%',
    padding: '0.75rem',
    backgroundColor: '#932428',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    marginBottom: '1rem',
  },
  note: {
    padding: '1rem',
    backgroundColor: '#fef3c7',
    border: '1px solid #f59e0b',
    borderRadius: '8px',
    fontSize: '0.875rem',
    color: '#92400e',
    lineHeight: '1.5',
  },
  code: {
    display: 'block',
    backgroundColor: '#2d3748',
    color: '#68d391',
    padding: '0.5rem',
    borderRadius: '4px',
    marginTop: '0.5rem',
    fontFamily: 'monospace',
  },
};

export default SupabaseTest;