/**
 * Configuración de Supabase para Planner Universitario
 * 
 * Este archivo inicializa y exporta el cliente de Supabase
 * usando las variables de entorno configuradas en .env
 */

import { createClient } from '@supabase/supabase-js';

// Obtener las variables de entorno de Vite
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validar que las variables de entorno estén definidas
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Error: Variables de entorno de Supabase no configuradas');
  console.error('Verifica que .env contenga:');
  console.error('- VITE_SUPABASE_URL');
  console.error('- VITE_SUPABASE_ANON_KEY');
  throw new Error('Configuración de Supabase incompleta');
}

// Crear cliente de Supabase
const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
});

// Log de confirmación en desarrollo
if (import.meta.env.DEV) {
  console.log('✅ Supabase conectado:', supabaseUrl);
}

export default supabase;
export {supabase}