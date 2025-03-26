from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/apps", tags=["applications"])

class GreetingRequest(BaseModel):
    name: str

@router.post("/hello-world/greet")
async def get_greeting(request: GreetingRequest):
    """Get a greeting for the given name."""
    try:
        return {
            "greeting": f"Hello, {request.name}! Welcome to Mosaic."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
