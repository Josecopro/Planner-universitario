"""
Utilidades de validación para datos del sistema.

Funciones para validar emails, códigos, porcentajes, y otros formatos comunes.
"""

import re
from datetime import time
from typing import Optional


def validar_email(email: str) -> bool:
    """
    Valida el formato de un email.
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si el email es válido
        
    Example:
        >>> validar_email("estudiante@universidad.edu")
        True
        >>> validar_email("invalido@")
        False
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefono(telefono: str) -> bool:
    """
    Valida el formato de un número de teléfono.
    Acepta formatos: 1234567890, 123-456-7890, (123) 456-7890, +57 123 4567890
    
    Args:
        telefono: Número de teléfono a validar
        
    Returns:
        bool: True si el teléfono es válido
        
    Example:
        >>> validar_telefono("3001234567")
        True
        >>> validar_telefono("+57 300 1234567")
        True
    """
    if not telefono:
        return False
    
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    
    pattern = r'^\+?\d{7,15}$'
    return re.match(pattern, telefono_limpio) is not None


def validar_url(url: str) -> bool:
    """
    Valida el formato de una URL.
    
    Args:
        url: URL a validar
        
    Returns:
        bool: True si la URL es válida
        
    Example:
        >>> validar_url("https://www.universidad.edu")
        True
    """
    if not url:
        return False
    
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return re.match(pattern, url) is not None


def validar_codigo(codigo: str, max_length: int = 30) -> bool:
    """
    Valida el formato de un código académico (curso, programa, facultad).
    Debe contener solo letras, números y guiones, sin espacios.
    
    Args:
        codigo: Código a validar
        max_length: Longitud máxima permitida
        
    Returns:
        bool: True si el código es válido
        
    Example:
        >>> validar_codigo("IS-101")
        True
        >>> validar_codigo("MAT-201")
        True
        >>> validar_codigo("ING SIS")
        False
    """
    if not codigo or len(codigo) > max_length:
        return False
    
    pattern = r'^[A-Z0-9\-]+$'
    return re.match(pattern, codigo.upper()) is not None


def validar_documento(documento: str) -> bool:
    """
    Valida el formato de un documento de identidad.
    Acepta entre 5 y 20 caracteres alfanuméricos.
    
    Args:
        documento: Documento a validar
        
    Returns:
        bool: True si el documento es válido
        
    Example:
        >>> validar_documento("1234567890")
        True
        >>> validar_documento("ABC123456")
        True
    """
    if not documento:
        return False
    
    doc_limpio = re.sub(r'[\s\-]', '', documento)
    
    return 5 <= len(doc_limpio) <= 20 and doc_limpio.isalnum()


def validar_porcentaje(valor: float, incluir_cero: bool = True) -> bool:
    """
    Valida que un valor esté en el rango de porcentaje válido.
    
    Args:
        valor: Valor a validar
        incluir_cero: Si True, permite 0%; si False, el mínimo es 0.01%
        
    Returns:
        bool: True si el porcentaje es válido
        
    Example:
        >>> validar_porcentaje(50.5)
        True
        >>> validar_porcentaje(101)
        False
    """
    if incluir_cero:
        return 0 <= valor <= 100
    else:
        return 0 < valor <= 100


def validar_nota(nota: float, escala_min: float = 0.0, escala_max: float = 5.0) -> bool:
    """
    Valida que una nota esté dentro de la escala permitida.
    
    Args:
        nota: Nota a validar
        escala_min: Valor mínimo de la escala (por defecto 0.0)
        escala_max: Valor máximo de la escala (por defecto 5.0)
        
    Returns:
        bool: True si la nota es válida
        
    Example:
        >>> validar_nota(4.5)
        True
        >>> validar_nota(6.0)
        False
        >>> validar_nota(85, escala_min=0, escala_max=100)
        True
    """
    return escala_min <= nota <= escala_max


def validar_cupo(cupo: int, minimo: int = 1, maximo: int = 100) -> bool:
    """
    Valida que el cupo esté dentro de un rango válido.
    
    Args:
        cupo: Número de cupo
        minimo: Cupo mínimo permitido (por defecto 1)
        maximo: Cupo máximo permitido (por defecto 100)
        
    Returns:
        bool: True si el cupo es válido
        
    Example:
        >>> validar_cupo(30)
        True
        >>> validar_cupo(150)
        False
        >>> validar_cupo(5, minimo=1, maximo=10)
        True
    """
    return minimo <= cupo <= maximo


def validar_semestre(semestre: str) -> bool:
    """
    Valida el formato de un código de semestre.
    Formato esperado: YYYY-N (ej: 2025-1, 2024-2)
    
    Args:
        semestre: Semestre a validar
        
    Returns:
        bool: True si el semestre es válido
        
    Example:
        >>> validar_semestre("2025-1")
        True
        >>> validar_semestre("2025-2")
        True
        >>> validar_semestre("2025-3")
        False
    """
    if not semestre:
        return False
    
    pattern = r'^\d{4}-[12]$'
    return re.match(pattern, semestre) is not None


def validar_rango_tiempo(
    hora_inicio: time,
    hora_fin: time,
    hora_min: Optional[time] = None,
    hora_max: Optional[time] = None
) -> bool:
    """
    Valida que un rango de tiempo sea coherente y esté dentro de límites.
    
    Args:
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        hora_min: Hora mínima permitida (opcional)
        hora_max: Hora máxima permitida (opcional)
        
    Returns:
        bool: True si el rango es válido
        
    Example:
        >>> validar_rango_tiempo(time(8, 0), time(10, 0), time(6, 0), time(22, 0))
        True
        >>> validar_rango_tiempo(time(10, 0), time(8, 0))
        False
    """
    if hora_fin <= hora_inicio:
        return False
    
    if hora_min and hora_inicio < hora_min:
        return False
    
    if hora_max and hora_fin > hora_max:
        return False
    
    return True


def validar_duracion_horario(
    hora_inicio: time,
    hora_fin: time,
    min_minutos: int = 30,
    max_minutos: int = 240
) -> bool:
    """
    Valida que la duración de un horario esté dentro de límites razonables.
    
    Args:
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        min_minutos: Duración mínima en minutos (por defecto 30)
        max_minutos: Duración máxima en minutos (por defecto 240 = 4 horas)
        
    Returns:
        bool: True si la duración es válida
        
    Example:
        >>> validar_duracion_horario(time(8, 0), time(9, 30))
        True
        >>> validar_duracion_horario(time(8, 0), time(14, 0))
        False
    """
    inicio_mins = hora_inicio.hour * 60 + hora_inicio.minute
    fin_mins = hora_fin.hour * 60 + hora_fin.minute
    duracion = fin_mins - inicio_mins
    
    return min_minutos <= duracion <= max_minutos


def sanitizar_texto(
    texto: str,
    max_length: Optional[int] = None,
    permitir_vacio: bool = False
) -> str:
    """
    Limpia y sanitiza un texto.
    
    Args:
        texto: Texto a sanitizar
        max_length: Longitud máxima (opcional)
        permitir_vacio: Si False, retorna error si el texto está vacío
        
    Returns:
        str: Texto sanitizado
        
    Raises:
        ValueError: Si el texto está vacío y permitir_vacio es False
        
    Example:
        >>> sanitizar_texto("  Hola Mundo  ", max_length=10)
        'Hola Mundo'
    """
    texto_limpio = texto.strip()
    
    if not texto_limpio and not permitir_vacio:
        raise ValueError("El texto no puede estar vacío")
    
    if max_length and len(texto_limpio) > max_length:
        texto_limpio = texto_limpio[:max_length].strip()
    
    return texto_limpio


def validar_longitud_texto(
    texto: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> bool:
    """
    Valida la longitud de un texto.
    
    Args:
        texto: Texto a validar
        min_length: Longitud mínima (opcional)
        max_length: Longitud máxima (opcional)
        
    Returns:
        bool: True si la longitud es válida
        
    Example:
        >>> validar_longitud_texto("Hola", min_length=2, max_length=10)
        True
    """
    longitud = len(texto.strip())
    
    if min_length and longitud < min_length:
        return False
    
    if max_length and longitud > max_length:
        return False
    
    return True


def validar_nombre_salon(salon: str) -> bool:
    """
    Valida el formato de un nombre de salón.
    
    Args:
        salon: Nombre del salón a validar
        
    Returns:
        bool: True si el salón es válido
        
    Example:
        >>> validar_nombre_salon("Bloque 5 - 101")
        True
        >>> validar_nombre_salon("Virtual")
        True
    """
    if not salon:
        return False
    
    if len(salon) > 50:
        return False
    
    pattern = r'^[A-Za-z0-9\s\-]+$'
    return re.match(pattern, salon) is not None


def es_password_seguro(
    password: str,
    min_length: int = 8,
    requiere_mayuscula: bool = True,
    requiere_minuscula: bool = True,
    requiere_numero: bool = True,
    requiere_especial: bool = False
) -> bool:
    """
    Valida que una contraseña cumpla con criterios de seguridad.
    
    Args:
        password: Contraseña a validar
        min_length: Longitud mínima (por defecto 8)
        requiere_mayuscula: Requiere al menos una mayúscula
        requiere_minuscula: Requiere al menos una minúscula
        requiere_numero: Requiere al menos un número
        requiere_especial: Requiere al menos un carácter especial
        
    Returns:
        bool: True si la contraseña es segura
        
    Example:
        >>> es_password_seguro("Abc12345")
        True
        >>> es_password_seguro("abc")
        False
    """
    if len(password) < min_length:
        return False
    
    if requiere_mayuscula and not re.search(r'[A-Z]', password):
        return False
    
    if requiere_minuscula and not re.search(r'[a-z]', password):
        return False
    
    if requiere_numero and not re.search(r'\d', password):
        return False
    
    if requiere_especial and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True


def validar_estado_inscripcion(estado: str) -> bool:
    """
    Valida que un estado de inscripción sea válido.
    
    Args:
        estado: Estado a validar
        
    Returns:
        bool: True si el estado es válido
        
    Example:
        >>> validar_estado_inscripcion("activa")
        True
    """
    estados_validos = {'activa', 'cancelada', 'retirada', 'finalizada'}
    return estado.lower() in estados_validos


def validar_estado_entrega(estado: str) -> bool:
    """
    Valida que un estado de entrega sea válido.
    
    Args:
        estado: Estado a validar
        
    Returns:
        bool: True si el estado es válido
        
    Example:
        >>> validar_estado_entrega("entregada")
        True
    """
    estados_validos = {'pendiente', 'entregada', 'tardia', 'revisada', 'calificada'}
    return estado.lower() in estados_validos


def validar_dia_semana(dia: str) -> bool:
    """
    Valida que un nombre de día de la semana sea válido.
    Acepta nombres completos en español.
    
    Args:
        dia: Nombre del día
        
    Returns:
        bool: True si el día es válido
        
    Example:
        >>> validar_dia_semana('Lunes')
        True
        >>> validar_dia_semana('Monday')
        False
    """
    dias_validos = {
        'lunes', 'martes', 'miércoles', 'miercoles', 
        'jueves', 'viernes', 'sábado', 'sabado', 'domingo'
    }
    return dia.lower() in dias_validos


def validar_tipo_actividad(tipo: str) -> bool:
    """
    Valida que un tipo de actividad evaluativa sea válido.
    
    Args:
        tipo: Tipo de actividad
        
    Returns:
        bool: True si el tipo es válido
        
    Example:
        >>> validar_tipo_actividad("Tarea")
        True
        >>> validar_tipo_actividad("Examen Parcial")
        True
    """
    tipos_validos = {
        'tarea', 'quiz', 'examen parcial', 'examen final', 
        'proyecto', 'laboratorio', 'otro'
    }
    return tipo.lower() in tipos_validos


def validar_prioridad(prioridad: str) -> bool:
    """
    Valida que una prioridad de actividad sea válida.
    
    Args:
        prioridad: Prioridad a validar
        
    Returns:
        bool: True si la prioridad es válida
        
    Example:
        >>> validar_prioridad("Alta")
        True
        >>> validar_prioridad("Urgente")
        False
    """
    prioridades_validas = {'baja', 'media', 'alta'}
    return prioridad.lower() in prioridades_validas
