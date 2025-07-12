"""
🎯 Configuración para el Extractor de Datos Jira

Configuración centralizada para el sistema de extracción.
Versión: 2.0 (Refactorizada)
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN JIRA
# ==========================================

JIRA_SERVER = os.getenv('JIRA_SERVER', 'https://baufest.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL', '')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')

# ==========================================
# CONFIGURACIÓN DE PROYECTOS
# ==========================================

DEFAULT_PROJECT = 'CMZ100'

# Máximo número de issues a procesar por proyecto
MAX_ISSUES_PER_PROJECT = 500

# ==========================================
# CONFIGURACIÓN DE EXPORTACIÓN
# ==========================================

REPORTS_DIR = 'reports'
EXPORT_FORMATS = ['excel', 'csv']

# Configuración de archivos Excel
EXCEL_CONFIG = {
    'engine': 'openpyxl',
    'max_column_width': 50,
    'auto_adjust_columns': True
}

# Configuración de archivos CSV
CSV_CONFIG = {
    'encoding': 'utf-8-sig',
    'index': False
}

# ==========================================
# CONFIGURACIÓN DE TIMETRACKING
# ==========================================

# Campos de tiempo a extraer (en segundos para cálculos)
TIME_FIELDS = [
    'time_spent_seconds',
    'original_estimate_seconds', 
    'remaining_estimate_seconds'
]

# Formato de tiempo para visualización
TIME_FORMAT = 'hours'  # 'hours' o 'days'

# ==========================================
# CONFIGURACIÓN DE CAMPOS JIRA
# ==========================================

# Campos esenciales a extraer de cada issue
ESSENTIAL_FIELDS = [
    'key',
    'summary',
    'status', 
    'assignee',
    'issuetype',
    'priority',
    'created',
    'updated',
    'project'
]

# Campos adicionales (opcionales)
ADDITIONAL_FIELDS = [
    'parent',
    'components',
    'labels',
    'timetracking'
]

# ==========================================
# CONFIGURACIÓN DE BÚSQUEDA
# ==========================================

# Estrategias JQL en orden de prioridad
JQL_SEARCH_STRATEGIES = [
    'project = {project} AND status NOT IN (Cerrado, Finalizado, Done, Resolved) ORDER BY updated DESC',
    'project = {project} AND updated >= -60d ORDER BY created DESC', 
    'project = {project} ORDER BY created DESC'
]

# ==========================================
# CONFIGURACIÓN DE INTERFAZ
# ==========================================

# Configuración de Rich Console
CONSOLE_CONFIG = {
    'show_progress': True,
    'progress_description': 'Procesando issues...',
    'table_style': 'blue'
}
