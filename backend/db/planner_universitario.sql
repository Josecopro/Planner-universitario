-- =================================================================
--  SCRIPT DE INICIALIZACIÓN PARA EL PLANNER UNIVERSITARIO
--  Base de Datos: PostgreSQL (Compatible con NeonDB)
--  Tablas: Roles y Usuarios
-- =================================================================

-- Primero, creamos un tipo ENUM personalizado para el estado del usuario.
-- Esto es más eficiente y seguro que usar un simple VARCHAR.
CREATE TYPE estado_usuario AS ENUM (
    'Activo', 
    'Inactivo', 
    'Pendiente de Verificacion'
);

-- =================================================================
--  1. TABLA DE ROLES
--  Almacena los diferentes roles que un usuario puede tener en el sistema.
-- =================================================================
CREATE TABLE Rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Añadimos un comentario a la tabla para mayor claridad
COMMENT ON TABLE Rol IS 'Catálogo de roles para el control de acceso (Superadmin, Profesor, Estudiante, etc.)';


-- =================================================================
--  2. TABLA DE USUARIOS
--  Almacena la información de identidad y autenticación de todos los usuarios.
-- =================================================================
CREATE TABLE Usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INTEGER NOT NULL,
    avatar_url VARCHAR(255),
    estado estado_usuario NOT NULL DEFAULT 'Pendiente de Verificacion',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ultimo_acceso TIMESTAMPTZ,

    -- Definimos la llave foránea que conecta Usuario con Rol
    CONSTRAINT fk_rol
        FOREIGN KEY(rol_id) 
        REFERENCES Rol(id)
        ON DELETE RESTRICT -- Impide eliminar un rol si hay usuarios con él
);

-- Creamos un índice en la columna de correo para acelerar las búsquedas de login
CREATE INDEX idx_usuario_correo ON Usuario(correo);

-- Comentarios para mayor claridad
COMMENT ON TABLE Usuario IS 'Entidad central para la identidad y autenticación de los usuarios.';
COMMENT ON COLUMN Usuario.password_hash IS 'Hash de la contraseña, nunca la contraseña en texto plano.';
COMMENT ON COLUMN Usuario.estado IS 'Estado de la cuenta del usuario (Activo, Inactivo, etc.).';


-- =================================================================
--  3. INSERCIÓN DE DATOS INICIALES
--  Poblamos la tabla de roles con los valores fundamentales para el sistema.
-- =================================================================
INSERT INTO Rol (nombre, descripcion) VALUES
('Superadmin', 'Acceso total al sistema y a la configuración de la plataforma.'),
('Profesor', 'Acceso a la gestión de grupos, actividades y calificaciones.'),
('Estudiante', 'Acceso a la visualización de cursos, entrega de actividades y consulta de notas.');

-- =================================================================
--  SCRIPT PARA LA ESTRUCTURA ACADÉMICA
--  Base de Datos: PostgreSQL (Compatible con NeonDB)
--  Tablas: Facultad, ProgramaAcademico, Profesor, Estudiante
-- =================================================================

-- Primero, definimos los tipos ENUM personalizados para los estados
CREATE TYPE estado_programa AS ENUM ('Activo', 'Inactivo', 'En Liquidacion');
CREATE TYPE estado_academico_estudiante AS ENUM ('Matriculado', 'Retirado', 'Graduado', 'En Prueba Academica');

-- =================================================================
--  1. TABLA FACULTAD
--  Representa las divisiones académicas principales de la institución.
-- =================================================================
CREATE TABLE Facultad (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(150) UNIQUE NOT NULL
);

COMMENT ON TABLE Facultad IS 'Representa las facultades o escuelas de la institución (ej. Facultad de Ingeniería).';

-- =================================================================
--  2. TABLA PROGRAMA ACADEMICO
--  Representa las carreras o programas ofrecidos por las facultades.
-- =================================================================
CREATE TABLE ProgramaAcademico (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    facultad_id INTEGER NOT NULL,
    duracion_semestres INTEGER,
    estado estado_programa NOT NULL DEFAULT 'Activo',

    CONSTRAINT fk_facultad
        FOREIGN KEY(facultad_id)
        REFERENCES Facultad(id)
        ON DELETE RESTRICT -- Impide eliminar una facultad si tiene programas asociados
);

COMMENT ON TABLE ProgramaAcademico IS 'Carreras o programas de estudio (ej. Ingeniería de Sistemas).';

-- =================================================================
--  3. TABLA PROFESOR (Perfil)
--  Almacena los datos específicos del perfil de un usuario con rol de Profesor.
-- =================================================================
CREATE TABLE Profesor (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL, -- UNIQUE para forzar la relación 1 a 1
    documento VARCHAR(50),
    tipo_documento VARCHAR(50),
    facultad_id INTEGER,
    titulo_academico VARCHAR(255),

    CONSTRAINT fk_usuario_profesor
        FOREIGN KEY(usuario_id)
        REFERENCES Usuario(id)
        ON DELETE CASCADE, -- Si se elimina el Usuario, se elimina su perfil de profesor
    
    CONSTRAINT fk_facultad_profesor
        FOREIGN KEY(facultad_id)
        REFERENCES Facultad(id)
        ON DELETE SET NULL -- Si se elimina la facultad, el profesor queda sin facultad asignada
);

COMMENT ON TABLE Profesor IS 'Perfil con datos específicos para usuarios con rol de Profesor.';

-- =================================================================
--  4. TABLA ESTUDIANTE (Perfil)
--  Almacena los datos específicos del perfil de un usuario con rol de Estudiante.
-- =================================================================
CREATE TABLE Estudiante (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL, -- UNIQUE para forzar la relación 1 a 1
    documento VARCHAR(50),
    tipo_documento VARCHAR(50),
    programa_id INTEGER NOT NULL,
    estado_academico estado_academico_estudiante NOT NULL DEFAULT 'Matriculado',

    CONSTRAINT fk_usuario_estudiante
        FOREIGN KEY(usuario_id)
        REFERENCES Usuario(id)
        ON DELETE CASCADE, -- Si se elimina el Usuario, se elimina su perfil de estudiante

    CONSTRAINT fk_programa_estudiante
        FOREIGN KEY(programa_id)
        REFERENCES ProgramaAcademico(id)
        ON DELETE RESTRICT -- Impide eliminar un programa si tiene estudiantes inscritos
);

COMMENT ON TABLE Estudiante IS 'Perfil con datos específicos para usuarios con rol de Estudiante.';

-- =================================================================
--  SCRIPT PARA LA GESTIÓN DE CURSOS, GRUPOS Y HORARIOS
--  Base de Datos: PostgreSQL (Compatible con NeonDB)
-- =================================================================

-- Primero, definimos los tipos ENUM personalizados para los estados
-- (Asumiendo que los ENUMs del script anterior ya existen)

CREATE TYPE estado_curso AS ENUM (
    'Activo', 
    'Inactivo',
    'En Revision'
);

CREATE TYPE estado_grupo AS ENUM (
    'Programado', 
    'Abierto', -- Abierto para inscripciones
    'Cerrado', -- Inscripciones cerradas (cupo lleno o fecha límite)
    'En Curso',
    'Finalizado',
    'Cancelado'
);


-- =================================================================
--  1. TABLA CURSO
--  Basada en la imagen 'image_ed777a.png'.
--  Representa las materias o asignaturas del plan de estudios.
-- =================================================================
CREATE TABLE Curso (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    facultad_id INTEGER NOT NULL,
    estado estado_curso NOT NULL DEFAULT 'Activo',

    -- Llave foránea que conecta Curso con Facultad (de tu script anterior)
    CONSTRAINT fk_facultad_curso
        FOREIGN KEY(facultad_id)
        REFERENCES Facultad(id)
        ON DELETE RESTRICT -- Impide eliminar una facultad si tiene cursos
);

COMMENT ON TABLE Curso IS 'Catálogo de materias o asignaturas (ej. Cálculo I, Introducción a la Programación).';
COMMENT ON COLUMN Curso.codigo IS 'Código único de la asignatura, ej: IS-101.';


-- =================================================================
--  2. TABLA GRUPO
--  Basada en la imagen 'image_ed777d.png'.
--  Representa una instancia específica de un Curso en un semestre.
-- =================================================================
CREATE TABLE Grupo (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL,
    profesor_id INTEGER, -- Puede ser NULO si aún no está asignado
    semestre VARCHAR(20) NOT NULL, -- Ej: '2025-1'
    cupo_maximo INTEGER NOT NULL DEFAULT 0,
    cupo_actual INTEGER NOT NULL DEFAULT 0,
    estado estado_grupo NOT NULL DEFAULT 'Programado',

    -- Llave foránea (Relación 1-N con Curso)
    CONSTRAINT fk_curso_grupo
        FOREIGN KEY(curso_id)
        REFERENCES Curso(id)
        ON DELETE CASCADE, -- Si se elimina el Curso, se eliminan sus Grupos

    -- Llave foránea (Relación 1-N con Profesor)
    CONSTRAINT fk_profesor_grupo
        FOREIGN KEY(profesor_id)
        REFERENCES Profesor(id)
        ON DELETE SET NULL, -- Si se elimina el Profesor, el grupo queda sin docente asignado

    -- Restricción para que los cupos sean lógicos
    CONSTRAINT chk_cupos_logicos
        CHECK (cupo_actual >= 0 AND cupo_maximo >= cupo_actual)
);

COMMENT ON TABLE Grupo IS 'Instancia de un Curso en un semestre/periodo específico, con un profesor y cupos.';
COMMENT ON COLUMN Grupo.semestre IS 'Periodo académico, ej: 2025-1, 2025-2.';
COMMENT ON COLUMN Grupo.profesor_id IS 'Referencia al perfil del profesor que imparte el grupo.';


-- =================================================================
--  3. TABLA HORARIO
--  Basada en la imagen 'image_ed777d.png'.
--  Almacena los bloques de día/hora/lugar para un Grupo.
-- =================================================================
CREATE TABLE Horario (
    id SERIAL PRIMARY KEY,
    grupo_id INTEGER NOT NULL,
    dia VARCHAR(15) NOT NULL, -- Ej: 'Lunes', 'Martes', 'Miércoles'
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    salon VARCHAR(50), -- Ej: 'Bloque 5 - 101' o 'Virtual'

    -- Llave foránea (Relación 1-N con Grupo)
    CONSTRAINT fk_grupo_horario
        FOREIGN KEY(grupo_id)
        REFERENCES Grupo(id)
        ON DELETE CASCADE, -- Si se borra el Grupo, se borran sus entradas de horario

    -- Restricción para que la hora de fin sea posterior a la de inicio
    CONSTRAINT chk_horas_validas
        CHECK (hora_fin > hora_inicio)
);

COMMENT ON TABLE Horario IS 'Bloques de día/hora/salón para un grupo. Un grupo puede tener múltiples entradas aquí (ej. Lunes y Miércoles).';

-- =================================================================
--  SCRIPT PARA LA GESTIÓN DE INSCRIPCIONES, ACTIVIDADES Y CALIFICACIONES
--  Base de Datos: PostgreSQL (Compatible con NeonDB)
-- =================================================================

-- -----------------------------------------------------------------
--  DEFINICIÓN DE TIPOS ENUM PERSONALIZADOS
-- -----------------------------------------------------------------

CREATE TYPE estado_inscripcion AS ENUM (
    'Inscrito',
    'Retirado',
    'Aprobado',
    'Reprobado',
    'Cancelado'
);

CREATE TYPE estado_actividad AS ENUM (
    'Programada', -- Creada por el profesor, no visible aún
    'Publicada',  -- Visible para estudiantes, no acepta entregas
    'Abierta',    -- Aceptando entregas
    'Cerrada',    -- Fecha de entrega pasada
    'Cancelada'
);

CREATE TYPE tipo_actividad AS ENUM (
    'Tarea',
    'Quiz',
    'Examen Parcial',
    'Examen Final',
    'Proyecto',
    'Laboratorio',
    'Otro'
);

CREATE TYPE prioridad_actividad AS ENUM (
    'Baja',
    'Media',
    'Alta'
);

CREATE TYPE estado_entrega AS ENUM (
    'Pendiente',        -- El estudiante no ha entregado
    'Entregada',        -- Entregada a tiempo
    'Entregada Tarde',  -- Entregada fuera de fecha
    'Calificada'
);


-- =================================================================
--  1. TABLA INSCRIPCION
--  Conecta a un Estudiante con un Grupo (M-M).
-- =================================================================
CREATE TABLE Inscripcion (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    fecha_inscripcion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estado estado_inscripcion NOT NULL DEFAULT 'Inscrito',
    nota_definitiva NUMERIC(5, 2) NULL, -- Columna añadida según 'image_ed68f8.png'

    -- Llave foránea a la tabla Estudiante (de tu script anterior)
    CONSTRAINT fk_estudiante_inscripcion
        FOREIGN KEY(estudiante_id)
        REFERENCES Estudiante(id)
        ON DELETE CASCADE, -- Si se borra el estudiante, se borran sus inscripciones

    -- Llave foránea a la tabla Grupo (de tu script anterior)
    CONSTRAINT fk_grupo_inscripcion
        FOREIGN KEY(grupo_id)
        REFERENCES Grupo(id)
        ON DELETE CASCADE, -- Si se borra el grupo, se borran sus inscripciones

    -- Restricción para que un estudiante no se inscriba 2 veces en el mismo grupo
    CONSTRAINT uq_estudiante_grupo
        UNIQUE (estudiante_id, grupo_id),
    
    -- Restricción para que la nota definitiva sea lógica (si no es nula)
    CONSTRAINT chk_nota_definitiva_logica
        CHECK (nota_definitiva IS NULL OR nota_definitiva >= 0.0)
);

COMMENT ON TABLE Inscripcion IS 'Tabla de unión que registra qué estudiante está en qué grupo (M2M).';
COMMENT ON COLUMN Inscripcion.nota_definitiva IS 'Nota final del estudiante en el grupo, calculada al finalizar el semestre.';


-- =================================================================
--  2. TABLA ACTIVIDAD EVALUATIVA
--  Actividades (tareas, exámenes, etc.) de un grupo específico.
-- =================================================================
CREATE TABLE ActividadEvaluativa (
    id SERIAL PRIMARY KEY,
    grupo_id INTEGER NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    estado estado_actividad NOT NULL DEFAULT 'Programada',
    fecha_entrega TIMESTAMPTZ NOT NULL, -- Fecha límite (due date)
    tipo tipo_actividad NOT NULL DEFAULT 'Tarea',
    prioridad prioridad_actividad NOT NULL DEFAULT 'Media',
    porcentaje NUMERIC(5, 2) NOT NULL DEFAULT 0.0,

    -- Conexión con la tabla Grupo
    CONSTRAINT fk_grupo_actividad
        FOREIGN KEY(grupo_id)
        REFERENCES Grupo(id)
        ON DELETE CASCADE, -- Si se borra el Grupo, se borran sus actividades

    -- Restricción para que el porcentaje sea lógico (0 a 100)
    CONSTRAINT chk_porcentaje
        CHECK (porcentaje >= 0.0 AND porcentaje <= 100.0)
);

COMMENT ON TABLE ActividadEvaluativa IS 'Entidad que define una tarea, examen o cualquier actividad calificable.';
COMMENT ON COLUMN ActividadEvaluativa.fecha_entrega IS 'Fecha y hora límite para la entrega de la actividad.';


-- =================================================================
--  3. TABLA ENTREGA
--  Representa la entrega de un estudiante para una actividad.
-- =================================================================
CREATE TABLE Entrega (
    id SERIAL PRIMARY KEY,
    actividad_id INTEGER NOT NULL,
    inscripcion_id INTEGER NOT NULL, -- Referencia a Inscripcion(id)
    fecha_entrega TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Cuándo la entregó
    estado estado_entrega NOT NULL DEFAULT 'Entregada',
    texto_entrega TEXT,
    archivos_adjuntos TEXT[], -- Un array de URLs o rutas de archivos

    -- Conexión con la actividad que se está entregando
    CONSTRAINT fk_actividad_entrega
        FOREIGN KEY(actividad_id)
        REFERENCES ActividadEvaluativa(id)
        ON DELETE CASCADE, -- Si se borra la actividad, se borran sus entregas

    -- Conexión con la inscripción (Estudiante + Grupo)
    CONSTRAINT fk_inscripcion_entrega
        FOREIGN KEY(inscripcion_id)
        REFERENCES Inscripcion(id)
        ON DELETE CASCADE, -- Si se anula la inscripción, se borran las entregas

    -- Restricción para evitar entregas duplicadas
    CONSTRAINT uq_actividad_inscripcion
        UNIQUE (actividad_id, inscripcion_id)
);

COMMENT ON TABLE Entrega IS 'Registro de la sumisión de un estudiante para una actividad evaluativa.';
COMMENT ON COLUMN Entrega.inscripcion_id IS 'Referencia a la inscripción del estudiante en el grupo, para saber quién entrega.';
COMMENT ON COLUMN Entrega.archivos_adjuntos IS 'Array de strings (rutas o URLs) de los archivos adjuntados por el estudiante.';


-- =================================================================
--  4. TABLA CALIFICACION
--  Representa la nota y feedback de una entrega.
-- =================================================================
CREATE TABLE Calificacion (
    id SERIAL PRIMARY KEY,
    entrega_id INTEGER UNIQUE NOT NULL, -- UNIQUE para forzar relación 1 a 1
    nota_obtenida NUMERIC(5, 2) NOT NULL,
    fecha_calificacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retroalimentacion TEXT,

    -- Conexión 1 a 1 con la Entrega
    CONSTRAINT fk_entrega_calificacion
        FOREIGN KEY(entrega_id)
        REFERENCES Entrega(id)
        ON DELETE CASCADE, -- Si se borra la entrega, se borra su calificación

    -- Restricción para que la nota sea positiva
    CONSTRAINT chk_nota_valida
        CHECK (nota_obtenida >= 0.0)
);

COMMENT ON TABLE Calificacion IS 'Nota y retroalimentación asignada por un profesor a una entrega.';
COMMENT ON COLUMN Calificacion.entrega_id IS 'Referencia única a la entrega que se está calificando (Relación 1 a 1).';

-- =================================================================
--  SCRIPT PARA LA GESTIÓN DE ASISTENCIA
--  Base de Datos: PostgreSQL (Compatible con NeonDB)
-- =================================================================

-- -----------------------------------------------------------------
--  DEFINICIÓN DE TIPO ENUM PERSONALIZADO
-- -----------------------------------------------------------------

CREATE TYPE estado_asistencia AS ENUM (
    'Presente',
    'Ausente',
    'Justificado', -- Ausencia con excusa
    'Tardanza'     -- Llegó tarde
);

-- =================================================================
--  TABLA ASISTENCIA
--  Registra la asistencia de un estudiante (inscripción) en una fecha.
-- =================================================================
CREATE TABLE Asistencia (
    id SERIAL PRIMARY KEY,
    inscripcion_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    estado estado_asistencia NOT NULL,
    grupo_id INTEGER NOT NULL, -- Incluido por el diagrama (probablemente por rendimiento)

    -- Llave foránea a la inscripción (Estudiante + Grupo)
    CONSTRAINT fk_inscripcion_asistencia
        FOREIGN KEY(inscripcion_id)
        REFERENCES Inscripcion(id)
        ON DELETE CASCADE, -- Si se borra la inscripción, se borra el registro de asistencia

    -- Llave foránea al Grupo (para consultas rápidas por grupo)
    CONSTRAINT fk_grupo_asistencia
        FOREIGN KEY(grupo_id)
        REFERENCES Grupo(id)
        ON DELETE CASCADE, -- Si se borra el grupo, se borra el registro de asistencia
    
    -- Restricción para evitar duplicados: un estudiante por fecha
    CONSTRAINT uq_asistencia_estudiante_fecha
        UNIQUE (inscripcion_id, fecha)
);

-- Índice para optimizar la búsqueda de asistencia por grupo y fecha
-- (Basado en la función obtener_asistencia_por_fecha del diagrama)
CREATE INDEX idx_asistencia_grupo_fecha ON Asistencia(grupo_id, fecha);

COMMENT ON TABLE Asistencia IS 'Registro de asistencia (Presente, Ausente, etc.) de un estudiante en una fecha específica.';
COMMENT ON COLUMN Asistencia.inscripcion_id IS 'Referencia a la inscripción (el estudiante en el grupo).';
COMMENT ON COLUMN Asistencia.grupo_id IS 'Referencia denormalizada al grupo para optimizar consultas de lista de asistencia.';
COMMENT ON COLUMN Asistencia.fecha IS 'Día específico de la toma de asistencia.';