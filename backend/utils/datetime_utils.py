"""
Utilidades para manejo de fechas, horas y tiempos.

Funciones para formateo, conversión y cálculos con datetime/time/date.
"""

from datetime import datetime, time, date, timedelta
from typing import Optional, Union


# ============ FORMATEO DE TIEMPO ============

def format_time_range(hora_inicio: time, hora_fin: time) -> str:
    """
    Formatea un rango de horas en formato legible.
    
    Args:
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        
    Returns:
        str: Rango formateado como "08:00 - 10:00"
        
    Example:
        >>> format_time_range(time(8, 0), time(10, 0))
        '08:00 - 10:00'
    """
    return f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"


def parse_time_string(time_str: str) -> Optional[time]:
    """
    Convierte un string a objeto time.
    
    Args:
        time_str: String en formato "HH:MM" o "HH:MM:SS"
        
    Returns:
        Optional[time]: Objeto time o None si el formato es inválido
        
    Example:
        >>> parse_time_string("14:30")
        time(14, 30)
    """
    if not time_str:
        return None
    
    # Intentar con formato HH:MM
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        pass
    
    # Intentar con formato HH:MM:SS
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        return None


# ============ CONVERSIÓN DE DÍAS DE LA SEMANA ============

def dias_semana_to_name(dia: str) -> str:
    """
    Convierte código de día a nombre completo en español.
    
    Args:
        dia: Código del día ('L', 'M', 'X', 'J', 'V', 'S', 'D')
        
    Returns:
        str: Nombre completo del día
        
    Example:
        >>> dias_semana_to_name('L')
        'Lunes'
    """
    dias = {
        'L': 'Lunes',
        'M': 'Martes', 
        'X': 'Miércoles',
        'J': 'Jueves',
        'V': 'Viernes',
        'S': 'Sábado',
        'D': 'Domingo'
    }
    return dias.get(dia.upper(), dia)


def name_to_dias_semana(nombre: str) -> Optional[str]:
    """
    Convierte nombre de día a código.
    
    Args:
        nombre: Nombre del día (puede ser completo o abreviado)
        
    Returns:
        Optional[str]: Código del día o None si no se reconoce
        
    Example:
        >>> name_to_dias_semana('Lunes')
        'L'
        >>> name_to_dias_semana('lun')
        'L'
    """
    nombre_lower = nombre.lower()
    
    mapeo = {
        'lunes': 'L', 'lun': 'L', 'l': 'L',
        'martes': 'M', 'mar': 'M', 'm': 'M',
        'miércoles': 'X', 'miercoles': 'X', 'mié': 'X', 'mie': 'X', 'x': 'X',
        'jueves': 'J', 'jue': 'J', 'j': 'J',
        'viernes': 'V', 'vie': 'V', 'v': 'V',
        'sábado': 'S', 'sabado': 'S', 'sáb': 'S', 'sab': 'S', 's': 'S',
        'domingo': 'D', 'dom': 'D', 'd': 'D',
    }
    
    return mapeo.get(nombre_lower)


# ============ CÁLCULOS CON FECHAS ============

def calcular_dias_vencimiento(fecha_entrega: Union[date, datetime]) -> int:
    """
    Calcula días hasta una fecha de vencimiento.
    
    Args:
        fecha_entrega: Fecha de vencimiento
        
    Returns:
        int: Días hasta el vencimiento (positivo = futuro, negativo = pasado)
        
    Example:
        >>> calcular_dias_vencimiento(date(2025, 10, 30))  # Hoy es 2025-10-23
        7
    """
    if isinstance(fecha_entrega, datetime):
        fecha_entrega = fecha_entrega.date()
    
    hoy = date.today()
    return (fecha_entrega - hoy).days


def es_fecha_pasada(fecha: Union[date, datetime]) -> bool:
    """
    Verifica si una fecha está en el pasado.
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        bool: True si la fecha es pasada
        
    Example:
        >>> es_fecha_pasada(date(2025, 10, 20))  # Hoy es 2025-10-23
        True
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    return fecha < date.today()


def es_fecha_futura(fecha: Union[date, datetime]) -> bool:
    """
    Verifica si una fecha está en el futuro.
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        bool: True si la fecha es futura
        
    Example:
        >>> es_fecha_futura(date(2025, 10, 25))  # Hoy es 2025-10-23
        True
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    return fecha > date.today()


def obtener_fecha_actual() -> date:
    """
    Retorna la fecha actual.
    
    Returns:
        date: Fecha actual
        
    Example:
        >>> obtener_fecha_actual()
        date(2025, 10, 23)
    """
    return date.today()


def obtener_datetime_actual() -> datetime:
    """
    Retorna la fecha y hora actual.
    
    Returns:
        datetime: Fecha y hora actual
        
    Example:
        >>> obtener_datetime_actual()
        datetime(2025, 10, 23, 14, 30, 0)
    """
    return datetime.now()


# ============ FORMATEO DE FECHAS ============

def format_date_spanish(fecha: Union[date, datetime], formato: str = 'completo') -> str:
    """
    Formatea una fecha en español.
    
    Args:
        fecha: Fecha a formatear
        formato: Tipo de formato ('completo', 'corto', 'medio')
        
    Returns:
        str: Fecha formateada
        
    Example:
        >>> format_date_spanish(date(2025, 10, 23), 'completo')
        '23 de octubre de 2025'
        >>> format_date_spanish(date(2025, 10, 23), 'corto')
        '23/10/2025'
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    if formato == 'corto':
        return fecha.strftime('%d/%m/%Y')
    
    elif formato == 'medio':
        meses = [
            'ene', 'feb', 'mar', 'abr', 'may', 'jun',
            'jul', 'ago', 'sep', 'oct', 'nov', 'dic'
        ]
        return f"{fecha.day} {meses[fecha.month - 1]} {fecha.year}"
    
    else:  # completo
        meses = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


def parse_date_string(date_str: str) -> Optional[date]:
    """
    Convierte un string a objeto date.
    
    Args:
        date_str: String en formato "YYYY-MM-DD", "DD/MM/YYYY" o "DD-MM-YYYY"
        
    Returns:
        Optional[date]: Objeto date o None si el formato es inválido
        
    Example:
        >>> parse_date_string("2025-10-23")
        date(2025, 10, 23)
        >>> parse_date_string("23/10/2025")
        date(2025, 10, 23)
    """
    if not date_str:
        return None
    
    # Intentar con formato ISO (YYYY-MM-DD)
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        pass
    
    # Intentar con formato DD/MM/YYYY
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        pass
    
    # Intentar con formato DD-MM-YYYY
    try:
        return datetime.strptime(date_str, '%d-%m-%Y').date()
    except ValueError:
        return None


# ============ UTILIDADES PARA HORARIOS ============

def calcular_duracion_minutos(hora_inicio: time, hora_fin: time) -> int:
    """
    Calcula la duración en minutos entre dos horas.
    
    Args:
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        
    Returns:
        int: Duración en minutos
        
    Example:
        >>> calcular_duracion_minutos(time(8, 0), time(10, 30))
        150
    """
    inicio_mins = hora_inicio.hour * 60 + hora_inicio.minute
    fin_mins = hora_fin.hour * 60 + hora_fin.minute
    return fin_mins - inicio_mins


def agregar_minutos_a_time(hora: time, minutos: int) -> time:
    """
    Agrega minutos a un objeto time.
    
    Args:
        hora: Hora base
        minutos: Minutos a agregar (puede ser negativo)
        
    Returns:
        time: Nueva hora
        
    Example:
        >>> agregar_minutos_a_time(time(8, 0), 90)
        time(9, 30)
    """
    # Convertir time a datetime para hacer la suma
    dt = datetime.combine(date.today(), hora)
    dt_nuevo = dt + timedelta(minutes=minutos)
    return dt_nuevo.time()


def esta_en_rango_horario(
    hora_verificar: time,
    hora_inicio: time,
    hora_fin: time,
    inclusivo: bool = True
) -> bool:
    """
    Verifica si una hora está dentro de un rango.
    
    Args:
        hora_verificar: Hora a verificar
        hora_inicio: Hora de inicio del rango
        hora_fin: Hora de fin del rango
        inclusivo: Si True, incluye los límites del rango
        
    Returns:
        bool: True si la hora está en el rango
        
    Example:
        >>> esta_en_rango_horario(time(9, 0), time(8, 0), time(10, 0))
        True
    """
    if inclusivo:
        return hora_inicio <= hora_verificar <= hora_fin
    else:
        return hora_inicio < hora_verificar < hora_fin


def calcular_estado_entrega(fecha_limite: Union[date, datetime]) -> str:
    """
    Calcula el estado de una entrega basado en la fecha límite.
    
    Args:
        fecha_limite: Fecha límite de entrega
        
    Returns:
        str: Estado ('a_tiempo', 'por_vencer', 'vencida')
        
    Example:
        >>> calcular_estado_entrega(date(2025, 10, 25))  # Hoy es 2025-10-23
        'a_tiempo'
    """
    dias = calcular_dias_vencimiento(fecha_limite)
    
    if dias < 0:
        return 'vencida'
    elif dias <= 2:
        return 'por_vencer'
    else:
        return 'a_tiempo'


def es_entrega_tardia(
    fecha_entrega: Union[date, datetime],
    fecha_limite: Union[date, datetime]
) -> bool:
    """
    Verifica si una entrega fue tardía.
    
    Args:
        fecha_entrega: Fecha de la entrega realizada
        fecha_limite: Fecha límite
        
    Returns:
        bool: True si la entrega fue tardía
        
    Example:
        >>> es_entrega_tardia(date(2025, 10, 25), date(2025, 10, 23))
        True
    """
    if isinstance(fecha_entrega, datetime):
        fecha_entrega = fecha_entrega.date()
    if isinstance(fecha_limite, datetime):
        fecha_limite = fecha_limite.date()
    
    return fecha_entrega > fecha_limite
