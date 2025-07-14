"""
Extractor de datos de timetracking
"""
from typing import Dict, Any
from .base_extractor import BaseExtractor


class TimetrackingExtractor(BaseExtractor):
    """Extractor especializado en datos de timetracking"""
    
    def extract(self, issue: Any) -> Dict[str, Any]:
        """
        Extrae datos de timetracking del issue (incluyendo agregados)
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con datos de timetracking
        """
        time_data = {
            'time_spent': '0,0',
            'original_estimate': '0,0', 
            'remaining_estimate': '0,0',
            'aggregate_time_spent': '0,0',
            'aggregate_original_estimate': '0,0',
            'aggregate_time_estimate': '0,0'
        }
        
        # Timetracking regular (solo del issue)
        timetracking = self._safe_get_nested_attribute(issue, 'fields.timetracking')
        if timetracking:
            # Tiempo gastado
            time_spent_seconds = self._safe_get_attribute(timetracking, 'timeSpentSeconds')
            if time_spent_seconds:
                time_data['time_spent'] = self._convert_seconds_to_hours(time_spent_seconds)
            
            # Estimación original
            original_estimate_seconds = self._safe_get_attribute(timetracking, 'originalEstimateSeconds')
            if original_estimate_seconds:
                time_data['original_estimate'] = self._convert_seconds_to_hours(original_estimate_seconds)
            
            # Tiempo restante
            remaining_estimate_seconds = self._safe_get_attribute(timetracking, 'remainingEstimateSeconds')
            if remaining_estimate_seconds:
                time_data['remaining_estimate'] = self._convert_seconds_to_hours(remaining_estimate_seconds)
        
        # Timetracking agregado (incluyendo subtareas)
        aggregate_time_spent = self._safe_get_nested_attribute(issue, 'fields.aggregatetimespent')
        if aggregate_time_spent:
            time_data['aggregate_time_spent'] = self._convert_seconds_to_hours(aggregate_time_spent)
        
        aggregate_original_estimate = self._safe_get_nested_attribute(issue, 'fields.aggregatetimeoriginalestimate')
        if aggregate_original_estimate:
            time_data['aggregate_original_estimate'] = self._convert_seconds_to_hours(aggregate_original_estimate)
        
        aggregate_time_estimate = self._safe_get_nested_attribute(issue, 'fields.aggregatetimeestimate')
        if aggregate_time_estimate:
            time_data['aggregate_time_estimate'] = self._convert_seconds_to_hours(aggregate_time_estimate)
        
        return time_data
