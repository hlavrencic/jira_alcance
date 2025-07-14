#!/usr/bin/env python3
"""
Jira Sprint Data Extractor - Script principal
Automatización para extracción de datos de timetracking de Jira
"""
import argparse
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.jira_extractor import JiraDataExtractor


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Extrae datos de timetracking de proyectos Jira',
        epilog="""
Ejemplos de uso:
  # Extraer datos con selección de sprints (modo por defecto):
  python main.py --project CMZ100
  
  # Extraer datos con búsqueda tradicional (sin sprints):
  python main.py --project CMZ100 --no-sprints
  
  # Exportar solo a Excel:
  python main.py --project CMZ100 --format excel
  
  # Limitar a 1000 issues:
  python main.py --project CMZ100 --limit 1000
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--project',
        required=True,
        help='Clave del proyecto Jira (ej: CMZ100, DEV, SUPPORT)'
    )
    
    parser.add_argument(
        '--format',
        choices=['excel', 'csv', 'both'],
        default='both',
        help='Formato de exportación (por defecto: both)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Límite máximo de issues a extraer (por defecto: sin límite)'
    )
    
    parser.add_argument(
        '--no-sprints',
        action='store_true',
        help='Usar búsqueda tradicional sin selección de sprints'
    )
    
    args = parser.parse_args()
    
    # Determinar si usar sprints (por defecto sí, a menos que se especifique --no-sprints)
    use_sprints = not args.no_sprints
    
    # Crear y ejecutar extractor
    extractor = JiraDataExtractor()
    
    success = extractor.run(
        project_key=args.project,
        export_format=args.format,
        max_results=args.limit,
        use_sprints=use_sprints
    )
    
    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
