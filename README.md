# 🎯 Jira Sprint Data Extractor - Arquitectura Modular v2.0

Herramienta profesional refactorizada para extraer datos de timetracking de proyectos Jira con soporte completo para sprints, epics, subtareas y campos personalizados.

![Version](https://img.shields.io/badge/version-2.0-blue) ![Python](https://img.shields.io/badge/python-3.11+-green) ![Status](https://img.shields.io/badge/status-refactored-brightgreen)

## 📋 Características Principales

- ✅ **Extracción por Sprints**: Selección inteligente de sprints activos
- ✅ **Búsqueda Tradicional**: Extracción completa del proyecto  
- ✅ **Timetracking Completo**: Datos individuales y agregados (incluyendo subtareas)
- ✅ **Relaciones Epic-Feature**: Mapeo automático de jerarquías
- ✅ **Subtareas Categorizadas**: Análisis, Testing, Desarrollo
- ✅ **Campos Personalizados**: 3 campos genéricos configurables
- ✅ **Exportación Múltiple**: Excel y CSV con formato optimizado
- ✅ **Interfaz Rica**: Terminal interactiva con Rich


## 🚀 Uso del Sistema

```bash
# Extracción con selección de sprints (modo por defecto)
# ✨ NUEVO: Muestra sprints activos + últimos 2 cerrados por tablero
python main.py --project CMZ100

# Búsqueda tradicional sin sprints
python main.py --project CMZ100 --no-sprints

# Solo Excel con límite
python main.py --project CMZ100 --format excel --limit 1000

# Solo CSV
python main.py --project CMZ100 --format csv
```

## ⚙️ Configuración

### Variables de Entorno (.env)
```bash
JIRA_SERVER=https://tuinstancia.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_API_TOKEN=tu-token-api
```

### Campos Personalizados Configurables
En `src/config.py`:
```python
CUSTOM_FIELDS = {
    'generico1': 'customfield_14399',  # Campo personalizado 1
    'generico2': 'customfield_14400',  # Campo personalizado 2  
    'generico3': 'customfield_14401'   # Campo personalizado 3
}
```

### Configuración Avanzada
```python
# src/config.py
EXTRACTION_CONFIG = {
    'extract_all_issues': True,     # Extraer todos los issues
    'max_issues_fallback': 5000,    # Límite de seguridad
    'page_size': 100,               # Tamaño de página API
    'recent_sprint_days': 60        # Días para sprints "recientes"
}

SUBTASK_MAPPING = {
    'análisis': ['análisis', 'analysis', 'diseño'],
    'testing': ['testing', 'test', 'qa', 'prueba'],
    'desarrollo': ['desarrollo', 'dev', 'implementation']
}
```

## 📊 Datos Extraídos

### Información Básica
- Key, Summary, Issue Type, Status, Priority
- Assignee, Reporter, Created, Updated
- Project Key, Components, Labels

### Timetracking Detallado
- **Individual**: Time Spent, Original Estimate, Remaining  
- **Agregado**: Incluye tiempo de subtareas automáticamente
- **Categorizado**: Análisis, Testing, Desarrollo por subtareas

### Estructura y Relaciones
- **Epic Key**: Identificación automática del Epic
- **Feature**: Issue padre o self-reference
- **Sprint**: Nombre, ID, Estado actual
- **Subtasks**: Procesamiento automático de relaciones

### Fix Versions y Campos Personalizados
- **Fix Versions**: Versiones de corrección planificadas
- **Genérico 1-3**: Campos personalizados configurables

## 📈 Reportes Generados

### Excel (.xlsx)
- Columnas auto-ajustadas
- Formato optimizado para análisis
- Hoja nombrada por proyecto

### CSV (.csv) 
- Encoding UTF-8 BOM
- Compatible con Excel
- Separación por comas

### Estructura de Columnas
```
epic_key | feature | key | summary | issue_type | status | ...
time_spent | original_estimate | remaining_estimate | 
aggregate_time_spent | aggregate_original_estimate | aggregate_time_estimate |
analisis_time_spent | testing_time_spent | desarrollo_time_spent | ...
components | labels | fixversion | generico1 | generico2 | generico3
```

## � Solución de Problemas

### Problemas de Conexión
```bash
❌ Error de conexión: 401 Authentication failed
```
**Solución**: 
1. Verificar credenciales en `.env`
2. Comprobar acceso de red a Jira
3. Validar permisos del token API

### Issues No Encontrados
```bash
❌ No se encontraron issues para procesar
```
**Solución**:
1. Verificar clave del proyecto
2. Comprobar permisos de lectura
3. Revisar filtros de búsqueda

### Campos Personalizados Vacíos
```bash
⚠️ Campos genéricos vacíos
```
**Solución**:
1. Verificar IDs de customfields en `src/config.py`
2. Comprobar permisos de lectura en campos
3. Validar que los campos existen en el proyecto

### Problemas con Módulos
```bash
❌ ModuleNotFoundError: No module named 'src.services'
```
**Solución**:
1. Ejecutar desde el directorio raíz del proyecto
2. Verificar estructura de directorios
3. Usar `python main.py` en lugar de llamadas directas

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.
