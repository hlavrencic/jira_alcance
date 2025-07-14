"""
Extractor principal de datos de Jira - Versión refactorizada
"""
import time
from typing import List, Dict, Any, Optional
from rich.progress import track

from .config import EXTRACTION_CONFIG, get_jql_strategies
from .services import JiraService  
from .extractors import TimetrackingExtractor, MetadataExtractor, StructureExtractor
from .utils import SprintManager, SubtaskProcessor, DisplayUtils
from .exporters import ExcelExporter, CSVExporter


class JiraDataExtractor:
    """Extractor principal de datos de proyectos Jira con timetracking"""
    
    def __init__(self):
        """Inicializa el extractor con todos sus componentes"""
        # Servicios
        self.jira_service = JiraService()
        
        # Extractores especializados
        self.timetracking_extractor = TimetrackingExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.structure_extractor = StructureExtractor()
        
        # Utilidades
        self.sprint_manager = SprintManager(self.jira_service)
        self.subtask_processor = SubtaskProcessor()
        self.display_utils = DisplayUtils()
        
        # Exportadores
        self.excel_exporter = ExcelExporter()
        self.csv_exporter = CSVExporter()
    
    def run(self, project_key: str, export_format: str = 'both', 
            max_results: int = None, use_sprints: bool = True) -> bool:
        """
        Ejecuta el proceso completo de extracción
        
        Args:
            project_key: Clave del proyecto
            export_format: Formato de exportación ('excel', 'csv', 'both')
            max_results: Límite máximo de issues (None = extraer todos)
            use_sprints: Si True, permite seleccionar sprints específicos
            
        Returns:
            True si el proceso fue exitoso
        """
        # Mostrar encabezado
        mode_description = self._get_mode_description(max_results, use_sprints)
        self.display_utils.show_extraction_header(project_key, mode_description)
        
        # Conectar a Jira
        if not self.jira_service.connect():
            return False
        
        # Procesar datos del proyecto
        data = self._process_project_data(project_key, max_results, use_sprints)
        
        if not data:
            self.jira_service.console.print("⚠️ [yellow]No se encontraron datos para extraer[/yellow]")
            return False
        
        # Mostrar resumen
        self.display_utils.show_extraction_summary(data)
        
        # Exportar datos
        if not self._export_data(data, project_key, export_format):
            return False
        
        # Mostrar mensaje de finalización
        self.display_utils.show_completion_message(len(data))
        
        return True
    
    def _process_project_data(self, project_key: str, max_results: int = None, 
                             use_sprints: bool = True) -> List[Dict[str, Any]]:
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
            issues = self._get_sprint_issues(project_key, max_results)
        else:
            issues = self._search_project_issues(project_key, max_results)
        
        if not issues:
            self.jira_service.console.print("❌ [red]No se encontraron issues para procesar[/red]")
            return []
        
        return self._process_issues(issues)
    
    def _get_sprint_issues(self, project_key: str, max_results: int = None) -> List[Any]:
        """Obtiene issues de sprints seleccionados"""
        # Obtener sprints activos y cerrados recientes
        self.jira_service.console.print("🏃‍♂️ [cyan]Obteniendo sprints activos y cerrados recientes del proyecto...[/cyan]")
        available_sprints = self.sprint_manager.get_active_project_sprints(project_key)
        
        # Mostrar tabla de sprints disponibles
        if available_sprints:
            self.sprint_manager.display_active_sprints_table(available_sprints)
        
        # Obtener IDs de sprints del usuario
        sprint_ids = self.sprint_manager.get_sprint_ids_from_user(available_sprints)
        
        if not sprint_ids:
            self.jira_service.console.print("❌ [red]No se seleccionaron sprints para procesar[/red]")
            self.jira_service.console.print("   [yellow]Continuando con búsqueda tradicional...[/yellow]")
            return self._search_project_issues(project_key, max_results)
        else:
            return self._search_sprint_issues(project_key, sprint_ids, max_results)
    
    def _search_project_issues(self, project_key: str, max_results: int = None) -> List[Any]:
        """
        Busca TODOS los issues del proyecto usando paginación automática
        
        Args:
            project_key: Clave del proyecto (ej: CMZ100)
            max_results: Límite opcional (None = extraer todos los issues)
            
        Returns:
            Lista completa de issues encontrados
        """
        self.jira_service.console.print(f"🔍 [cyan]Buscando issues del proyecto {project_key}...[/cyan]")
        
        # Determinar configuración de extracción
        extract_all = EXTRACTION_CONFIG['extract_all_issues'] and max_results is None
        safety_limit = max_results or EXTRACTION_CONFIG['max_issues_fallback']
        
        mode_text = "Extracción completa (todos los issues)" if extract_all else f"Límite de {safety_limit} issues"
        self.jira_service.console.print(f"   🌐 [blue]Modo: {mode_text}[/blue]")
        
        # Probar estrategias de búsqueda
        search_strategies = get_jql_strategies(project_key)
        
        for i, strategy in enumerate(search_strategies, 1):
            try:
                self.jira_service.console.print(f"   📋 [dim]Estrategia {i}: {strategy['description']}[/dim]")
                
                issues = self._paginated_search(strategy['jql'], safety_limit, extract_all)
                
                if issues:
                    self.jira_service.console.print(f"   ✅ [bold green]Estrategia {i} exitosa: {len(issues)} issues totales[/bold green]")
                    return self._remove_duplicates(issues)
                else:
                    self.jira_service.console.print(f"   ⚠️ [yellow]Sin resultados con estrategia {i}[/yellow]")
                    
            except Exception as e:
                self.jira_service.console.print(f"   ❌ [red]Error en estrategia {i}: {str(e)}[/red]")
                continue
        
        self.jira_service.console.print("❌ [red]No se encontraron issues en ninguna estrategia[/red]")
        return []
    
    def _search_sprint_issues(self, project_key: str, sprint_ids: List[int], 
                             max_results: int = None) -> List[Any]:
        """Busca issues de sprints específicos"""
        self.jira_service.console.print(f"🔍 [cyan]Buscando issues de {len(sprint_ids)} sprint(s)...[/cyan]")
        
        # Configuración
        extract_all = EXTRACTION_CONFIG['extract_all_issues'] and max_results is None
        safety_limit = max_results or EXTRACTION_CONFIG['max_issues_fallback']
        
        mode_text = "Extracción completa de sprints" if extract_all else f"Límite de {safety_limit} issues"
        self.jira_service.console.print(f"   🌐 [blue]Modo: {mode_text}[/blue]")
        
        # Crear JQL para los sprints seleccionados
        sprint_clause = " OR ".join([f"sprint = {sprint_id}" for sprint_id in sprint_ids])
        jql = f"project = {project_key} AND ({sprint_clause}) ORDER BY updated DESC"
        
        self.jira_service.console.print(f"   📋 [dim]JQL: {jql}[/dim]")
        self.jira_service.console.print(f"   🎯 [dim]Sprint IDs: {', '.join(map(str, sprint_ids))}[/dim]")
        
        # Buscar issues
        issues = self._paginated_search(jql, safety_limit, extract_all)
        
        if issues:
            final_issues = self._remove_duplicates(issues)
            self.jira_service.console.print(f"📊 [bold blue]TOTAL ENCONTRADO: {len(final_issues)} issues de sprints[/bold blue]")
            return final_issues
        else:
            self.jira_service.console.print("❌ [red]No se encontraron issues en los sprints seleccionados[/red]")
            return []
    
    def _paginated_search(self, jql: str, safety_limit: int, extract_all: bool) -> List[Any]:
        """Realiza búsqueda paginada"""
        start_at = 0
        page_size = EXTRACTION_CONFIG['page_size']
        all_issues = []
        
        while True:
            # Verificar límite de seguridad
            if len(all_issues) >= safety_limit:
                self.jira_service.console.print(f"   🛡️ [yellow]Límite de seguridad alcanzado: {safety_limit} issues[/yellow]")
                break
            
            # Calcular tamaño de página actual
            remaining = safety_limit - len(all_issues)
            current_page_size = min(page_size, remaining) if not extract_all else page_size
            
            self.jira_service.console.print(f"   📄 [dim]Página: desde {start_at}, tamaño {current_page_size}[/dim]")
            
            # Hacer búsqueda
            page_issues = self.jira_service.search_issues(jql, start_at, current_page_size)
            
            if not page_issues:
                self.jira_service.console.print(f"   🏁 [green]Última página: 0 < {current_page_size}[/green]")
                break
            
            all_issues.extend(page_issues)
            self.jira_service.console.print(f"   📊 [green]+{len(page_issues)} issues (total: {len(all_issues)})[/green]")
            
            # Verificar si es la última página
            if len(page_issues) < current_page_size:
                self.jira_service.console.print(f"   🏁 [green]Última página: {len(page_issues)} < {current_page_size}[/green]")
                break
            
            start_at += len(page_issues)
            
            # Pausa para evitar rate limiting
            if EXTRACTION_CONFIG['page_delay'] > 0:
                time.sleep(EXTRACTION_CONFIG['page_delay'])
        
        return all_issues
    
    def _remove_duplicates(self, issues: List[Any]) -> List[Any]:
        """Elimina issues duplicados"""
        unique_issues = {issue.key: issue for issue in issues}
        final_issues = list(unique_issues.values())
        
        duplicates_removed = len(issues) - len(final_issues)
        if duplicates_removed > 0:
            self.jira_service.console.print(f"   🔄 [yellow]Duplicados eliminados: {duplicates_removed}[/yellow]")
        
        return final_issues
    
    def _process_issues(self, issues: List[Any]) -> List[Dict[str, Any]]:
        """Procesa lista de issues extrayendo todos los datos"""
        self.jira_service.console.print("⚙️ [cyan]Procesando datos de timetracking...[/cyan]")
        
        # Procesar todos los issues
        all_issues_data = []
        for issue in track(issues, description="Procesando issues..."):
            issue_data = self._extract_issue_data(issue)
            if issue_data:
                all_issues_data.append(issue_data)
        
        # Separar subtareas de issues principales
        main_issues = [issue for issue in all_issues_data if not issue.get('is_subtask', False)]
        subtasks = [issue for issue in all_issues_data if issue.get('is_subtask', False)]
        
        # Procesar relaciones de subtareas
        self.jira_service.console.print("🔗 [cyan]Procesando relaciones de subtareas...[/cyan]")
        final_data = self.subtask_processor.process_subtask_relationships(main_issues, subtasks)
        
        return final_data
    
    def _extract_issue_data(self, issue: Any) -> Dict[str, Any]:
        """Extrae todos los datos relevantes de un issue usando extractores especializados"""
        try:
            # Datos básicos del issue
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
            
            # Usar extractores especializados
            data.update(self.timetracking_extractor.extract(issue))
            data.update(self.structure_extractor.extract(issue))
            data.update(self.metadata_extractor.extract(issue))
            
            return data
            
        except Exception as e:
            self.jira_service.console.print(f"⚠️ [yellow]Error procesando {issue.key}: {str(e)}[/yellow]")
            return {}
    
    def _export_data(self, data: List[Dict[str, Any]], project_key: str, 
                    export_format: str) -> bool:
        """Exporta los datos usando los exportadores especializados"""
        if not data:
            self.jira_service.console.print("❌ [red]No hay datos para exportar[/red]")
            return False
        
        success = True
        
        # Exportar según el formato solicitado
        if export_format in ['excel', 'both']:
            if not self.excel_exporter.export(data, project_key):
                success = False
        
        if export_format in ['csv', 'both']:
            if not self.csv_exporter.export(data, project_key):
                success = False
        
        return success
    
    def _get_mode_description(self, max_results: int, use_sprints: bool) -> str:
        """Genera descripción del modo de ejecución"""
        mode_description = "COMPLETA" if max_results is None else f"LIMITADA ({max_results})"
        if use_sprints:
            mode_description += " - SELECCIÓN DE SPRINTS"
        else:
            mode_description += " - BÚSQUEDA TRADICIONAL"
        return mode_description
