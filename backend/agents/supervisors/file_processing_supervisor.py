"""
File Processing Supervisor Agent Module for MOSAIC

This module defines a file processing supervisor agent that orchestrates file processing.
It determines the file type and routes processing to specialized agents.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.file_processing_supervisor")


def create_file_processing_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a file processing supervisor that orchestrates file processing agents.
    
    This function creates a supervisor that can determine file types and route
    processing to specialized agents like the Excel processing agent.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure all required agents are registered
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.regular.file_processing import register_file_processing_agent
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.regular.file_processing import register_file_processing_agent
    
    # Register file processing agent if it doesn't exist
    file_processing = agent_registry.get("file_processing")
    if file_processing is None:
        logger.info("File processing agent not found in registry, registering it now")
        file_processing = register_file_processing_agent(model)
    
    # Define the agent names to include
    agent_names = ["file_processing"]
    
    # Create the file processing supervisor prompt
    prompt = (
        "You are a file processing coordinator managing specialized file processing agents:\n"
        "1. file_processing: Use for processing Excel (XLSX) files, extracting data, and performing analysis.\n"
        "\n"
        "Your job is to coordinate file processing based on the file type. When a user uploads a file, "
        "you should determine the file type and route it to the appropriate agent for processing. "
        "Currently, you can process Excel files, but more file types will be added in the future.\n"
        "\n"
        "For Excel files, you can:\n"
        "- Extract basic information and preview data using process_excel_file_tool\n"
        "- Perform specific analyses like correlation, summary statistics, or groupby using analyze_excel_data_tool\n"
        "\n"
        "IMPORTANT: When a user uploads a file or mentions a file, you should IMMEDIATELY use the transfer_to_file_processing tool "
        "to hand off the request to the file_processing agent. The file_processing agent has special logic to "
        "handle file attachments that you don't have access to. DO NOT try to process the file yourself.\n"
        "\n"
        "CRITICAL: If you see any message that mentions a file, Excel, spreadsheet, data, or analysis, "
        "you should assume the user wants to process a file and use the transfer_to_file_processing tool immediately. "
        "The file_processing agent will handle all the details.\n"
        "\n"
        "Important rules:\n"
        "- Always check the file type before processing\n"
        "- For Excel files, use the file_processing agent by calling transfer_to_file_processing\n"
        "- For unsupported file types, clearly explain that the file type is not yet supported\n"
        "- Never make up information or hallucinate details\n"
        "- Provide clear explanations of the data and analysis results\n"
        "- If processing fails, provide a clear error report and suggest alternatives\n"
        "\n"
        "Example conversation:\n"
        "User: Can you analyze this Excel file? [Uploads file.xlsx]\n"
        "You: I'll help you analyze that Excel file.\n"
        "\n"
        "IMPORTANT: Do not respond to the user with a message saying you will transfer them. "
        "Instead, immediately use the transfer_to_file_processing tool without saying anything. "
        "The tool will handle the transfer automatically.\n"
        "\n"
        "CRITICAL INSTRUCTION: When you see a message with an attachment or a message that mentions a file, "
        "your ONLY response should be to use the transfer_to_file_processing tool. Do not say anything else. "
        "Do not try to process the file yourself. Just use the transfer_to_file_processing tool immediately.\n"
        "\n"
        "IMPORTANT: If you see a message that contains '[Attached Excel file:' or '[Attached file:', "
        "this indicates that a file has been uploaded. You should immediately use the transfer_to_file_processing tool. "
        "The file_processing agent has special logic to handle file attachments that you don't have access to.\n"
        "\n"
        "CRITICAL: When the file_processing agent returns results, you MUST include those results in your response to the user. "
        "Do not summarize or paraphrase the results. Include the FULL results exactly as they were returned by the file_processing agent. "
        "This is essential for the user to see the complete analysis of their file.\n"
        "\n"
        "EXTREMELY IMPORTANT: When you receive results from the file_processing agent after using the transfer_to_file_processing tool, "
        "DO NOT just say 'I've successfully transferred the results back'. Instead, you MUST respond with the COMPLETE results "
        "that were returned by the file_processing agent. The user should see the full analysis, not just a confirmation message.\n"
        "\n"
        "Example of INCORRECT response after receiving results:\n"
        "\"I've successfully transferred the results back to the file processing supervisor. If you have any more questions or need further analysis, feel free to ask!\"\n"
        "\n"
        "Example of CORRECT response after receiving results:\n"
        "\"Here's the analysis of your Excel file:\n\n[FULL RESULTS FROM FILE PROCESSING AGENT]\"\n"
    )
    
    # Create the supervisor
    logger.info(f"Creating file processing supervisor with agents: {', '.join(agent_names)}")
    
    # First, make sure the file_processing agent is registered
    file_processing = agent_registry.get("file_processing")
    if file_processing is None:
        logger.info("File processing agent not found in registry, registering it now")
        file_processing = register_file_processing_agent(model)
        logger.info(f"Registered file_processing agent: {file_processing.name}")
    else:
        logger.info(f"Found existing file_processing agent: {file_processing.name}")
    
    # Create the supervisor with explicit agent instances
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="file_processing_supervisor",
        output_mode=output_mode
    )
    
    # Note: The relationship between file_processing_supervisor and file_processing
    # will be automatically determined by the agent_api._extract_agent_relationships method
    # based on the agent_names list provided to create_supervisor
    logger.info(f"Relationship between file_processing_supervisor and file_processing will be determined by the API")
    
    logger.info("Successfully created file processing supervisor")
    return supervisor.compile()
