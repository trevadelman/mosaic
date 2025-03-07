"""
File Processing Agent Module for MOSAIC

This module defines a file processing agent that can process uploaded files.
It currently focuses on Excel (XLSX) files, extracting and analyzing tabular data.
"""

import logging
import json
import base64
import io
import pandas as pd
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.file_processing")

@tool
def process_excel_file_tool(file_data_base64: str, file_name: str) -> str:
    """
    Process an Excel (XLSX) file and extract its contents.
    
    Args:
        file_data_base64: Base64 encoded file data
        file_name: Name of the file
        
    Returns:
        A string containing the extracted data and analysis
    """
    logger.info(f"Processing Excel file: {file_name}")
    try:
        # Initialize file_data to None to ensure it's always defined
        file_data = None
        
        # Log the length of the base64 data
        logger.info(f"Base64 data length: {len(file_data_base64)}")
        
        # Log the first 100 characters of the base64 data
        logger.info(f"First 100 characters of base64 data: {file_data_base64[:100]}")
        
        # If the base64 data is empty, try to get the attachment from the database
        if not file_data_base64:
            logger.info("Base64 data is empty, trying to get attachment from database")
            
            # Try to get the attachment from the database
            try:
                # Import the attachment service
                try:
                    from mosaic.backend.database.service import AttachmentService
                except ImportError:
                    from backend.database.service import AttachmentService
                
                # Try to get the most recent attachment with the same file name
                try:
                    from mosaic.backend.database.repository import AttachmentRepository
                    from mosaic.backend.database.database import get_db_session
                    from mosaic.backend.database.models import Attachment as AttachmentModel
                except ImportError:
                    from backend.database.repository import AttachmentRepository
                    from backend.database.database import get_db_session
                    from backend.database.models import Attachment as AttachmentModel
                
                # Use the database session to query for attachments with the same file name
                try:
                    with get_db_session() as session:
                        # Query for attachments with the same file name
                        matching_attachments = session.query(AttachmentModel).filter(AttachmentModel.filename == file_name).order_by(AttachmentModel.id.desc()).all()
                        
                        if matching_attachments:
                            # Get the most recent one
                            attachment = matching_attachments[0]
                            attachment_id = attachment.id
                            logger.info(f"Found attachment with ID {attachment_id} and file name {file_name}")
                            
                            # Get the attachment data
                            if attachment.data:
                                file_data_base64 = base64.b64encode(attachment.data).decode('ascii')
                                logger.info(f"Successfully retrieved attachment data from database, length: {len(file_data_base64)}")
                            else:
                                logger.error(f"Attachment {attachment_id} has no data")
                        else:
                            logger.error(f"No attachments found with file name {file_name}")
                except Exception as e:
                    logger.error(f"Error querying database for attachments: {str(e)}")
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
                    # Try to get the attachment from the database
                    try:
                        # Import the attachment service
                        try:
                            from mosaic.backend.database.service import AttachmentService
                        except ImportError:
                            from backend.database.service import AttachmentService
                        
                        # Try to extract the attachment ID from the file name
                        import re
                        match = re.search(r'id=(\d+)', file_name)
                        if match:
                            attachment_id = int(match.group(1))
                            logger.info(f"Extracted attachment ID from file name: {attachment_id}")
                            
                            # Get the attachment from the database
                            attachment = AttachmentService.get_attachment(attachment_id)
                            if attachment and attachment.get("data"):
                                file_data = base64.b64decode(attachment["data"])
                                logger.info(f"Successfully retrieved attachment data from database, length: {len(file_data)}")
                            else:
                                logger.error(f"Attachment {attachment_id} not found or has no data")
                        else:
                            logger.error(f"Could not extract attachment ID from file name: {file_name}")
                    except Exception as e:
                        logger.error(f"Error retrieving attachment from database: {str(e)}")
                        raise
        else:
            logger.error("No base64 data available after trying to retrieve from database")
            return f"Error processing Excel file: No data available for file {file_name}"
        
        # Read Excel file
        logger.info(f"Reading Excel file with pandas...")
        try:
            # Try with default engine
            df = pd.read_excel(io.BytesIO(file_data))
        except Exception as e:
            logger.error(f"Error reading Excel file with default engine: {str(e)}")
            try:
                # Try with openpyxl engine
                logger.info("Trying with openpyxl engine...")
                df = pd.read_excel(io.BytesIO(file_data), engine="openpyxl")
            except Exception as e2:
                logger.error(f"Error reading Excel file with openpyxl engine: {str(e2)}")
                try:
                    # Try with xlrd engine
                    logger.info("Trying with xlrd engine...")
                    df = pd.read_excel(io.BytesIO(file_data), engine="xlrd")
                except Exception as e3:
                    logger.error(f"Error reading Excel file with xlrd engine: {str(e3)}")
                    # If all engines fail, raise the original error
                    raise e
        
        # Get basic information about the dataframe
        rows = len(df)
        columns = len(df.columns)
        column_names = df.columns.tolist()
        
        logger.info(f"Excel file has {rows} rows and {columns} columns")
        
        # Generate summary statistics
        logger.info(f"Generating summary statistics...")
        summary_stats = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                summary_stats[col] = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std())
                }
            elif pd.api.types.is_string_dtype(df[col]):
                # For string columns, count unique values
                unique_values = df[col].nunique()
                most_common = df[col].value_counts().head(3).to_dict()
                summary_stats[col] = {
                    "unique_values": unique_values,
                    "most_common": most_common
                }
        
        # Convert dataframe to markdown table for preview
        logger.info(f"Converting data to markdown table...")
        preview_rows = min(10, rows)  # Limit to 10 rows for preview
        markdown_table = df.head(preview_rows).to_markdown(index=False)
        
        # Format the results
        result = f"# Excel File Analysis: {file_name}\n\n"
        result += f"## Basic Information\n"
        result += f"- Rows: {rows}\n"
        result += f"- Columns: {columns}\n"
        result += f"- Column Names: {', '.join(column_names)}\n\n"
        
        result += f"## Data Preview\n"
        result += markdown_table + "\n\n"
        
        result += f"## Summary Statistics\n"
        for col, stats in summary_stats.items():
            result += f"### {col}\n"
            if "min" in stats:  # Numeric column
                result += f"- Min: {stats['min']}\n"
                result += f"- Max: {stats['max']}\n"
                result += f"- Mean: {stats['mean']}\n"
                result += f"- Median: {stats['median']}\n"
                result += f"- Standard Deviation: {stats['std']}\n"
            else:  # String column
                result += f"- Unique Values: {stats['unique_values']}\n"
                result += f"- Most Common Values:\n"
                for value, count in stats['most_common'].items():
                    result += f"  - '{value}': {count} occurrences\n"
            result += "\n"
        
        logger.info(f"Excel file processing completed successfully")
        return result
    
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        error_report = {
            "task": "Process Excel File",
            "status": "Failed",
            "file_name": file_name,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error processing Excel file: {json.dumps(error_report, indent=2)}"

@tool
def analyze_excel_data_tool(file_data_base64: str, file_name: str, analysis_type: str) -> str:
    """
    Perform specific analysis on Excel data.
    
    Args:
        file_data_base64: Base64 encoded file data
        file_name: Name of the file
        analysis_type: Type of analysis to perform (correlation, pivot, groupby)
        
    Returns:
        A string containing the analysis results
    """
    logger.info(f"Performing {analysis_type} analysis on Excel file: {file_name}")
    try:
        # Initialize file_data to None to ensure it's always defined
        file_data = None
        
        # Log the length of the base64 data
        logger.info(f"Base64 data length: {len(file_data_base64)}")
        
        # Log the first 100 characters of the base64 data
        logger.info(f"First 100 characters of base64 data: {file_data_base64[:100]}")
        
        # If the base64 data is empty, try to get the attachment from the database
        if not file_data_base64:
            logger.info("Base64 data is empty, trying to get attachment from database")
            
            # Try to get the attachment from the database
            try:
                # Import the attachment service
                try:
                    from mosaic.backend.database.service import AttachmentService
                except ImportError:
                    from backend.database.service import AttachmentService
                
                # Try to get the most recent attachment with the same file name
                try:
                    from mosaic.backend.database.repository import AttachmentRepository
                    from mosaic.backend.database.database import get_db_session
                    from mosaic.backend.database.models import Attachment as AttachmentModel
                except ImportError:
                    from backend.database.repository import AttachmentRepository
                    from backend.database.database import get_db_session
                    from backend.database.models import Attachment as AttachmentModel
                
                # Use the database session to query for attachments with the same file name
                try:
                    with get_db_session() as session:
                        # Query for attachments with the same file name
                        matching_attachments = session.query(AttachmentModel).filter(AttachmentModel.filename == file_name).order_by(AttachmentModel.id.desc()).all()
                        
                        if matching_attachments:
                            # Get the most recent one
                            attachment = matching_attachments[0]
                            attachment_id = attachment.id
                            logger.info(f"Found attachment with ID {attachment_id} and file name {file_name}")
                            
                            # Get the attachment data
                            if attachment.data:
                                file_data_base64 = base64.b64encode(attachment.data).decode('ascii')
                                logger.info(f"Successfully retrieved attachment data from database, length: {len(file_data_base64)}")
                            else:
                                logger.error(f"Attachment {attachment_id} has no data")
                        else:
                            logger.error(f"No attachments found with file name {file_name}")
                except Exception as e:
                    logger.error(f"Error querying database for attachments: {str(e)}")
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
                    # Try to get the attachment from the database
                    try:
                        # Import the attachment service
                        try:
                            from mosaic.backend.database.service import AttachmentService
                        except ImportError:
                            from backend.database.service import AttachmentService
                        
                        # Try to extract the attachment ID from the file name
                        import re
                        match = re.search(r'id=(\d+)', file_name)
                        if match:
                            attachment_id = int(match.group(1))
                            logger.info(f"Extracted attachment ID from file name: {attachment_id}")
                            
                            # Get the attachment from the database
                            attachment = AttachmentService.get_attachment(attachment_id)
                            if attachment and attachment.get("data"):
                                file_data = base64.b64decode(attachment["data"])
                                logger.info(f"Successfully retrieved attachment data from database, length: {len(file_data)}")
                            else:
                                logger.error(f"Attachment {attachment_id} not found or has no data")
                        else:
                            logger.error(f"Could not extract attachment ID from file name: {file_name}")
                    except Exception as e:
                        logger.error(f"Error retrieving attachment from database: {str(e)}")
                        raise
        else:
            logger.error("No base64 data available after trying to retrieve from database")
            return f"Error analyzing Excel file: No data available for file {file_name}"
        
        # Read Excel file
        logger.info(f"Reading Excel file with pandas...")
        try:
            # Try with default engine
            df = pd.read_excel(io.BytesIO(file_data))
        except Exception as e:
            logger.error(f"Error reading Excel file with default engine: {str(e)}")
            try:
                # Try with openpyxl engine
                logger.info("Trying with openpyxl engine...")
                df = pd.read_excel(io.BytesIO(file_data), engine="openpyxl")
            except Exception as e2:
                logger.error(f"Error reading Excel file with openpyxl engine: {str(e2)}")
                try:
                    # Try with xlrd engine
                    logger.info("Trying with xlrd engine...")
                    df = pd.read_excel(io.BytesIO(file_data), engine="xlrd")
                except Exception as e3:
                    logger.error(f"Error reading Excel file with xlrd engine: {str(e3)}")
                    # If all engines fail, raise the original error
                    raise e
        
        # Perform the requested analysis
        if analysis_type.lower() == "correlation":
            logger.info(f"Calculating correlation matrix...")
            # Only include numeric columns
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.empty:
                return "No numeric columns found for correlation analysis."
            
            corr_matrix = numeric_df.corr()
            result = f"# Correlation Analysis for {file_name}\n\n"
            result += corr_matrix.to_markdown()
            
            # Highlight strong correlations
            result += "\n\n## Strong Correlations (|r| > 0.7)\n\n"
            strong_corrs = []
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    if col1 != col2 and abs(corr_matrix.loc[col1, col2]) > 0.7:
                        strong_corrs.append((col1, col2, corr_matrix.loc[col1, col2]))
            
            if strong_corrs:
                for col1, col2, corr in strong_corrs:
                    result += f"- {col1} and {col2}: {corr:.3f}\n"
            else:
                result += "No strong correlations found.\n"
            
            return result
            
        elif analysis_type.lower() == "summary":
            logger.info(f"Generating summary statistics...")
            summary = df.describe(include='all').to_markdown()
            return f"# Summary Statistics for {file_name}\n\n{summary}"
            
        elif analysis_type.lower() == "groupby":
            logger.info(f"Performing groupby analysis...")
            # Try to identify a categorical column for groupby
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            if not categorical_cols:
                return "No categorical columns found for groupby analysis."
            
            # Use the first categorical column
            group_col = categorical_cols[0]
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                return "No numeric columns found for groupby analysis."
            
            # Group by the categorical column and calculate statistics for numeric columns
            grouped = df.groupby(group_col)[numeric_cols].agg(['mean', 'count', 'sum'])
            
            result = f"# Groupby Analysis for {file_name}\n\n"
            result += f"Grouped by: {group_col}\n\n"
            result += grouped.to_markdown()
            
            return result
        
        else:
            return f"Unknown analysis type: {analysis_type}. Supported types are: correlation, summary, groupby."
    
    except Exception as e:
        logger.error(f"Error analyzing Excel file: {str(e)}")
        error_report = {
            "task": "Analyze Excel File",
            "status": "Failed",
            "file_name": file_name,
            "analysis_type": analysis_type,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error analyzing Excel file: {json.dumps(error_report, indent=2)}"

class FileProcessingAgent(BaseAgent):
    """
    File processing agent that can process uploaded files.
    
    This agent provides tools for processing Excel files and extracting
    useful information from them.
    """
    
    def __init__(
        self,
        name: str = "file_processing",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "📄",
    ):
        """
        Initialize a new file processing agent.
        
        Args:
            name: The name of the agent (default: "file_processing")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📄")
        """
        # Create the file processing tools
        file_processing_tools = [
            process_excel_file_tool,
            analyze_excel_data_tool
        ]
        
        # Combine with any additional tools
        all_tools = file_processing_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Excel Processing", "Data Analysis"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "File Processing Agent for processing Excel files and extracting data",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.info(f"Initialized file processing agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the file processing agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a file processing specialist that can analyze Excel files. "
            "Your job is to extract and analyze data from uploaded files, providing insights and summaries. "
            "\n\n"
            "You have tools for file processing: "
            "- Use process_excel_file_tool to extract basic information and preview data from Excel files. "
            "- Use analyze_excel_data_tool to perform specific analyses like correlation, summary statistics, or groupby. "
            "\n\n"
            "Always work with the actual data provided to you. "
            "If you cannot process a file or extract meaningful information, clearly state that and explain why. "
            "Never make up information or hallucinate details. "
            "Always provide clear explanations of your analysis and what the data shows."
        )
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a file and return the extracted information.
        
        This method overrides the default invoke method to handle file attachments.
        It checks for attachments in the messages, extracts the file data, and processes it.
        
        Args:
            state: The current state of the conversation
            
        Returns:
            The updated state with the processed file information
        """
        logger.info("FileProcessingAgent invoke method called")
        
        # First, check if there are any attachments in the messages
        has_attachments = False
        attachment_data = None
        attachment_filename = None
        attachment_content_type = None
        
        # Get the messages from the state
        messages = state.get("messages", [])
        logger.info(f"Found {len(messages)} messages in state")
        
        # Look for attachments in the last user message
        if messages:
            # Find the last user message
            for message in reversed(messages):
                if isinstance(message, dict) and message.get("role") == "user":
                    logger.info("Found last user message")
                    
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
                    # Import the attachment service
                    try:
                        from mosaic.backend.database.service import AttachmentService
                    except ImportError:
                        from backend.database.service import AttachmentService
                    
                    # Get the attachment ID if available
                    attachment_id = attachment.get("id")
                    if attachment_id:
                        logger.info(f"Trying to get attachment data from database for ID: {attachment_id}")
                        
                        # Import the repository to directly access the attachment data
                        try:
                            from mosaic.backend.database.repository import AttachmentRepository
                            from mosaic.backend.database.database import get_db_session
                        except ImportError:
                            from backend.database.repository import AttachmentRepository
                            from backend.database.database import get_db_session
                        
                        # Get the attachment directly from the repository
                        db_attachment = AttachmentRepository.get_attachment(attachment_id)
                        if db_attachment and db_attachment.data:
                            # Convert binary data to base64
                            attachment_data = base64.b64encode(db_attachment.data).decode('ascii')
                            logger.info(f"Successfully retrieved attachment data from database ({len(db_attachment.data)} bytes)")
                            
                            # Log the first few bytes for debugging
                            if len(db_attachment.data) > 0:
                                logger.info(f"First few bytes: {db_attachment.data[:20]}")
                        else:
                            logger.error(f"Attachment {attachment_id} not found or has no data")
                            
                            # Try to get the attachment directly from the database session
                            try:
                                from mosaic.backend.database.database import get_db_session
                                from mosaic.backend.database.models import Attachment as AttachmentModel
                            except ImportError:
                                from backend.database.database import get_db_session
                                from backend.database.models import Attachment as AttachmentModel
                            
                            with get_db_session() as session:
                                # Include user_id in the query if available
                                query = session.query(AttachmentModel).filter(AttachmentModel.id == attachment_id)
                                
                                # If user_id is available, filter by it as well
                                user_id = message.get("user_id")
                                if user_id:
                                    query = query.filter(AttachmentModel.user_id == user_id)
                                
                                db_attachment = query.first()
                                if db_attachment and db_attachment.data:
                                    # Convert binary data to base64
                                    attachment_data = base64.b64encode(db_attachment.data).decode('ascii')
                                    logger.info(f"Successfully retrieved attachment data directly from session ({len(db_attachment.data)} bytes)")
                                else:
                                    logger.error(f"Attachment {attachment_id} not found or has no data in direct session query")
                except Exception as e:
                    logger.error(f"Error retrieving attachment data from database: {str(e)}")
            
            # Check if it's an Excel file
            if (attachment_content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or
                attachment_content_type == "application/vnd.ms-excel" or
                attachment_filename.endswith(".xlsx") or
                attachment_filename.endswith(".xls")):
                
                logger.info("Detected Excel file")
                
                if attachment_data:
                    logger.info("Processing Excel file with process_excel_file_tool")
                    
                    # Process the Excel file using the invoke method instead of direct call
                    try:
                        # Make sure the base64 data is properly padded
                        # Add padding if needed (base64 strings should have a length that is a multiple of 4)
                        padding_needed = len(attachment_data) % 4
                        if padding_needed > 0:
                            attachment_data += "=" * (4 - padding_needed)
                            logger.info(f"Added {4 - padding_needed} padding characters to base64 data")
                        
                        # Use the invoke method with proper input format
                        result = process_excel_file_tool.invoke({
                            "file_data_base64": attachment_data,
                            "file_name": attachment_filename
                        })
                    except Exception as e:
                        logger.error(f"Error invoking process_excel_file_tool: {str(e)}")
                        # Fallback to direct implementation
                        try:
                            # Decode base64 data
                            file_data = base64.b64decode(attachment_data)
                            
                            # Read Excel file
                            logger.info(f"Reading Excel file with pandas (fallback)...")
                            try:
                                # Try with default engine
                                df = pd.read_excel(io.BytesIO(file_data))
                            except Exception as e:
                                logger.error(f"Error reading Excel file with default engine (fallback): {str(e)}")
                                try:
                                    # Try with openpyxl engine
                                    logger.info("Trying with openpyxl engine (fallback)...")
                                    df = pd.read_excel(io.BytesIO(file_data), engine="openpyxl")
                                except Exception as e2:
                                    logger.error(f"Error reading Excel file with openpyxl engine (fallback): {str(e2)}")
                                    try:
                                        # Try with xlrd engine
                                        logger.info("Trying with xlrd engine (fallback)...")
                                        df = pd.read_excel(io.BytesIO(file_data), engine="xlrd")
                                    except Exception as e3:
                                        logger.error(f"Error reading Excel file with xlrd engine (fallback): {str(e3)}")
                                        # If all engines fail, raise the original error
                                        raise e
                            
                            # Get basic information about the dataframe
                            rows = len(df)
                            columns = len(df.columns)
                            column_names = df.columns.tolist()
                            
                            # Format the results
                            result = f"# Excel File Analysis: {attachment_filename}\n\n"
                            result += f"## Basic Information\n"
                            result += f"- Rows: {rows}\n"
                            result += f"- Columns: {columns}\n"
                            result += f"- Column Names: {', '.join(column_names)}\n\n"
                            
                            # Convert dataframe to markdown table for preview
                            preview_rows = min(10, rows)  # Limit to 10 rows for preview
                            markdown_table = df.head(preview_rows).to_markdown(index=False)
                            result += f"## Data Preview\n"
                            result += markdown_table + "\n\n"
                            
                            logger.info(f"Excel file processing completed successfully (fallback)")
                        except Exception as inner_e:
                            logger.error(f"Error in fallback Excel processing: {str(inner_e)}")
                            result = f"Error processing Excel file: {str(inner_e)}"
                else:
                    logger.error("Cannot process Excel file: attachment data is missing")
                    result = "Error: Could not process the Excel file because the file data is missing."
                
                # Add the result to the state
                if "messages" not in state:
                    state["messages"] = []
                
                # Replace any existing assistant messages with the new result
                # First, keep all user messages
                user_messages = [msg for msg in state["messages"] if isinstance(msg, dict) and msg.get("role") == "user"]
                
                # Then add the new assistant message
                user_messages.append({
                    "role": "assistant",
                    "content": result
                })
                
                # Replace the state messages with our filtered list
                state["messages"] = user_messages
                
                logger.info(f"Replaced assistant messages with new result: {result[:100]}...")
                
                logger.info("Excel file processing completed and added to state")
                
                # Return the updated state
                return state
            else:
                logger.warning(f"Unsupported file type: {attachment_content_type}")
                
                # Add a message indicating unsupported file type
                if "messages" not in state:
                    state["messages"] = []
                
                state["messages"].append({
                    "role": "assistant",
                    "content": f"Sorry, I can only process Excel files (.xlsx, .xls). The file '{attachment_filename}' appears to be a {attachment_content_type} file, which is not supported."
                })
                
                return state
        
        # If we didn't find any attachments or couldn't process them, use the default behavior
        logger.info("No valid attachments found, using default agent behavior")
        return super().invoke(state)

# Register the file processing agent with the registry
def register_file_processing_agent(model: LanguageModelLike) -> FileProcessingAgent:
    """
    Create and register a file processing agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created file processing agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    file_processing = FileProcessingAgent(model=model)
    agent_registry.register(file_processing)
    return file_processing
