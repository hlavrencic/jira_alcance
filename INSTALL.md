# 🚀 Guía de Instalación y Uso

## 📋 Requisitos Previos

- Python 3.8 o superior
- Acceso a Jira con API token
- Permisos para leer proyectos y sprints

## 🔧 Instalación

### 1. Configurar entorno Python

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales

#### Opción A: Archivo .env (Recomendado)
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
JIRA_SERVER=https://baufest.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_API_TOKEN=tu-api-token
```

#### Opción B: Editar config.py directamente
```python
JIRA_SERVER = 'https://baufest.atlassian.net'
JIRA_EMAIL = 'tu-email@empresa.com'
JIRA_API_TOKEN = 'tu-api-token'
```

### 4. Obtener API Token de Jira

1. Ve a [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Crea un nuevo token
3. Copia el token generado en tu configuración

## 🎯 Uso

### Uso Básico

```bash
# Extraer datos del proyecto CMZ100 (por defecto)
python jira_sprint_extractor.py

# Extraer datos de un proyecto específico
python jira_sprint_extractor.py --project ARMOA258

# Exportar solo a Excel
python jira_sprint_extractor.py --format excel

# Exportar solo a CSV
python jira_sprint_extractor.py --format csv
```

### Uso desde VS Code

1. Abre la paleta de comandos: `Ctrl+Shift+P`
2. Busca "Tasks: Run Task"
3. Selecciona una de las tareas disponibles:
   - "Run Jira Extractor - CMZ100"
   - "Run Jira Extractor - Custom Project"
   - "Install Dependencies"

### Ejemplo Programático

```python
from jira_sprint_extractor import JiraSprintExtractor

# Crear extractor
extractor = JiraSprintExtractor()

# Ejecutar extracción
success = extractor.run(
    project_key="CMZ100",
    export_format="both"
)

if success:
    print("✅ Datos extraídos exitosamente")
```

## 📊 Datos Extraídos

Para cada tarea se obtiene:

### Información Básica
- **key**: Clave del ticket (ej: CMZ100-123)
- **summary**: Título/resumen de la tarea
- **issue_type**: Tipo de issue (Story, Task, Bug, Subtask)
- **status**: Estado actual (To Do, In Progress, Done, etc.)
- **assignee**: Persona asignada
- **priority**: Prioridad (High, Medium, Low, etc.)

### Información de Tiempo
- **time_spent**: Tiempo registrado (formato legible)
- **original_estimate**: Estimación original
- **remaining_estimate**: Tiempo restante estimado
- **time_spent_seconds**: Tiempo registrado en segundos
- **original_estimate_seconds**: Estimación original en segundos
- **remaining_estimate_seconds**: Tiempo restante en segundos

### Información de Sprint y Proyecto
- **sprint_id**: ID del sprint
- **sprint_name**: Nombre del sprint
- **board_id**: ID del board
- **board_name**: Nombre del board
- **project_key**: Clave del proyecto

### Relaciones
- **is_subtask**: Indica si es una subtarea
- **parent_key**: Clave de la tarea padre (si es subtarea)

### Metadatos
- **created**: Fecha de creación
- **updated**: Fecha de última actualización
- **components**: Componentes asignados

## 📈 Reportes Generados

Los reportes se generan en la carpeta `reports/` con formato:
`sprint_data_{PROJECT_KEY}_{TIMESTAMP}.{xlsx|csv}`

### Ejemplo:
- `reports/sprint_data_CMZ100_20250711_143022.xlsx`
- `reports/sprint_data_CMZ100_20250711_143022.csv`

## 🐛 Troubleshooting

### Error de Conexión
```
❌ Error conectando a Jira: HTTP 401
```
**Solución**: Verificar credenciales en config.py o .env

### No se encuentran sprints activos
```
⚠️ No hay sprints activos en board
```
**Solución**: Verificar que el proyecto tenga sprints en estado "active"

### Error de permisos
```
❌ Error: Forbidden
```
**Solución**: Verificar permisos de usuario en Jira para el proyecto

### Problemas con dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 📝 Logs

Los logs se guardan en `jira_extractor.log` con información detallada sobre:
- Conexiones a Jira
- Sprints y boards procesados
- Errores y warnings
- Estadísticas de extracción

## 🔄 Automatización

### Ejecución Programada (Windows)
```bash
# Crear tarea programada para ejecutar diariamente
schtasks /create /tn "Jira Sprint Extract" /tr "python C:\path\to\jira_sprint_extractor.py" /sc daily /st 09:00
```

### Ejecución Programada (Linux/Mac)
```bash
# Agregar a crontab para ejecutar diariamente a las 9:00 AM
0 9 * * * cd /path/to/project && python jira_sprint_extractor.py
```

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.
