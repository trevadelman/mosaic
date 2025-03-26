from fastapi import APIRouter, HTTPException
from .service import DatabaseVisualizerService
from .models import DatabaseStructure, GraphData
from typing import Dict

# Get database URL from config
from ...config import settings

router = APIRouter(prefix="/api/apps/db-visualizer", tags=["applications"])
db_service = DatabaseVisualizerService(settings.DATABASE_URL)

@router.get("/structure", response_model=DatabaseStructure)
async def get_database_structure():
    """Get the complete database structure."""
    try:
        return db_service.get_database_structure()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph", response_model=GraphData)
async def get_graph_data():
    """Get the database structure in D3 force graph format."""
    try:
        return db_service.get_graph_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}", response_model=Dict)
async def get_table_details(table_name: str):
    """Get detailed information about a specific table."""
    try:
        return db_service.get_table_details(table_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}/data", response_model=Dict)
async def get_table_data(table_name: str, page: int = 1, page_size: int = 50):
    """Get paginated data from a specific table."""
    try:
        return db_service.get_table_data(table_name, page, page_size)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
