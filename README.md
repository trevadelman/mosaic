# MOSAIC: Multi-agent Orchestration System for Adaptive Intelligent Collaboration

MOSAIC is a production-ready system for creating, managing, and interacting with intelligent agents. It builds upon the proof-of-concept multi-agent orchestration system to create a robust, extensible platform for agent-based applications.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Environment                         │
│                                                                 │
│  ┌─────────────────┐           ┌──────────────────────────┐    │
│  │                 │           │                          │    │
│  │  Next.js        │           │  FastAPI Backend         │    │
│  │  Frontend       │◄─────────►│                          │    │
│  │  (Port 3000)    │   REST    │  (Port 8000)             │    │
│  │                 │    +      │                          │    │
│  │  - UI Components│  WebSocket│  - API Endpoints         │    │
│  │  - Chat Interface│          │  - WebSocket Server      │    │
│  │  - Agent UI     │           │  - Database Access       │    │
│  │                 │           │                          │    │
│  └─────────────────┘           └──────────┬───────────────┘    │
│                                           │                     │
│                                           ▼                     │
│                               ┌──────────────────────────┐     │
│                               │                          │     │
│                               │  Agent System            │     │
│                               │                          │     │
│                               │  - Base Agent Framework  │     │
│                               │  - Specialized Agents    │     │
│                               │  - Supervisor System     │     │
│                               │                          │     │
│                               └──────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

- **Next.js Frontend**: Modern, responsive UI with shadcn components
- **FastAPI Backend**: High-performance Python API with WebSocket support
- **Agent Framework**: Flexible, extensible agent system built on LangChain and LangGraph
- **Supervisor System**: Orchestrate multiple agents to solve complex problems
- **Calculator Agent**: Example agent that can perform mathematical operations
- **Docker Containerization**: Secure, isolated environments for development and deployment

## Getting Started

### Prerequisites

1. Python 3.11 or higher
2. Node.js 18 or higher
3. OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mosaic.git
   cd mosaic
   ```

2. Install the Python package in development mode:
   ```bash
   pip install -e .
   ```

3. Create a `.env` file in the mosaic directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Testing the System

#### Calculator Agent Test

The simplest way to test the agent system is to run the calculator agent test script:

```bash
python -m mosaic.backend.test_calculator
```

This will start an interactive session where you can test the calculator agent's capabilities.

#### Integration Test

To test the integration between the backend and frontend components:

```bash
python -m mosaic.test_integration
```

This script will:
1. Start the backend server
2. Test the API endpoints
3. Test the WebSocket connection
4. Report the test results

This is useful for verifying that the backend is correctly set up and can handle API requests and WebSocket connections.

### Running the Full System

#### Option 1: Using the Startup Script (Recommended)

1. Run the startup script:
   ```bash
   cd mosaic
   ./startup.sh
   ```

   This script will:
   - Start the backend server on port 8000
   - Start the frontend development server on port 3000
   - Display logs from both services in a single terminal

2. Open your browser to http://localhost:3000 to access the MOSAIC interface.

3. Press Ctrl+C to stop both services.

#### Option 2: Running Services Separately

1. Start the backend server:
   ```bash
   python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a separate terminal, start the frontend development server:
   ```bash
   cd frontend
   npm install  # Only needed the first time
   npm run dev
   ```

3. Open your browser to http://localhost:3000 to access the MOSAIC interface.

#### Option 2: Running with Docker

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the mosaic directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Build and start the containers:
   ```bash
   cd mosaic
   docker-compose -f docker/docker-compose.yml up --build
   ```

4. Open your browser to http://localhost:3000 to access the MOSAIC interface.

5. To stop the containers, press Ctrl+C in the terminal where docker-compose is running, or run:
   ```bash
   docker-compose -f docker/docker-compose.yml down
   ```

## Project Structure

```
mosaic/
├── docker/         # Docker configuration files
├── frontend/       # Next.js frontend application
├── backend/        # FastAPI backend application
│   ├── app/        # FastAPI application
│   ├── agents/     # Agent system
│   └── test_*.py   # Test scripts
├── database/       # SQLite database files
├── setup.py        # Package setup file
└── ROADMAP.md      # Development roadmap
```

## Development

See the [ROADMAP.md](ROADMAP.md) file for the current development status and upcoming features.

### Component Documentation

- [Backend README](backend/README.md): Documentation for the backend components
- [Frontend README](frontend/README.md): Documentation for the frontend components
- [Agents README](backend/agents/README.md): Documentation for the agent system

## Troubleshooting

See the component-specific README files for troubleshooting information.

## License

[MIT License](LICENSE)
