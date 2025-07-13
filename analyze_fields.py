#!/usr/bin/env python3
"""
Script para analizar campos disponibles en la API de Jira que no están siendo utilizados
"""

import sys
import os
from jira import JIRA
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import config

def analyze_available_fields():
    """Analiza los campos disponibles en la API de Jira"""
    
    console = Console()
    
    try:
        # Conectar a Jira
        console.print("🔗 [cyan]Conectando a Jira...[/cyan]")
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        
        # Obtener un issue de ejemplo para analizar sus campos
        console.print("🔍 [cyan]Obteniendo issue de ejemplo...[/cyan]")
        issues = jira.search_issues('project = CMZ100', maxResults=1, expand='changelog')
        
        if not issues:
            console.print("❌ [red]No se encontraron issues para analizar[/red]")
            return
        
        issue = issues[0]
        console.print(f"📋 [green]Analizando issue: {issue.key}[/green]")
        
        # Campos que YA estamos usando en el reporte
        used_fields = {
            'key', 'summary', 'issuetype', 'status', 'priority', 'assignee', 
            'reporter', 'created', 'updated', 'project', 'timetracking',
            'parent', 'components', 'labels', 'fixVersions'
        }
        
        # Obtener todos los campos disponibles
        console.print("🔎 [cyan]Analizando campos disponibles...[/cyan]")
        
        # Campos estándar disponibles
        available_fields = []
        
        # Analizar campos en issue.fields
        for field_name in dir(issue.fields):
            if not field_name.startswith('_'):
                field_value = getattr(issue.fields, field_name)
                field_type = type(field_value).__name__
                
                # Determinar si ya lo usamos
                is_used = field_name in used_fields
                
                # Obtener valor de ejemplo (truncado)
                if field_value is not None:
                    if isinstance(field_value, str):
                        example_value = field_value[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
                    elif isinstance(field_value, list):
                        example_value = f"[Lista con {len(field_value)} elementos]"
                    elif hasattr(field_value, 'name'):
                        example_value = field_value.name
                    elif hasattr(field_value, 'displayName'):
                        example_value = field_value.displayName
                    else:
                        example_value = str(field_value)[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
                else:
                    example_value = "None"
                
                available_fields.append({
                    'field': field_name,
                    'type': field_type,
                    'used': is_used,
                    'example': example_value
                })
        
        # Separar campos usados y no usados
        used_fields_list = [f for f in available_fields if f['used']]
        unused_fields_list = [f for f in available_fields if not f['used']]
        
        # Mostrar tabla de campos NO USADOS
        console.print("\n")
        console.print(Panel.fit("🔍 CAMPOS DISPONIBLES NO UTILIZADOS EN EL REPORTE", style="bold red"))
        
        table = Table()
        table.add_column("Campo", style="cyan", no_wrap=True)
        table.add_column("Tipo", style="magenta")
        table.add_column("Valor de ejemplo", style="green")
        
        for field in sorted(unused_fields_list, key=lambda x: x['field']):
            table.add_row(
                field['field'],
                field['type'],
                field['example']
            )
        
        console.print(table)
        
        # Mostrar resumen
        console.print(f"\n📊 [bold blue]RESUMEN:[/bold blue]")
        console.print(f"   • Campos totales disponibles: {len(available_fields)}")
        console.print(f"   • Campos actualmente utilizados: {len(used_fields_list)}")
        console.print(f"   • Campos NO utilizados: {len(unused_fields_list)}")
        
        # Mostrar campos usados para referencia
        console.print(f"\n✅ [bold green]CAMPOS ACTUALMENTE UTILIZADOS:[/bold green]")
        used_fields_names = [f['field'] for f in used_fields_list]
        console.print(f"   {', '.join(sorted(used_fields_names))}")
        
        # Analizar campos custom (customfield_*)
        custom_fields = [f for f in unused_fields_list if f['field'].startswith('customfield_')]
        if custom_fields:
            console.print(f"\n🎛️ [bold yellow]CAMPOS PERSONALIZADOS DISPONIBLES ({len(custom_fields)}):[/bold yellow]")
            for field in custom_fields[:10]:  # Mostrar solo los primeros 10
                console.print(f"   • {field['field']}: {field['example']}")
            if len(custom_fields) > 10:
                console.print(f"   ... y {len(custom_fields) - 10} más")
        
        # Campos potencialmente útiles
        potentially_useful = []
        useful_keywords = ['description', 'resolution', 'environment', 'due', 'version', 
                          'security', 'votes', 'watches', 'worklog', 'comment', 'attachment',
                          'estimate', 'progress', 'team', 'epic', 'story']
        
        for field in unused_fields_list:
            for keyword in useful_keywords:
                if keyword.lower() in field['field'].lower() and field['example'] != "None":
                    potentially_useful.append(field)
                    break
        
        if potentially_useful:
            console.print(f"\n💡 [bold yellow]CAMPOS POTENCIALMENTE ÚTILES:[/bold yellow]")
            for field in potentially_useful[:15]:  # Limitar a 15
                console.print(f"   • {field['field']}: {field['example']}")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        return

if __name__ == "__main__":
    analyze_available_fields()
