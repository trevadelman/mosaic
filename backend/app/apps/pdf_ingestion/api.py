"""
PDF Ingestion API Module for MOSAIC

This module provides API endpoints for processing PDF files with Gemini.
"""

import os
import json
import logging
from typing import Dict, Any, List, Union
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .services.xeto_service import XetoService
from .services.json_converter import JsonConverterService
from google import genai
import uuid
import dotenv
import shutil

# Configure logging
logger = logging.getLogger("mosaic.apps.pdf_ingestion")
logger.setLevel(logging.DEBUG)

# Add file handler if it doesn't exist
if not logger.handlers:
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Add file handler
    fh = logging.FileHandler(os.path.join(log_dir, "pdf_ingestion.log"))
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

router = APIRouter(prefix="/api/apps/pdf-ingestion", tags=["applications"])

# Load environment variables
dotenv.load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Available models
MODELS = {
    "Google/Gemini-2.5": "gemini-2.5-pro-exp-03-25",
    "Google/Gemini-1.5-Pro": "models/gemini-1.5-pro"
}

# File storage paths
TEMP_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "temp_uploads")
DOCUMENT_STORAGE = os.path.join(os.path.dirname(__file__), "document_storage")

# Create directories if they don't exist
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCUMENT_STORAGE, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HVAC PDF Prompt
PDF_PROMPT = """You are a specialized PDF parsing agent for HVAC device documentation. Extract all device properties, BACnet object properties, and Modbus point properties from the provided document.

Your ONLY response should be a valid JSON object with the following structure:

{
  "device": {
    "manufacturer": "string",
    "model": "string",
    "type": "string",
    "dimensions": {"width": "string", "height": "string", "depth": "string", "units": "string"},
    "power": {"voltage": "string", "frequency": "string", "power_consumption": "string"},
    "operating_conditions": {"temp_min": "string", "temp_max": "string", "humidity_range": "string"},
    "communication_protocols": ["string"],
    "firmware_version": "string",
    "certifications": ["string"]
  },
  "bacnet": {
    "ai": [
      {
        "dis": "String Name",
        "bacnetAddr": "AI1",
        "units": "String if exists"
        "description: "String if it exists in the doc"
      }
    ],
    "ao": [
      {
        "dis": "String Name",
        "bacnetAddr": "AO1",
        "units": "String if exists"
      }
    ],
    "av": [
      {
        "dis": "String Name",
        "bacnetAddr": "AV1",
        "units": "String if exists"
      }
    ],
    "bi": [
      {
        "dis": "String Name",
        "bacnetAddr": "BI1",
        "units": "String if exists"
      }
    ],
    "bo": [
      {
        "dis": "String Name",
        "bacnetAddr": "BO1",
        "units": "String if exists"
      }
    ],
    "bv": [
      {
        "dis": "String Name",
        "bacnetAddr": "BV1",
        "units": "String if exists"
      }
    ],
    "msi": [
      {
        "dis": "String Name",
        "bacnetAddr": "MSI1",
        "units": "String if exists"
      }
    ],
    "mso": [
      {
        "dis": "String Name",
        "bacnetAddr": "MSO1",
        "units": "String if exists"
      }
    ],
    "msv": [
      {
        "dis": "String Name",
        "bacnetAddr": "MSV1",
        "units": "String if exists"
      }
    ]
  },
  "modbus_registers": [
    {
      "register_address": "string",
      "register_type": "string",
      "description": "string",
      "units": "string"
    }
  ]
}

For each BACnet object:
- The "dis" field should contain the object's name
- The "bacnetAddr" field should follow the format of object type abbreviation + instance number (e.g., "AI1", "BO3")
- The "units" field should only be included if unit information exists
- The "description" field should be pulled word for word from the doc if available. Left blank otherwise. 

Group all BACnet objects by their type (AI, AO, AV, BI, BO, BV, MSI, MSO, MSV, OTHER) into their respective arrays.

If certain properties or sections are not found in the documentation, include them as empty objects or arrays. Only output the JSON structure with no additional explanation or commentary. Do not hallucinate any values."""

# Follow-up prompt for subsequent documents
FOLLOW_UP_PROMPT = """You are a specialized PDF parsing agent for HVAC device documentation. We have already extracted information from previous documents, provided below. Your task is to enhance this information with any new details found in the current document.

EXISTING INFORMATION:
{existing_json}

Your response must be a valid JSON object with EXACTLY this structure:

{
  "device": {
    "manufacturer": "string",
    "model": "string",
    "type": "string",
    "dimensions": {"width": "string", "height": "string", "depth": "string", "units": "string"},
    "power": {"voltage": "string", "frequency": "string", "power_consumption": "string"},
    "operating_conditions": {"temp_min": "string", "temp_max": "string", "humidity_range": "string"},
    "communication_protocols": ["string"],
    "firmware_version": "string",
    "certifications": ["string"]
  },
  "bacnet": {
    "ai": [
      {
        "dis": "String Name",
        "bacnetAddr": "AI1",
        "units": "String if exists",
        "description": "String if it exists in the doc"
      }
    ],
    "ao": [{"dis": "String Name", "bacnetAddr": "AO1", "units": "String if exists"}],
    "av": [{"dis": "String Name", "bacnetAddr": "AV1", "units": "String if exists"}],
    "bi": [{"dis": "String Name", "bacnetAddr": "BI1", "units": "String if exists"}],
    "bo": [{"dis": "String Name", "bacnetAddr": "BO1", "units": "String if exists"}],
    "bv": [{"dis": "String Name", "bacnetAddr": "BV1", "units": "String if exists"}],
    "msi": [{"dis": "String Name", "bacnetAddr": "MSI1", "units": "String if exists"}],
    "mso": [{"dis": "String Name", "bacnetAddr": "MSO1", "units": "String if exists"}],
    "msv": [{"dis": "String Name", "bacnetAddr": "MSV1", "units": "String if exists"}]
  },
  "modbus_registers": [
    {
      "register_address": "string",
      "register_type": "string",
      "description": "string",
      "units": "string"
    }
  ]
}

Critical Rules:
1. Device Section:
   - Preserve ALL existing device information
   - ONLY add new information to empty fields
   - If a field has existing data, keep it unless new data is clearly more complete
   - Never remove or blank out existing fields

2. BACnet Objects:
   - Keep ALL existing BACnet objects
   - Add ANY new BACnet objects found
   - Use exact bacnetAddr format (e.g., "AI1", "BO3")
   - Include units ONLY if specifically mentioned
   - Copy descriptions word-for-word from documentation

3. Modbus Registers:
   - Keep ALL existing registers
   - Add ANY new registers found
   - Never modify existing register information
   - Add new registers with complete information only

4. Output Format:
   - Return ONLY the JSON structure
   - No additional text or explanations
   - Maintain exact field names and structure
   - Keep all arrays even if empty ([])

If certain properties or sections are not found in the new documentation, preserve the existing values. Only output the JSON structure with no additional explanation or commentary. Do not hallucinate any values."""

class JsonData(BaseModel):
    """Request model for saving JSON data"""
    manufacturer: str
    data: str = Field(..., description="JSON string to save")

class ProcessResponse(BaseModel):
    """Response model for file processing"""
    success: bool
    response: str = ""
    error: str = ""
    manufacturer: str = ""
    model: str = ""

class XetoConvertRequest(BaseModel):
    """Request model for converting JSON to Xeto"""
    json_path: str
    manufacturer: str
    model: str

class XetoCompileRequest(BaseModel):
    """Request model for compiling Xeto library"""
    lib_content: str
    specs_content: str
    manufacturer: str
    model: str

class XetoSaveRequest(BaseModel):
    """Request model for saving Xeto files"""
    lib_content: str
    specs_content: str
    manufacturer: str
    model: str

class XetoResponse(BaseModel):
    """Response model for Xeto operations"""
    success: bool
    lib_content: str = ""
    specs_content: str = ""
    output: str = ""
    error: str = ""
    paths: Dict[str, str] = {}

class ManufacturerCreate(BaseModel):
    """Request model for creating a manufacturer"""
    name: str

class ManufacturerResponse(BaseModel):
    """Response model for manufacturer operations"""
    success: bool
    name: str = ""
    error: str = ""

class DeviceInfo(BaseModel):
    """Model for device information"""
    name: str
    manufacturer: str
    type: str  # 'file' or 'directory'
    path: str

class DeviceList(BaseModel):
    """Response model for device listing"""
    devices: List[DeviceInfo]

def get_manufacturers() -> List[str]:
    """Get list of all manufacturers"""
    try:
        return [d for d in os.listdir(DOCUMENT_STORAGE) 
                if os.path.isdir(os.path.join(DOCUMENT_STORAGE, d))]
    except Exception:
        return []

def get_device_files(manufacturer: str, device: str) -> List[Dict[str, str]]:
    """Get list of files for a device"""
    try:
        device_dir = os.path.join(DOCUMENT_STORAGE, manufacturer, device)
        if not os.path.exists(device_dir):
            return []

        files = []
        
        # Special handling for xeto directory
        if manufacturer == 'xeto':
            # List all files and directories recursively
            for root, dirs, filenames in os.walk(device_dir):
                # Add directories
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    files.append({
                        "name": d,
                        "type": "directory",
                        "path": os.path.relpath(dir_path, os.path.join(DOCUMENT_STORAGE, manufacturer))
                    })
                # Add files
                for f in filenames:
                    file_path = os.path.join(root, f)
                    files.append({
                        "name": f,
                        "type": "file",
                        "path": os.path.relpath(file_path, os.path.join(DOCUMENT_STORAGE, manufacturer))
                    })
            return files
            
        # Regular device handling
        json_path = os.path.join(device_dir, "productInfo.json")
        if os.path.exists(json_path):
            files.append({
                "name": "productInfo.json",
                "type": "file",
                "path": os.path.relpath(json_path, os.path.join(DOCUMENT_STORAGE, manufacturer))
            })

        # Add raw_docs directory and its contents if they exist
        raw_docs_dir = os.path.join(device_dir, "raw_docs")
        if os.path.exists(raw_docs_dir):
            files.append({
                "name": "raw_docs",
                "type": "directory",
                "path": os.path.relpath(raw_docs_dir, os.path.join(DOCUMENT_STORAGE, manufacturer))
            })
            for pdf in os.listdir(raw_docs_dir):
                if pdf.endswith('.pdf'):
                    files.append({
                        "name": pdf,
                        "type": "file",
                        "path": os.path.relpath(os.path.join(raw_docs_dir, pdf), 
                                              os.path.join(DOCUMENT_STORAGE, manufacturer))
                    })
        return files
    except Exception:
        return []

def get_devices(manufacturer: str) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """Get list of devices and their files for a manufacturer"""
    try:
        manufacturer_dir = os.path.join(DOCUMENT_STORAGE, manufacturer)
        if not os.path.exists(manufacturer_dir):
            return []
        
        devices = []
        
        # Special handling for xeto directory - just recursively list all files and directories
        if manufacturer == 'xeto':
            for root, dirs, files in os.walk(manufacturer_dir):
                # Add directories
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    devices.append({
                        "name": d,
                        "type": "directory",
                        "path": os.path.relpath(dir_path, os.path.join(DOCUMENT_STORAGE, manufacturer))
                    })
                # Add files
                for f in files:
                    file_path = os.path.join(root, f)
                    devices.append({
                        "name": f,
                        "type": "file",
                        "path": os.path.relpath(file_path, os.path.join(DOCUMENT_STORAGE, manufacturer))
                    })
            return devices
        
        # Regular manufacturer handling
        for device in os.listdir(manufacturer_dir):
            device_path = os.path.join(manufacturer_dir, device)
            if os.path.isdir(device_path):
                files = get_device_files(manufacturer, device)
                devices.append({
                    "name": device,
                    "type": "directory",
                    "files": files
                })
        return devices
    except Exception:
        return []

async def process_file_with_gemini(file_path: str, prompt: str, model_name: str) -> Dict[str, Any]:
    """Process a file with the Gemini model"""
    try:
        # Upload the file to Gemini API
        try:
            file_ref = client.files.upload(file=file_path)
        except Exception as e:
            logger.error(f"Error uploading file to Gemini: {str(e)}", exc_info=True)
            raise
        
        # Generate content with the file reference
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt, file_ref]
            )
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}", exc_info=True)
            raise
        
        # Clean the response text to remove markdown code block syntax
        try:
            response_text = response.text
            
            # Remove markdown code block syntax if present
            if response_text.startswith("```json") or response_text.startswith("```JSON"):
                start_idx = response_text.find("\n")
                if start_idx != -1:
                    end_idx = response_text.rfind("```")
                    if end_idx != -1:
                        response_text = response_text[start_idx + 1:end_idx].strip()
        
            # Parse the response to extract manufacturer and model
            try:
                parsed = json.loads(response_text)
                device_info = parsed.get("device", {})
                
                result = {
                    "success": True,
                    "response": response_text,
                    "manufacturer": device_info.get("manufacturer", ""),
                    "model": device_info.get("model", "")
                }
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                return {
                    "success": True,
                    "response": response_text,
                    "manufacturer": "",
                    "model": ""
                }
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}", exc_info=True)
            raise
    except Exception as e:
        logger.error(f"Unexpected error in process_file_with_gemini: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "manufacturer": "",
            "model": ""
        }

@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers():
    """List all manufacturers"""
    return get_manufacturers()

@router.post("/manufacturers", response_model=ManufacturerResponse)
async def create_manufacturer(data: ManufacturerCreate):
    """Create a new manufacturer directory"""
    try:
        manufacturer_dir = os.path.join(DOCUMENT_STORAGE, data.name)
        if os.path.exists(manufacturer_dir):
            return ManufacturerResponse(
                success=False,
                error=f"Manufacturer '{data.name}' already exists"
            )
        
        os.makedirs(manufacturer_dir)
        return ManufacturerResponse(success=True, name=data.name)
    except Exception as e:
        return ManufacturerResponse(success=False, error=str(e))

@router.get("/manufacturers/{manufacturer}/devices", response_model=DeviceList)
async def list_devices(manufacturer: str):
    """List all devices and their files for a manufacturer"""
    devices = []
    device_list = get_devices(manufacturer)
    
    # Special handling for xeto directory
    if manufacturer == 'xeto':
        for device in device_list:
            # Add the directory itself
            devices.append(DeviceInfo(
                name=device["name"],
                manufacturer=manufacturer,
                type=device["type"],
                path=device["path"]
            ))
            # Add its contents
            for file in device.get("files", []):
                devices.append(DeviceInfo(
                    name=file["name"],
                    manufacturer=manufacturer,
                    type=file["type"],
                    path=file["path"]
                ))
    else:
        # Regular manufacturer handling
        for device in device_list:
            # Add the device directory
            devices.append(DeviceInfo(
                name=device["name"],
                manufacturer=manufacturer,
                type="directory",
                path=device["name"]
            ))
            # Add all files
            for file in device["files"]:
                devices.append(DeviceInfo(
                    name=file["name"],
                    manufacturer=manufacturer,
                    type=file["type"],
                    path=file["path"]
                ))
    return DeviceList(devices=devices)

@router.post("/save", response_model=ProcessResponse)
async def save_json(data: JsonData) -> ProcessResponse:
    """Save edited JSON data"""
    try:
        # Validate JSON
        json_data = json.loads(data.data)
        device_info = json_data.get("device", {})
        model = device_info.get("model", "")

        if not model:
            raise HTTPException(status_code=400, detail="JSON must contain device.model")

        # Create device directory
        device_dir = os.path.join(DOCUMENT_STORAGE, data.manufacturer, model)
        os.makedirs(device_dir, exist_ok=True)

        # Save the JSON file
        json_path = os.path.join(device_dir, "productInfo.json")
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)

        return ProcessResponse(
            success=True,
            manufacturer=device_info.get("manufacturer", ""),
            model=model
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        logger.error(f"Error in process_pdf endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manufacturers/{manufacturer}/devices/{device}/info")
async def get_device_info(manufacturer: str, device: str):
    """Get device information JSON"""
    try:
        json_path = os.path.join(DOCUMENT_STORAGE, manufacturer, device, "productInfo.json")
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Device information not found")

        with open(json_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize services
xeto_service = XetoService()
json_converter = JsonConverterService()

@router.post("/convert-to-xeto", response_model=XetoResponse)
async def convert_to_xeto(request: XetoConvertRequest) -> XetoResponse:
    """Convert JSON data to Xeto format"""
    try:
        # Resolve JSON path relative to DOCUMENT_STORAGE
        json_path = os.path.join(DOCUMENT_STORAGE, request.json_path)
        
        # Check if file exists
        if not os.path.exists(json_path):
            return XetoResponse(
                success=False,
                error=f"JSON file not found. Please save the JSON data first."
            )
            
        try:
            # Read JSON file
            with open(json_path, 'r') as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            return XetoResponse(
                success=False,
                error="Invalid JSON file format"
            )
        
        # Get PDF name from JSON path
        pdf_name = os.path.basename(json_path).replace('.json', '.pdf')
        
        # Convert JSON to Xeto
        lib_content, specs_content = json_converter.convert_json_to_xeto(
            json_data,
            pdf_name,
            mode='simple'  # Start with simple mode
        )
        
        return XetoResponse(
            success=True,
            lib_content=lib_content,
            specs_content=specs_content
        )
        
    except Exception as e:
        logger.error(f"Error converting to Xeto: {str(e)}")
        return XetoResponse(
            success=False,
            error=str(e)
        )

@router.post("/compile-xeto", response_model=XetoResponse)
async def compile_xeto(request: XetoCompileRequest) -> XetoResponse:
    """Compile Xeto library"""
    try:
        # Create library name
        lib_name = f"{request.manufacturer}.{request.model}".lower()
        lib_name = "".join(c if c.isalnum() or c == '.' else '_' for c in lib_name)
        
        # Compile library with content directly
        compile_result = await xeto_service.compile_library(
            lib_name,
            lib_content=request.lib_content,
            specs_content=request.specs_content
        )
        
        # Always include output if available
        response = XetoResponse(
            success=compile_result["success"],
            output=compile_result.get("output", "")
        )
        
        # Add error if compilation failed
        if not compile_result["success"]:
            response.error = compile_result["error"]
        
        return response
        
    except Exception as e:
        logger.error(f"Error compiling Xeto: {str(e)}")
        return XetoResponse(
            success=False,
            error=str(e)
        )

@router.post("/save-xeto", response_model=XetoResponse)
async def save_xeto(request: XetoSaveRequest) -> XetoResponse:
    """Save Xeto library files"""
    try:
        result = await xeto_service.save_library_files(
            request.manufacturer,
            request.model,
            request.lib_content,
            request.specs_content
        )
        
        if not result["success"]:
            return XetoResponse(
                success=False,
                error=result["error"]
            )
        
        return XetoResponse(
            success=True,
            paths=result["paths"]
        )
        
    except Exception as e:
        logger.error(f"Error saving Xeto files: {str(e)}")
        return XetoResponse(
            success=False,
            error=str(e)
        )

@router.get("/manufacturers/{manufacturer}/{path:path}")
async def get_file(manufacturer: str, path: str):
    """Get a file from the document storage"""
    try:
        file_path = os.path.join(DOCUMENT_STORAGE, manufacturer, path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Handle different file types
        if file_path.endswith('.pdf'):
            return FileResponse(
                file_path,
                media_type='application/pdf',
                filename=os.path.basename(file_path),
                headers={"Content-Disposition": "inline"}
            )
        elif file_path.endswith('.xeto') or file_path.endswith('.xetolib'):
            # Return xeto files as text
            with open(file_path, 'r') as f:
                content = f.read()
            return Response(content=content, media_type='text/plain')

        raise HTTPException(status_code=400, detail="Invalid file type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=ProcessResponse)
async def process_pdf(
    files: List[UploadFile] = File(...),
    manufacturer: str = Body(...)
) -> ProcessResponse:
    """Process multiple PDF files and extract combined information"""
    # Validate files
    for file in files:
        if not file.filename or not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Verify manufacturer exists
    if not os.path.exists(os.path.join(DOCUMENT_STORAGE, manufacturer)):
        raise HTTPException(status_code=404, detail=f"Manufacturer '{manufacturer}' not found")
    
    try:
        # Process files sequentially
        result = await process_multiple_pdfs(files, manufacturer)
        
        return ProcessResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_multiple_pdfs(files: List[UploadFile], manufacturer: str) -> Dict[str, Any]:
    """Process multiple PDF files sequentially, combining their information"""
    temp_filepaths = []
    try:
        logger.info(f"Starting to process {len(files)} files for manufacturer {manufacturer}")
        
        # Save all files temporarily
        for i, file in enumerate(files, 1):
            logger.info(f"Processing file {i}/{len(files)}: {file.filename}")
            temp_filename = f"{uuid.uuid4()}.pdf"
            temp_filepath = os.path.join(TEMP_UPLOAD_FOLDER, temp_filename)
            temp_filepaths.append((temp_filepath, file.filename))
            
            try:
                with open(temp_filepath, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
            except Exception as e:
                logger.error(f"Error saving file {file.filename} to temp location: {str(e)}", exc_info=True)
                raise
        
        # Process first file with original prompt
        first_file_path = temp_filepaths[0][0]
        logger.info(f"Processing first file {temp_filepaths[0][1]} with original prompt")
        try:
            result = await process_file_with_gemini(
                first_file_path,
                PDF_PROMPT,
                MODELS["Google/Gemini-2.5"]
            )
        except Exception as e:
            logger.error(f"Error processing first file: {str(e)}", exc_info=True)
            raise
        
        if not result["success"]:
            logger.error(f"Failed to process first file: {result.get('error', 'Unknown error')}")
            return result
        
        logger.info("Successfully processed first file")
        
        # Process remaining files with context
        for i, (temp_filepath, original_filename) in enumerate(temp_filepaths[1:], 2):
            logger.info(f"Processing file {i}/{len(files)}: {original_filename}")
            try:
                # Create context-aware prompt with escaped JSON template
                follow_up_prompt = FOLLOW_UP_PROMPT.replace(
                    "{existing_json}",
                    result["response"]
                )
                
                # Process with context
                new_result = await process_file_with_gemini(
                    temp_filepath,
                    follow_up_prompt,
                    MODELS["Google/Gemini-2.5"]
                )
                
                if new_result["success"]:
                    result = new_result
                    logger.info(f"Successfully processed file {i}/{len(files)}")
                else:
                    # Log error but continue processing
                    logger.error(f"Error processing file {original_filename}: {new_result['error']}")
            except Exception as e:
                logger.error(f"Unexpected error processing file {original_filename}: {str(e)}", exc_info=True)
                # Continue processing remaining files
        
        if result["success"] and result["manufacturer"] and result["model"]:
            logger.info(f"Processing successful. Saving results for model: {result['model']}")
            # Create device directory structure
            device_dir = os.path.join(DOCUMENT_STORAGE, manufacturer, result["model"])
            raw_docs_dir = os.path.join(device_dir, "raw_docs")
            os.makedirs(raw_docs_dir, exist_ok=True)
            
            # Save the final JSON response
            json_path = os.path.join(device_dir, "productInfo.json")
            try:
                with open(json_path, "w") as f:
                    json.dump(json.loads(result["response"]), f, indent=2)
                logger.info(f"Successfully saved JSON to {json_path}")
            except Exception as e:
                logger.error(f"Error saving JSON file: {str(e)}", exc_info=True)
                raise
            
            # Copy all PDFs to raw_docs
            logger.info("Copying PDFs to raw_docs directory")
            for temp_filepath, original_filename in temp_filepaths:
                # Handle filename conflicts
                pdf_filename = original_filename
                pdf_path = os.path.join(raw_docs_dir, pdf_filename)
                counter = 1
                
                while os.path.exists(pdf_path):
                    name, ext = os.path.splitext(original_filename)
                    pdf_filename = f"{name}_{counter}{ext}"
                    pdf_path = os.path.join(raw_docs_dir, pdf_filename)
                    counter += 1
                
                try:
                    shutil.copy2(temp_filepath, pdf_path)
                except Exception as e:
                    logger.error(f"Error copying file {original_filename}: {str(e)}", exc_info=True)
                    raise
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in process_multiple_pdfs: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up temporary files
        logger.info("Cleaning up temporary files")
        for temp_filepath, original_filename in temp_filepaths:
            try:
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
            except Exception as e:
                logger.error(f"Error removing temporary file {temp_filepath}: {str(e)}", exc_info=True)
