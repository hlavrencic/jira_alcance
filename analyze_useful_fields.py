#!/usr/bin/env python3
"""
Script mejorado para analizar campos específicos de Jira y generar recomendaciones
"""

import sys
import os
from jira import JIRA
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import config

def analyze_useful_fields():
    """Analiza campos específicos útiles para el reporte"""
    
    console = Console()
    
    try:
        # Conectar a Jira
        console.print("🔗 [cyan]Conectando a Jira...[/cyan]")
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        
        # Obtener varios issues para analizar campos con datos
        console.print("🔍 [cyan]Obteniendo múltiples issues para análisis...[/cyan]")
        issues = jira.search_issues('project = CMZ100', maxResults=10, expand='changelog')
        
        if not issues:
            console.print("❌ [red]No se encontraron issues para analizar[/red]")
            return
        
        console.print(f"📋 [green]Analizando {len(issues)} issues[/green]")
        
        # Campos específicos que podrían ser útiles
        interesting_fields = {
            # Campos estándar útiles
            'description': 'Descripción del issue',
            'duedate': 'Fecha de vencimiento',
            'environment': 'Entorno/ambiente',
            'resolution': 'Resolución del issue',
            'resolutiondate': 'Fecha de resolución',
            'security': 'Nivel de seguridad',
            'versions': 'Versiones afectadas',
            'votes': 'Votos del issue',
            'workratio': 'Ratio de trabajo',
            'issuelinks': 'Links a otros issues',
            'subtasks': 'Subtareas',
            'attachment': 'Archivos adjuntos',
            'comment': 'Comentarios',
            'worklog': 'Registro de trabajo',
            'aggregatetimeestimate': 'Tiempo estimado agregado',
            'aggregatetimeoriginalestimate': 'Estimación original agregada',
            'aggregatetimespent': 'Tiempo gastado agregado',
            'timeestimate': 'Tiempo estimado',
            'timeoriginalestimate': 'Estimación original',
            'timespent': 'Tiempo gastado',
            'progress': 'Progreso',
            'aggregateprogress': 'Progreso agregado',
            'statusCategory': 'Categoría de estado',
            'statuscategorychangedate': 'Fecha cambio categoría estado',
            'lastViewed': 'Última visualización',
            'creator': 'Creador'
        }
        
        # Analizar campos en los issues
        field_analysis = {}
        
        for field_name, description in interesting_fields.items():
            values_found = []
            issues_with_data = 0
            
            for issue in issues:
                try:
                    if hasattr(issue.fields, field_name):
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            issues_with_data += 1
                            
                            # Procesar valor según tipo
                            if isinstance(field_value, str):
                                if len(field_value) > 100:
                                    values_found.append(f"{field_value[:100]}...")
                                else:
                                    values_found.append(field_value)
                            elif isinstance(field_value, list):
                                if field_value:
                                    values_found.append(f"[{len(field_value)} elementos]")
                                else:
                                    values_found.append("[Lista vacía]")
                            elif hasattr(field_value, 'name'):
                                values_found.append(field_value.name)
                            elif hasattr(field_value, 'displayName'):
                                values_found.append(field_value.displayName)
                            else:
                                values_found.append(str(field_value)[:100])
                            
                            # Solo tomar primeros 3 ejemplos
                            if len(values_found) >= 3:
                                break
                except:
                    continue
            
            if issues_with_data > 0:
                field_analysis[field_name] = {
                    'description': description,
                    'issues_with_data': issues_with_data,
                    'total_issues': len(issues),
                    'examples': values_found[:3],
                    'usage_percentage': round((issues_with_data / len(issues)) * 100, 1)
                }
        
        # Mostrar tabla de campos útiles NO utilizados
        console.print("\n")
        console.print(Panel.fit("📊 CAMPOS ÚTILES DISPONIBLES NO INCLUIDOS EN EL REPORTE", style="bold yellow"))
        
        table = Table()
        table.add_column("Campo", style="cyan", no_wrap=True)
        table.add_column("Descripción", style="magenta")
        table.add_column("Uso", style="green")
        table.add_column("Ejemplos", style="white")
        
        # Ordenar por porcentaje de uso
        sorted_fields = sorted(field_analysis.items(), key=lambda x: x[1]['usage_percentage'], reverse=True)
        
        for field_name, data in sorted_fields:
            usage_text = f"{data['issues_with_data']}/{data['total_issues']} ({data['usage_percentage']}%)"
            examples_text = " | ".join(data['examples']) if data['examples'] else "Sin ejemplos"
            
            # Colorear según utilidad
            if data['usage_percentage'] >= 50:
                usage_style = "bold green"
            elif data['usage_percentage'] >= 20:
                usage_style = "yellow"
            else:
                usage_style = "dim"
            
            table.add_row(
                field_name,
                data['description'],
                Text(usage_text, style=usage_style),
                examples_text[:80] + "..." if len(examples_text) > 80 else examples_text
            )
        
        console.print(table)
        
        # Analizar campos custom con valores
        console.print("\n🎛️ [bold yellow]ANALIZANDO CAMPOS PERSONALIZADOS CON DATOS...[/bold yellow]")
        
        custom_field_analysis = {}
        
        for issue in issues[:3]:  # Analizar solo primeros 3 issues para custom fields
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            if field_name not in custom_field_analysis:
                                custom_field_analysis[field_name] = []
                            
                            # Procesar valor
                            if isinstance(field_value, str):
                                custom_field_analysis[field_name].append(field_value[:100])
                            elif isinstance(field_value, list):
                                if field_value:
                                    custom_field_analysis[field_name].append(f"[{len(field_value)} elementos]")
                            elif hasattr(field_value, 'name'):
                                custom_field_analysis[field_name].append(field_value.name)
                            elif hasattr(field_value, 'value'):
                                custom_field_analysis[field_name].append(str(field_value.value))
                            else:
                                custom_field_analysis[field_name].append(str(field_value)[:100])
                    except:
                        continue
        
        if custom_field_analysis:
            console.print("\n📋 [cyan]CAMPOS PERSONALIZADOS CON DATOS:[/cyan]")
            for field_name, values in list(custom_field_analysis.items())[:15]:  # Mostrar solo primeros 15
                unique_values = list(set(values))[:3]  # Máximo 3 valores únicos
                console.print(f"   • {field_name}: {' | '.join(unique_values)}")
        
        # Recomendaciones
        console.print("\n")
        console.print(Panel.fit("💡 RECOMENDACIONES PARA AGREGAR AL REPORTE", style="bold green"))
        
        high_value_fields = [
            name for name, data in sorted_fields 
            if data['usage_percentage'] >= 30
        ]
        
        medium_value_fields = [
            name for name, data in sorted_fields 
            if 10 <= data['usage_percentage'] < 30
        ]
        
        if high_value_fields:
            console.print("🟢 [bold green]ALTA PRIORIDAD (>30% de uso):[/bold green]")
            for field in high_value_fields:
                data = field_analysis[field]
                console.print(f"   • {field}: {data['description']} ({data['usage_percentage']}% uso)")
        
        if medium_value_fields:
            console.print("\n🟡 [bold yellow]MEDIA PRIORIDAD (10-30% de uso):[/bold yellow]")
            for field in medium_value_fields:
                data = field_analysis[field]
                console.print(f"   • {field}: {data['description']} ({data['usage_percentage']}% uso)")
        
        # Campos específicos de timetracking agregado
        console.print("\n⏱️ [bold blue]CAMPOS DE TIMETRACKING AGREGADO:[/bold blue]")
        console.print("   Nota: Estos campos muestran tiempo agregado incluyendo subtareas")
        for field in ['aggregatetimeestimate', 'aggregatetimeoriginalestimate', 'aggregatetimespent']:
            if field in field_analysis:
                data = field_analysis[field]
                console.print(f"   • {field}: {data['usage_percentage']}% uso")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_useful_fields()
