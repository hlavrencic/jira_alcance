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

## 🏗️ Arquitectura Modular (v2.0)

### Estructura Refactorizada
```
📁 jira_alcance/
├── 🎯 main.py                    # Punto de entrada modular (NUEVO)
├── 🔧 jira_extractor.py          # Script original (compatible)
├── � src/                       # Arquitectura modular (NUEVA)
│   ├── 🎯 jira_extractor.py      # Clase principal refactorizada
│   ├── ⚙️ config.py              # Configuración centralizada
│   ├── 📁 services/              # Capa de servicios
│   │   └── jira_service.py       # Comunicación con Jira API
│   ├── 📁 extractors/            # Extractores especializados
│   │   ├── base_extractor.py     # Clase base para extractores
│   │   ├── timetracking_extractor.py
│   │   ├── metadata_extractor.py
│   │   └── structure_extractor.py
│   ├── 📁 utils/                 # Utilidades de apoyo
│   │   ├── sprint_manager.py     # Gestión de sprints
│   │   ├── subtask_processor.py  # Procesamiento de subtareas
│   │   └── display_utils.py      # Utilidades de visualización
│   └── � exporters/             # Generadores de archivos
│       ├── base_exporter.py      # Clase base para exportadores
│       ├── excel_exporter.py     # Exportación Excel optimizada
│       └── csv_exporter.py       # Exportación CSV con UTF-8
├── 📊 reports/                   # Reportes generados
├── � requirements.txt           # Dependencias del proyecto
└── 🔐 .env                      # Configuración de credenciales
```

### 🔄 Beneficios de la Refactorización

#### 🧩 **Modularidad**
- **Separación de Responsabilidades**: Cada módulo tiene una función específica
- **Extractores Especializados**: Timetracking, metadatos, estructura por separado
- **Servicios Independientes**: API de Jira aislada en su propio módulo

#### 🔧 **Extensibilidad**
- **Patrones de Diseño**: BaseExtractor y BaseExporter para nuevas funcionalidades
- **Configuración Centralizada**: Todos los parámetros en `src/config.py`
- **Inyección de Dependencias**: Componentes intercambiables

#### 🧪 **Testabilidad**
- **Módulos Independientes**: Fácil testing unitario
- **Mocking Simplificado**: Servicios separados para pruebas
- **Cobertura Granular**: Testing por responsabilidad

#### 🛡️ **Robustez**
- **Manejo Granular de Errores**: Cada módulo gestiona sus excepciones
- **Validación de Datos**: Extractores con validación específica
- **Configuración Validada**: Carga segura de configuraciones

## 🚀 Uso del Sistema

### Opción 1: Script Modular (✨ Recomendado)
```bash
# Extracción con selección de sprints (modo por defecto)
python main.py --project CMZ100

# Búsqueda tradicional sin sprints
python main.py --project CMZ100 --no-sprints

# Solo Excel con límite
python main.py --project CMZ100 --format excel --limit 1000

# Solo CSV
python main.py --project CMZ100 --format csv
```

### Opción 2: Script Original (🔄 Compatibilidad)
```bash
# El script original sigue funcionando exactamente igual
python jira_extractor.py --project CMZ100
python jira_extractor.py --project CMZ100 --no-sprints --limit 500
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

## 🔧 Instalación

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd jira_alcance

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales

# 4. Probar instalación
python main.py --project CMZ100 --limit 5
```

## 🔍 Extensibilidad del Sistema

### Agregar Nuevo Extractor
```python
# src/extractors/custom_extractor.py
from .base_extractor import BaseExtractor

class CustomExtractor(BaseExtractor):
    """Extractor personalizado para campos específicos"""
    
    def extract(self, issue):
        return {
            'custom_field': self._safe_get_attribute(issue, 'custom_field', 'default'),
            'calculated_metric': self._calculate_custom_metric(issue)
        }
    
    def _calculate_custom_metric(self, issue):
        # Lógica personalizada
        return "custom_value"
```

### Agregar Nuevo Exportador
```python
# src/exporters/json_exporter.py
from .base_exporter import BaseExporter
import json

class JSONExporter(BaseExporter):
    """Exportador JSON para integraciones"""
    
    def export(self, data, project_key, filename=None):
        if not filename:
            filename = f"{project_key}_data.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
```

### Usar Nuevos Componentes
```python
# En main.py o script personalizado
from src.extractors.custom_extractor import CustomExtractor
from src.exporters.json_exporter import JSONExporter

# Agregar al pipeline
extractor.add_extractor(CustomExtractor())
extractor.add_exporter(JSONExporter())
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

## 📝 Changelog

### v2.0.0 (Refactorización Completa) 🎉
- ✨ **Arquitectura Modular**: Separación en services, extractors, utils, exporters
- ✨ **Extractores Especializados**: TimetrackingExtractor, MetadataExtractor, StructureExtractor
- ✨ **Servicios Independientes**: JiraService para comunicación API
- ✨ **Utilidades Modulares**: SprintManager, SubtaskProcessor, DisplayUtils
- ✨ **Exportadores Flexibles**: ExcelExporter, CSVExporter con BaseExporter
- ✨ **Configuración Centralizada**: src/config.py con todas las configuraciones
- ✨ **Punto de Entrada Nuevo**: main.py como entrada modular
- ✅ **Compatibilidad Total**: jira_extractor.py original sigue funcionando
- ✅ **Testing Completo**: Validación en ambos modos (sprint y tradicional)

### v1.x (Original)
- ✅ Extracción básica de timetracking
- ✅ Soporte para sprints y epics
- ✅ Exportación Excel/CSV
- ✅ Interfaz de terminal rica

## 🤝 Contribución

### Proceso de Desarrollo
1. **Fork** del proyecto
2. **Crear rama feature** (`git checkout -b feature/nueva-funcionalidad`)
3. **Desarrollar** siguiendo la arquitectura modular
4. **Testing** de módulos independientes
5. **Commit** cambios (`git commit -am 'Agregar nueva funcionalidad'`)
6. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
7. **Crear Pull Request**

### Estándares de Código
- ✅ **Separación de Responsabilidades**: Un módulo, una responsabilidad
- ✅ **Patrones de Diseño**: Usar BaseExtractor/BaseExporter para consistencia
- ✅ **Manejo de Errores**: Cada módulo gestiona sus excepciones
- ✅ **Documentación**: Docstrings en todas las clases y métodos públicos
- ✅ **Type Hints**: Tipado cuando sea posible
- ✅ **Rich Console**: Interfaz visual consistente

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 📞 Soporte

### **Documentación Técnica**
- 📘 **README.md**: Documentación principal (este archivo)
- 🛠️ **INSTALL.md**: Guía de instalación detallada
- ⚙️ **src/config.py**: Todas las configuraciones disponibles
- 🏗️ **REFACTORIZACION_COMPLETADA.md**: Detalles técnicos de la refactorización

### **Reporte de Issues**
Para reportar bugs o solicitar funcionalidades, crear un issue en el repositorio con:
1. **Versión**: Especificar si usa `main.py` (v2.0) o `jira_extractor.py` (v1.x)
2. **Módulo**: Indicar qué componente presenta el problema
3. **Logs**: Incluir mensajes de error completos
4. **Configuración**: Detalles relevantes de `src/config.py`

---

## 🏆 Sistema Listo para Producción

**La refactorización está completa y el sistema está listo para uso en producción.**

✅ **Arquitectura Robusta**: Módulos especializados y bien definidos  
✅ **Backward Compatibility**: Script original funciona sin cambios  
✅ **Extensibilidad**: Fácil agregar nuevos extractores y exportadores  
✅ **Testabilidad**: Componentes independientes para testing  
✅ **Mantenibilidad**: Código organizado y bien documentado  

**¡Usa `python main.py` para la experiencia modular completa!** 🚀
```

**Configurar en `.env`:**
```env
JIRA_SERVER=https://tu-empresa.atlassian.net
JIRA_EMAIL=tu-email@empresa.com
JIRA_API_TOKEN=tu-api-token
```

### 4️⃣ **¡Listo para Usar!**
```bash
python jira_extractor.py --project CMZ100
```

## 🎯 Uso del Sistema

### **Extracción Completa (Sin Límites)**
```bash
# Extraer TODOS los issues del proyecto (recomendado)
python jira_extractor.py --project CMZ100

# Equivalente explícito
python jira_extractor.py --project CMZ100 --format both
```

### **Extracción con Límites (Opcional)**
```bash
# Limitar a un número específico de issues
python jira_extractor.py --project CMZ100 --limit 500

# Combinar límite con formato específico
python jira_extractor.py --project ABC123 --limit 1000 --format excel
```

### **Opciones de Formato**
```bash
# Solo Excel
python jira_extractor.py --project CMZ100 --format excel

# Solo CSV
python jira_extractor.py --project CMZ100 --format csv

# Ambos formatos (default)
python jira_extractor.py --project CMZ100 --format both
```

### **🌐 Sistema de Paginación Inteligente**

El extractor utiliza **paginación automática** para obtener todos los issues:

- ✅ **Sin límites artificiales**: Extrae todos los issues disponibles
- ✅ **Paginación eficiente**: 100 issues por página (óptimo para Jira API)
- ✅ **Múltiples estrategias**: Issues activos → recientes → todos
- ✅ **Rate limiting**: Pausas automáticas entre páginas
- ✅ **Límite de seguridad**: Protección contra bucles infinitos (10,000 issues)

### **Ejemplo de Salida Completa**
```
🎯 EXTRACCIÓN DE DATOS JIRA
Proyecto: CMZ100
Modo: COMPLETA

🔄 Conectando a Jira...
✅ Conectado como: usuario@empresa.com
🔍 Buscando issues del proyecto CMZ100...
   🌐 Modo: Extracción completa (todos los issues)
   📋 Estrategia 1: Issues activos
   📄 Página: desde 0, tamaño 100
   📊 +100 issues (total: 100)
   📄 Página: desde 100, tamaño 100
   📊 +100 issues (total: 200)
   ... [continúa hasta obtener todos]
   🏁 Última página: 45 < 100
   ✅ Estrategia 1 exitosa: 1,245 issues totales
📊 TOTAL ENCONTRADO: 1,245 issues únicos

📈 Métricas Generales
├── Total Issues: 1,245
├── Tiempo Registrado: 2,890.5 horas
├── Tiempo Estimado: 1,830.0 horas
└── Progreso: 158.0%

✅ EXTRACCIÓN COMPLETADA
```

## 📁 Estructura del Proyecto

```
jira_alcance/
├── 📄 jira_extractor.py      # 🎯 Extractor principal
├── ⚙️ config.py              # 🔧 Configuración centralizada
├── 📋 requirements.txt       # 📦 Dependencias
├── 🔐 .env                   # 🔑 Credenciales (crear desde .env.example)
├── 📊 reports/               # 📈 Reportes generados
├── 📖 README.md              # 📘 Esta documentación
└── 📋 INSTALL.md             # 🛠️ Guía de instalación detallada
```

## 📊 Estructura de Datos Extraídos

### **Campos Principales (20 columnas)**
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `key` | Clave del issue | `CMZ100-1234` |
| `summary` | Título/resumen | `Implementar nueva funcionalidad` |
| `issue_type` | Tipo de issue | `Story`, `Bug`, `Task` |
| `status` | Estado actual | `In Progress`, `Done` |
| `time_spent` | Tiempo registrado | `8.50h` |
| `original_estimate` | Estimación original | `5.00h` |
| `remaining_estimate` | Tiempo restante | `2.00h` |
| `is_subtask` | Es subtarea | `True`/`False` |
| `parent_key` | Issue padre | `CMZ100-1000` |

### **Métricas Automáticas**
- ✅ **Progreso por Issue**: `(tiempo_gastado / estimado) * 100`
- ✅ **Distribución por Tipo**: Conteo y porcentajes automáticos
- ✅ **Totales de Proyecto**: Suma de tiempos y estimaciones
- ✅ **Identificación de Subtareas**: Relaciones padre-hijo

## 🔧 Configuración Avanzada

### **Variables de Entorno (.env)**
```env
# Conexión Jira (REQUERIDO)
JIRA_SERVER=https://empresa.atlassian.net
JIRA_EMAIL=usuario@empresa.com
JIRA_API_TOKEN=ATATT3xFfGF0...

# Configuración Opcional
DEFAULT_PROJECT=CMZ100
```

### **Personalización en config.py**
- ⚙️ **Estrategias de búsqueda JQL**
- 📊 **Formatos de exportación**
- 🎨 **Configuración de interfaz**
- 📏 **Límites de procesamiento**

## 🚀 Casos de Uso

### 👨‍💼 **Para Project Managers**
- **Seguimiento de Progreso**: Métricas en tiempo real
- **Reportes Ejecutivos**: Datos listos para presentaciones
- **Identificación de Bloqueos**: Issues con sobreestimación

### 👩‍💻 **Para Equipos de Desarrollo**
- **Análisis de Estimaciones**: Precisión histórica
- **Gestión de Subtareas**: Relaciones y dependencias
- **Timetracking**: Registro detallado por desarrollador

### 📊 **Para Análisis de Datos**
- **Datos Estructurados**: CSV para herramientas BI
- **Métricas Automáticas**: KPIs calculados
- **Exportación Flexible**: Excel para análisis ad-hoc

## 🔍 Solución de Problemas

### **Error de Conexión**
```bash
❌ Error de conexión: 401 Authentication failed
```
**Solución**: Verificar credenciales en `.env`

### **Proyecto No Encontrado**
```bash
❌ No se encontraron issues para procesar
```
**Solución**: Verificar clave del proyecto y permisos

### **Sin Datos de Timetracking**
```bash
⚠️ Tiempo: 0h / 0h
```
**Solución**: El proyecto puede no usar timetracking de Jira

## 📈 Ejemplos de Métricas Generadas

### **Reporte Típico CMZ100**
```
📊 RESUMEN DE DATOS EXTRAÍDOS

📈 Métricas Generales
├── Total Issues: 100
├── Tiempo Registrado: 291.2 horas
├── Tiempo Estimado: 183.0 horas
└── Progreso: 159.2%

📋 Distribución por Tipo
├── Subtarea: 25 (25.0%)
├── Error: 17 (17.0%)
├── Historia: 16 (16.0%)
└── Tarea: 11 (11.0%)
```

## 🤝 Contribución

### **Proceso de Desarrollo**
1. **Fork** del repositorio
2. **Branch** para nueva funcionalidad
3. **Desarrollo** con tests
4. **Pull Request** con descripción detallada

### **Estándares de Código**
- ✅ **PEP 8**: Estilo de código Python
- ✅ **Type Hints**: Tipado cuando sea posible
- ✅ **Docstrings**: Documentación de funciones
- ✅ **Rich Console**: Interfaz visual consistente

## 📞 Soporte

### **Documentación**
- 📘 **README.md**: Documentación principal (este archivo)
- 🛠️ **INSTALL.md**: Guía de instalación detallada
- ⚙️ **config.py**: Configuraciones disponibles

### **Issues Comunes**
- 🔐 **Credenciales**: Verificar API token y email
- 🌐 **Conectividad**: Verificar URL del servidor Jira
- 📊 **Permisos**: Asegurar acceso al proyecto

---

## 🏆 Versión 2.0 - Refactorizada

**Cambios Principales:**
- ✅ **Código Limpio**: Eliminación de archivos de prueba
- ✅ **Arquitectura Mejorada**: Separación clara de responsabilidades
- ✅ **Configuración Centralizada**: Sistema de configuración unificado
- ✅ **Documentación Completa**: Guías y ejemplos actualizados
- ✅ **Manejo de Errores**: Gestión robusta de excepciones

**¡Sistema listo para uso en producción!** 🚀
