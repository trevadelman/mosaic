from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
import os
from typing import Dict, Any, Optional

from .database import get_db
from sqlalchemy.orm import Session
from ..database.user_repository import UserRepository

def get_webhook_api_router():
    """
    Get the webhook API router.
    
    Returns:
        The webhook API router
    """
    router = APIRouter(prefix="/api", tags=["webhooks"])
    
    # Get the Clerk webhook secret from environment variables
    CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")
    
    def verify_clerk_webhook(request: Request, payload: bytes) -> bool:
        """
        Verify that the webhook request is coming from Clerk.
        """
        if not CLERK_WEBHOOK_SECRET:
            # In development, we might not have a webhook secret
            # In production, this should raise an error
            return True
        
        signature = request.headers.get("svix-signature")
        if not signature:
            return False
        
        # The signature is a comma-separated list of timestamps and signatures
        # We need to verify at least one of them
        signature_pairs = signature.split(" ")
        for pair in signature_pairs:
            if "," not in pair:
                continue
            
            timestamp, signature = pair.split(",")
            
            # Compute the expected signature
            expected_signature = hmac.new(
                CLERK_WEBHOOK_SECRET.encode(),
                msg=timestamp.encode() + b"." + payload,
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Compare the signatures
            if hmac.compare_digest(expected_signature, signature):
                return True
        
        return False
    
    @router.post("/webhook/clerk")
    async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
        """
        Handle Clerk webhooks.
        """
        # Read the request body
        payload = await request.body()
        
        # Verify the webhook signature
        if not verify_clerk_webhook(request, payload):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Get the event type
        event_type = data.get("type")
        if not event_type:
            raise HTTPException(status_code=400, detail="Missing event type")
        
        # Handle the event
        user_repo = UserRepository(db)
        
        if event_type == "user.created":
            # A new user was created in Clerk
            user_data = data.get("data", {})
            user_id = user_data.get("id")
            email = user_data.get("email_addresses", [{}])[0].get("email_address")
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            
            if not user_id:
                raise HTTPException(status_code=400, detail="Missing user ID")
            
            # Create or update the user in our database
            user_repo.create_or_update_user(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        
        elif event_type == "user.updated":
            # A user was updated in Clerk
            user_data = data.get("data", {})
            user_id = user_data.get("id")
            email = user_data.get("email_addresses", [{}])[0].get("email_address")
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            
            if not user_id:
                raise HTTPException(status_code=400, detail="Missing user ID")
            
            # Create or update the user in our database
            user_repo.create_or_update_user(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        
        elif event_type == "user.deleted":
            # A user was deleted in Clerk
            user_data = data.get("data", {})
            user_id = user_data.get("id")
            
            if not user_id:
                raise HTTPException(status_code=400, detail="Missing user ID")
            
            # Delete the user from our database
            user_repo.delete_user(user_id=user_id)
        
        # Return a success response
        return JSONResponse(content={"status": "success"})
    
    return router
