"""
Xeto Service Module

This module provides a service layer for interacting with Xeto tools through Node.js.
It handles initialization, compilation, and management of Xeto libraries.
"""

import os
import json
import shutil
import asyncio
import logging
from typing import Dict, Any, Tuple, Optional

from ..utils.file_utils import FileSystemManager

logger = logging.getLogger("mosaic.apps.pdf_ingestion")

class XetoService:
    """Service for managing Xeto library operations"""
    
    def __init__(self):
        """Initialize the Xeto service with required paths"""
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        # Set up paths
        self.document_storage = os.path.join(self.base_path, "document_storage")
        self.xeto_root = os.path.join(self.base_path, ".xeto")  # Hidden directory for xeto tooling
        
        # Xeto directories in document_storage
        self.xeto_path = os.path.join(self.document_storage, "xeto")  # Root for xeto files
        self.src_path = os.path.join(self.xeto_path, "src", "xeto")  # xeto/src/xeto for source files
        self.lib_path = os.path.join(self.xeto_path, "lib")  # xeto/lib for compiled output
        
        # Initialize file system manager
        self.fs_manager = FileSystemManager(self.base_path)
        
        # Ensure all required directories exist
        os.makedirs(self.src_path, exist_ok=True)
        os.makedirs(self.lib_path, exist_ok=True)

    async def _run_command(self, command: str) -> Tuple[str, str, int]:
        """
        Run a shell command asynchronously and return its output
        
        Args:
            command: The shell command to execute
            
        Returns:
            Tuple containing (stdout, stderr, return_code)
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        return (
            stdout.decode() if stdout else "",
            stderr.decode() if stderr else "",
            process.returncode
        )

    def _resolve_json_path(self, json_path: str) -> str:
        """
        Resolve a relative JSON path to an absolute path
        
        Args:
            json_path: Relative path from document_storage
            
        Returns:
            Absolute path to the JSON file
        """
        # If path starts with document_storage, treat it as relative to base_path
        if json_path.startswith("document_storage/"):
            return os.path.join(self.base_path, json_path)
        return json_path

    async def init_library(self, manufacturer: str, model: str) -> Dict[str, Any]:
        """
        Initialize a new Xeto library for a device
        
        Args:
            manufacturer: The device manufacturer name
            model: The device model name
            
        Returns:
            Dict containing operation result
        """
        try:
            # Create library name in format manufacturer.model
            lib_name = f"{manufacturer}.{model}".lower()
            lib_name = "".join(c if c.isalnum() or c == '.' else '_' for c in lib_name)
            
            # Initialize library using xeto init
            command = f"cd {self.xeto_root} && npx xeto init -dir {self.src_path} -noconfirm {lib_name}"
            stdout, stderr, return_code = await self._run_command(command)
            
            if return_code != 0:
                logger.error(f"Failed to initialize Xeto library: {stderr}")
                return {
                    "success": False,
                    "error": f"Failed to initialize Xeto library: {stderr}"
                }
            
            # Create lib directory for compiled output
            lib_dir = os.path.join(self.lib_path, lib_name)
            os.makedirs(lib_dir, exist_ok=True)
            
            # Get build directory path
            build_dir = os.path.join(self.src_path, lib_name)
            
            logger.info(f"Successfully initialized Xeto library: {lib_name}")
            return {
                "success": True,
                "lib_name": lib_name,
                "src_path": build_dir
            }
            
        except Exception as e:
            logger.error(f"Error initializing Xeto library: {str(e)}")
            return {
                "success": False,
                "error": f"Error initializing Xeto library: {str(e)}"
            }

    async def compile_library(
        self,
        lib_name: str,
        lib_content: str = None,
        specs_content: str = None
    ) -> Dict[str, Any]:
        """
        Compile a Xeto library
        
        Args:
            lib_name: The name of the library to compile
            lib_content: Optional content for lib.xeto
            specs_content: Optional content for specs.xeto
            
        Returns:
            Dict containing compilation result
        """
        try:
            # Split lib_name into manufacturer and model
            manufacturer, model = lib_name.split('.')
            
            # Initialize library if it doesn't exist
            build_dir = os.path.join(self.src_path, lib_name)
            if not os.path.exists(build_dir):
                init_result = await self.init_library(manufacturer, model)
                if not init_result["success"]:
                    return init_result
            
            # Get stored files from file manager if no content provided
            if lib_content is None or specs_content is None:
                files = self.fs_manager.get_device_files(manufacturer, model)
                
                if not files.get("xeto"):
                    return {
                        "success": False,
                        "error": "Xeto files not found"
                    }
            
            # Write or copy lib.xeto
            build_lib = os.path.join(build_dir, "lib.xeto")
            if lib_content is not None:
                with open(build_lib, 'w') as f:
                    f.write(lib_content)
            else:
                shutil.copy2(files["xeto"]["lib"], build_lib)
            
            # Write or copy specs.xeto
            build_specs = os.path.join(build_dir, "specs.xeto")
            if specs_content is not None:
                with open(build_specs, 'w') as f:
                    f.write(specs_content)
            else:
                shutil.copy2(files["xeto"]["specs"], build_specs)
            
            # Run xeto build command from .xeto directory where xeto.props is located
            command = f"cd {self.xeto_root} && npx xeto build {lib_name}"
            stdout, stderr, return_code = await self._run_command(command)
            
            # Check both return code and output for errors
            has_error = return_code != 0 or "ERROR:" in stdout or "ERROR:" in stderr
            
            if has_error:
                error_msg = stderr if stderr else stdout
                logger.error(f"Failed to compile Xeto library: {error_msg}")
                return {
                    "success": False,
                    "error": f"Compilation failed: {error_msg}",
                    "output": stdout + stderr
                }
            
            logger.info(f"Successfully compiled Xeto library: {lib_name}")
            return {
                "success": True,
                "output": stdout + stderr,
                "lib_path": os.path.join(self.lib_path, lib_name)
            }
            
        except Exception as e:
            logger.error(f"Error compiling Xeto library: {str(e)}")
            return {
                "success": False,
                "error": f"Error compiling Xeto library: {str(e)}"
            }

    async def save_library_files(
        self,
        manufacturer: str,
        model: str,
        lib_content: str,
        specs_content: str,
        overwrite: bool = True
    ) -> Dict[str, Any]:
        """
        Save Xeto library files to the appropriate location
        
        Args:
            manufacturer: The device manufacturer name
            model: The device model name
            lib_content: Content for lib.xeto
            specs_content: Content for specs.xeto
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dict containing save operation result
        """
        try:
            # Use file system manager to save files
            lib_path, specs_path = self.fs_manager.save_xeto_files(
                manufacturer,
                model,
                lib_content,
                specs_content,
                overwrite=overwrite
            )
            
            logger.info(f"Successfully saved Xeto files for {manufacturer} {model}")
            return {
                "success": True,
                "paths": {
                    "lib": lib_path,
                    "specs": specs_path
                }
            }
            
        except FileExistsError as e:
            logger.warning(f"Xeto files already exist for {manufacturer} {model}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error saving Xeto files: {str(e)}")
            return {
                "success": False,
                "error": f"Error saving Xeto files: {str(e)}"
            }

    async def read_library_files(
        self,
        manufacturer: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Read existing Xeto library files
        
        Args:
            manufacturer: The device manufacturer name
            model: The device model name
            
        Returns:
            Dict containing file contents or error
        """
        try:
            # Get device files using file system manager
            files = self.fs_manager.get_device_files(manufacturer, model)
            
            if not files.get("xeto"):
                return {
                    "success": False,
                    "error": "Xeto files not found"
                }
            
            lib_path = files["xeto"].get("lib")
            specs_path = files["xeto"].get("specs")
            
            if not lib_path or not specs_path:
                return {
                    "success": False,
                    "error": "Incomplete Xeto files found"
                }
            
            # Read files
            with open(lib_path, 'r') as f:
                lib_content = f.read()
            
            with open(specs_path, 'r') as f:
                specs_content = f.read()
            
            return {
                "success": True,
                "contents": {
                    "lib": lib_content,
                    "specs": specs_content
                }
            }
            
        except Exception as e:
            logger.error(f"Error reading Xeto files: {str(e)}")
            return {
                "success": False,
                "error": f"Error reading Xeto files: {str(e)}"
            }

    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        try:
            self.fs_manager.cleanup_temp_files()
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
