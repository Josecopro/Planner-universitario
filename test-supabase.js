import { createClient } from '@supabase/supabase-js';

// Configuración de Supabase
const supabaseUrl = 'https://rxpkocjhimzyxhbxur.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ4cHBrb2NqaGltenlneGhieHVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3OTE4NDksImV4cCI6MjA3NzM2Nzg0OX0.uaV0KpWFSQripGl2_0sBfMh9ivQfuA4ba8-eHiWrvUw';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  console.log('🔍 Probando conexión con Supabase...');

  try {
    // Verificar conexión básica
    const { data, error } = await supabase.from('_metadata').select('count');

    if (error) {
      console.error('❌ Error de conexión:', error.message);
      return false;
    }

    console.log('✅ Conexión exitosa con Supabase');
    console.log('📊 Datos de metadata:', data);

    // Intentar consultar una tabla común
    const { data: tables, error: tablesError } = await supabase.from('usuarios').select('*').limit(1);

    if (tablesError) {
      console.log('⚠️ No se pudo acceder a la tabla "usuarios":', tablesError.message);
    } else {
      console.log('✅ Tabla "usuarios" accesible');
      console.log('📋 Primer registro:', tables?.[0] || 'Sin datos');
    }

    return true;

  } catch (error) {
    console.error('❌ Error inesperado:', error.message);
    return false;
  }
}

testConnection();