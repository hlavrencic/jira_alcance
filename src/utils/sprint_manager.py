"""
Gestor de sprints y selección de usuario
"""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from ..config import EXTRACTION_CONFIG
from ..services import JiraService


class SprintManager:
    """Gestor para operaciones relacionadas con sprints"""
    
    def __init__(self, jira_service: JiraService):
        self.jira_service = jira_service
        self.console = Console()
    
    def get_active_project_sprints(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sprints activos de todos los boards del proyecto
        
        Args:
            project_key: Clave del proyecto
            
        Returns:
            Lista de sprints activos ordenados por fecha de creación
        """
        try:
            # Calcular fecha límite para optimización
            cutoff_date = datetime.now() - timedelta(days=EXTRACTION_CONFIG['recent_sprint_days'])
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            
            self.console.print(f"⏰ [cyan]Optimización: buscando sprints creados después del {cutoff_date_str}[/cyan]")
            
            # Obtener todos los boards del proyecto
            boards = self.jira_service.get_project_boards(project_key)
            
            if not boards:
                self.console.print("⚠️ [yellow]No se encontraron boards para obtener sprints[/yellow]")
                return []
            
            self.console.print(f"📋 [cyan]Encontrados {len(boards)} boards: {[b['name'] for b in boards]}[/cyan]")
            
            all_active_sprints = []
            
            # Obtener sprints activos de todos los boards
            for board in boards:
                self.console.print(f"   📊 [dim]Obteniendo sprints del board: {board['name']} (ID: {board['id']})[/dim]")
                
                board_sprints = self.jira_service.get_board_sprints(board['id'])
                board_active_sprints = 0
                
                for sprint in board_sprints:
                    sprint_state = sprint.get('state', '').lower()
                    sprint_created = sprint.get('createdDate', '')
                    sprint_name = sprint.get('name', 'Sin nombre')
                    
                    # Verificar si el sprint fue creado dentro del rango
                    is_recent = self._is_sprint_recent(sprint_created, cutoff_date)
                    
                    self.console.print(f"   🔍 [dim]Sprint: {sprint_name[:20]} - Estado: {sprint_state} - Reciente: {is_recent}[/dim]")
                    
                    # Solo incluir sprints activos Y recientes
                    if sprint_state == 'active' and is_recent:
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
                
                self.console.print(f"   📊 [blue]Board {board['name']}: {board_active_sprints} sprints activos recientes[/blue]")
            
            # Mostrar resumen total
            self.console.print(f"🏁 [bold cyan]TOTAL: {len(all_active_sprints)} sprints activos encontrados en todos los boards[/bold cyan]")
            
            if not all_active_sprints:
                self.console.print("⚠️ [yellow]No se encontraron sprints activos en ningún board[/yellow]")
                return []
            
            # Eliminar duplicados y ordenar
            unique_sprints = self._remove_duplicates_and_sort(all_active_sprints)
            
            return unique_sprints
            
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
            start_date = self._format_date(sprint['startDate'])
            end_date = self._format_date(sprint['endDate'])
            
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
                    self._show_selected_sprints(active_sprints)
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
                    sprint_id = int(id_str)
                    sprint_ids.append(sprint_id)
                
                if not sprint_ids:
                    self.console.print("⚠️ [yellow]No se ingresaron IDs válidos[/yellow]")
                    continue
                
                # Mostrar confirmación
                self.console.print(f"\n✅ [green]IDs de sprints ingresados: {len(sprint_ids)}[/green]")
                self.console.print("🔍 [cyan]Obteniendo información detallada de los sprints...[/cyan]")
                
                # Obtener información completa de cada sprint desde la API
                sprint_details = self.jira_service.get_sprint_details(sprint_ids)
                self._show_sprint_confirmation_table(sprint_ids, sprint_details)
                
                return sprint_ids
                
            except ValueError:
                self.console.print("❌ [red]Error: Ingresa solo números separados por comas[/red]")
                continue
            except Exception as e:
                self.console.print(f"❌ [red]Error procesando IDs: {str(e)}[/red]")
                continue
    
    def _is_sprint_recent(self, sprint_created: str, cutoff_date: datetime) -> bool:
        """Verifica si un sprint es reciente"""
        if not sprint_created:
            return True  # Por defecto asumir que es reciente
        
        try:
            created_date = datetime.fromisoformat(sprint_created.replace('Z', '+00:00')).replace(tzinfo=None)
            return created_date >= cutoff_date
        except Exception:
            return True
    
    def _remove_duplicates_and_sort(self, sprints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina duplicados y ordena sprints"""
        # Eliminar duplicados por ID de sprint
        unique_sprints = {}
        for sprint in sprints:
            sprint_id = sprint['id']
            if sprint_id not in unique_sprints:
                unique_sprints[sprint_id] = sprint
            else:
                # Si ya existe, combinar información de boards
                existing = unique_sprints[sprint_id]
                if existing['board_name'] != sprint['board_name']:
                    existing['board_name'] = f"{existing['board_name']} (+{sprint['board_name']})"
        
        # Convertir de vuelta a lista
        unique_active_sprints = list(unique_sprints.values())
        
        duplicates_removed = len(sprints) - len(unique_active_sprints)
        if duplicates_removed > 0:
            self.console.print(f"🔄 [yellow]Sprints duplicados eliminados: {duplicates_removed}[/yellow]")
            self.console.print(f"📊 [cyan]Sprints únicos: {len(unique_active_sprints)}[/cyan]")
        
        # Ordenar por ID (los IDs más altos son más recientes)
        unique_active_sprints.sort(key=lambda x: x['id'], reverse=True)
        
        return unique_active_sprints
    
    def _format_date(self, date_str: str) -> str:
        """Formatea una fecha ISO a formato legible"""
        if not date_str or date_str == 'No definida':
            return date_str
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        except Exception:
            return date_str
    
    def _show_selected_sprints(self, sprints: List[Dict[str, Any]]) -> None:
        """Muestra los sprints seleccionados"""
        for sprint in sprints:
            self.console.print(f"  🟢 [green]{sprint['name']} (ID: {sprint['id']}) [{sprint['board_name']}][/green]")
    
    def _show_sprint_confirmation_table(self, sprint_ids: List[int], sprint_details: List[Dict[str, Any]]) -> None:
        """Muestra tabla de confirmación de sprints"""
        confirmation_table = Table(title="🔍 Sprints Seleccionados para Confirmación", show_header=True)
        confirmation_table.add_column("ID", style="blue", width=8)
        confirmation_table.add_column("Nombre", style="green", width=30)
        confirmation_table.add_column("Estado", style="yellow", width=10)
        confirmation_table.add_column("Fecha Inicio", style="magenta", width=12)
        confirmation_table.add_column("Fecha Fin", style="magenta", width=12)
        confirmation_table.add_column("Objetivo", style="cyan", width=25)
        confirmation_table.add_column("Existe", style="bright_green", width=8)
        
        sprints_found = 0
        details_dict = {detail['id']: detail for detail in sprint_details}
        
        for sprint_id in sprint_ids:
            if sprint_id in details_dict:
                detail = details_dict[sprint_id]
                sprints_found += 1
                
                confirmation_table.add_row(
                    str(sprint_id),
                    detail.get('name', 'Sin nombre')[:30],
                    detail.get('state', 'N/A'),
                    self._format_date(detail.get('startDate', 'No definida')),
                    self._format_date(detail.get('endDate', 'No definida')),
                    (detail.get('goal', 'Sin objetivo')[:22] + "...") if len(detail.get('goal', '')) > 25 else detail.get('goal', 'Sin objetivo'),
                    "✅ Sí"
                )
            else:
                confirmation_table.add_row(
                    str(sprint_id),
                    "Sprint no encontrado",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "❌ No"
                )
        
        self.console.print(confirmation_table)
        self.console.print(f"📊 [cyan]Resumen: {sprints_found}/{len(sprint_ids)} sprints encontrados[/cyan]")
