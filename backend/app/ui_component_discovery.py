"""
UI Component Discovery Module for MOSAIC

This module provides functionality for dynamically discovering and registering UI components.
It scans the UI components directory for Python files, extracts UI component classes,
and registers them automatically during startup.
"""

import os
import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Any, Callable, Optional, Type
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.ui_component_discovery")

# Try to import the UI component registry and base classes
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.base import UIComponent, ui_component_registry
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.base import UIComponent, ui_component_registry
    from backend.agents.base import agent_registry

class UIComponentDiscovery:
    """
    Class for discovering and registering UI components dynamically.
    """
    
    def __init__(self, ui_components_package: str = "backend.ui.components"):
        """
        Initialize the UI component discovery system.
        
        Args:
            ui_components_package: The package path where UI components are located
        """
        self.ui_components_package = ui_components_package
        self.discovered_components: Dict[str, Dict[str, Any]] = {}
        
        # Try to import the UI components package
        try:
            self.ui_components_module = importlib.import_module(ui_components_package)
            self.ui_components_path = os.path.dirname(self.ui_components_module.__file__)
            logger.debug(f"UI components module found at: {self.ui_components_path}")
            
            # Create the directory if it doesn't exist
            os.makedirs(self.ui_components_path, exist_ok=True)
            
        except ImportError:
            logger.error(f"Could not import UI components package: {ui_components_package}")
            self.ui_components_module = None
            self.ui_components_path = None
    
    def discover_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all UI component modules in the UI components package.
        
        Returns:
            A dictionary mapping component names to their metadata
        """
        if not self.ui_components_module:
            logger.error("UI components module not found, cannot discover components")
            return {}
        
        logger.info(f"Discovering UI components in package: {self.ui_components_package}")
        
        # Discover UI components
        if os.path.exists(self.ui_components_path):
            logger.info(f"Discovering UI components in: {self.ui_components_path}")
            self._discover_components_in_directory(self.ui_components_path, self.ui_components_package)
        
        return self.discovered_components
    
    def _find_component_classes(self, module) -> Dict[str, Type[UIComponent]]:
        """
        Find all UI component classes in a module that inherit from UIComponent.
        
        Args:
            module: The module to search
            
        Returns:
            A dictionary mapping class names to class objects
        """
        component_classes = {}
        
        for name, obj in inspect.getmembers(module):
            # Check if it's a class that inherits from UIComponent
            if (inspect.isclass(obj) and 
                issubclass(obj, UIComponent) and 
                obj != UIComponent):
                
                # Skip abstract classes (those with abstract methods)
                if not any(inspect.isabstract(method) for _, method in inspect.getmembers(obj, predicate=inspect.isfunction)):
                    component_classes[name] = obj
                    logger.debug(f"Found UI component class: {name}")
        
        return component_classes
    
    def _extract_component_metadata(self, module, component_classes: Dict[str, Type[UIComponent]]) -> Dict[str, Any]:
        """
        Extract metadata from UI component classes.
        
        Args:
            module: The module containing the component classes
            component_classes: A dictionary mapping class names to class objects
            
        Returns:
            A dictionary containing component metadata
        """
        metadata = {}
        
        # Try to extract metadata from the module docstring
        if module.__doc__:
            metadata["description"] = module.__doc__.strip()
        
        # Extract metadata from the first component class
        if component_classes:
            first_class_name = next(iter(component_classes))
            first_class = component_classes[first_class_name]
            
            # Get the default name from the class
            if hasattr(first_class, "name"):
                metadata["name"] = getattr(first_class, "name")
            else:
                # Extract name from the class name
                name = first_class_name.lower()
                if name.endswith("component"):
                    name = name[:-9]  # Remove "component" suffix
                metadata["name"] = name
            
            # Get the description from the class docstring
            if first_class.__doc__:
                metadata["description"] = first_class.__doc__.strip()
            
            # Try to extract required features from class attributes
            if hasattr(first_class, "required_features"):
                metadata["required_features"] = getattr(first_class, "required_features")
            else:
                metadata["required_features"] = []
        
        return metadata
    
    def _discover_components_in_directory(self, directory_path: str, package_prefix: str) -> None:
        """
        Discover UI components in a specific directory.
        
        Args:
            directory_path: The directory path to search
            package_prefix: The package prefix for importing modules
        """
        # Walk through the directory and find all Python modules
        for _, name, is_pkg in pkgutil.iter_modules([directory_path]):
            # Skip __pycache__ and other special directories
            if name.startswith("__"):
                continue
            
            # Skip mock implementations
            if name.startswith("mock_"):
                logger.debug(f"Skipping mock implementation: {name}")
                continue
            
            # Try to import the module
            module_name = f"{package_prefix}.{name}"
            try:
                module = importlib.import_module(module_name)
                logger.debug(f"Examining module: {module_name}")
                
                # Look for component classes that inherit from UIComponent
                component_classes = self._find_component_classes(module)
                
                if component_classes:
                    # Extract metadata from the component classes
                    metadata = self._extract_component_metadata(module, component_classes)
                    
                    # Store the discovered component
                    self.discovered_components[name] = {
                        "module": module,
                        "classes": component_classes,
                        "metadata": metadata
                    }
                    
                    logger.info(f"Discovered UI component: {name} with {len(component_classes)} classes")
                else:
                    logger.debug(f"No UI component classes found in module: {module_name}")
            
            except ImportError as e:
                logger.error(f"Error importing module {module_name}: {str(e)}")
    
    def register_components(self) -> Dict[str, Any]:
        """
        Register all discovered UI components with the UI component registry.
        
        Returns:
            A dictionary mapping component IDs to component instances
        """
        registered_components = {}
        
        logger.info(f"Registering {len(self.discovered_components)} UI components")
        
        # Instantiate and register each component class
        for module_name, module_data in self.discovered_components.items():
            for class_name, component_class in module_data["classes"].items():
                try:
                    logger.debug(f"Instantiating UI component class: {class_name}")
                    
                    # Skip classes that start with "Mock"
                    if class_name.startswith("Mock"):
                        logger.debug(f"Skipping mock component class: {class_name}")
                        continue
                    
                    # Instantiate the component
                    component = component_class()
                    
                    # Register the component with the UI component registry
                    ui_component_registry.register(component)
                    
                    # Store the registered component
                    registered_components[component.component_id] = component
                    
                    logger.info(f"Successfully registered UI component: {component.name} (ID: {component.component_id})")
                
                except Exception as e:
                    logger.error(f"Error registering UI component class {class_name}: {str(e)}")
        
        return registered_components


# Function to discover and register all UI components
def discover_and_register_components() -> Dict[str, Any]:
    """
    Discover and register all UI components.
    
    Returns:
        A dictionary mapping component IDs to their instances
    """
    # Create the UI component discovery system
    discovery = UIComponentDiscovery()
    
    # Discover all UI components
    discovery.discover_components()
    
    # Register all UI components
    registered_components = discovery.register_components()
    
    return registered_components
