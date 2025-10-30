import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useSupabaseCRUD';
import './Auth.css';


const Login = () => {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [useSupabase, setUseSupabase] = useState(true); // Cambiar entre Supabase y backend tradicional

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

    // 🔍 LOG 1: Datos que se intentarán enviar
    console.log('=== INICIO DE LOGIN ===');
    console.log('📤 Datos del formulario:', {
      email: formData.email,
      password: '***' + formData.password.slice(-3), // Mostrar solo últimos 3 caracteres
      passwordLength: formData.password.length,
      useSupabase: useSupabase
    });

    try {
      // Intentar login con Supabase primero si está habilitado
      if (useSupabase) {
        try {
          console.log('🔐 Intentando login con Supabase...');
          console.log('📧 Email enviado:', formData.email);
          
          const { user, session } = await signIn(formData.email, formData.password);
          
          console.log('✅ Login con Supabase exitoso');
          console.log('👤 Usuario:', user);
          console.log('🎫 Sesión:', session);
          
          // Buscar información adicional del usuario en la tabla usuarios
          console.log('🔍 Buscando información adicional del usuario...');
          const { supabase } = await import('../../config/supabase');
          
          const { data: usuarioData, error: userError } = await supabase
            .from('usuarios')
            .select(`
              id,
              nombre,
              apellido,
              correo,
              rol_id,
              rol:rol_id(nombre)
            `)
            .eq('correo', formData.email)
            .single();
          
          if (userError) {
            console.warn('⚠️ No se pudo obtener información adicional:', userError);
          } else {
            console.log('✅ Información adicional obtenida:', usuarioData);
            
            // Combinar información de Supabase Auth con información de la BD
            const userWithDetails = {
              ...user,
              nombre: usuarioData.nombre,
              apellido: usuarioData.apellido,
              correo: usuarioData.correo,
              rol_id: usuarioData.rol_id,
              rol_nombre: usuarioData.rol?.nombre || 'Usuario'
            };
            
            console.log('✅ Usuario completo para localStorage:', userWithDetails);
            localStorage.setItem('user', JSON.stringify(userWithDetails));
          }
          
          // Guardar sesión en localStorage para persistencia
          localStorage.setItem('supabase_session', JSON.stringify(session));
          
          // Redirigir al dashboard
          navigate('/mis-cursos');
          return;
        } catch (supabaseError) {
          console.warn('❌ Supabase login failed');
          console.error('📋 Error completo de Supabase:', supabaseError);
          console.error('📋 Mensaje de error:', supabaseError.message);
          console.error('📋 Stack trace:', supabaseError.stack);
          // Si falla Supabase, intentar con el backend tradicional
        }
      }

      // Login con backend tradicional (como fallback o si useSupabase es false)
      console.log('🌐 Intentando login con backend tradicional...');
      
      // 🔍 LOG 2: Objeto exacto que se envía al servidor
      const loginPayload = {
        email: formData.email,
        password: formData.password
      };
      console.log('📦 Payload enviado al backend:', {
        ...loginPayload,
        password: '***' + loginPayload.password.slice(-3)
      });
      console.log('📦 Payload COMPLETO (con contraseña):', loginPayload);
      
      const userRole = result.usuario.rol.nombre;
      
      console.log('✅ Login con backend exitoso');
      console.log('👤 Usuario:', result.usuario);
      console.log('🎭 Rol:', userRole);
      
      switch (userRole) {
        case 'Superadmin':
          navigate('/mis-cursos');
          break;
        case 'Profesor':
          navigate('/mis-cursos');
          break;
        case 'Estudiante':
          navigate('/inicio');
          break;
        default:
          navigate('/dashboard');
      }
      
    } catch (err) {
      console.error('=== ERROR EN LOGIN ===');
      console.error('❌ Error capturado:', err);
      console.error('📋 Error message:', err.message);
      console.error('📋 Error response:', err.response);
      console.error('📋 Error response data:', err.response?.data);
      console.error('📋 Error response status:', err.response?.status);
      console.error('📋 Error response headers:', err.response?.headers);
      console.error('📋 Error config:', err.config);
      
      // 🔍 LOG 3: Datos que se enviaron cuando falló
      console.log('📤 Datos que se enviaron (al momento del error):', {
        email: formData.email,
        password:formData.password,
        passwordLength: formData.password.length
      });
      
      if (err.response?.status === 401 || err.message?.includes('Invalid')) {
        setError('Email o contraseña incorrectos');
        console.error('🔒 Credenciales inválidas');
      } else if (err.response?.status === 403) {
        setError('Tu cuenta está inactiva. Contacta al administrador');
        console.error('🚫 Cuenta inactiva');
      } else if (err.response?.status === 429) {
        setError('Demasiados intentos. Intenta nuevamente en unos minutos');
        console.error('⏱️ Rate limit excedido');
      } else {
        setError('Error al iniciar sesión. Intenta nuevamente');
        console.error('❓ Error desconocido');
      }
      
      console.log('=== FIN DE ERROR ===');
    } finally {
      setLoading(false);
      console.log('=== FIN DE LOGIN ===');
    }
  };

  const handleForgotPassword = () => {
    navigate('/recuperar-password');
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