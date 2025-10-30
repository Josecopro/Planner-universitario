/**
 * Integración de Supabase con Auth Service
 * 
 * Este archivo muestra cómo integrar Supabase con el sistema
 * de autenticación existente del Planner Universitario
 */

import supabaseService from './supabase.service';

/**
 * Adaptador de autenticación que combina el backend tradicional
 * con Supabase como alternativa o complemento
 */
const authSupabaseAdapter = {
  /**
   * Login con Supabase
   * 
   * Autentica usuario usando Supabase Auth
   * y mapea el resultado al formato esperado por el sistema
   */
  async loginWithSupabase(email, password) {
    try {
      // Autenticar con Supabase
      const { user, session } = await supabaseService.signIn(email, password);
      
      // Mapear a formato del sistema
      const loginResponse = {
        access_token: session.access_token,
        token_type: 'Bearer',
        usuario: {
          id: user.id,
          email: user.email,
          nombre: user.user_metadata?.nombre || user.email.split('@')[0],
          apellido: user.user_metadata?.apellido || '',
          estado: 'Activo',
          rol: {
            id: user.user_metadata?.rol_id || 3,
            nombre: user.user_metadata?.rol || 'Estudiante',
            descripcion: 'Usuario de Supabase'
          },
          ultimo_acceso: new Date().toISOString(),
          fecha_creacion: user.created_at
        }
      };
      
      return loginResponse;
    } catch (error) {
      console.error('Error en login con Supabase:', error);
      throw error;
    }
  },

  /**
   * Registrar usuario con Supabase
   */
  async registerWithSupabase(email, password, userData = {}) {
    try {
      const { user } = await supabaseService.signUp(email, password, {
        nombre: userData.nombre,
        apellido: userData.apellido,
        rol: userData.rol || 'Estudiante',
        rol_id: userData.rol_id || 3
      });
      
      return {
        success: true,
        user,
        message: 'Usuario registrado. Verifica tu email para activar la cuenta.'
      };
    } catch (error) {
      console.error('Error en registro con Supabase:', error);
      throw error;
    }
  },

  /**
   * Verificar sesión actual de Supabase
   */
  async checkSupabaseSession() {
    try {
      const session = await supabaseService.getSession();
      if (session) {
        const user = await supabaseService.getCurrentUser();
        return {
          isAuthenticated: true,
          user,
          session
        };
      }
      return {
        isAuthenticated: false,
        user: null,
        session: null
      };
    } catch (error) {
      console.error('Error verificando sesión:', error);
      return {
        isAuthenticated: false,
        user: null,
        session: null
      };
    }
  },

  /**
   * Sincronizar datos de usuario entre backend y Supabase
   */
  async syncUserData(userId, userData) {
    try {
      // Guardar en tabla de usuarios personalizada
      const result = await supabaseService.update('usuarios', userId, userData);
      return result;
    } catch (error) {
      console.error('Error sincronizando datos:', error);
      throw error;
    }
  }
};

export default authSupabaseAdapter;