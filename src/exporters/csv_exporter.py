"""
Exportador a formato CSV
"""
import os
from typing import List, Dict, Any
from .base_exporter import BaseExporter


class CSVExporter(BaseExporter):
    """Exportador especializado en formato CSV"""
    
    def export(self, data: List[Dict[str, Any]], project_key: str, filename: str = None) -> bool:
        """
        Exporta los datos a formato CSV
        
        Args:
            data: Datos a exportar
            project_key: Clave del proyecto
            filename: Nombre del archivo (opcional, se genera automáticamente)
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            reports_dir = self.ensure_reports_directory()
            
            if not filename:
                filename = self.generate_filename(project_key, 'csv')
            
            csv_path = os.path.join(reports_dir, filename)
            self.console.print(f"📄 [cyan]Generando CSV: {csv_path}[/cyan]")
            
            # Preparar DataFrame
            df = self.prepare_dataframe(data)
            
            # Exportar a CSV con encoding UTF-8 BOM para compatibilidad
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            self.console.print(f"✅ [green]CSV generado: {csv_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Error generando CSV: {str(e)}[/red]")
            return False
