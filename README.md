# 🎯 Jira Data Extractor - Sistema Refactorizado

**Extractor profesional de datos de proyectos Jira con timetracking completo**

![Version](https://img.shields.io/badge/version-2.0-blue) ![Python](https://img.shields.io/badge/python-3.11+-green) ![Status](https://img.shields.io/badge/status-production-brightgreen)

## 📋 Descripción

Sistema automatizado para extraer datos completos de proyectos Jira, incluyendo:
- ⏱️ **Timetracking detallado** (tiempo registrado, estimado, restante)
- 🔗 **Relaciones entre issues** (subtareas, padres)
- 📊 **Métricas automáticas** de progreso y distribución
- 📈 **Reportes profesionales** en Excel y CSV

## 🚀 Características Principales

### ✅ **Funcionalidades Core**
- **Extracción Completa**: Todos los datos de timetracking por issue
- **Adaptabilidad**: Funciona con proyectos con o sin sprints activos
- **Múltiples Formatos**: Exportación a Excel y CSV
- **Interfaz Visual**: Progreso y resúmenes con Rich Console
- **Configuración Flexible**: Adaptable a diferentes instancias de Jira

### 📊 **Datos Extraídos**
- **Básicos**: Clave, resumen, tipo, estado, prioridad
- **Asignación**: Asignado, reportero, fechas
- **Timetracking**: Tiempo gastado, estimado, restante (horas y segundos)
- **Estructura**: Subtareas, componentes, labels
- **Métricas**: Progreso calculado, distribuciones automáticas

## 🛠️ Instalación Rápida

### 1️⃣ **Clonar Repositorio**
```bash
git clone <repository-url>
cd jira_alcance
```

### 2️⃣ **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Configurar Credenciales**
```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tus credenciales
notepad .env
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

### **Extracción Básica**
```bash
# Extraer proyecto completo (Excel + CSV)
python jira_extractor.py --project CMZ100

# Solo Excel
python jira_extractor.py --project ABC123 --format excel

# Solo CSV
python jira_extractor.py --project XYZ789 --format csv
```

### **Ejemplo de Salida**
```
🎯 EXTRACCIÓN DE DATOS JIRA
Proyecto: CMZ100

🔄 Conectando a Jira...
✅ Conectado como: usuario@empresa.com
🔍 Buscando issues del proyecto CMZ100...
✅ Encontrados 100 issues
⚙️ Procesando datos de timetracking...
📊 RESUMEN DE DATOS EXTRAÍDOS

📈 Métricas Generales
├── Total Issues: 100
├── Tiempo Registrado: 291.2 horas
├── Tiempo Estimado: 183.0 horas
└── Progreso: 159.2%

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
