# MOSAIC Backend

This directory contains the backend components of the MOSAIC system, including the FastAPI application, agent system, and database models.

## System Architecture

The MOSAIC backend consists of several key components:

1. **FastAPI Application**: Provides REST API endpoints and WebSocket connections for the frontend
2. **Agent System**: Implements the agent framework, specialized agents, and supervisor system
3. **Database Models**: Defines the data models for storing queries, responses, and agent configurations

## How to Test the System

### Prerequisites

1. Python 3.11 or higher
2. OpenAI API key (set in .env file)

### Setting Up the Environment

1. Create a virtual environment:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   pip install -e mosaic
   ```

   This installs the mosaic package in development mode, which means any changes you make to the code will be immediately reflected without needing to reinstall the package.

3. Create a .env file in the mosaic directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Testing the Calculator Agent

The simplest way to test the system is to run the calculator agent test script:

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
python -m mosaic.backend.test_calculator
```

This will start an interactive session where you can test the calculator agent's capabilities by entering mathematical expressions.

### Running the FastAPI Backend

To run the full backend server:

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

This will start the FastAPI server on http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## Integration with Frontend

The frontend communicates with the backend through:

1. **REST API Endpoints**:
   - `/api/query`: Submit a new query to the agent system
   - `/api/history`: Get the history of queries and responses

2. **WebSocket Connection**:
   - `/ws`: Real-time communication for agent responses and logs

## Testing the Full System

To test the full system (frontend + backend):

1. Start the backend server:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a separate terminal, start the frontend development server:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms/mosaic/frontend
   npm install  # Only needed the first time
   npm run dev
   ```

3. Open your browser to http://localhost:3000 to access the MOSAIC interface.

## Troubleshooting

### Module Not Found Errors

If you encounter "Module not found" errors, make sure you're running the commands from the root directory (/Users/trevoradelman/Documents/devStuff/langChainDev/swarms) and that the Python module structure is correctly set up.

### OpenAI API Key Issues

If you encounter authentication errors with the OpenAI API, check that your API key is correctly set in the .env file and that it has the necessary permissions.

### WebSocket Connection Issues

If the WebSocket connection fails, make sure both the frontend and backend are running and that there are no network restrictions blocking WebSocket connections.
