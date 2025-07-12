#!/usr/bin/env python3
"""
🎯 Jira Data Extractor - Versión Refactorizada

Herramienta principal para extraer datos de proyectos Jira con timetracking.
Adaptado para proyectos con o sin sprints activos.

Autor: Sistema Automatizado
Fecha: Julio 2025
Versión: 2.0 (Refactorizada)
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from jira import JIRA
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

import config

# Cargar variables de entorno
load_dotenv()


class JiraDataExtractor:
    """Extractor de datos de proyectos Jira con timetracking"""
    
    def __init__(self):
        """Inicializa el extractor"""
        self.console = Console()
        self.jira: Optional[JIRA] = None
        
    def connect_to_jira(self) -> bool:
        """
        Establece conexión con Jira usando credenciales del archivo .env
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            server = os.getenv('JIRA_SERVER')
            email = os.getenv('JIRA_EMAIL')
            token = os.getenv('JIRA_API_TOKEN')
            
            if not all([server, email, token]):
                self.console.print("❌ [red]Error: Credenciales no configuradas en .env[/red]")
                return False
            
            self.console.print("🔄 [cyan]Conectando a Jira...[/cyan]")
            
            self.jira = JIRA(
                server=server,
                basic_auth=(email, token)
            )
            
            # Verificar conexión
            current_user = self.jira.current_user()
            self.console.print(f"✅ [green]Conectado como: {current_user}[/green]")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Error de conexión: {str(e)}[/red]")
            return False
    
    def search_project_issues(self, project_key: str, max_results: int = 200) -> List[Any]:
        """
        Busca issues del proyecto usando múltiples estrategias
        
        Args:
            project_key: Clave del proyecto (ej: CMZ100)
            max_results: Máximo número de resultados
            
        Returns:
            Lista de issues encontrados
        """
        self.console.print(f"🔍 [cyan]Buscando issues del proyecto {project_key}...[/cyan]")
        
        # Estrategias de búsqueda en orden de prioridad
        search_strategies = [
            f'project = {project_key} AND status NOT IN (Cerrado, Finalizado, Done, Resolved) ORDER BY updated DESC',
            f'project = {project_key} AND updated >= -60d ORDER BY created DESC',
            f'project = {project_key} ORDER BY created DESC'
        ]
        
        all_issues = []
        
        for i, jql in enumerate(search_strategies, 1):
            try:
                self.console.print(f"   📋 [dim]Estrategia {i}: Buscando issues...[/dim]")
                
                issues = self.jira.search_issues(
                    jql, 
                    maxResults=max_results,
                    expand='changelog'
                )
                
                if issues:
                    self.console.print(f"   ✅ [green]Encontrados {len(issues)} issues[/green]")
                    all_issues.extend(issues)
                    
                    # Si encontramos suficientes datos, no seguimos buscando
                    if len(all_issues) >= 50:
                        break
                else:
                    self.console.print(f"   ⚠️ [yellow]Sin resultados con esta estrategia[/yellow]")
                    
            except Exception as e:
                self.console.print(f"   ❌ [red]Error en estrategia {i}: {str(e)}[/red]")
                continue
        
        # Remover duplicados manteniendo el orden
        unique_issues = {issue.key: issue for issue in all_issues}
        final_issues = list(unique_issues.values())
        
        self.console.print(f"📊 [bold]Total issues únicos: {len(final_issues)}[/bold]")
        
        return final_issues
    
    def extract_issue_data(self, issue: Any) -> Dict[str, Any]:
        """
        Extrae todos los datos relevantes de un issue
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con datos del issue
        """
        try:
            # Datos básicos
            data = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'issue_type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else 'Sin Prioridad',
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Sin Asignar',
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Desconocido',
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'project_key': issue.fields.project.key
            }
            
            # Datos de timetracking
            time_data = self._extract_timetracking(issue)
            data.update(time_data)
            
            # Relaciones y estructura
            structure_data = self._extract_structure_data(issue)
            data.update(structure_data)
            
            # Componentes y labels
            metadata = self._extract_metadata(issue)
            data.update(metadata)
            
            return data
            
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Error procesando {issue.key}: {str(e)}[/yellow]")
            return {}
    
    def _extract_timetracking(self, issue: Any) -> Dict[str, Any]:
        """Extrae datos de timetracking del issue"""
        time_data = {
            'time_spent': '0h',
            'original_estimate': '0h', 
            'remaining_estimate': '0h',
            'time_spent_seconds': 0,
            'original_estimate_seconds': 0,
            'remaining_estimate_seconds': 0
        }
        
        if hasattr(issue.fields, 'timetracking') and issue.fields.timetracking:
            tt = issue.fields.timetracking
            
            # Tiempo gastado
            if hasattr(tt, 'timeSpentSeconds') and tt.timeSpentSeconds:
                seconds = tt.timeSpentSeconds
                time_data['time_spent_seconds'] = seconds
                time_data['time_spent'] = f"{seconds / 3600:.2f}h"
            
            # Estimación original
            if hasattr(tt, 'originalEstimateSeconds') and tt.originalEstimateSeconds:
                seconds = tt.originalEstimateSeconds
                time_data['original_estimate_seconds'] = seconds
                time_data['original_estimate'] = f"{seconds / 3600:.2f}h"
            
            # Tiempo restante
            if hasattr(tt, 'remainingEstimateSeconds') and tt.remainingEstimateSeconds:
                seconds = tt.remainingEstimateSeconds
                time_data['remaining_estimate_seconds'] = seconds
                time_data['remaining_estimate'] = f"{seconds / 3600:.2f}h"
        
        return time_data
    
    def _extract_structure_data(self, issue: Any) -> Dict[str, Any]:
        """Extrae datos de estructura (subtareas, padre, etc.)"""
        return {
            'is_subtask': getattr(issue.fields.issuetype, 'subtask', False),
            'parent_key': issue.fields.parent.key if hasattr(issue.fields, 'parent') and issue.fields.parent else None,
            'sprint_name': 'Sin Sprint Activo',  # Puede ser expandido para detectar sprints
            'board_name': f'{issue.fields.project.key} - Proyecto Principal'
        }
    
    def _extract_metadata(self, issue: Any) -> Dict[str, Any]:
        """Extrae metadatos (componentes, labels, etc.)"""
        components = [comp.name for comp in issue.fields.components] if issue.fields.components else []
        labels = issue.fields.labels if issue.fields.labels else []
        
        return {
            'components': ', '.join(components) if components else 'Sin Componentes',
            'labels': ', '.join(labels) if labels else 'Sin Labels'
        }
    
    def process_project_data(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Procesa todos los datos de un proyecto
        
        Args:
            project_key: Clave del proyecto
            
        Returns:
            Lista de datos procesados
        """
        # Buscar issues
        issues = self.search_project_issues(project_key)
        
        if not issues:
            self.console.print("❌ [red]No se encontraron issues para procesar[/red]")
            return []
        
        # Procesar datos
        self.console.print("⚙️ [cyan]Procesando datos de timetracking...[/cyan]")
        
        processed_data = []
        
        for issue in track(issues, description="Procesando issues..."):
            issue_data = self.extract_issue_data(issue)
            if issue_data:  # Solo agregar si se procesó correctamente
                processed_data.append(issue_data)
        
        return processed_data
    
    def display_summary(self, data: List[Dict[str, Any]]) -> None:
        """Muestra resumen de los datos procesados"""
        if not data:
            return
        
        self.console.print("\n📊 [bold]RESUMEN DE DATOS EXTRAÍDOS[/bold]")
        
        # Métricas generales
        total_issues = len(data)
        total_time_spent = sum(item['time_spent_seconds'] for item in data)
        total_estimated = sum(item['original_estimate_seconds'] for item in data)
        
        # Tabla de métricas
        metrics_table = Table(title="📈 Métricas Generales", show_header=True)
        metrics_table.add_column("Métrica", style="cyan")
        metrics_table.add_column("Valor", style="green")
        
        metrics_table.add_row("Total Issues", str(total_issues))
        metrics_table.add_row("Tiempo Registrado", f"{total_time_spent/3600:.1f} horas")
        metrics_table.add_row("Tiempo Estimado", f"{total_estimated/3600:.1f} horas")
        
        if total_estimated > 0:
            progress = (total_time_spent / total_estimated) * 100
            metrics_table.add_row("Progreso", f"{progress:.1f}%")
        
        self.console.print(metrics_table)
        
        # Distribución por tipo
        type_counts = {}
        for item in data:
            issue_type = item['issue_type']
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
    
    def export_data(self, data: List[Dict[str, Any]], project_key: str, format_type: str = 'both') -> bool:
        """
        Exporta los datos a archivos
        
        Args:
            data: Datos a exportar
            project_key: Clave del proyecto
            format_type: Formato de exportación ('excel', 'csv', 'both')
            
        Returns:
            True si la exportación fue exitosa
        """
        if not data:
            self.console.print("❌ [red]No hay datos para exportar[/red]")
            return False
        
        # Crear directorio de reportes
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{project_key.lower()}_data_{timestamp}"
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        success = True
        
        # Exportar a Excel
        if format_type in ['excel', 'both']:
            try:
                excel_path = os.path.join(reports_dir, f"{base_filename}.xlsx")
                self.console.print(f"📊 [cyan]Generando Excel: {excel_path}[/cyan]")
                
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=f'{project_key}_Data', index=False)
                    
                    # Formatear columnas
                    worksheet = writer.sheets[f'{project_key}_Data']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                self.console.print(f"✅ [green]Excel generado: {excel_path}[/green]")
                
            except Exception as e:
                self.console.print(f"❌ [red]Error generando Excel: {str(e)}[/red]")
                success = False
        
        # Exportar a CSV
        if format_type in ['csv', 'both']:
            try:
                csv_path = os.path.join(reports_dir, f"{base_filename}.csv")
                self.console.print(f"📄 [cyan]Generando CSV: {csv_path}[/cyan]")
                
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                self.console.print(f"✅ [green]CSV generado: {csv_path}[/green]")
                
            except Exception as e:
                self.console.print(f"❌ [red]Error generando CSV: {str(e)}[/red]")
                success = False
        
        return success
    
    def run(self, project_key: str, export_format: str = 'both') -> bool:
        """
        Ejecuta el proceso completo de extracción
        
        Args:
            project_key: Clave del proyecto
            export_format: Formato de exportación
            
        Returns:
            True si el proceso fue exitoso
        """
        self.console.print(Panel.fit(
            f"🎯 [bold]EXTRACCIÓN DE DATOS JIRA[/bold]\n"
            f"Proyecto: {project_key}",
            border_style="blue"
        ))
        
        # Conectar a Jira
        if not self.connect_to_jira():
            return False
        
        # Procesar datos del proyecto
        data = self.process_project_data(project_key)
        
        if not data:
            self.console.print("⚠️ [yellow]No se encontraron datos para extraer[/yellow]")
            return False
        
        # Mostrar resumen
        self.display_summary(data)
        
        # Exportar datos
        if not self.export_data(data, project_key, export_format):
            return False
        
        self.console.print(Panel.fit(
            "✅ [bold green]EXTRACCIÓN COMPLETADA[/bold green]\n"
            f"Se procesaron {len(data)} issues exitosamente",
            border_style="green"
        ))
        
        return True


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Extractor de datos de proyectos Jira con timetracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python jira_extractor.py --project CMZ100
  python jira_extractor.py --project CMZ100 --format excel
  python jira_extractor.py --project ABC123 --format csv
        """
    )
    
    parser.add_argument(
        '--project', '-p',
        required=True,
        help='Clave del proyecto (requerido, ej: CMZ100)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['excel', 'csv', 'both'],
        default='both',
        help='Formato de exportación (default: both)'
    )
    
    args = parser.parse_args()
    
    # Ejecutar extractor
    extractor = JiraDataExtractor()
    success = extractor.run(args.project, args.format)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
