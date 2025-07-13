#!/usr/bin/env python3
"""
Script para identificar campos custom específicos (Genérico 1, 2, 3)
"""

import sys
import os
from jira import JIRA
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import config

def find_generic_fields():
    """Busca los campos Genérico 1, 2, 3 en la API"""
    
    console = Console()
    
    try:
        # Conectar a Jira
        console.print("🔗 [cyan]Conectando a Jira...[/cyan]")
        jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
        
        # Obtener varios issues para analizar campos con datos
        console.print("🔍 [cyan]Obteniendo issues con datos...[/cyan]")
        issues = jira.search_issues('project = CMZ100', maxResults=20)
        
        if not issues:
            console.print("❌ [red]No se encontraron issues para analizar[/red]")
            return
        
        console.print(f"📋 [green]Analizando {len(issues)} issues[/green]")
        
        # Buscar campos que contengan "genérico" o valores como "Facturable", "Estimado"
        potential_fields = {}
        
        for issue in issues:
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            # Convertir valor a string para búsqueda
                            value_str = str(field_value).lower()
                            
                            # Buscar valores específicos
                            if any(keyword in value_str for keyword in 
                                  ['facturable', 'estimado', 'ninguno', 'genérico', 'generic']):
                                
                                if field_name not in potential_fields:
                                    potential_fields[field_name] = []
                                
                                # Obtener valor legible
                                if hasattr(field_value, 'name'):
                                    display_value = field_value.name
                                elif hasattr(field_value, 'value'):
                                    display_value = str(field_value.value)
                                else:
                                    display_value = str(field_value)
                                
                                if display_value not in potential_fields[field_name]:
                                    potential_fields[field_name].append(display_value)
                    except:
                        continue
        
        # También buscar por opciones específicas en todos los campos custom
        console.print("🔍 [cyan]Buscando campos con opciones específicas...[/cyan]")
        
        target_values = ['facturable', 'estimado', 'ninguno']
        additional_fields = {}
        
        for issue in issues[:10]:  # Limitar para no sobrecargar
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None:
                            # Obtener valor para comparación
                            if hasattr(field_value, 'name'):
                                check_value = field_value.name.lower()
                            elif hasattr(field_value, 'value'):
                                check_value = str(field_value.value).lower()
                            else:
                                check_value = str(field_value).lower()
                            
                            # Verificar si contiene algún valor objetivo
                            for target in target_values:
                                if target in check_value:
                                    if field_name not in additional_fields:
                                        additional_fields[field_name] = []
                                    
                                    display_val = field_value.name if hasattr(field_value, 'name') else str(field_value)
                                    if display_val not in additional_fields[field_name]:
                                        additional_fields[field_name].append(display_val)
                    except:
                        continue
        
        # Combinar resultados
        all_fields = {**potential_fields, **additional_fields}
        
        if all_fields:
            console.print("\n")
            console.print(Panel.fit("🎯 CAMPOS CUSTOM POTENCIALES PARA GENÉRICO 1, 2, 3", style="bold green"))
            
            table = Table()
            table.add_column("Campo Custom", style="cyan")
            table.add_column("Valores encontrados", style="green")
            table.add_column("Posible asignación", style="yellow")
            
            for field_name, values in all_fields.items():
                values_str = " | ".join(values[:5])  # Máximo 5 valores
                
                # Determinar posible asignación
                values_lower = [v.lower() for v in values]
                if 'facturable' in ' '.join(values_lower):
                    assignment = "🔹 Posible Genérico 2"
                elif 'estimado' in ' '.join(values_lower):
                    assignment = "🔸 Posible Genérico 3"
                elif 'ninguno' in ' '.join(values_lower):
                    assignment = "🔺 Posible Genérico 1"
                else:
                    assignment = "❓ Revisar manualmente"
                
                table.add_row(field_name, values_str, assignment)
            
            console.print(table)
        else:
            console.print("❌ [red]No se encontraron campos que coincidan con los criterios[/red]")
        
        # Buscar también por posición o número de campo
        console.print(f"\n🔍 [cyan]Buscando campos custom por rango numérico...[/cyan]")
        custom_fields_with_data = []
        
        for issue in issues[:5]:
            for field_name in dir(issue.fields):
                if field_name.startswith('customfield_'):
                    try:
                        field_value = getattr(issue.fields, field_name)
                        if field_value is not None and field_name not in [f[0] for f in custom_fields_with_data]:
                            # Obtener número del campo
                            field_num = int(field_name.replace('customfield_', ''))
                            
                            display_val = ""
                            if hasattr(field_value, 'name'):
                                display_val = field_value.name
                            elif hasattr(field_value, 'value'):
                                display_val = str(field_value.value)
                            else:
                                display_val = str(field_value)[:50]
                            
                            custom_fields_with_data.append((field_name, field_num, display_val))
                    except:
                        continue
        
        # Ordenar por número y mostrar campos recientes
        custom_fields_with_data.sort(key=lambda x: x[1], reverse=True)
        
        console.print(f"\n📋 [cyan]CAMPOS CUSTOM RECIENTES (últimos 20):[/cyan]")
        for field_name, field_num, value in custom_fields_with_data[:20]:
            console.print(f"   • {field_name} (#{field_num}): {value}")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_generic_fields()
