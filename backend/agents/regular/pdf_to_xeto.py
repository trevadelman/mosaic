"""
PDF to Xeto Agent Module for MOSAIC

This module defines an agent that processes PDF files using Google Gemini.
It uploads PDFs to Gemini with a user message and returns the response.
"""

import logging
import json
import base64
import os
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool
from google import genai

# Import database models
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
    from mosaic.backend.database.service import AttachmentService
    from mosaic.backend.database.repository import AttachmentRepository
    from mosaic.backend.database.database import get_db_session
    from mosaic.backend.database.models import Attachment as AttachmentModel
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry
    from backend.database.service import AttachmentService
    from backend.database.repository import AttachmentRepository
    from backend.database.database import get_db_session
    from backend.database.models import Attachment as AttachmentModel

# Configure logging
logger = logging.getLogger("mosaic.agents.pdf_to_xeto")

@tool
def process_pdf_with_gemini(file_data_base64: str, file_name: str, user_message: str) -> str:
    """
    Process a PDF file using Google Gemini.
    
    Args:
        file_data_base64: Base64 encoded file data
        file_name: Name of the file
        user_message: User message to send to Gemini along with the PDF
        
    Returns:
        A string containing the Gemini response
    """
    logger.info(f"Processing PDF file: {file_name}")
    try:
        # Initialize file_data to None to ensure it's always defined
        file_data = None
        
        # Log the length of the base64 data
        logger.info(f"Base64 data length: {len(file_data_base64)}")
        
        # If the base64 data is empty, try to get the attachment from the database
        if not file_data_base64:
            logger.info("Base64 data is empty, trying to get attachment from database")
            
            # Try to get the attachment from the database
            try:
                # Use the database session to query for attachments with the same file name
                with get_db_session() as session:
                    # Query for attachments with the same file name
                    matching_attachments = session.query(AttachmentModel).filter(AttachmentModel.filename == file_name).order_by(AttachmentModel.id.desc()).all()
                    
                    if matching_attachments:
                        # Get the most recent one
                        attachment = matching_attachments[0]
                        attachment_id = attachment.id
                        logger.info(f"Found attachment with ID {attachment_id} and file name {file_name}")
                        
                        # Get the data within the session context
                        data = attachment.data
                        if data:
                            # Convert binary data to base64
                            file_data_base64 = base64.b64encode(data).decode('ascii')
                            logger.info(f"Successfully retrieved attachment data from database, length: {len(data)} bytes")
                            
                            # Log the first few bytes for debugging
                            if len(data) > 0:
                                logger.info(f"First few bytes: {data[:20]}")
                        else:
                            logger.error(f"Attachment {attachment_id} has no data")
                    else:
                        logger.error(f"No attachments found with file name {file_name}")
            except Exception as e:
                logger.error(f"Error retrieving attachment from database: {str(e)}")
        
        # Process the base64 data if available
        if file_data_base64:
            # Clean up the base64 data first to fix common issues
            file_data_base64 = file_data_base64.replace(' ', '+')
            file_data_base64 = file_data_base64.replace('\n', '')
            file_data_base64 = file_data_base64.replace('\r', '')
            
            # Make sure the base64 data is properly padded
            # Add padding if needed (base64 strings should have a length that is a multiple of 4)
            padding_needed = len(file_data_base64) % 4
            if padding_needed > 0:
                file_data_base64 += "=" * (4 - padding_needed)
                logger.info(f"Added {4 - padding_needed} padding characters to base64 data")
            
            # Decode base64 data
            try:
                file_data = base64.b64decode(file_data_base64)
                logger.info(f"Successfully decoded base64 data, length: {len(file_data)}")
            except Exception as e:
                logger.error(f"Error decoding base64 data: {str(e)}")
                logger.info("Trying alternative base64 decoding approach")
                try:
                    file_data = base64.b64decode(file_data_base64)
                    logger.info(f"Successfully decoded base64 data after cleanup, length: {len(file_data)}")
                except Exception as e:
                    logger.error(f"Error decoding base64 data after cleanup: {str(e)}")
                    raise
        else:
            logger.error("No base64 data available after trying to retrieve from database")
            return f"Error processing PDF file: No data available for file {file_name}"
        
        # Save the PDF to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
            logger.info(f"Saved PDF to temporary file: {temp_path}")
        
        try:
            # Initialize the Gemini client
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not found")
            
            client = genai.Client(api_key=api_key)
            
            # Upload the file to Gemini
            file_ref = client.files.upload(file=temp_path)
            logger.info(f"Successfully uploaded file to Gemini: {file_ref}")
            
            # Generate content with Gemini
            response = client.models.generate_content(
                model="gemini-2.0-pro-exp-02-05",
                contents=[user_message, file_ref]
            )
            
            # Get the response text
            result = response.text
            logger.info("Successfully got response from Gemini")
            
            # Clean up the temporary file
            os.unlink(temp_path)
            logger.info("Cleaned up temporary file")
            
            # Return both the result and file reference
            return {"result": result, "file_ref": file_ref}
            
        except Exception as e:
            logger.error(f"Error processing with Gemini: {str(e)}")
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
                logger.info("Cleaned up temporary file after error")
            except:
                pass
            raise
    
    except Exception as e:
        logger.error(f"Error processing PDF file: {str(e)}")
        error_report = {
            "task": "Process PDF File",
            "status": "Failed",
            "file_name": file_name,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error processing PDF file: {json.dumps(error_report, indent=2)}"

class PDFToXetoAgent(BaseAgent):
    """
    PDF to Xeto agent that processes PDF files using Google Gemini.
    
    This agent provides tools for uploading PDFs to Google Gemini and
    getting responses based on the PDF content.
    """
    
    def __init__(
        self,
        name: str = "pdf_to_xeto",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Data Processing",
        capabilities: List[str] = None,
        icon: str = "📄",
    ):
        """
        Initialize a new PDF to Xeto agent.
        
        Args:
            name: The name of the agent (default: "pdf_to_xeto")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📄")
        """
        # Create the agent tools
        agent_tools = [
            process_pdf_with_gemini
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["PDF Processing", "Gemini Integration"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "PDF to Xeto Agent for processing PDFs with Google Gemini",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized PDF to Xeto agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the PDF to Xeto agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a PDF processing specialist that can analyze PDFs using Google Gemini. "
            "Your job is to process PDFs and get insights from them using Gemini's capabilities. "
            "\n\n"
            "You have tools for PDF processing: "
            "- Use process_pdf_with_gemini to process PDFs with Google Gemini. "
            "\n\n"
            "Always work with the actual data provided to you. "
            "If you cannot process a file or extract meaningful information, clearly state that and explain why. "
            "Never make up information or hallucinate details. "
            "Always provide clear explanations of your analysis and what the data shows."
        )
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PDF file and return the Gemini response.
        
        This method overrides the default invoke method to handle file attachments.
        It checks for attachments in the messages, extracts the file data, and processes it.
        
        Args:
            state: The current state of the conversation
            
        Returns:
            The updated state with the processed file information
        """
        logger.info("PDFToXetoAgent invoke method called")
        
        # First, check if there are any attachments in the messages
        has_attachments = False
        attachment_data = None
        attachment_filename = None
        attachment_content_type = None
        user_message = None
        
        # Get the messages from the state
        messages = state.get("messages", [])
        logger.info(f"Found {len(messages)} messages in state")
        
        # Look for attachments in the last user message
        if messages:
            # Find the last user message
            for message in reversed(messages):
                if isinstance(message, dict) and message.get("role") == "user":
                    logger.info("Found last user message")
                    
                    # Get the user message
                    user_message = message.get("content", "Tell me about this PDF")
                    
                    # Check for attachments
                    attachments = message.get("attachments", [])
                    if attachments:
                        logger.info(f"Found {len(attachments)} attachments in user message")
                        
                        # Process the first attachment (for now)
                        attachment = attachments[0]
                        attachment_data = attachment.get("data")
                        attachment_filename = attachment.get("filename", "unknown_file")
                        attachment_content_type = attachment.get("contentType", "application/octet-stream")
                        
                        # Get the user_id from the message if available
                        user_id = message.get("user_id")
                        if user_id:
                            logger.info(f"Found user_id: {user_id}")
                        
                        has_attachments = True
                        logger.info(f"Found attachment: {attachment_filename} ({attachment_content_type})")
                        break
                    else:
                        logger.info("No attachments found in user message")
                        break
        
        # If we found an attachment, process it
        if has_attachments:
            logger.info(f"Processing attachment: {attachment_filename}")
            
            # Log attachment data status
            if attachment_data:
                logger.info("Attachment data is present")
            else:
                logger.info("Attachment data is missing")
                
                # Try to get the attachment data from the database
                try:
                    # Get the attachment ID if available
                    attachment_id = attachment.get("id")
                    if attachment_id:
                        logger.info(f"Trying to get attachment data from database for ID: {attachment_id}")
                        
                        # Get the attachment using a database session
                        with get_db_session() as session:
                            # Include user_id in the query if available
                            query = session.query(AttachmentModel).filter(AttachmentModel.id == attachment_id)
                            
                            # If user_id is available, filter by it as well
                            user_id = message.get("user_id")
                            if user_id:
                                query = query.filter(AttachmentModel.user_id == user_id)
                            
                            db_attachment = query.first()
                            if db_attachment:
                                # Get the data within the session context
                                data = db_attachment.data
                                if data:
                                    # Convert binary data to base64
                                    attachment_data = base64.b64encode(data).decode('ascii')
                                    logger.info(f"Successfully retrieved attachment data from database ({len(data)} bytes)")
                                    
                                    # Log the first few bytes for debugging
                                    if len(data) > 0:
                                        logger.info(f"First few bytes: {data[:20]}")
                                else:
                                    logger.error(f"Attachment {attachment_id} has no data")
                            else:
                                logger.error(f"Attachment {attachment_id} not found")
                except Exception as e:
                    logger.error(f"Error retrieving attachment data from database: {str(e)}")
            
            # Check if it's a PDF file
            if (attachment_content_type == "application/pdf" or
                attachment_filename.lower().endswith(".pdf")):
                
                logger.info("Detected PDF file")
                
                if attachment_data:
                    logger.info("Processing PDF file with process_pdf_with_gemini")
                    
                    # Process the PDF file using the invoke method instead of direct call
                    try:
                        # Make sure the base64 data is properly padded
                        # Add padding if needed (base64 strings should have a length that is a multiple of 4)
                        padding_needed = len(attachment_data) % 4
                        if padding_needed > 0:
                            attachment_data += "=" * (4 - padding_needed)
                            logger.info(f"Added {4 - padding_needed} padding characters to base64 data")
                        
                        # Use the invoke method with proper input format
                        response = process_pdf_with_gemini.invoke({
                            "file_data_base64": attachment_data,
                            "file_name": attachment_filename,
                            "user_message": user_message
                        })
                        
                        if isinstance(response, dict):
                            result = response["result"]
                            file_ref = response["file_ref"]
                            
                            # Add the new assistant message to state with file_ref in custom_data
                            state["messages"].append({
                                "role": "assistant",
                                "content": result,
                                "custom_data": {
                                    "file_ref": file_ref
                                }
                            })
                        else:
                            # Handle error case where response is a string
                            state["messages"].append({
                                "role": "assistant",
                                "content": response
                            })
                            
                    except Exception as e:
                        logger.error(f"Error invoking process_pdf_with_gemini: {str(e)}")
                        state["messages"].append({
                            "role": "assistant",
                            "content": f"Error processing PDF file: {str(e)}"
                        })
                else:
                    logger.error("Cannot process PDF file: attachment data is missing")
                    state["messages"].append({
                        "role": "assistant",
                        "content": "Error: Could not process the PDF file because the file data is missing."
                    })
                
                logger.info("PDF file processing completed and added to state")
                
                # Return the updated state
                return state
            else:
                logger.warning(f"Unsupported file type: {attachment_content_type}")
                
                # Add a message indicating unsupported file type
                if "messages" not in state:
                    state["messages"] = []
                
                state["messages"].append({
                    "role": "assistant",
                    "content": f"Sorry, I can only process PDF files. The file '{attachment_filename}' appears to be a {attachment_content_type} file, which is not supported."
                })
                
                return state
        
        # Check for file reference in previous messages
        file_ref = None
        # Get only the messages before the current user message
        current_messages = []
        for message in messages:
            if message == state["messages"][-1]:  # Stop at current user message
                break
            current_messages.append(message)
        
        # Look for file reference in these messages
        for message in reversed(current_messages):
            if isinstance(message, dict) and message.get("role") == "assistant":
                custom_data = message.get("custom_data", {})
                if custom_data and "file_ref" in custom_data:
                    file_ref = custom_data["file_ref"]
                    logger.info(f"Found file_ref in message custom_data: {file_ref}")
                    break
        
        # Log the result of our search
        if file_ref:
            logger.info("Found file reference in message history")
        else:
            logger.info("No file reference found in message history")
        
        if file_ref:
            logger.info("No new attachments, but found stored file reference in message history")
            
            # Initialize the Gemini client
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not found")
            
            client = genai.Client(api_key=api_key)
            
            # Get the current user message
            current_message = state["messages"][-1]
            if isinstance(current_message, dict) and current_message.get("role") == "user":
                user_message = current_message.get("content")
                logger.info(f"Using current user message: {user_message}")
                
                # Generate content with Gemini using the stored file reference
                response = client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=[user_message, file_ref]
                )
                
                # Get the response text
                result = response.text
                logger.info("Successfully got response from Gemini using stored file reference")
                
                # Add the new assistant message with file_ref in custom_data
                state["messages"].append({
                    "role": "assistant",
                    "content": result,
                    "custom_data": {
                        "file_ref": file_ref
                    }
                })
                
                return state
            else:
                logger.error("Current message is not a user message")
                state["messages"].append({
                    "role": "assistant",
                    "content": "I encountered an error processing your request. Please try asking your question again."
                })
                return state
        
        # If no attachments or stored file reference, inform the user
        logger.info("No attachments or stored file reference found")
        
        # Initialize messages list if not present
        if "messages" not in state:
            state["messages"] = []
        
        # Add message asking user to upload the PDF again
        state["messages"].append({
            "role": "assistant",
            "content": "I don't have access to the PDF anymore. Could you please upload it again so I can answer your question?"
        })
        
        return state

def register_pdf_to_xeto_agent(model: LanguageModelLike) -> PDFToXetoAgent:
    """
    Create and register a PDF to Xeto agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created PDF to Xeto agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    pdf_to_xeto = PDFToXetoAgent(model=model)
    agent_registry.register(pdf_to_xeto)
    return pdf_to_xeto
