# 📊 ANÁLISIS DE CAMPOS DISPONIBLES EN JIRA API
*Campos obtenidos de la API que no se están incluyendo en el reporte actual*

---

## 🎯 RESUMEN EJECUTIVO

**Total de campos analizados:** 173 campos  
**Campos actualmente utilizados:** 14 campos  
**Campos disponibles no utilizados:** 159 campos  

---

## ✅ CAMPOS ACTUALMENTE INCLUIDOS EN EL REPORTE

```
assignee, components, created, fixVersions, issuetype, labels, 
parent, priority, project, reporter, status, summary, timetracking, updated
```

---

## 🟢 ALTA PRIORIDAD - Campos recomendados para agregar

### 1. **`description`** - Descripción del issue (30% uso)
- **Tipo:** Texto
- **Utilidad:** Información detallada del requirement/bug
- **Ejemplo:** "Verificar que no permita pagar solo el concepto gas de la factura..."

### 2. **`duedate`** - Fecha de vencimiento (20% uso) 
- **Tipo:** Fecha
- **Utilidad:** Planning y seguimiento de deadlines
- **Ejemplo:** "2025-08-15", "2025-08-30"

### 3. **`resolution`** - Resolución del issue (10% uso)
- **Tipo:** Texto
- **Utilidad:** Cómo se resolvió el issue
- **Ejemplo:** "Hecho", "No se puede reproducir", "Duplicado"

### 4. **`resolutiondate`** - Fecha de resolución (10% uso)
- **Tipo:** Fecha
- **Utilidad:** Métricas de tiempo de resolución
- **Ejemplo:** "2025-07-11T19:38:46.614-0300"

### 5. **`creator`** - Creador del issue (30% uso)
- **Tipo:** Usuario
- **Utilidad:** Diferente del reporter, es quien realmente creó el issue
- **Ejemplo:** "Hernán Lavrencic", "Danilo José Alcalá Barrientos"

---

## 🟡 MEDIA PRIORIDAD - Campos opcionales útiles

### 6. **`statusCategory`** - Categoría de estado (30% uso)
- **Tipo:** Categoría
- **Utilidad:** Agrupación de estados (Por hacer, En progreso, Listo)
- **Ejemplo:** "Listo", "Por hacer", "En progreso"

### 7. **`environment`** - Entorno/ambiente
- **Tipo:** Texto  
- **Utilidad:** Información técnica sobre el entorno del bug
- **Ejemplo:** "Producción", "Testing", "Desarrollo"

### 8. **`security`** - Nivel de seguridad (30% uso)
- **Tipo:** Nivel
- **Utilidad:** Control de acceso y visibilidad
- **Ejemplo:** "Público", "Privado"

### 9. **`versions`** - Versiones afectadas (30% uso)
- **Tipo:** Lista
- **Utilidad:** En qué versiones se encontró el problema
- **Diferencia con fixVersions:** versions = donde está el bug, fixVersions = donde se va a arreglar

### 10. **`issuelinks`** - Links a otros issues (30% uso)
- **Tipo:** Lista de relaciones
- **Utilidad:** Relaciones como "bloquea", "depende de", "relacionado con"
- **Ejemplo:** Conexiones entre issues del mismo proyecto

---

## 🔧 CAMPOS TÉCNICOS DE INTERÉS

### 11. **`workratio`** - Ratio de trabajo (30% uso)
- **Tipo:** Entero
- **Utilidad:** Porcentaje de progreso (-1 = no calculado)

### 12. **`votes`** - Votos del issue (30% uso)
- **Tipo:** Número
- **Utilidad:** Popularidad/prioridad percibida por usuarios

### 13. **`lastViewed`** - Última visualización (30% uso)
- **Tipo:** Fecha
- **Utilidad:** Actividad reciente en el issue

### 14. **`statuscategorychangedate`** - Fecha cambio categoría estado (30% uso)
- **Tipo:** Fecha
- **Utilidad:** Cuándo cambió de "Por hacer" a "En progreso", etc.

---

## 📎 CAMPOS DE CONTENIDO

### 15. **`attachment`** - Archivos adjuntos (30% uso)
- **Tipo:** Lista
- **Utilidad:** Cantidad de archivos adjuntos
- **Recomendación:** Agregar solo contador de attachments

### 16. **`comment`** - Comentarios (30% uso)
- **Tipo:** Colección
- **Utilidad:** Cantidad de comentarios
- **Recomendación:** Agregar solo contador de comentarios

### 17. **`subtasks`** - Subtareas (30% uso)
- **Tipo:** Lista
- **Utilidad:** Cantidad de subtareas (ya tenemos parent-child mapping)
- **Nota:** Podríamos agregar contador de subtareas

---

## ⏱️ CAMPOS DE TIMETRACKING AVANZADO

**Nota:** Estos campos NO fueron encontrados con datos en el análisis, pero están disponibles:

### 18. **`aggregatetimeestimate`** - Tiempo estimado agregado
- **Utilidad:** Suma total incluyendo subtareas
- **Estado:** Sin datos en muestra analizada

### 19. **`aggregatetimeoriginalestimate`** - Estimación original agregada  
- **Utilidad:** Estimación inicial total incluyendo subtareas
- **Estado:** Sin datos en muestra analizada

### 20. **`aggregatetimespent`** - Tiempo gastado agregado
- **Utilidad:** Tiempo total gastado incluyendo subtareas  
- **Estado:** Sin datos en muestra analizada

---

## 🎛️ CAMPOS PERSONALIZADOS (CUSTOM FIELDS)

**Total encontrados:** 132 campos custom  
**Con datos:** 11 campos

### Campos custom con valores interesantes:
- **`customfield_10007`** - Sprint information (lista con elementos)
- **`customfield_14900`** - "Delivery" (posible campo de tipo de entrega)
- **`customfield_16431`** - "Peer review" (estado de revisión)
- **`customfield_16435`** - "Sin evaluar" (estado de evaluación)
- **`customfield_16632`** - "No" (campo booleano)
- **`customfield_16633`** - "Hired" (posible estado de contratación)

---

## 🚀 RECOMENDACIONES DE IMPLEMENTACIÓN

### **Fase 1 - Campos Esenciales (Implementar primero)**
1. `description` - Descripción del issue
2. `duedate` - Fecha de vencimiento  
3. `resolution` - Resolución
4. `resolutiondate` - Fecha de resolución
5. `creator` - Creador del issue

### **Fase 2 - Campos de Análisis**
6. `statusCategory` - Categoría de estado
7. `versions` - Versiones afectadas
8. `issuelinks` - Conteo de links a otros issues
9. `attachment` - Conteo de archivos adjuntos
10. `comment` - Conteo de comentarios

### **Fase 3 - Campos Avanzados**
11. `environment` - Entorno
12. `security` - Nivel de seguridad
13. `workratio` - Ratio de trabajo
14. `votes` - Votos
15. `lastViewed` - Última visualización

---

## 💡 CASOS DE USO POR CAMPO

### **Para Gestión de Proyectos:**
- `duedate` - Planning y deadlines
- `resolution` + `resolutiondate` - Métricas de resolución
- `statusCategory` - Estados macro del workflow

### **Para Análisis de Calidad:**
- `description` - Análisis de requerimientos
- `versions` - Tracking de bugs por versión
- `environment` - Problemas por entorno

### **Para Análisis de Colaboración:**
- `creator` vs `reporter` - Quién crea vs quién reporta
- `issuelinks` - Relaciones entre trabajo
- `votes` - Prioridad percibida por usuarios

### **Para Auditoría y Compliance:**
- `security` - Nivel de confidencialidad
- `lastViewed` - Actividad y seguimiento
- `attachment` count - Documentación adjunta

---

*Análisis generado el 13 de julio de 2025*  
*Basado en muestra de 10 issues del proyecto CMZ100*
