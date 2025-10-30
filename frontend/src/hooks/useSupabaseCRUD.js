import { useState, useEffect } from 'react';
import { supabase } from '../../supabaseClient';

/**
 * Hook personalizado para operaciones CRUD con Supabase
 * 
 * @param {string} table - Nombre de la tabla en Supabase
 * @returns {Object} Métodos y estado para CRUD
 */
export const useSupabaseCRUD = (table) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Obtener todos los registros
  const fetchAll = async (options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      let query = supabase.from(table).select(options.select || '*');

      // Aplicar filtros si existen
      if (options.filters) {
        Object.entries(options.filters).forEach(([key, value]) => {
          query = query.eq(key, value);
        });
      }

      // Aplicar ordenamiento
      if (options.orderBy) {
        query = query.order(options.orderBy.column, { 
          ascending: options.orderBy.ascending !== false 
        });
      }

      // Aplicar límite
      if (options.limit) {
        query = query.limit(options.limit);
      }

      const { data: result, error: fetchError } = await query;
      
      if (fetchError) throw fetchError;
      
      setData(result || []);
      return result;
    } catch (err) {
      setError(err.message);
      console.error(`Error fetching from ${table}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Obtener un registro por ID
  const fetchById = async (id) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data: result, error: fetchError } = await supabase
        .from(table)
        .select('*')
        .eq('id', id)
        .single();
      
      if (fetchError) throw fetchError;
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error(`Error fetching ${table} by id:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Crear un nuevo registro
  const create = async (newData) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data: result, error: createError } = await supabase
        .from(table)
        .insert(newData)
        .select()
        .single();
      
      if (createError) throw createError;
      
      // Actualizar la lista local
      setData(prevData => [...prevData, result]);
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error(`Error creating in ${table}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Actualizar un registro
  const update = async (id, updatedData) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data: result, error: updateError } = await supabase
        .from(table)
        .update(updatedData)
        .eq('id', id)
        .select()
        .single();
      
      if (updateError) throw updateError;
      
      // Actualizar la lista local
      setData(prevData => 
        prevData.map(item => item.id === id ? result : item)
      );
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error(`Error updating ${table}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Eliminar un registro
  const remove = async (id) => {
    setLoading(true);
    setError(null);
    
    try {
      const { error: deleteError } = await supabase
        .from(table)
        .delete()
        .eq('id', id);
      
      if (deleteError) throw deleteError;
      
      // Actualizar la lista local
      setData(prevData => prevData.filter(item => item.id !== id));
      
      return true;
    } catch (err) {
      setError(err.message);
      console.error(`Error deleting from ${table}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading,
    error,
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    setData, // Para actualizar manualmente si es necesario
  };
};

/**
 * Hook para autenticación con Supabase
 */
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Obtener sesión actual
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Escuchar cambios de autenticación
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Login con email y contraseña
  const signIn = async (email, password) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) throw error;
      
      return data;
    } catch (error) {
      console.error('Error signing in:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Registro
  const signUp = async (email, password, metadata = {}) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata,
        },
      });
      
      if (error) throw error;
      
      return data;
    } catch (error) {
      console.error('Error signing up:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const signOut = async () => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
  };
};

export default useSupabaseCRUD;