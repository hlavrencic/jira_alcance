"""
Extractor base para datos de Jira
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExtractor(ABC):
    """Clase base para extractores de datos de Jira"""
    
    @abstractmethod
    def extract(self, issue: Any) -> Dict[str, Any]:
        """
        Extrae datos del issue
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con datos extraídos
        """
        pass
    
    def _safe_get_attribute(self, obj: Any, attribute: str, default: Any = None) -> Any:
        """
        Obtiene un atributo de forma segura
        
        Args:
            obj: Objeto del cual extraer el atributo
            attribute: Nombre del atributo
            default: Valor por defecto si no existe
            
        Returns:
            Valor del atributo o valor por defecto
        """
        try:
            return getattr(obj, attribute, default)
        except (AttributeError, TypeError):
            return default
    
    def _safe_get_nested_attribute(self, obj: Any, path: str, default: Any = None) -> Any:
        """
        Obtiene un atributo anidado de forma segura
        
        Args:
            obj: Objeto del cual extraer el atributo
            path: Ruta del atributo separada por puntos (ej: 'fields.assignee.displayName')
            default: Valor por defecto si no existe
            
        Returns:
            Valor del atributo anidado o valor por defecto
        """
        try:
            current = obj
            for attr in path.split('.'):
                current = getattr(current, attr)
                if current is None:
                    return default
            return current
        except (AttributeError, TypeError):
            return default
    
    def _convert_seconds_to_hours(self, seconds: int) -> str:
        """
        Convierte segundos a horas con formato decimal usando coma
        
        Args:
            seconds: Tiempo en segundos
            
        Returns:
            Horas formateadas con coma decimal
        """
        if not seconds:
            return '0,0'
        
        hours = round(seconds / 3600, 1)
        return str(hours).replace('.', ',')
