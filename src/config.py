"""
Configuración centralizada del extractor de Jira
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión a Jira
JIRA_CONFIG = {
    'server': os.getenv('JIRA_SERVER'),
    'email': os.getenv('JIRA_EMAIL'),
    'token': os.getenv('JIRA_API_TOKEN')
}

# Configuración de extracción
EXTRACTION_CONFIG = {
    'extract_all_issues': True,
    'max_issues_fallback': 5000,
    'page_size': 100,
    'page_delay': 0.1,  # Segundos entre páginas para evitar rate limiting
    'recent_sprint_days': 60,  # Días para considerar un sprint como "reciente"
}

# Configuración de exportación
EXPORT_CONFIG = {
    'reports_dir': 'reports',
    'timestamp_format': '%Y%m%d_%H%M%S',
    'excel_sheet_name_template': '{project_key}_Data',
    'max_column_width': 50,
    'min_column_width': 10
}

# Campos personalizados de Jira (customfields)
CUSTOM_FIELDS = {
    'generico1': 'customfield_14399',
    'generico2': 'customfield_14400', 
    'generico3': 'customfield_14401'
}

# Mapeo de tipos de subtareas
SUBTASK_MAPPING = {
    'analisis': ['analisis', 'análisis', 'analysis', 'diseño', 'design'],
    'testing': ['testing', 'test', 'qa', 'prueba', 'pruebas'],
    'desarrollo': ['desarrollo', 'dev', 'development', 'implementación', 'implementation']
}

# Configuración de columnas para exportación
COLUMN_ORDER = {
    'base': ['epic_key', 'feature'],
    'main': ['key', 'summary', 'issue_type', 'status', 'priority', 
             'assignee', 'reporter', 'created', 'updated', 'project_key'],
    'time': ['time_spent', 'original_estimate', 'remaining_estimate'],
    'aggregate_time': ['aggregate_time_spent', 'aggregate_original_estimate', 'aggregate_time_estimate'],
    'subtask': [
        'analisis_time_spent', 'analisis_original_estimate', 'analisis_remaining',
        'testing_time_spent', 'testing_original_estimate', 'testing_remaining',
        'desarrollo_time_spent', 'desarrollo_original_estimate', 'desarrollo_remaining'
    ],
    'metadata': ['is_subtask', 'parent_key', 'sprint_name', 'sprint_id', 
                 'sprint_state', 'board_name', 'components', 'labels', 'fixversion',
                 'generico1', 'generico2', 'generico3']
}

def validate_config() -> Dict[str, Any]:
    """
    Valida la configuración de conexión a Jira
    
    Returns:
        Dict con el resultado de la validación
    """
    missing_vars = []
    
    for key, value in JIRA_CONFIG.items():
        if not value:
            missing_vars.append(f'JIRA_{key.upper()}')
    
    return {
        'valid': len(missing_vars) == 0,
        'missing_vars': missing_vars,
        'config': JIRA_CONFIG
    }

def get_jql_strategies(project_key: str) -> list:
    """
    Retorna las estrategias de búsqueda JQL en orden de prioridad
    
    Args:
        project_key: Clave del proyecto
        
    Returns:
        Lista de estrategias de búsqueda
    """
    return [
        {
            'jql': f'project = {project_key} AND status NOT IN (Cerrado, Finalizado, Done, Resolved, Closed) ORDER BY updated DESC',
            'description': 'Issues activos'
        },
        {
            'jql': f'project = {project_key} AND updated >= -90d ORDER BY updated DESC',
            'description': 'Issues recientes (90 días)'
        },
        {
            'jql': f'project = {project_key} ORDER BY created DESC',
            'description': 'Todos los issues'
        }
    ]
