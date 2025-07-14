"""
Extractor de metadatos de issues
"""
from typing import Dict, Any, List
from .base_extractor import BaseExtractor
from ..config import CUSTOM_FIELDS


class MetadataExtractor(BaseExtractor):
    """Extractor especializado en metadatos de issues"""
    
    def extract(self, issue: Any) -> Dict[str, Any]:
        """
        Extrae metadatos (componentes, labels, fix versions, campos genéricos, etc.)
        
        Args:
            issue: Issue de Jira
            
        Returns:
            Diccionario con metadatos del issue
        """
        # Componentes
        components = self._extract_components(issue)
        
        # Labels
        labels = self._extract_labels(issue)
        
        # Fix Versions
        fix_versions = self._extract_fix_versions(issue)
        
        # Campos genéricos
        generic_fields = self._extract_generic_fields(issue)
        
        return {
            'components': ', '.join(components) if components else 'Sin Componentes',
            'labels': ', '.join(labels) if labels else 'Sin Labels',
            'fixversion': '; '.join(fix_versions) if fix_versions else 'Sin Fix Version',
            **generic_fields
        }
    
    def _extract_components(self, issue: Any) -> List[str]:
        """Extrae componentes del issue"""
        components = self._safe_get_nested_attribute(issue, 'fields.components', [])
        return [comp.name for comp in components if hasattr(comp, 'name')]
    
    def _extract_labels(self, issue: Any) -> List[str]:
        """Extrae labels del issue"""
        return self._safe_get_nested_attribute(issue, 'fields.labels', [])
    
    def _extract_fix_versions(self, issue: Any) -> List[str]:
        """Extrae fix versions del issue"""
        fix_versions = self._safe_get_nested_attribute(issue, 'fields.fixVersions', [])
        return [version.name for version in fix_versions if hasattr(version, 'name')]
    
    def _extract_generic_fields(self, issue: Any) -> Dict[str, str]:
        """Extrae campos genéricos personalizados"""
        generic_data = {}
        
        for field_name, custom_field in CUSTOM_FIELDS.items():
            field_value = self._safe_get_nested_attribute(issue, f'fields.{custom_field}')
            
            if field_value:
                if hasattr(field_value, 'name'):
                    generic_data[field_name] = field_value.name
                elif hasattr(field_value, 'value'):
                    generic_data[field_name] = str(field_value.value)
                else:
                    generic_data[field_name] = str(field_value)
            else:
                generic_data[field_name] = 'Sin Datos'
        
        return generic_data
