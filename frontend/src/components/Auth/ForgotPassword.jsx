import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';


const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [emailSent, setEmailSent] = useState(false);

 
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Maneja el cambio en el campo de email
   */
  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    // Limpiar mensajes cuando el usuario empiece a escribir
    if (error) setError('');
    if (message) setMessage('');
  };

  /**
   * Maneja el envío del formulario de recuperación
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validación básica
    if (!email) {
      setError('Por favor, ingresa tu email');
      return;
    }

    if (!isValidEmail(email)) {
      setError('Por favor, ingresa un email válido');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      // Simular llamada al backend para recuperación de contraseña
      // En un escenario real, esto haría una llamada a la API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulamos una respuesta exitosa
      setEmailSent(true);
      setMessage(
        `Se ha enviado un enlace de recuperación a ${email}. ` +
        'Revisa tu bandeja de entrada y sigue las instrucciones.'
      );
      
      // TODO: Implementar llamada real al backend
      // const response = await authService.requestPasswordReset({ email });
      
    } catch (err) {
      console.error('Error en recuperación:', err);
      
      // Manejo de errores
      if (err.response?.status === 404) {
        setError('No existe una cuenta asociada a este email');
      } else if (err.response?.status === 429) {
        setError('Demasiadas solicitudes. Intenta nuevamente en unos minutos');
      } else {
        setError('Error al enviar el email. Intenta nuevamente');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Navegar de vuelta al login
   */
  const handleBackToLogin = () => {
    navigate('/login');
  };

  /**
   * Reenviar email de recuperación
   */
  const handleResendEmail = () => {
    setEmailSent(false);
    setMessage('');
    handleSubmit({ preventDefault: () => {} });
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Recuperar Contraseña</h1>
          <p>
            {emailSent 
              ? 'Revisa tu email' 
              : 'Ingresa tu email para recibir instrucciones'
            }
          </p>
        </div>

        {!emailSent ? (
          /* Formulario de Solicitud */
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <div className="input-wrapper">
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={email}
                  onChange={handleEmailChange}
                  placeholder="tu-email@universidad.edu"
                  className={error ? 'error' : ''}
                  disabled={loading}
                  autoComplete="email"
                  required
                />
                <i className="input-icon email-icon">📧</i>
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
                  Enviando...
                </>
              ) : (
                'Enviar Instrucciones'
              )}
            </button>

            {/* Enlace de Vuelta al Login */}
            <div className="auth-links">
              <button
                type="button"
                className="link-button"
                onClick={handleBackToLogin}
                disabled={loading}
              >
                ← Volver al inicio de sesión
              </button>
            </div>
          </form>
        ) : (
          /* Mensaje de Confirmación */
          <div className="success-message-container">
            <div className="success-icon">✅</div>
            
            {/* Mensaje de Éxito */}
            {message && (
              <div className="success-message">
                {message}
              </div>
            )}

            <div className="success-instructions">
              <h3>¿Qué hacer ahora?</h3>
              <ol>
                <li>Revisa tu bandeja de entrada (y spam)</li>
                <li>Haz clic en el enlace del email</li>
                <li>Crea una nueva contraseña</li>
                <li>Regresa al login con tu nueva contraseña</li>
              </ol>
            </div>

            {/* Opciones después del envío */}
            <div className="post-submit-actions">
              <button
                type="button"
                className="auth-button secondary"
                onClick={handleResendEmail}
                disabled={loading}
              >
                {loading ? 'Enviando...' : 'Reenviar Email'}
              </button>
              
              <button
                type="button"
                className="link-button"
                onClick={handleBackToLogin}
                disabled={loading}
              >
                ← Volver al inicio de sesión
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default ForgotPassword;