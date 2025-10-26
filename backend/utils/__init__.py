"""
Módulo de utilidades del backend.

Contiene funciones auxiliares para:
- Formateo y conversión de fechas/horas
- Validaciones comunes
- Helpers para servicios
"""

from .datetime_utils import (
    format_time_range,
    parse_time_string,
    dias_semana_to_name,
    name_to_dias_semana,
    calcular_dias_vencimiento,
    es_fecha_pasada,
    es_fecha_futura,
    obtener_fecha_actual,
    obtener_datetime_actual,
    format_date_spanish,
    parse_date_string,
)

from .validators import (
    validar_email,
    validar_porcentaje,
    validar_codigo,
    validar_documento,
    validar_rango_tiempo,
    validar_duracion_horario,
    sanitizar_texto,
    validar_telefono,
    validar_url,
    validar_nota,
    validar_cupo,
    validar_semestre,
    validar_nombre_salon,
    validar_dia_semana,
    validar_tipo_actividad,
    validar_prioridad,
    validar_estado_inscripcion,
    validar_estado_entrega,
    validar_longitud_texto,
    es_password_seguro,
)

__all__ = [
    # datetime_utils
    'format_time_range',
    'parse_time_string',
    'dias_semana_to_name',
    'name_to_dias_semana',
    'calcular_dias_vencimiento',
    'es_fecha_pasada',
    'es_fecha_futura',
    'obtener_fecha_actual',
    'obtener_datetime_actual',
    'format_date_spanish',
    'parse_date_string',
    # validators
    'validar_email',
    'validar_porcentaje',
    'validar_codigo',
    'validar_documento',
    'validar_rango_tiempo',
    'validar_duracion_horario',
    'sanitizar_texto',
    'validar_telefono',
    'validar_url',
    'validar_nota',
    'validar_cupo',
    'validar_semestre',
    'validar_nombre_salon',
    'validar_dia_semana',
    'validar_tipo_actividad',
    'validar_prioridad',
    'validar_estado_inscripcion',
    'validar_estado_entrega',
    'validar_longitud_texto',
    'es_password_seguro',
]
