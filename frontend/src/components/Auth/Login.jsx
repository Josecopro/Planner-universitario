import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth.service';
import './Auth.css';


const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError('Por favor, completa todos los campos');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await authService.login(formData);
      
      const userRole = result.usuario.rol.nombre;
      
      switch (userRole) {
        case 'Superadmin':
          navigate('/dashboard');
          break;
        case 'Profesor':
          navigate('/dashboard');
          break;
        case 'Estudiante':
          navigate('/inicio');
          break;
        default:
          navigate('/dashboard');
      }
      
    } catch (err) {
      console.error('Error en login:', err);
      
      if (err.response?.status === 401) {
        setError('Email o contraseña incorrectos');
      } else if (err.response?.status === 403) {
        setError('Tu cuenta está inactiva. Contacta al administrador');
      } else if (err.response?.status === 429) {
        setError('Demasiados intentos. Intenta nuevamente en unos minutos');
      } else {
        setError('Error al iniciar sesión. Intenta nuevamente');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    navigate('/recuperar-password');
  };

  /**
   * Maneja el llenado automático de credenciales desde el componente demo
   */
  const handleFillCredentials = (credentials) => {
    setFormData(credentials);
    setError(''); // Limpiar cualquier error previo
  };

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ border: 'none' }}>
        <div className="auth-header">
          <h1>Iniciar Sesión</h1>
          <p>Bienvenido al Planner Universitario</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Campo Email */}
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <div className="input-wrapper">
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="tu-email@universidad.edu"
                className={error ? 'error' : ''}
                disabled={loading}
                autoComplete="email"
                required

              />
              <i className="input-icon email-icon">📧</i>
            </div>
          </div>

          {/* Campo Contraseña */}
          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <div className="input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Tu contraseña"
                className={error ? 'error' : ''}
                disabled={loading}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {/* Mensaje de Error */}
          {error && (
            <div className="error-message">
              <i className="error-icon">⚠️</i>
              {error}
            </div>
          )}

          {/* Botón de Envío */}
          <button
            type="submit"
            className={`auth-button ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Iniciando sesión...
              </>
            ) : (
              'Iniciar Sesión'
            )}
          </button>

          {/* Enlace de Recuperación */}
          <div className="auth-links">
            <button
              type="button"
              className="link-button"
              onClick={handleForgotPassword}
              disabled={loading}
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;