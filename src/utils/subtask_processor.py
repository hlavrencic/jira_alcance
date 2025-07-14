"""
Procesador de subtareas y relaciones padre-hijo
"""
from typing import List, Dict, Any
from rich.console import Console

from ..config import SUBTASK_MAPPING


class SubtaskProcessor:
    """Procesador para manejar subtareas y sus relaciones"""
    
    def __init__(self):
        self.console = Console()
    
    def process_subtask_relationships(self, main_issues: List[Dict[str, Any]], 
                                    subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa las relaciones entre issues principales y sus subtareas
        
        Args:
            main_issues: Lista de issues principales
            subtasks: Lista de subtareas
            
        Returns:
            Lista de issues principales con datos de subtareas agregados
        """
        if not subtasks:
            self.console.print("   📝 [dim]No hay subtareas para procesar[/dim]")
            return main_issues
        
        # Agrupar subtareas por issue padre
        subtasks_by_parent = {}
        for subtask in subtasks:
            parent_key = subtask.get('parent_key')
            if parent_key:
                if parent_key not in subtasks_by_parent:
                    subtasks_by_parent[parent_key] = []
                subtasks_by_parent[parent_key].append(subtask)
        
        self.console.print(f"   🔗 [cyan]Procesando {len(subtasks)} subtareas para {len(subtasks_by_parent)} issues padre[/cyan]")
        
        # Procesar cada issue principal
        for issue in main_issues:
            issue_key = issue['key']
            
            # Inicializar campos de subtareas
            self._initialize_subtask_fields(issue)
            
            # Procesar subtareas de este issue
            if issue_key in subtasks_by_parent:
                issue_subtasks = subtasks_by_parent[issue_key]
                self._aggregate_subtask_data(issue, issue_subtasks)
                
                self.console.print(f"     📎 [dim]{issue_key}: {len(issue_subtasks)} subtareas procesadas[/dim]")
        
        return main_issues
    
    def _initialize_subtask_fields(self, issue: Dict[str, Any]) -> None:
        """Inicializa los campos de subtareas en un issue"""
        subtask_fields = [
            'analisis_time_spent', 'analisis_original_estimate', 'analisis_remaining',
            'testing_time_spent', 'testing_original_estimate', 'testing_remaining',
            'desarrollo_time_spent', 'desarrollo_original_estimate', 'desarrollo_remaining'
        ]
        
        for field in subtask_fields:
            issue[field] = '0,0'
    
    def _aggregate_subtask_data(self, parent_issue: Dict[str, Any], 
                               subtasks: List[Dict[str, Any]]) -> None:
        """
        Agrega datos de timetracking de subtareas al issue padre
        
        Args:
            parent_issue: Issue padre donde agregar los datos
            subtasks: Lista de subtareas del issue padre
        """
        # Inicializar acumuladores por categoría
        categories = {
            'analisis': {'time_spent': 0, 'original_estimate': 0, 'remaining': 0},
            'testing': {'time_spent': 0, 'original_estimate': 0, 'remaining': 0},
            'desarrollo': {'time_spent': 0, 'original_estimate': 0, 'remaining': 0}
        }
        
        # Procesar cada subtarea
        for subtask in subtasks:
            category = self._categorize_subtask(subtask)
            
            # Agregar tiempos a la categoría correspondiente
            categories[category]['time_spent'] += self._parse_time_value(subtask.get('time_spent', '0,0'))
            categories[category]['original_estimate'] += self._parse_time_value(subtask.get('original_estimate', '0,0'))
            categories[category]['remaining'] += self._parse_time_value(subtask.get('remaining_estimate', '0,0'))
        
        # Asignar totales al issue padre
        for category, times in categories.items():
            parent_issue[f'{category}_time_spent'] = self._format_time_value(times['time_spent'])
            parent_issue[f'{category}_original_estimate'] = self._format_time_value(times['original_estimate'])
            parent_issue[f'{category}_remaining'] = self._format_time_value(times['remaining'])
    
    def _categorize_subtask(self, subtask: Dict[str, Any]) -> str:
        """
        Categoriza una subtarea según su tipo o resumen
        
        Args:
            subtask: Datos de la subtarea
            
        Returns:
            Categoría de la subtarea ('analisis', 'testing', 'desarrollo')
        """
        # Obtener texto para categorizar (tipo de issue + resumen)
        issue_type = subtask.get('issue_type', '').lower()
        summary = subtask.get('summary', '').lower()
        
        text_to_analyze = f"{issue_type} {summary}"
        
        # Buscar coincidencias con los mapeos configurados
        for category, keywords in SUBTASK_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    return category
        
        # Si no hay coincidencia, usar desarrollo como categoría por defecto
        return 'desarrollo'
    
    def _parse_time_value(self, time_str: str) -> float:
        """
        Convierte un valor de tiempo con formato de coma a float
        
        Args:
            time_str: Tiempo en formato string con coma
            
        Returns:
            Valor numérico del tiempo
        """
        try:
            return float(str(time_str).replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
    
    def _format_time_value(self, time_float: float) -> str:
        """
        Convierte un valor float a formato string con coma
        
        Args:
            time_float: Tiempo en formato float
            
        Returns:
            Tiempo formateado con coma
        """
        return str(round(time_float, 1)).replace('.', ',')
