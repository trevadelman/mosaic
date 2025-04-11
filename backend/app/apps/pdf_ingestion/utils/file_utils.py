"""
File System Utilities for PDF Ingestion App

This module provides utilities for managing file system operations,
particularly for handling Xeto file storage and cleanup.
"""

import os
import shutil
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger("mosaic.apps.pdf_ingestion")

class FileSystemManager:
    """Manages file system operations for the PDF ingestion app"""
    
    def __init__(self, base_path: str):
        """
        Initialize the file system manager
        
        Args:
            base_path: Base directory for all file operations
        """
        self.base_path = base_path
        self.document_storage = os.path.join(base_path, "document_storage")
        
    def ensure_device_directories(
        self,
        manufacturer: str,
        model: str
    ) -> Dict[str, str]:
        """
        Ensure all required directories exist for a device
        
        Args:
            manufacturer: Device manufacturer name
            model: Device model name
            
        Returns:
            Dictionary of created paths
        """
        try:
            # Create main paths
            device_dir = os.path.join(self.document_storage, manufacturer, model)
            raw_docs_dir = os.path.join(device_dir, "raw_docs")
            xeto_dir = os.path.join(device_dir, "xeto")
            
            # Create all directories
            os.makedirs(raw_docs_dir, exist_ok=True)
            os.makedirs(xeto_dir, exist_ok=True)
            
            return {
                "device": device_dir,
                "raw_docs": raw_docs_dir,
                "xeto": xeto_dir
            }
            
        except Exception as e:
            logger.error(f"Error creating device directories: {str(e)}")
            raise

    def save_xeto_files(
        self,
        manufacturer: str,
        model: str,
        lib_content: str,
        specs_content: str,
        overwrite: bool = False
    ) -> Tuple[str, str]:
        """
        Save Xeto library files
        
        Args:
            manufacturer: Device manufacturer name
            model: Device model name
            lib_content: Content for lib.xeto
            specs_content: Content for specs.xeto
            overwrite: Whether to overwrite existing files
            
        Returns:
            Tuple of (lib_path, specs_path)
        """
        try:
            # Ensure directories exist
            paths = self.ensure_device_directories(manufacturer, model)
            xeto_dir = paths["xeto"]
            
            # Create file paths
            lib_path = os.path.join(xeto_dir, "lib.xeto")
            specs_path = os.path.join(xeto_dir, "specs.xeto")
            
            # Check for existing files
            if not overwrite:
                if os.path.exists(lib_path) or os.path.exists(specs_path):
                    raise FileExistsError(
                        "Xeto files already exist. Set overwrite=True to replace."
                    )
            
            # Save files
            with open(lib_path, "w") as f:
                f.write(lib_content)
            
            with open(specs_path, "w") as f:
                f.write(specs_content)
            
            return lib_path, specs_path
            
        except Exception as e:
            logger.error(f"Error saving Xeto files: {str(e)}")
            raise

    def cleanup_temp_files(self, older_than_hours: int = 24) -> None:
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Remove files older than this many hours
        """
        try:
            import time
            current_time = time.time()
            
            # Clean up temp uploads
            temp_dir = os.path.join(self.base_path, "temp_uploads")
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isfile(filepath):
                        # Check file age
                        file_time = os.path.getmtime(filepath)
                        if (current_time - file_time) > (older_than_hours * 3600):
                            try:
                                os.remove(filepath)
                                logger.info(f"Removed old temp file: {filepath}")
                            except Exception as e:
                                logger.error(
                                    f"Error removing temp file {filepath}: {str(e)}"
                                )
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            # Don't raise the error - cleanup failures shouldn't break the app

    def get_device_files(
        self,
        manufacturer: str,
        model: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Get all files associated with a device
        
        Args:
            manufacturer: Device manufacturer name
            model: Device model name
            
        Returns:
            Dictionary of file categories and their paths
        """
        try:
            device_dir = os.path.join(self.document_storage, manufacturer, model)
            if not os.path.exists(device_dir):
                return {}
            
            result = {
                "json": {},
                "raw_docs": {},
                "xeto": {}
            }
            
            # Check for productInfo.json
            json_path = os.path.join(device_dir, "productInfo.json")
            if os.path.exists(json_path):
                result["json"]["productInfo"] = json_path
            
            # Check raw_docs directory
            raw_docs_dir = os.path.join(device_dir, "raw_docs")
            if os.path.exists(raw_docs_dir):
                for filename in os.listdir(raw_docs_dir):
                    if filename.endswith(".pdf"):
                        result["raw_docs"][filename] = os.path.join(
                            raw_docs_dir,
                            filename
                        )
            
            # Check xeto directory
            xeto_dir = os.path.join(device_dir, "xeto")
            if os.path.exists(xeto_dir):
                lib_path = os.path.join(xeto_dir, "lib.xeto")
                specs_path = os.path.join(xeto_dir, "specs.xeto")
                
                if os.path.exists(lib_path):
                    result["xeto"]["lib"] = lib_path
                if os.path.exists(specs_path):
                    result["xeto"]["specs"] = specs_path
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting device files: {str(e)}")
            return {}
