"""
JSON to Xeto Converter Service

This module provides functionality to convert JSON device data into Xeto library format.
It handles the conversion of device properties, BACnet points, and Modbus registers.
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger("mosaic.apps.pdf_ingestion")

class JsonConverterService:
    """Service for converting JSON data to Xeto format"""

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize a name to be Xeto-compatible
        
        Args:
            name: The name to sanitize
            
        Returns:
            Sanitized name
        """
        # Remove all non-alphanumeric characters except underscores
        name = re.sub(r'[^\w\s]', '_', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Ensure it starts with a letter
        if name and not name[0].isalpha():
            name = 'x_' + name
        return name

    @staticmethod
    def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten a nested dictionary
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(JsonConverterService._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle lists that aren't empty and contain strings
                if v and all(isinstance(x, str) for x in v):
                    items.append((new_key, ', '.join(v)))
            elif v is not None and v != '':  # Only add non-empty values
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def _create_device_name(org: str, model: str) -> str:
        """
        Create a valid Xeto device name
        
        Args:
            org: Organization/manufacturer name
            model: Model name
            
        Returns:
            Valid Xeto device name
        """
        # Remove all non-alphanumeric characters and convert to camel case
        org = ''.join(word.capitalize() for word in re.findall(r'\w+', org))
        model = ''.join(word.capitalize() for word in re.findall(r'\w+', model))
        
        # Combine org and model
        device_name = f"{org}{model}"
        
        # Ensure the name starts with a letter
        if not device_name[0].isalpha():
            device_name = 'Device' + device_name
        
        return device_name

    def _create_point_definition(
        self,
        point_name: str,
        point_data: Dict[str, Any],
        mode: str = 'simple'
    ) -> str:
        """
        Create a point definition in Xeto format
        
        Args:
            point_name: Name of the point
            point_data: Point data dictionary
            mode: 'simple' or 'advanced' point definition mode
            
        Returns:
            Xeto point definition string
        """
        if mode == 'advanced':
            return self._create_advanced_point(point_name, point_data)
        return self._create_simple_point(point_name, point_data)

    def _create_simple_point(self, point_name: str, point_data: Dict[str, Any]) -> str:
        """Create a simple point definition"""
        content = f"{point_name}: ph::Point {{\n"
        
        # Add BACnet address
        if point_data.get('bacnet_address'):
            content += f'  bacnetCur: "{point_data["bacnet_address"]}"\n'
        
        # Add units if present
        if point_data.get('units'):
            content += f'  unit: "{point_data["units"]}"\n'
        
        # Add description if present
        if point_data.get('description'):
            content += f'  dis: "{point_data["description"]}"\n'
        
        content += "}\n\n"
        return content

    def _create_advanced_point(self, point_name: str, point_data: Dict[str, Any]) -> str:
        """Create an advanced point definition with protocol addressing"""
        point_type = point_data.get('point_type', 'ElecPoint')
        content = f"{point_name}: {point_type} {{\n"
        
        # Handle BACnet address
        bacnet_addr = point_data.get('bacnet_address', '')
        if bacnet_addr and re.match(r'[A-Za-z]+\d+', bacnet_addr):
            content += "  bacnetAddr: BacnetAddr {\n"
            content += f'    addr: "{bacnet_addr}"\n'
            if point_data.get('trend'):
                content += f'    trend: "{point_data["trend"]}"\n'
            content += "  }\n"
        
        # Handle Modbus address
        modbus_addr = point_data.get('modbus_address', '')
        if modbus_addr and re.match(r'\b(0|1|3|4)(\d{4})\b', modbus_addr):
            content += "  modbusAddr: ModbusAddr {\n"
            content += f'    addr: "{modbus_addr}"\n'
            for key in ['encoding', 'access', 'scale', 'offset']:
                if point_data.get(key):
                    content += f'    {key}: "{point_data[key]}"\n'
            if point_data.get('bit_index') is not None:
                content += f'    bitIndex: "{point_data["bit_index"]}"\n'
            content += "  }\n"
        
        # Add remaining properties
        skip_keys = [
            'name', 'description', 'bacnet_address', 'modbus_address',
            'point_type', 'trend', 'encoding', 'access', 'scale',
            'offset', 'bit_index'
        ]
        for key, value in point_data.items():
            if key not in skip_keys:
                content += f'  {self._sanitize_name(key).replace("_", "")}: "{value}"\n'
        
        content += "}\n\n"
        return content

    def convert_json_to_xeto(
        self,
        json_data: Dict[str, Any],
        pdf_name: str,
        mode: str = 'simple'
    ) -> Tuple[str, str]:
        """
        Convert JSON data to Xeto library format
        
        Args:
            json_data: The JSON data to convert
            pdf_name: Name of the source PDF file
            mode: 'simple' or 'advanced' conversion mode
            
        Returns:
            Tuple of (lib_content, specs_content)
        """
        try:
            lib_content = ""
            specs_content = ""

            # Add generation timestamp
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            lib_content += f"// Generated on {generation_time}\n\n"
            specs_content += f"// Generated on {generation_time}\n\n"

            # Library Information
            lib_content += f"pragma: Lib <\n"
            lib_content += f'  doc: "{json_data.get("libname", "UnknownLib")} library"\n'
            lib_content += f'  version: "{json_data.get("version", "1.0")}"\n'
            lib_content += f"  depends: {{\n"
            lib_content += '    { lib: "sys", versions: "0.1.x" }\n'
            lib_content += '    { lib: "ph", versions: "0.1.x" }\n'
            lib_content += '    { lib: "ph.resources", versions: "0.1.x" }\n'
            lib_content += "  }\n"
            lib_content += "  org: {\n"
            lib_content += f'    dis: "{json_data.get("device_properties", {}).get("vendor_name", "Unknown")}"\n'
            lib_content += f'    uri: "{json_data.get("device_properties", {}).get("vendor_uri", "https://example.com")}"\n'
            lib_content += "  }\n"
            lib_content += ">\n\n"

            # Device Properties
            device_props = json_data.get('device', {})
            
            # Extract model numbers
            model_numbers = device_props.get('model', '').split(', ')
            model_numbers = [model.strip() for model in model_numbers if model.strip()]

            if not model_numbers:
                model_numbers = ['UnknownDevice']

            # Get manufacturer
            manufacturer = device_props.get('manufacturer', 'Unknown')

            # Flatten nested structures
            flattened_props = self._flatten_dict(device_props)

            # Create a spec for each model number
            for model in model_numbers:
                device_name = self._create_device_name(manufacturer, model)
                specs_content += f"{device_name}: Device {{\n"
                specs_content += f'  org: "{manufacturer}"\n'
                specs_content += f'  type: "{device_props.get("type", "Unknown")}"\n'

                specs_content += "  attrs: {\n"
                # Add device attributes
                for key, value in flattened_props.items():
                    if value and key not in ['manufacturer', 'model', 'type']:
                        attr_name = self._sanitize_name(key)
                        attr_name = attr_name[0].upper() + attr_name[1:] + "Attr"
                        if isinstance(value, str) and value.lower() not in ['null', 'none', '']:
                            specs_content += f'    {attr_name} : StrAttr {{ val: "{value}" }}\n'
                specs_content += f'    ModelNumberAttr : StrAttr {{ val: "{model}" }}\n'
                specs_content += "  }\n"
                
                # Handle BACnet points
                bacnet = json_data.get('bacnet', {})
                if any(bacnet.values()):
                    specs_content += "  points: {\n"
                    for obj_type, points in bacnet.items():
                        for point in points:
                            point_name = self._sanitize_name(point.get('dis', ''))
                            if point_name:
                                specs_content += f"    {point_name}\n"
                    specs_content += "  }\n"

                # Add PDF resource reference
                pdf_resource_name = self._sanitize_name(pdf_name).replace('_', '')
                specs_content += "  resources: {\n"
                specs_content += f"    {pdf_resource_name}\n"
                specs_content += "  }\n"
                
                specs_content += "}\n\n"

            # Add BACnet points
            bacnet = json_data.get('bacnet', {})
            if any(bacnet.values()):
                for obj_type, points in bacnet.items():
                    for point in points:
                        point_name = self._sanitize_name(point.get('dis', ''))
                        if point_name:
                            point_data = {
                                'bacnet_address': point.get('bacnetAddr', ''),
                                'units': point.get('units', ''),
                                'description': point.get('description', '')
                            }
                            specs_content += f"// {point_data['description']}\n"
                            specs_content += self._create_point_definition(point_name, point_data, mode)

            # Add PDF Resource
            specs_content += f"{pdf_resource_name}: ph.resources::PdfDocument {{\n"
            specs_content += f'  dis: "{pdf_name}"\n'
            specs_content += f'  uri: "{pdf_name}"\n'
            specs_content += f'  associatedEntities: {{ {", ".join(self._create_device_name(manufacturer, model) for model in model_numbers)} }}\n'
            specs_content += "}\n\n"

            return lib_content, specs_content

        except Exception as e:
            logger.error(f"Error converting JSON to Xeto: {str(e)}")
            raise
