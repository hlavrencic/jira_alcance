"""
Utilidades para mostrar información en consola
"""
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class DisplayUtils:
    """Utilidades para mostrar información formateada en consola"""
    
    def __init__(self):
        self.console = Console()
    
    def show_extraction_summary(self, data: List[Dict[str, Any]]) -> None:
        """
        Muestra resumen de los datos extraídos
        
        Args:
            data: Lista de datos procesados
        """
        if not data:
            return
        
        self.console.print("\n📊 [bold]RESUMEN DE DATOS EXTRAÍDOS[/bold]")
        
        # Métricas generales
        self._show_general_metrics(data)
        
        # Distribución por tipo
        self._show_type_distribution(data)
        
        # Distribución por sprint (si hay información)
        self._show_sprint_distribution(data)
    
    def show_extraction_header(self, project_key: str, mode_description: str) -> None:
        """
        Muestra el encabezado de la extracción
        
        Args:
            project_key: Clave del proyecto
            mode_description: Descripción del modo de extracción
        """
        self.console.print(Panel.fit(
            f"🎯 [bold]EXTRACCIÓN DE DATOS JIRA[/bold]\n"
            f"Proyecto: {project_key}\n"
            f"Modo: {mode_description}",
            border_style="blue"
        ))
    
    def show_completion_message(self, issues_count: int) -> None:
        """
        Muestra mensaje de finalización
        
        Args:
            issues_count: Número de issues procesados
        """
        self.console.print(Panel.fit(
            "✅ [bold green]EXTRACCIÓN COMPLETADA[/bold green]\n"
            f"Se procesaron {issues_count} issues exitosamente",
            border_style="green"
        ))
    
    def _show_general_metrics(self, data: List[Dict[str, Any]]) -> None:
        """Muestra métricas generales"""
        total_issues = len(data)
        
        # Convertir valores con coma a float para cálculos
        total_time_spent = sum(self._parse_time_value(item.get('time_spent', '0,0')) for item in data)
        total_estimated = sum(self._parse_time_value(item.get('original_estimate', '0,0')) for item in data)
        
        # Tabla de métricas
        metrics_table = Table(title="📈 Métricas Generales", show_header=True)
        metrics_table.add_column("Métrica", style="cyan")
        metrics_table.add_column("Valor", style="green")
        
        metrics_table.add_row("Total Issues", str(total_issues))
        metrics_table.add_row("Tiempo Registrado", f"{total_time_spent:.1f} horas".replace('.', ','))
        metrics_table.add_row("Tiempo Estimado", f"{total_estimated:.1f} horas".replace('.', ','))
        
        if total_estimated > 0:
            progress = (total_time_spent / total_estimated) * 100
            metrics_table.add_row("Progreso", f"{progress:.1f}%".replace('.', ','))
        
        self.console.print(metrics_table)
    
    def _show_type_distribution(self, data: List[Dict[str, Any]]) -> None:
        """Muestra distribución por tipo de issue"""
        total_issues = len(data)
        type_counts = {}
        
        for item in data:
            issue_type = item.get('issue_type', 'Sin Tipo')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        if type_counts:
            type_table = Table(title="📋 Distribución por Tipo", show_header=True)
            type_table.add_column("Tipo", style="blue")
            type_table.add_column("Cantidad", style="yellow")
            type_table.add_column("Porcentaje", style="green")
            
            for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_issues) * 100
                type_table.add_row(issue_type, str(count), f"{percentage:.1f}%")
            
            self.console.print(type_table)
    
    def _show_sprint_distribution(self, data: List[Dict[str, Any]]) -> None:
        """Muestra distribución por sprint si hay información disponible"""
        total_issues = len(data)
        sprint_counts = {}
        has_sprint_info = False
        
        for item in data:
            sprint_name = item.get('sprint_name', 'Sin Sprint')
            if sprint_name and sprint_name != 'Sin Sprint':
                has_sprint_info = True
                sprint_counts[sprint_name] = sprint_counts.get(sprint_name, 0) + 1
        
        if has_sprint_info and sprint_counts:
            sprint_table = Table(title="🏃‍♂️ Distribución por Sprint", show_header=True)
            sprint_table.add_column("Sprint", style="magenta")
            sprint_table.add_column("Issues", style="yellow")
            sprint_table.add_column("Porcentaje", style="green")
            
            for sprint_name, count in sorted(sprint_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_issues) * 100
                sprint_table.add_row(sprint_name, str(count), f"{percentage:.1f}%")
            
            self.console.print(sprint_table)
    
    def _parse_time_value(self, time_str: str) -> float:
        """Convierte un valor de tiempo con formato de coma a float"""
        try:
            return float(str(time_str).replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
