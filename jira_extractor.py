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
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from jira import JIRA
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from rich.prompt import Prompt, Confirm

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
    
    def search_project_issues(self, project_key: str, max_results: int = None) -> List[Any]:
        """
        Busca TODOS los issues del proyecto usando paginación automática
        
        Args:
            project_key: Clave del proyecto (ej: CMZ100)
            max_results: Límite opcional (None = extraer todos los issues)
            
        Returns:
            Lista completa de issues encontrados
        """
        self.console.print(f"🔍 [cyan]Buscando issues del proyecto {project_key}...[/cyan]")
        
        # Determinar si extraer todos o usar límite
        extract_all = config.EXTRACT_ALL_ISSUES and max_results is None
        safety_limit = max_results or config.MAX_ISSUES_FALLBACK
        
        if extract_all:
            self.console.print("   🌐 [blue]Modo: Extracción completa (todos los issues)[/blue]")
        else:
            self.console.print(f"   📊 [blue]Modo: Límite de {safety_limit} issues[/blue]")
        
        # Estrategias de búsqueda JQL en orden de prioridad
        search_strategies = [
            # 1. Issues activos primero
            {
                'jql': f'project = {project_key} AND status NOT IN (Cerrado, Finalizado, Done, Resolved, Closed) ORDER BY updated DESC',
                'description': 'Issues activos'
            },
            # 2. Issues recientes (últimos 90 días)
            {
                'jql': f'project = {project_key} AND updated >= -90d ORDER BY updated DESC',
                'description': 'Issues recientes (90 días)'
            },
            # 3. Todos los issues del proyecto
            {
                'jql': f'project = {project_key} ORDER BY created DESC',
                'description': 'Todos los issues'
            }
        ]
        
        all_issues = []
        successful_strategy = None
        
        for i, strategy in enumerate(search_strategies, 1):
            try:
                self.console.print(f"   📋 [dim]Estrategia {i}: {strategy['description']}[/dim]")
                
                # Implementar paginación completa
                start_at = 0
                page_size = config.JIRA_PAGE_SIZE
                strategy_issues = []
                
                while True:
                    # Verificar límite de seguridad
                    if len(strategy_issues) >= safety_limit:
                        self.console.print(f"   🛡️ [yellow]Límite de seguridad alcanzado: {safety_limit} issues[/yellow]")
                        break
                    
                    # Calcular el tamaño de la página actual
                    remaining = safety_limit - len(strategy_issues)
                    current_page_size = min(page_size, remaining) if not extract_all else page_size
                    
                    self.console.print(f"   📄 [dim]Página: desde {start_at}, tamaño {current_page_size}[/dim]")
                    
                    # Hacer la consulta paginada
                    page_issues = self.jira.search_issues(
                        strategy['jql'],
                        startAt=start_at,
                        maxResults=current_page_size,
                        expand='changelog'
                    )
                    
                    # Si no hay más resultados, terminar
                    if not page_issues:
                        self.console.print(f"   ✅ [green]Fin de resultados en posición {start_at}[/green]")
                        break
                    
                    # Agregar issues encontrados
                    strategy_issues.extend(page_issues)
                    total_found = len(strategy_issues)
                    
                    self.console.print(f"   📊 [green]+{len(page_issues)} issues (total: {total_found})[/green]")
                    
                    # Si la página devolvió menos issues que el solicitado, ya no hay más
                    if len(page_issues) < current_page_size:
                        self.console.print(f"   🏁 [green]Última página: {len(page_issues)} < {current_page_size}[/green]")
                        break
                    
                    # Preparar siguiente página
                    start_at += len(page_issues)
                    
                    # Pequeña pausa para evitar rate limiting
                    if config.PAGE_DELAY > 0:
                        time.sleep(config.PAGE_DELAY)
                
                # Si encontramos issues con esta estrategia, usarla
                if strategy_issues:
                    all_issues = strategy_issues
                    successful_strategy = i
                    self.console.print(f"   ✅ [bold green]Estrategia {i} exitosa: {len(all_issues)} issues totales[/bold green]")
                    break
                else:
                    self.console.print(f"   ⚠️ [yellow]Sin resultados con estrategia {i}[/yellow]")
                    
            except Exception as e:
                self.console.print(f"   ❌ [red]Error en estrategia {i}: {str(e)}[/red]")
                continue
        
        # Remover duplicados manteniendo el orden (por si acaso)
        if all_issues:
            unique_issues = {issue.key: issue for issue in all_issues}
            final_issues = list(unique_issues.values())
            
            duplicates_removed = len(all_issues) - len(final_issues)
            if duplicates_removed > 0:
                self.console.print(f"   🔄 [yellow]Duplicados eliminados: {duplicates_removed}[/yellow]")
        else:
            final_issues = []
        
        # Resumen final
        if final_issues:
            self.console.print(f"📊 [bold blue]TOTAL ENCONTRADO: {len(final_issues)} issues únicos[/bold blue]")
            if successful_strategy:
                self.console.print(f"   🎯 [dim]Usando estrategia {successful_strategy}[/dim]")
        else:
            self.console.print("❌ [red]No se encontraron issues en ninguna estrategia[/red]")
        
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
        
        # Obtener información de sprint
        sprint_info = self._extract_sprint_info(issue)
        
        return {
            'is_subtask': getattr(issue.fields.issuetype, 'subtask', False),
            'parent_key': issue.fields.parent.key if hasattr(issue.fields, 'parent') and issue.fields.parent else None,
            'sprint_name': sprint_info['name'],
            'sprint_id': sprint_info['id'],
            'sprint_state': sprint_info['state'],
            'board_name': f'{issue.fields.project.key} - Proyecto Principal'
        }
    
    def _extract_sprint_info(self, issue: Any) -> Dict[str, str]:
        """
        Extrae información del sprint del issue
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con información del sprint
        """
        sprint_info = {
            'name': 'Sin Sprint',
            'id': 'N/A',
            'state': 'N/A'
        }
        
        try:
            # Buscar en campos personalizados que contengan información de sprint
            for field_name, field_value in issue.fields.__dict__.items():
                if 'sprint' in field_name.lower() and field_value:
                    # Los sprints en Jira suelen estar en un campo como customfield_xxxxx
                    if isinstance(field_value, list) and field_value:
                        # Tomar el último sprint (el más reciente)
                        last_sprint = field_value[-1]
                        if hasattr(last_sprint, 'name'):
                            sprint_info['name'] = last_sprint.name
                            sprint_info['id'] = str(getattr(last_sprint, 'id', 'N/A'))
                            sprint_info['state'] = getattr(last_sprint, 'state', 'N/A')
                        elif isinstance(last_sprint, str):
                            # Algunos casos el sprint viene como string
                            sprint_info['name'] = last_sprint
                        break
                    elif hasattr(field_value, 'name'):
                        sprint_info['name'] = field_value.name
                        sprint_info['id'] = str(getattr(field_value, 'id', 'N/A'))
                        sprint_info['state'] = getattr(field_value, 'state', 'N/A')
                        break
        except Exception as e:
            # En caso de error, mantener valores por defecto
            pass
        
        return sprint_info
    
    def _extract_metadata(self, issue: Any) -> Dict[str, Any]:
        """Extrae metadatos (componentes, labels, etc.)"""
        components = [comp.name for comp in issue.fields.components] if issue.fields.components else []
        labels = issue.fields.labels if issue.fields.labels else []
        
        return {
            'components': ', '.join(components) if components else 'Sin Componentes',
            'labels': ', '.join(labels) if labels else 'Sin Labels'
        }
    
    def process_project_data(self, project_key: str, max_results: int = None, use_sprints: bool = False) -> List[Dict[str, Any]]:
        """
        Procesa todos los datos de un proyecto
        
        Args:
            project_key: Clave del proyecto
            max_results: Límite máximo de issues (None = todos)
            use_sprints: Si True, permite seleccionar sprints específicos
            
        Returns:
            Lista de datos procesados
        """
        if use_sprints:
            # Obtener sprints activos de todos los boards del proyecto
            self.console.print("🏃‍♂️ [cyan]Obteniendo sprints activos del proyecto...[/cyan]")
            active_sprints = self.get_active_project_sprints(project_key)
            
            # Mostrar tabla de sprints activos
            if active_sprints:
                self.display_active_sprints_table(active_sprints)
            
            # Obtener IDs de sprints del usuario
            sprint_ids = self.get_sprint_ids_from_user(active_sprints)
            
            if not sprint_ids:
                self.console.print("❌ [red]No se seleccionaron sprints para procesar[/red]")
                self.console.print("   [yellow]Continuando con búsqueda tradicional...[/yellow]")
                issues = self.search_project_issues(project_key, max_results)
            else:
                # Buscar issues de los sprints seleccionados
                issues = self.search_sprint_issues(project_key, sprint_ids, max_results)
        else:
            # Búsqueda tradicional (todos los issues del proyecto)
            issues = self.search_project_issues(project_key, max_results)
        
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
        
        # Distribución por sprint (si hay información de sprints)
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
    
    def run(self, project_key: str, export_format: str = 'both', max_results: int = None, use_sprints: bool = False) -> bool:
        """
        Ejecuta el proceso completo de extracción
        
        Args:
            project_key: Clave del proyecto
            export_format: Formato de exportación
            max_results: Límite máximo de issues (None = extraer todos)
            use_sprints: Si True, permite seleccionar sprints específicos
            
        Returns:
            True si el proceso fue exitoso
        """
        mode_description = "COMPLETA" if max_results is None else f"LIMITADA ({max_results})"
        if use_sprints:
            mode_description += " - SPRINTS ESPECÍFICOS"
        
        self.console.print(Panel.fit(
            f"🎯 [bold]EXTRACCIÓN DE DATOS JIRA[/bold]\n"
            f"Proyecto: {project_key}\n"
            f"Modo: {mode_description}",
            border_style="blue"
        ))
        
        # Conectar a Jira
        if not self.connect_to_jira():
            return False
        
        # Procesar datos del proyecto con opción de sprints
        data = self.process_project_data(project_key, max_results, use_sprints)
        
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

    def get_project_boards(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Obtiene los boards asociados al proyecto
        
        Args:
            project_key: Clave del proyecto
            
        Returns:
            Lista de boards del proyecto
        """
        # Usar directamente el método alternativo que sabemos que funciona
        try:
            # Usar la biblioteca requests directamente para la API de Agile con paginación               
            server = os.getenv('JIRA_SERVER')
            email = os.getenv('JIRA_EMAIL')
            token = os.getenv('JIRA_API_TOKEN')
            
            all_boards = []
            start_at = 0
            max_results = 50
            
            self.console.print("🔄 [cyan]Obteniendo todos los boards con paginación completa...[/cyan]")
            
            while True:
                url = f"{server}/rest/agile/1.0/board"
                params = {
                    'startAt': start_at,
                    'maxResults': max_results
                }
                auth = (email, token)
                
                response = requests.get(url, auth=auth, params=params)
                if response.status_code != 200:
                    self.console.print(f"⚠️ [yellow]API Agile no disponible (HTTP {response.status_code})[/yellow]")
                    return []
                
                data = response.json()
                boards = data.get('values', [])
                
                if not boards:
                    break
                
                all_boards.extend(boards)
                self.console.print(f"   📄 [dim]Página {start_at//max_results + 1}: +{len(boards)} boards (total: {len(all_boards)})[/dim]")
                
                # Si obtuvimos menos boards que el máximo, ya no hay más páginas
                if len(boards) < max_results:
                    break
                    
                start_at += max_results
            
            # Filtrar por proyecto
            project_boards = []
            for board in all_boards:
                if 'location' in board and 'projectKey' in board['location']:
                    if board['location']['projectKey'] == project_key:
                        project_boards.append({
                            'id': board['id'],
                            'name': board['name'],
                            'type': board['type']
                        })
                        self.console.print(f"   ✅ [green]Board encontrado: {board['name']} (ID: {board['id']})[/green]")
            
            self.console.print(f"📋 [cyan]Encontrados {len(all_boards)} boards totales, {len(project_boards)} del proyecto {project_key}[/cyan]")
            return project_boards
                
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Error obteniendo boards: {str(e)}[/yellow]")
            return []
    
    def get_active_project_sprints(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sprints activos de todos los boards del proyecto
        
        Args:
            project_key: Clave del proyecto
            
        Returns:
            Lista de sprints activos ordenados por fecha de creación (más recientes primero)
        """
        try:
            # Obtener todos los boards del proyecto
            boards = self.get_project_boards(project_key)
            
            if not boards:
                self.console.print("⚠️ [yellow]No se encontraron boards para obtener sprints[/yellow]")
                return []
            
            self.console.print(f"📋 [cyan]Encontrados {len(boards)} boards: {[b['name'] for b in boards]}[/cyan]")
            
            all_active_sprints = []
            
            # Obtener sprints activos de todos los boards
            for board in boards:
                self.console.print(f"   📊 [dim]Obteniendo sprints del board: {board['name']} (ID: {board['id']})[/dim]")
                
                try:
                    server = os.getenv('JIRA_SERVER')
                    email = os.getenv('JIRA_EMAIL')
                    token = os.getenv('JIRA_API_TOKEN')
                    
                    url = f"{server}/rest/agile/1.0/board/{board['id']}/sprint"
                    auth = (email, token)
                    
                    start_at = 0
                    max_results = 50
                    board_active_sprints = 0
                    
                    # Buscar primero todos los sprints del board y luego filtrar por activos
                    while True:
                        params = {
                            'startAt': start_at,
                            'maxResults': max_results
                            # Removemos el filtro 'state': 'active' para obtener todos y filtrar después
                        }
                        
                        response = requests.get(url, auth=auth, params=params)
                        if response.status_code != 200:
                            self.console.print(f"   ⚠️ [dim]Error HTTP {response.status_code} en board {board['name']}: {response.text[:100]}[/dim]")
                            break
                        
                        data = response.json()
                        sprints = data.get('values', [])
                        
                        if not sprints:
                            self.console.print(f"   📄 [dim]No hay más sprints en board {board['name']}[/dim]")
                            break
                        
                        self.console.print(f"   📄 [dim]Página {start_at//max_results + 1}: {len(sprints)} sprints encontrados[/dim]")
                        
                        # Procesar todos los sprints y filtrar por activos
                        for sprint in sprints:
                            sprint_state = sprint.get('state', '').lower()
                            self.console.print(f"   🔍 [dim]Sprint: {sprint['name'][:20]} - Estado: {sprint_state}[/dim]")
                            
                            if sprint_state == 'active':
                                sprint_data = {
                                    'id': sprint['id'],
                                    'name': sprint['name'],
                                    'state': sprint['state'],
                                    'startDate': sprint.get('startDate', 'No definida'),
                                    'endDate': sprint.get('endDate', 'No definida'),
                                    'goal': sprint.get('goal', 'Sin objetivo'),
                                    'board_name': board['name'],
                                    'board_id': board['id']
                                }
                                all_active_sprints.append(sprint_data)
                                board_active_sprints += 1
                                self.console.print(f"   ✅ [green]Sprint activo encontrado: {sprint['name']}[/green]")
                        
                        # Si obtuvimos menos sprints que el máximo, ya no hay más páginas
                        if len(sprints) < max_results:
                            break
                            
                        start_at += max_results
                    
                    self.console.print(f"   📊 [blue]Board {board['name']}: {board_active_sprints} sprints activos[/blue]")
                
                except Exception as e:
                    self.console.print(f"   ❌ [red]Error obteniendo sprints del board {board['name']}: {str(e)}[/red]")
                    continue
            
            # Mostrar resumen total
            self.console.print(f"🏁 [bold cyan]TOTAL: {len(all_active_sprints)} sprints activos encontrados en todos los boards[/bold cyan]")
            
            if not all_active_sprints:
                self.console.print("⚠️ [yellow]No se encontraron sprints activos en ningún board[/yellow]")
                return []
            
            # Eliminar duplicados por ID de sprint, manteniendo la primera ocurrencia
            unique_sprints = {}
            for sprint in all_active_sprints:
                sprint_id = sprint['id']
                if sprint_id not in unique_sprints:
                    unique_sprints[sprint_id] = sprint
                else:
                    # Si ya existe, podemos combinar información de boards
                    existing = unique_sprints[sprint_id]
                    # Mantener el board principal pero agregar info de que está en múltiples boards
                    if existing['board_name'] != sprint['board_name']:
                        existing['board_name'] = f"{existing['board_name']} (+{sprint['board_name']})"
            
            # Convertir de vuelta a lista
            unique_active_sprints = list(unique_sprints.values())
            
            duplicates_removed = len(all_active_sprints) - len(unique_active_sprints)
            if duplicates_removed > 0:
                self.console.print(f"🔄 [yellow]Sprints duplicados eliminados: {duplicates_removed}[/yellow]")
                self.console.print(f"📊 [cyan]Sprints únicos: {len(unique_active_sprints)}[/cyan]")
            
            # Ordenar por ID (los IDs más altos son más recientes)
            unique_active_sprints.sort(key=lambda x: x['id'], reverse=True)
            
            return unique_active_sprints
            
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Error obteniendo sprints activos del proyecto: {str(e)}[/yellow]")
            return []
    
    def display_active_sprints_table(self, sprints: List[Dict[str, Any]]) -> None:
        """
        Muestra una tabla con los sprints activos disponibles
        
        Args:
            sprints: Lista de sprints activos a mostrar
        """
        if not sprints:
            self.console.print("❌ [red]No se encontraron sprints activos[/red]")
            return
        
        table = Table(title="🟢 Sprints Activos Disponibles", show_header=True)
        table.add_column("ID", style="blue", width=8)
        table.add_column("Nombre", style="green", width=30)
        table.add_column("Board", style="bright_blue", width=20)
        table.add_column("Fecha Inicio", style="magenta", width=12)
        table.add_column("Fecha Fin", style="magenta", width=12)
        table.add_column("Objetivo", style="cyan", width=25)
        
        for sprint in sprints:
            # Formatear fechas
            start_date = sprint['startDate']
            end_date = sprint['endDate']
            
            if start_date and start_date != 'No definida':
                try:
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except:
                    pass
            
            if end_date and end_date != 'No definida':
                try:
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except:
                    pass
            
            # Obtener objetivo del sprint
            goal = sprint.get('goal', 'Sin objetivo')
            if goal and len(goal) > 25:
                goal = goal[:22] + "..."
            
            table.add_row(
                str(sprint['id']),
                sprint['name'][:30],
                sprint['board_name'][:20],
                start_date,
                end_date,
                goal
            )
        
        self.console.print(table)
    
    def get_sprint_ids_from_user(self, active_sprints: List[Dict[str, Any]]) -> List[int]:
        """
        Solicita al usuario que ingrese IDs de sprints o usa los activos por defecto
        
        Args:
            active_sprints: Lista de sprints activos disponibles
            
        Returns:
            Lista de IDs de sprints a procesar
        """
        self.console.print("\n📋 [bold]Selección de Sprints[/bold]")
        self.console.print("Opciones disponibles:")
        self.console.print("• [cyan]Presiona Enter[/cyan] para procesar todos los sprints activos mostrados")
        self.console.print("• Ingresa IDs específicos: [cyan]6393,6364,5847[/cyan]")
        self.console.print("• Ingresa un solo ID: [cyan]6393[/cyan]")
        
        while True:
            user_input = Prompt.ask(
                "\n¿Qué sprints quieres procesar? (Enter = sprints activos)",
                default=""
            ).strip()
            
            # Si no ingresa nada, usar todos los sprints activos
            if not user_input:
                if active_sprints:
                    sprint_ids = [sprint['id'] for sprint in active_sprints]
                    self.console.print(f"\n✅ [green]Procesando {len(sprint_ids)} sprints activos por defecto[/green]")
                    for sprint in active_sprints:
                        self.console.print(f"  🟢 {sprint['name']} (ID: {sprint['id']}) [{sprint['board_name']}]")
                    return sprint_ids
                else:
                    self.console.print("❌ [red]No hay sprints activos disponibles[/red]")
                    return []
            
            # Procesar IDs ingresados manualmente
            try:
                # Limpiar entrada y dividir por comas
                id_strings = [id_str.strip() for id_str in user_input.split(',')]
                sprint_ids = []
                
                for id_str in id_strings:
                    if id_str:  # Evitar strings vacíos
                        sprint_ids.append(int(id_str))
                
                if not sprint_ids:
                    self.console.print("❌ [red]No se ingresaron IDs válidos[/red]")
                    continue
                
                # Mostrar confirmación
                self.console.print(f"\n✅ [green]IDs de sprints ingresados: {len(sprint_ids)}[/green]")
                for sprint_id in sprint_ids:
                    # Buscar información del sprint si está en la lista de activos
                    sprint_info = next((s for s in active_sprints if s['id'] == sprint_id), None)
                    if sprint_info:
                        self.console.print(f"  🟢 {sprint_info['name']} (ID: {sprint_id}) [{sprint_info['board_name']}]")
                    else:
                        self.console.print(f"  ⚪ Sprint ID: {sprint_id} (no está en sprints activos)")
                
                if Confirm.ask("\n¿Confirmas estos IDs de sprints?", default=True):
                    return sprint_ids
                
            except ValueError:
                self.console.print("❌ [red]Error: Ingresa solo números separados por comas (ej: 6393,6364)[/red]")
            except Exception as e:
                self.console.print(f"❌ [red]Error procesando los IDs: {str(e)}[/red]")
    
    def search_sprint_issues(self, project_key: str, sprint_ids: List[int], max_results: int = None) -> List[Any]:
        """
        Busca issues de sprints específicos
        
        Args:
            project_key: Clave del proyecto
            sprint_ids: Lista de IDs de sprints
            max_results: Límite opcional de issues
            
        Returns:
            Lista de issues de los sprints seleccionados
        """
        self.console.print(f"🔍 [cyan]Buscando issues de {len(sprint_ids)} sprint(s)...[/cyan]")
        
        # Determinar límite
        extract_all = config.EXTRACT_ALL_ISSUES and max_results is None
        safety_limit = max_results or config.MAX_ISSUES_FALLBACK
        
        if extract_all:
            self.console.print("   🌐 [blue]Modo: Extracción completa de sprints[/blue]")
        else:
            self.console.print(f"   📊 [blue]Modo: Límite de {safety_limit} issues[/blue]")
        
        # Crear JQL para los sprints seleccionados
        sprint_clause = " OR ".join([f"sprint = {sprint_id}" for sprint_id in sprint_ids])
        jql = f"project = {project_key} AND ({sprint_clause}) ORDER BY updated DESC"
        
        self.console.print(f"   📋 [dim]JQL: {jql}[/dim]")
        self.console.print(f"   🎯 [dim]Sprint IDs: {', '.join(map(str, sprint_ids))}[/dim]")
        
        all_issues = []
        
        try:
            # Implementar paginación
            start_at = 0
            page_size = config.JIRA_PAGE_SIZE
            
            while True:
                # Verificar límite de seguridad
                if len(all_issues) >= safety_limit:
                    self.console.print(f"   🛡️ [yellow]Límite de seguridad alcanzado: {safety_limit} issues[/yellow]")
                    break
                
                # Calcular tamaño de página actual
                remaining = safety_limit - len(all_issues)
                current_page_size = min(page_size, remaining) if not extract_all else page_size
                
                self.console.print(f"   📄 [dim]Página: desde {start_at}, tamaño {current_page_size}[/dim]")
                
                # Hacer la consulta paginada
                page_issues = self.jira.search_issues(
                    jql,
                    startAt=start_at,
                    maxResults=current_page_size,
                    expand='changelog'
                )
                
                # Si no hay más resultados, terminar
                if not page_issues:
                    self.console.print(f"   ✅ [green]Fin de resultados en posición {start_at}[/green]")
                    break
                
                # Agregar issues encontrados
                all_issues.extend(page_issues)
                total_found = len(all_issues)
                
                self.console.print(f"   📊 [green]+{len(page_issues)} issues (total: {total_found})[/green]")
                
                # Si la página devolvió menos issues que el solicitado, ya no hay más
                if len(page_issues) < current_page_size:
                    self.console.print(f"   🏁 [green]Última página: {len(page_issues)} < {current_page_size}[/green]")
                    break
                
                # Preparar siguiente página
                start_at += len(page_issues)
                
                # Pequeña pausa para evitar rate limiting
                if config.PAGE_DELAY > 0:
                    time.sleep(config.PAGE_DELAY)
        
        except Exception as e:
            self.console.print(f"❌ [red]Error buscando issues de sprints: {str(e)}[/red]")
            return []
        
        # Resumen final
        if all_issues:
            self.console.print(f"📊 [bold blue]TOTAL ENCONTRADO: {len(all_issues)} issues de sprints[/bold blue]")
        else:
            self.console.print("❌ [red]No se encontraron issues en los sprints especificados[/red]")
        
        return all_issues


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Extractor de datos de proyectos Jira con timetracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python jira_extractor.py --project CMZ100
  python jira_extractor.py --project CMZ100 --format excel
  python jira_extractor.py --project CMZ100 --sprints
  python jira_extractor.py --project ABC123 --sprints --limit 500
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
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Límite máximo de issues a procesar (opcional)'
    )
    
    parser.add_argument(
        '--sprints', '-s',
        action='store_true',
        help='Permite seleccionar sprints específicos para extraer'
    )
    
    args = parser.parse_args()
    
    # Ejecutar extractor
    extractor = JiraDataExtractor()
    success = extractor.run(args.project, args.format, args.limit, args.sprints)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
