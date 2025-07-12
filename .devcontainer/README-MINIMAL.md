# 🚀 DevContainer Mínimo - Jira Extractor

## ⚡ Setup en 3 pasos

### **1. Abrir en VS Code**
```bash
code c:\Repositories\jira_alcance
```

### **2. Reabrir en Container**
- Presiona `Ctrl+Shift+P`
- Escribe: "Dev Containers: Reopen in Container"
- Espera a que se instalen las dependencias (2-3 minutos)

### **3. Ejecutar**
```bash
# Configurar credenciales (primera vez)
cp .env.example .env
nano .env

# Ejecutar extracción
python jira_extractor.py --project CMZ100
```

## 📋 Qué incluye este devcontainer

- ✅ **Python 3.11-slim** (imagen base ligera)
- ✅ **5 dependencias esenciales**:
  - `jira` - API de Jira
  - `pandas` - Procesamiento de datos
  - `openpyxl` - Exportar Excel
  - `rich` - Interfaz visual
  - `python-dotenv` - Variables de entorno

## 🎯 Sin configuraciones extras

- ❌ Sin extensiones VS Code complejas
- ❌ Sin herramientas de desarrollo adicionales
- ❌ Sin bind mounts problemáticos
- ❌ Sin features innecesarias

**Solo lo mínimo para que funcione la aplicación.**

## 🔧 Si falla

**Alternativa local:**
```bash
pip install jira pandas openpyxl rich python-dotenv
python jira_extractor.py --project CMZ100
```

**🎉 ¡Listo para extraer datos de Jira!**
