"""
Exportador base para diferentes formatos
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from rich.console import Console

from ..config import EXPORT_CONFIG, COLUMN_ORDER


class BaseExporter(ABC):
    """Clase base para exportadores de datos"""
    
    def __init__(self):
        self.console = Console()
    
    @abstractmethod
    def export(self, data: List[Dict[str, Any]], project_key: str, filename: str) -> bool:
        """
        Exporta los datos al formato específico
        
        Args:
            data: Datos a exportar
            project_key: Clave del proyecto
            filename: Nombre del archivo (sin extensión)
            
        Returns:
            True si la exportación fue exitosa
        """
        pass
    
    def prepare_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepara el DataFrame con el orden de columnas correcto
        
        Args:
            data: Datos a exportar
            
        Returns:
            DataFrame preparado y ordenado
        """
        if not data:
            return pd.DataFrame()
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Construir orden de columnas
        ordered_columns = []
        for col_group in [
            COLUMN_ORDER['base'],
            COLUMN_ORDER['main'], 
            COLUMN_ORDER['time'],
            COLUMN_ORDER['aggregate_time'],
            COLUMN_ORDER['subtask'],
            COLUMN_ORDER['metadata']
        ]:
            for col in col_group:
                if col in df.columns:
                    ordered_columns.append(col)
        
        # Agregar cualquier columna restante
        for col in df.columns:
            if col not in ordered_columns:
                ordered_columns.append(col)
        
        return df[ordered_columns]
    
    def ensure_reports_directory(self) -> str:
        """
        Asegura que existe el directorio de reportes
        
        Returns:
            Ruta del directorio de reportes
        """
        reports_dir = EXPORT_CONFIG['reports_dir']
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir
    
    def generate_filename(self, project_key: str, extension: str) -> str:
        """
        Genera un nombre de archivo con timestamp
        
        Args:
            project_key: Clave del proyecto
            extension: Extensión del archivo (sin punto)
            
        Returns:
            Nombre completo del archivo
        """
        timestamp = datetime.now().strftime(EXPORT_CONFIG['timestamp_format'])
        return f"{project_key.lower()}_data_{timestamp}.{extension}"
