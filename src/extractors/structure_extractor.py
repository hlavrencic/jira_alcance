"""
Extractor de estructura de issues (relaciones, sprints, etc.)
"""
from typing import Dict, Any, Optional
from .base_extractor import BaseExtractor


class StructureExtractor(BaseExtractor):
    """Extractor especializado en estructura y relaciones de issues"""
    
    def __init__(self):
        super().__init__()
        self.sprint_context = {}  # Diccionario para almacenar información de sprints
        
    def set_sprint_context(self, sprints: Dict[int, Dict[str, Any]]):
        """
        Establece el contexto de sprints para la extracción
        
        Args:
            sprints: Diccionario {sprint_id: sprint_data}
        """
        self.sprint_context = sprints
    
    def extract(self, issue: Any) -> Dict[str, Any]:
        """
        Extrae datos de estructura (subtareas, padre, sprint, etc.)
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con datos de estructura
        """
        # Obtener información de sprint
        sprint_info = self._extract_sprint_info(issue)
        
        # Determinar si es subtarea
        is_subtask = self._safe_get_nested_attribute(issue, 'fields.issuetype.subtask', False)
        parent_key = self._safe_get_nested_attribute(issue, 'fields.parent.key')
        
        # Lógica para la columna Parent
        # Para subtareas: usar parent_key, para el resto: usar key del issue
        parent_value = parent_key if is_subtask else issue.key
        
        # Lógica para la columna Epic
        epic_key = self._extract_epic_key(issue)
        
        return {
            'epic_key': epic_key,
            'feature': parent_value,
            'is_subtask': is_subtask,
            'parent_key': parent_key,
            'sprint_name': sprint_info['name'],
            'sprint_id': sprint_info['id'],
            'sprint_state': sprint_info['state'],
            'board_name': sprint_info.get('board_name', f'{self._safe_get_nested_attribute(issue, "fields.project.key", "UNKNOWN")} - Proyecto Principal')
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
            'state': 'N/A',
            'board_name': 'N/A'
        }
        
        try:
            # Obtener sprints del campo customfield_10007 (campo específico de sprint)
            sprints = self._safe_get_nested_attribute(issue, 'fields.customfield_10007', [])
            
            if sprints and isinstance(sprints, list):
                # Tomar el último sprint (el más reciente)
                last_sprint = sprints[-1]
                
                # Extraer información directamente del objeto sprint si está disponible
                if hasattr(last_sprint, 'name'):
                    # Información básica del sprint
                    sprint_info['name'] = last_sprint.name
                    sprint_id = getattr(last_sprint, 'id', None)
                    sprint_info['id'] = str(sprint_id) if sprint_id else 'N/A'
                    sprint_info['state'] = getattr(last_sprint, 'state', 'N/A')
                    
                    # Extraer board_name del sprint o del issue
                    board_id = getattr(last_sprint, 'boardId', None)
                    if board_id:
                        sprint_info['board_name'] = f"{self._safe_get_nested_attribute(issue, 'fields.project.key', 'UNKNOWN')} Board {board_id}"
                    
                    # Si tenemos contexto de sprints, complementar la información
                    if self.sprint_context and sprint_id:
                        if sprint_id in self.sprint_context:
                            context = self.sprint_context[sprint_id]
                            # Actualizar board_name solo si es más específico que el default
                            if 'board_name' in context and context['board_name'] != 'Sin Board':
                                sprint_info['board_name'] = context['board_name']
                            print(f"DEBUG - Issue {issue.key}: Found sprint {sprint_info['name']} (ID: {sprint_info['id']}) in context")
                        else:
                            # Extraer más información del objeto sprint
                            goal = getattr(last_sprint, 'goal', None)
                            if goal:
                                sprint_info['name'] = f"{sprint_info['name']} ({goal})"
                            print(f"DEBUG - Issue {issue.key}: Using sprint object data for ID {sprint_id}")
                            
                elif isinstance(last_sprint, str):
                    # Manejar el caso donde el sprint viene como string
                    sprint_info['name'] = last_sprint
                    print(f"DEBUG - Issue {issue.key}: Sprint as string: {last_sprint}")
            
        except Exception as e:
            # En caso de error, mantener valores por defecto
            print(f"DEBUG - Issue {issue.key}: Error extracting sprint info: {e}")
            pass
        
        return sprint_info
    
    def _extract_epic_key(self, issue: Any) -> str:
        """
        Extrae la clave del Epic asociado al issue
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Clave del Epic o 'Sin Epic'
        """
        # Estrategias para encontrar el Epic
        strategies = [
            # 1. Campo Epic Link directo
            lambda: self._safe_get_nested_attribute(issue, 'fields.customfield_10014'),
            # 2. Campo Epic Key
            lambda: self._safe_get_nested_attribute(issue, 'fields.customfield_10008'), 
            # 3. Si el issue mismo es un Epic
            lambda: issue.key if self._safe_get_nested_attribute(issue, 'fields.issuetype.name', '').lower() == 'epic' else None,
            # 4. Buscar en campos personalizados que contengan 'epic'
            lambda: self._search_epic_in_custom_fields(issue)
        ]
        
        for strategy in strategies:
            try:
                epic_key = strategy()
                if epic_key and epic_key != 'Sin Epic':
                    return epic_key
            except Exception:
                continue
        
        return 'Sin Epic'
    
    def _search_epic_in_custom_fields(self, issue: Any) -> str:
        """Busca Epic en campos personalizados"""
        try:
            fields = self._safe_get_nested_attribute(issue, 'fields.__dict__', {})
            
            for field_name, field_value in fields.items():
                if 'epic' in field_name.lower() and field_value:
                    if isinstance(field_value, str):
                        return field_value
                    elif hasattr(field_value, 'key'):
                        return field_value.key
                    elif hasattr(field_value, 'name'):
                        return field_value.name
        except Exception:
            pass
        
        return 'Sin Epic'
