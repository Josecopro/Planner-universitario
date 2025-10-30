/**
 * Servicio de Supabase para Planner Universitario
 * 
 * Este servicio proporciona métodos para interactuar con Supabase
 * incluyendo autenticación, base de datos y storage.
 */

import supabase from '../config/supabase';

/**
 * Servicio de Supabase
 */
const supabaseService = {
  /**
   * ========================================
   * AUTENTICACIÓN
   * ========================================
   */

  /**
   * Iniciar sesión con email y contraseña
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña del usuario
   * @returns {Promise<Object>} Datos del usuario y sesión
   */
  async signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) throw error;
    return data;
  },

  /**
   * Registrar nuevo usuario
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña del usuario
   * @param {Object} metadata - Metadatos adicionales del usuario
   * @returns {Promise<Object>} Datos del usuario registrado
   */
  async signUp(email, password, metadata = {}) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    });

    if (error) throw error;
    return data;
  },

  /**
   * Cerrar sesión
   * @returns {Promise<void>}
   */
  async signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

  /**
   * Obtener usuario actual
   * @returns {Promise<Object|null>} Usuario actual o null
   */
  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error) throw error;
    return user;
  },

  /**
   * Obtener sesión actual
   * @returns {Promise<Object|null>} Sesión actual o null
   */
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) throw error;
    return session;
  },

  /**
   * ========================================
   * BASE DE DATOS
   * ========================================
   */

  /**
   * Obtener registros de una tabla
   * @param {string} table - Nombre de la tabla
   * @param {Object} options - Opciones de consulta
   * @returns {Promise<Array>} Array de registros
   */
  async getAll(table, options = {}) {
    let query = supabase.from(table).select(options.select || '*');

    // Aplicar filtros
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

    const { data, error } = await query;
    if (error) throw error;
    return data;
  },

  /**
   * Obtener un registro por ID
   * @param {string} table - Nombre de la tabla
   * @param {number|string} id - ID del registro
   * @returns {Promise<Object>} Registro encontrado
   */
  async getById(table, id) {
    const { data, error } = await supabase
      .from(table)
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;
    return data;
  },

  /**
   * Crear un nuevo registro
   * @param {string} table - Nombre de la tabla
   * @param {Object} data - Datos a insertar
   * @returns {Promise<Object>} Registro creado
   */
  async create(table, data) {
    const { data: result, error } = await supabase
      .from(table)
      .insert(data)
      .select()
      .single();

    if (error) throw error;
    return result;
  },

  /**
   * Actualizar un registro
   * @param {string} table - Nombre de la tabla
   * @param {number|string} id - ID del registro
   * @param {Object} data - Datos a actualizar
   * @returns {Promise<Object>} Registro actualizado
   */
  async update(table, id, data) {
    const { data: result, error } = await supabase
      .from(table)
      .update(data)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return result;
  },

  /**
   * Eliminar un registro
   * @param {string} table - Nombre de la tabla
   * @param {number|string} id - ID del registro
   * @returns {Promise<void>}
   */
  async delete(table, id) {
    const { error } = await supabase
      .from(table)
      .delete()
      .eq('id', id);

    if (error) throw error;
  },

  /**
   * ========================================
   * STORAGE (ARCHIVOS)
   * ========================================
   */

  /**
   * Subir un archivo
   * @param {string} bucket - Nombre del bucket
   * @param {string} path - Ruta del archivo
   * @param {File} file - Archivo a subir
   * @returns {Promise<Object>} Datos del archivo subido
   */
  async uploadFile(bucket, path, file) {
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(path, file, {
        cacheControl: '3600',
        upsert: false,
      });

    if (error) throw error;
    return data;
  },

  /**
   * Obtener URL pública de un archivo
   * @param {string} bucket - Nombre del bucket
   * @param {string} path - Ruta del archivo
   * @returns {string} URL pública del archivo
   */
  getPublicUrl(bucket, path) {
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(path);

    return data.publicUrl;
  },

  /**
   * Eliminar un archivo
   * @param {string} bucket - Nombre del bucket
   * @param {string} path - Ruta del archivo
   * @returns {Promise<void>}
   */
  async deleteFile(bucket, path) {
    const { error } = await supabase.storage
      .from(bucket)
      .remove([path]);

    if (error) throw error;
  },

  /**
   * ========================================
   * UTILIDADES
   * ========================================
   */

  /**
   * Verificar conexión con Supabase
   * @returns {Promise<boolean>} true si está conectado
   */
  async checkConnection() {
    try {
      const { data, error } = await supabase.from('_metadata').select('count');
      return !error;
    } catch (error) {
      console.error('Error al verificar conexión:', error);
      return false;
    }
  },

  /**
   * Obtener cliente de Supabase directo
   * Para operaciones avanzadas
   * @returns {Object} Cliente de Supabase
   */
  getClient() {
    return supabase;
  },
};

export default supabaseService;