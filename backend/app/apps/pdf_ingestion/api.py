"""
PDF Ingestion API Module for MOSAIC

This module provides API endpoints for processing PDF files with Gemini.
"""

import os
import json
from typing import Dict, Any, List, Union
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai
import uuid
import dotenv
import shutil

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
        # Add productInfo.json if it exists
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
        file_ref = client.files.upload(file=file_path)
        
        # Generate content with the file reference
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, file_ref]
        )
        
        # Clean the response text to remove markdown code block syntax
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
            return {
                "success": True,
                "response": response_text,
                "manufacturer": device_info.get("manufacturer", ""),
                "model": device_info.get("model", "")
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "response": response_text,
                "manufacturer": "",
                "model": ""
            }
    except Exception as e:
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
    for device in get_devices(manufacturer):
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

@router.get("/manufacturers/{manufacturer}/{path:path}")
async def get_file(manufacturer: str, path: str):
    """Get a file from the document storage"""
    try:
        file_path = os.path.join(DOCUMENT_STORAGE, manufacturer, path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # For PDF files, return them directly
        if file_path.endswith('.pdf'):
            return FileResponse(
                file_path,
                media_type='application/pdf',
                filename=os.path.basename(file_path),
                headers={"Content-Disposition": "inline"}
            )

        raise HTTPException(status_code=400, detail="Invalid file type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=ProcessResponse)
async def process_pdf(
    file: UploadFile = File(...),
    manufacturer: str = Body(...)
) -> ProcessResponse:
    """Process a PDF file and extract information"""
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Verify manufacturer exists
    if not os.path.exists(os.path.join(DOCUMENT_STORAGE, manufacturer)):
        raise HTTPException(status_code=404, detail=f"Manufacturer '{manufacturer}' not found")
    
    try:
        # Create a unique filename
        temp_filename = f"{uuid.uuid4()}.pdf"
        temp_filepath = os.path.join(TEMP_UPLOAD_FOLDER, temp_filename)
        
        # Save the uploaded file temporarily
        with open(temp_filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file
        result = await process_file_with_gemini(
            temp_filepath, 
            PDF_PROMPT, 
            MODELS["Google/Gemini-2.5"]
        )
        
        if result["success"] and result["manufacturer"] and result["model"]:
            # Create device directory structure
            device_dir = os.path.join(DOCUMENT_STORAGE, manufacturer, result["model"])
            raw_docs_dir = os.path.join(device_dir, "raw_docs")
            os.makedirs(raw_docs_dir, exist_ok=True)
            
            # Save the JSON response
            json_path = os.path.join(device_dir, "productInfo.json")
            with open(json_path, "w") as f:
                json.dump(json.loads(result["response"]), f, indent=2)
            
            # Move the PDF to raw_docs directory with original filename
            # If file exists, append a number
            pdf_filename = file.filename
            pdf_path = os.path.join(raw_docs_dir, pdf_filename)
            counter = 1
            
            # If file exists, append a number until we find a unique name
            while os.path.exists(pdf_path):
                name, ext = os.path.splitext(file.filename)
                pdf_filename = f"{name}_{counter}{ext}"
                pdf_path = os.path.join(raw_docs_dir, pdf_filename)
                counter += 1
            
            shutil.copy2(temp_filepath, pdf_path)  # Use copy2 to preserve metadata
        
        # Delete the temporary file
        os.remove(temp_filepath)
        
        return ProcessResponse(**result)
        
    except Exception as e:
        # Ensure temp file is deleted even if processing fails
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=500, detail=str(e))
