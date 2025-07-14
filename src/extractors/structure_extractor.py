"""
Extractor de estructura de issues (relaciones, sprints, etc.)
"""
from typing import Dict, Any
from .base_extractor import BaseExtractor


class StructureExtractor(BaseExtractor):
    """Extractor especializado en estructura y relaciones de issues"""
    
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
            'board_name': f'{self._safe_get_nested_attribute(issue, "fields.project.key", "UNKNOWN")} - Proyecto Principal'
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
            fields = self._safe_get_nested_attribute(issue, 'fields.__dict__', {})
            
            for field_name, field_value in fields.items():
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
        except Exception:
            # En caso de error, mantener valores por defecto
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
