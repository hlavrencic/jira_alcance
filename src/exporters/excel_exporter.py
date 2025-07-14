"""
Exportador a formato Excel
"""
import os
from typing import List, Dict, Any
import pandas as pd
from .base_exporter import BaseExporter
from ..config import EXPORT_CONFIG


class ExcelExporter(BaseExporter):
    """Exportador especializado en formato Excel"""
    
    def export(self, data: List[Dict[str, Any]], project_key: str, filename: str = None) -> bool:
        """
        Exporta los datos a formato Excel
        
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
                filename = self.generate_filename(project_key, 'xlsx')
            
            excel_path = os.path.join(reports_dir, filename)
            self.console.print(f"📊 [cyan]Generando Excel: {excel_path}[/cyan]")
            
            # Preparar DataFrame
            df = self.prepare_dataframe(data)
            
            # Crear archivo Excel con formato
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                sheet_name = EXPORT_CONFIG['excel_sheet_name_template'].format(project_key=project_key)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Formatear columnas
                worksheet = writer.sheets[sheet_name]
                self._format_excel_columns(worksheet)
            
            self.console.print(f"✅ [green]Excel generado: {excel_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Error generando Excel: {str(e)}[/red]")
            return False
    
    def _format_excel_columns(self, worksheet) -> None:
        """
        Aplica formato a las columnas del Excel
        
        Args:
            worksheet: Hoja de cálculo de Excel
        """
        try:
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                # Calcular el ancho óptimo de la columna
                for cell in column:
                    try:
                        if cell.value:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                    except Exception:
                        pass
                
                # Aplicar ancho ajustado con límites
                min_width = EXPORT_CONFIG['min_column_width']
                max_width = EXPORT_CONFIG['max_column_width']
                adjusted_width = max(min_width, min(max_length + 2, max_width))
                
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Advertencia al formatear Excel: {str(e)}[/yellow]")
