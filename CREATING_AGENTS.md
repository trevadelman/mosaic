# Creating Agents in MOSAIC

This guide provides comprehensive instructions for creating new agents in the MOSAIC system. With the database-driven agent metadata system, there are multiple approaches to creating agents, each with its own advantages.

## Table of Contents

1. [JSON Template Approach](#json-template-approach)
2. [API-Based Approach](#api-based-approach)
3. [Python Script Approach](#python-script-approach)
4. [UI-Based Approach](#ui-based-approach)
5. [Agent Structure](#agent-structure)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## JSON Template Approach

This approach leverages the existing JSON template system and then saves it to the database.

### Step 1: Create a JSON Template

Create a new JSON file in `backend/agents/templates/` (e.g., `my_new_agent.json`) following the schema defined in `agent_schema.json`:

```json
{
  "agent": {
    "name": "my_new_agent",
    "type": "Utility",
    "description": "A new agent that does something useful",
    "systemPrompt": "You are a helpful assistant specialized in [specific domain]. Your task is to [specific task].",
    "icon": "🤖",
    "tools": [
      {
        "name": "my_tool",
        "description": "A tool that does something useful",
        "parameters": [
          {
            "name": "param1",
            "type": "string",
            "description": "First parameter"
          },
          {
            "name": "param2",
            "type": "integer",
            "description": "Second parameter"
          }
        ],
        "returns": {
          "type": "string",
          "description": "The result of the operation"
        },
        "implementation": {
          "code": "def my_tool(param1: str, param2: int) -> str:\n    return f\"Processed {param1} with value {param2}\""
        }
      }
    ],
    "capabilities": ["capability1", "capability2"]
  }
}
```

### Step 2: Validate and Save to Database

Use the migration script to validate and save the template to the database:

```bash
cd mosaic
python -m backend.database.migrations.migrate_agents_to_db
```

This script will:
1. Load all JSON templates from the templates directory
2. Validate each template against the schema
3. Save valid templates to the database
4. Skip templates that already exist in the database

### Step 3: Generate and Deploy the Agent

Use the API to generate code and deploy the agent:

```bash
# Generate code
curl -X POST "http://localhost:8000/api/agent-creator/db/generate-code/[agent_id]" \
  -H "Content-Type: application/json"

# Deploy the agent
curl -X POST "http://localhost:8000/api/agent-creator/db/deploy/[agent_id]" \
  -H "Content-Type: application/json" \
  -d '{"sandbox": true}'
```

Replace `[agent_id]` with the ID of the agent in the database.

## API-Based Approach

This approach creates the agent directly through the API without creating a template file.

### Step 1: Create the Agent Definition

Prepare a JSON object that follows the agent schema, including agent metadata, tools, and capabilities.

### Step 2: Save to Database via API

```bash
curl -X POST "http://localhost:8000/api/agent-creator/db/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "name": "my_new_agent",
      "type": "Utility",
      "description": "A new agent that does something useful",
      "systemPrompt": "You are a helpful assistant...",
      "icon": "🤖",
      "tools": [
        {
          "name": "my_tool",
          "description": "A tool that does something",
          "parameters": [
            {
              "name": "param1",
              "type": "string",
              "description": "A parameter"
            }
          ],
          "returns": {
            "type": "string",
            "description": "The result"
          },
          "implementation": {
            "code": "def my_tool(param1: str) -> str:\n    return f\"Processed: {param1}\""
          }
        }
      ],
      "capabilities": ["capability1", "capability2"]
    }
  }'
```

### Step 3: Generate and Deploy the Agent

Use the same API endpoints as in the JSON Template Approach to generate code and deploy the agent.

## Python Script Approach

For more complex agents or programmatic creation, you can use a Python script.

### Create and Deploy with a Script

```python
from backend.agents.agent_generator import AgentGenerator
from backend.database.repository import AgentRepository

# Create agent definition
agent_definition = {
    "agent": {
        "name": "my_new_agent",
        "type": "Utility",
        "description": "A new agent that does something useful",
        "systemPrompt": "You are a helpful assistant...",
        "icon": "🤖",
        "tools": [
            {
                "name": "my_tool",
                "description": "A tool that does something",
                "parameters": [
                    {
                        "name": "param1",
                        "type": "string",
                        "description": "A parameter"
                    }
                ],
                "returns": {
                    "type": "string",
                    "description": "The result"
                },
                "implementation": {
                    "code": """
def my_tool(param1: str) -> str:
    # Complex implementation here
    return f"Processed: {param1}"
                    """
                }
            }
        ],
        "capabilities": ["capability1", "capability2"]
    }
}

# Create agent generator
generator = AgentGenerator()

# Validate definition
generator.validate_definition(agent_definition)

# Save to database
agent, tools, capabilities = generator.save_definition_to_db(agent_definition)
print(f"Created agent with ID {agent.id}")

# Generate code
code = generator.generate_agent_class_from_db(agent.id)
print(f"Generated code: {len(code)} characters")

# Deploy agent
agent_obj = generator.register_agent_from_definition(agent.id, model="gpt-4", sandbox=True)
print(f"Deployed agent: {agent_obj.name}")
```

Save this script as `create_agent.py` and run it with:

```bash
cd mosaic
python create_agent.py
```

## UI-Based Approach

MOSAIC provides a web-based UI for creating agents without writing code.

### Step 1: Access the Agent Creation UI

Navigate to `http://localhost:3000/agents/create` in your browser.

### Step 2: Define Agent Metadata

Fill in the agent metadata form:
- Name: A unique identifier for the agent
- Type: The type of agent (Utility, Specialized, Supervisor)
- Description: A human-readable description of the agent
- System Prompt: Instructions for the agent
- Icon: An emoji icon for the agent

### Step 3: Add Tools

For each tool:
1. Click "Add Tool"
2. Fill in the tool metadata:
   - Name: A unique identifier for the tool
   - Description: A human-readable description of the tool
3. Define parameters:
   - Click "Add Parameter" for each parameter
   - Specify name, type, description, and whether it's required
4. Define the return type and description
5. Implement the tool:
   - Write Python code that implements the tool's functionality

### Step 4: Add Capabilities

Add capabilities that describe what the agent can do.

### Step 5: Validate and Save

1. Click "Validate" to check the agent definition
2. Click "Save" to save the agent to the database
3. Click "Deploy" to deploy the agent

## Agent Structure

### Agent Definition Schema

The agent definition follows this schema:

```json
{
  "agent": {
    "name": "string",
    "type": "string",
    "description": "string",
    "systemPrompt": "string",
    "icon": "string",
    "tools": [
      {
        "name": "string",
        "description": "string",
        "parameters": [
          {
            "name": "string",
            "type": "string",
            "description": "string",
            "required": "boolean"
          }
        ],
        "returns": {
          "type": "string",
          "description": "string"
        },
        "implementation": {
          "code": "string",
          "dependencies": ["string"]
        }
      }
    ],
    "capabilities": ["string"],
    "metadata": {
      "key": "value"
    }
  }
}
```

### Tool Implementation

Tools are implemented as Python functions with the following structure:

```python
def tool_name(param1: type1, param2: type2, ...) -> return_type:
    """
    Tool description.
    
    Args:
        param1: Parameter 1 description
        param2: Parameter 2 description
        
    Returns:
        Return value description
    """
    # Implementation
    return result
```

## Best Practices

### Agent Design

1. **Clear Purpose**: Define a clear, specific purpose for your agent
2. **Descriptive Name**: Use a name that clearly indicates the agent's function
3. **Comprehensive System Prompt**: Provide detailed instructions in the system prompt
4. **Focused Tools**: Create tools that perform specific, well-defined tasks
5. **Proper Error Handling**: Implement error handling in your tools
6. **Descriptive Parameters**: Use clear names and descriptions for parameters
7. **Documentation**: Document your agent and its tools thoroughly

### Tool Implementation

1. **Type Hints**: Always use type hints for parameters and return values
2. **Docstrings**: Include docstrings that explain what the tool does
3. **Input Validation**: Validate inputs before processing
4. **Error Handling**: Handle exceptions gracefully
5. **Logging**: Use logging to track tool execution
6. **Idempotency**: Make tools idempotent when possible
7. **Performance**: Optimize for performance when necessary

## Troubleshooting

### Common Issues

1. **Validation Errors**:
   - Check that your agent definition follows the schema
   - Ensure all required fields are present
   - Verify that types are correct

2. **Deployment Errors**:
   - Check that the agent ID exists in the database
   - Verify that the code generation was successful
   - Ensure the model is available

3. **Tool Execution Errors**:
   - Check for syntax errors in the tool implementation
   - Verify that dependencies are installed
   - Ensure input validation is correct

### Debugging

1. **Check Logs**:
   - Backend logs: `backend/logs/`
   - Frontend logs: Browser console

2. **Validate JSON**:
   - Use a JSON validator to check your template
   - Ensure the JSON is well-formed

3. **Test Tools Individually**:
   - Create a test script to test each tool
   - Verify that tools work as expected

4. **Check Database**:
   - Query the database to check agent metadata
   - Verify that tools and capabilities are saved correctly

For more help, refer to the [Backend README](backend/README.md) and [Agents README](backend/agents/README.md).
