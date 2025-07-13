#!/usr/bin/env python3
"""
Script para buscar específicamente el campo Genérico 1 (Ninguno)
"""

import sys
import os
from jira import JIRA
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import config

def search_for_generico1():
    """Busca específicamente el campo Genérico 1"""
    
    console = Console()
    
    try:
        # Conectar a Jira
        console.print("🔗 [cyan]Conectando a Jira...[/cyan]")
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        
        # Obtener más issues para encontrar el campo
        console.print("🔍 [cyan]Buscando en más issues...[/cyan]")
        issues = jira.search_issues('project = CMZ100', maxResults=50)
        
        console.print(f"📋 [green]Analizando {len(issues)} issues[/green]")
        
        # Buscar campos alrededor de los encontrados
        target_fields = ['customfield_14399', 'customfield_14400', 'customfield_14401', 'customfield_14402']
        
        found_fields = {}
        
        for issue in issues:
            for field_name in target_fields:
                try:
                    if hasattr(issue.fields, field_name):
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            if field_name not in found_fields:
                                found_fields[field_name] = []
                            
                            # Obtener valor legible
                            if hasattr(field_value, 'name'):
                                display_value = field_value.name
                            elif hasattr(field_value, 'value'):
                                display_value = str(field_value.value)
                            else:
                                display_value = str(field_value)
                            
                            if display_value not in found_fields[field_name]:
                                found_fields[field_name].append(display_value)
                except:
                    continue
        
        # Buscar también en un rango más amplio por si acaso
        console.print("🔍 [cyan]Buscando en rango amplio de campos...[/cyan]")
        for issue in issues[:10]:  # Limitar para no sobrecargar
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_143') or field_name.startswith('customfield_144'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            field_num = int(field_name.replace('customfield_', ''))
                            if 14390 <= field_num <= 14410:  # Rango alrededor de los encontrados
                                
                                if field_name not in found_fields:
                                    found_fields[field_name] = []
                                
                                if hasattr(field_value, 'name'):
                                    display_value = field_value.name
                                elif hasattr(field_value, 'value'):
                                    display_value = str(field_value.value)
                                else:
                                    display_value = str(field_value)
                                
                                if display_value not in found_fields[field_name]:
                                    found_fields[field_name].append(display_value)
                    except:
                        continue
        
        if found_fields:
            console.print("\n")
            console.print(Panel.fit("🎯 CAMPOS EN RANGO DE GENÉRICOS", style="bold green"))
            
            table = Table()
            table.add_column("Campo", style="cyan")
            table.add_column("Valores", style="green")
            table.add_column("Identificación", style="yellow")
            
            for field_name in sorted(found_fields.keys()):
                values = found_fields[field_name]
                values_str = " | ".join(values[:3])
                
                # Identificar el campo
                if field_name == 'customfield_14400':
                    identification = "✅ Genérico 2 - Facturable"
                elif field_name == 'customfield_14401':
                    identification = "✅ Genérico 3 - Estimado"
                elif 'ninguno' in ' '.join([v.lower() for v in values]):
                    identification = "✅ Posible Genérico 1"
                else:
                    identification = "❓ Verificar"
                
                table.add_row(field_name, values_str, identification)
            
            console.print(table)
            
            # Mostrar detalles específicos de cada campo
            console.print(f"\n📋 [cyan]DETALLES DE CAMPOS ENCONTRADOS:[/cyan]")
            for field_name, values in found_fields.items():
                console.print(f"\n   🔹 {field_name}:")
                for value in values[:5]:
                    console.print(f"      • {value}")
        else:
            console.print("❌ [red]No se encontraron campos en el rango esperado[/red]")
            
        # Si no encontramos el Genérico 1, busquemos por cualquier campo con "Ninguno"
        console.print(f"\n🔍 [cyan]Búsqueda general de 'Ninguno'...[/cyan]")
        ninguno_fields = {}
        
        for issue in issues[:20]:
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            value_str = ""
                            if hasattr(field_value, 'name'):
                                value_str = field_value.name.lower()
                            elif hasattr(field_value, 'value'):
                                value_str = str(field_value.value).lower()
                            else:
                                value_str = str(field_value).lower()
                            
                            if 'ninguno' in value_str:
                                if field_name not in ninguno_fields:
                                    ninguno_fields[field_name] = []
                                display = field_value.name if hasattr(field_value, 'name') else str(field_value)
                                if display not in ninguno_fields[field_name]:
                                    ninguno_fields[field_name].append(display)
                    except:
                        continue
        
        if ninguno_fields:
            console.print(f"   ✅ Campos con 'Ninguno' encontrados:")
            for field_name, values in ninguno_fields.items():
                console.print(f"      • {field_name}: {' | '.join(values)}")
        else:
            console.print(f"   ❌ No se encontraron campos con 'Ninguno'")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_for_generico1()
