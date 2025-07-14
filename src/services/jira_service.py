"""
Servicio de conexión y comunicación con Jira
"""
import os
import requests
from typing import Optional, List, Dict, Any
from jira import JIRA
from rich.console import Console

from ..config import JIRA_CONFIG, validate_config


class JiraService:
    """Servicio para manejar la conexión y comunicación con Jira"""
    
    def __init__(self):
        self.console = Console()
        self.jira: Optional[JIRA] = None
        self._boards_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def connect(self) -> bool:
        """
        Establece conexión con Jira usando credenciales del archivo .env
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            validation = validate_config()
            
            if not validation['valid']:
                self.console.print("❌ [red]Error: Credenciales no configuradas en .env[/red]")
                self.console.print(f"   [yellow]Variables faltantes: {', '.join(validation['missing_vars'])}[/yellow]")
                return False
            
            self.console.print("🔄 [cyan]Conectando a Jira...[/cyan]")
            
            self.jira = JIRA(
                server=JIRA_CONFIG['server'],
                basic_auth=(JIRA_CONFIG['email'], JIRA_CONFIG['token'])
            )
            
            # Verificar conexión
            current_user = self.jira.current_user()
            self.console.print(f"✅ [green]Conectado como: {current_user}[/green]")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Error de conexión: {str(e)}[/red]")
            return False
    
    def search_issues(self, jql: str, start_at: int = 0, max_results: int = 100, 
                     expand: str = 'changelog') -> List[Any]:
        """
        Busca issues usando JQL
        
        Args:
            jql: Query JQL
            start_at: Índice de inicio para paginación
            max_results: Máximo número de resultados por página
            expand: Campos adicionales a expandir
            
        Returns:
            Lista de issues encontrados
        """
        if not self.jira:
            raise RuntimeError("No hay conexión activa con Jira")
        
        return self.jira.search_issues(
            jql,
            startAt=start_at,
            maxResults=max_results,
            expand=expand
        )
    
    def get_project_boards(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Obtiene los boards asociados al proyecto con cache para optimizar
        
        Args:
            project_key: Clave del proyecto
            
        Returns:
            Lista de boards del proyecto
        """
        # Verificar cache primero
        if project_key in self._boards_cache:
            self.console.print(f"💾 [green]Usando boards en cache para {project_key}[/green]")
            return self._boards_cache[project_key]
        
        try:
            all_boards = []
            start_at = 0
            max_results = 50
            
            self.console.print("🔄 [cyan]Obteniendo todos los boards con paginación completa...[/cyan]")
            
            while True:
                url = f"{JIRA_CONFIG['server']}/rest/agile/1.0/board"
                params = {
                    'startAt': start_at,
                    'maxResults': max_results
                }
                auth = (JIRA_CONFIG['email'], JIRA_CONFIG['token'])
                
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
            
            # Guardar en cache
            self._boards_cache[project_key] = project_boards
            
            return project_boards
                
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Error obteniendo boards: {str(e)}[/yellow]")
            return []
    
    def get_board_sprints(self, board_id: int, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene sprints de un board específico
        
        Args:
            board_id: ID del board
            state: Estado de los sprints a filtrar (active, closed, future)
            
        Returns:
            Lista de sprints del board
        """
        try:
            url = f"{JIRA_CONFIG['server']}/rest/agile/1.0/board/{board_id}/sprint"
            auth = (JIRA_CONFIG['email'], JIRA_CONFIG['token'])
            
            start_at = 0
            max_results = 50
            all_sprints = []
            
            while True:
                params = {
                    'startAt': start_at,
                    'maxResults': max_results
                }
                if state:
                    params['state'] = state
                
                response = requests.get(url, auth=auth, params=params)
                if response.status_code != 200:
                    self.console.print(f"   ⚠️ [dim]Error HTTP {response.status_code} en board {board_id}[/dim]")
                    break
                
                data = response.json()
                sprints = data.get('values', [])
                
                if not sprints:
                    break
                
                all_sprints.extend(sprints)
                
                if len(sprints) < max_results:
                    break
                    
                start_at += max_results
            
            return all_sprints
            
        except Exception as e:
            self.console.print(f"   ❌ [red]Error obteniendo sprints del board {board_id}: {str(e)}[/red]")
            return []
    
    def get_sprint_details(self, sprint_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Obtiene detalles de sprints específicos
        
        Args:
            sprint_ids: Lista de IDs de sprints
            
        Returns:
            Lista de detalles de sprints
        """
        sprint_details = []
        
        for sprint_id in sprint_ids:
            try:
                url = f"{JIRA_CONFIG['server']}/rest/agile/1.0/sprint/{sprint_id}"
                auth = (JIRA_CONFIG['email'], JIRA_CONFIG['token'])
                
                response = requests.get(url, auth=auth)
                if response.status_code == 200:
                    sprint_data = response.json()
                    sprint_details.append(sprint_data)
                else:
                    self.console.print(f"   ⚠️ [yellow]Sprint {sprint_id} no encontrado (HTTP {response.status_code})[/yellow]")
                    
            except Exception as e:
                self.console.print(f"   ❌ [red]Error obteniendo sprint {sprint_id}: {str(e)}[/red]")
                continue
        
        return sprint_details
