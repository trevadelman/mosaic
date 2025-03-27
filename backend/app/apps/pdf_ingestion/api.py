"""
PDF Ingestion API Module for MOSAIC

This module provides API endpoints for processing PDF files with Gemini.
"""

import os
import json
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from google import genai
import uuid
import dotenv

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

# Temporary file storage
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "temp_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
      "register_address": "string (use decimal addredss if available)",
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

class ProcessResponse(BaseModel):
    """Response model for file processing"""
    success: bool
    response: str = ""
    error: str = ""

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
        
        return {
            "success": True,
            "response": response_text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/process", response_model=ProcessResponse)
async def process_pdf(file: UploadFile = File(...)) -> ProcessResponse:
    """Process a PDF file and extract information"""
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Create a unique filename
        temp_filename = f"{uuid.uuid4()}.pdf"
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        # Save the uploaded file temporarily
        with open(temp_filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file
        # Always use the specialized prompt and default model
        result = await process_file_with_gemini(
            temp_filepath, 
            PDF_PROMPT, 
            MODELS["Google/Gemini-2.5"]
        )
        
        # Delete the temporary file
        os.remove(temp_filepath)
        
        return ProcessResponse(**result)
        
    except Exception as e:
        # Ensure temp file is deleted even if processing fails
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=500, detail=str(e))
