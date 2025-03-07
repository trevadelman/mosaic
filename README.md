# MOSAIC: Multi-agent Orchestration System for Adaptive Intelligent Collaboration

MOSAIC is a production-ready system for creating, managing, and interacting with intelligent agents. It builds upon the proof-of-concept multi-agent orchestration system to create a robust, extensible platform for agent-based applications.

## Quick Start

**New to MOSAIC?** Check out these beginner-friendly guides to get started quickly:

- [**QUICKSTART.md**](QUICKSTART.md): Simple step-by-step instructions to get MOSAIC up and running
- [**Creating Agents**](backend/agents/CREATING_AGENTS.md): Learn how to create your own custom agents
- [**Creating Agent UIs**](backend/agents/CREATING_AGENT_UIS.md): Create specialized user interfaces for your agents

These guides are designed to be accessible even if you're new to programming or AI systems.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Docker Environment                                │
│                                                                             │
│  ┌──────────────────┐           ┌──────────────────────────┐                │
│  │                  │           │                          │                │
│  │  Next.js         │           │  FastAPI Backend         │                │
│  │  Frontend        │◄─────────►│                          │                │
│  │  (Port 3000)     │   REST    │  (Port 8000)             │                │
│  │                  │    +      │                          │                │
│  │  - UI Components │  WebSocket│  - API Endpoints         │                │
│  │  - Chat Interface│           │  - WebSocket Server      │    ┌─────────┐ │
│  │  - Agent UI      │           │  - Agent Discovery       │◄──►│ SQLite  │ │
│  │  - Specialized   │           │  - Database Access       │    │ Database│ │
│  │    UI Components │           │                          │    └─────────┘ │
│  │                  │           │                          │                │
│  └────────┬─────────┘           └──────────┬───────────────┘                │
│           │                               │                                 │
│           │                               ▼                                 │
│           │                   ┌──────────────────────────┐                  │
│           │                   │                          │                  │
│           │                   │  Agent System            │                  │
│           │                   │                          │                  │
│           └───────────────────►  - Base Agent Framework  │                  │
│                               │  - Specialized Agents    │                  │
│             Direct            │  - Supervisor System     │                  │
│             Agent-UI          │  - Agent UI Components   │                  │
│             Communication     │  - Agent Tools           │                  │
│                               │                          │                  │
│                               └──────────────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

- **Next.js Frontend**: Modern, responsive UI with shadcn components
- **User Authentication**: Secure authentication with Clerk
- **FastAPI Backend**: High-performance Python API with WebSocket support
- **Agent Framework**: Flexible, extensible agent system built on LangChain and LangGraph
- **Agent UI Framework**: Rich, interactive UI components for specialized agent interfaces
- **Regular Agents**:
  - **Calculator Agent**: Performs mathematical operations
  - **Web Search Agent**: Searches the web and retrieves webpage content
  - **Browser Interaction Agent**: Handles JavaScript-heavy websites
  - **Data Processing Agent**: Extracts and normalizes information
  - **Literature Agent**: Searches for academic papers and articles
  - **Safety Agent**: Validates agent actions for safety
  - **Writer Agent**: Handles file operations
  - **Agent Creator Agent**: Creates and deploys new agents
  - **Financial Analysis Agent**: Analyzes stock data and provides financial insights
- **Supervisor Agents**:
  - **Calculator Supervisor**: Orchestrates the calculator agent
  - **Research Supervisor**: Orchestrates multiple agents for comprehensive research tasks
  - **Multi-Agent Supervisor**: Generic supervisor that can orchestrate any combination of agents
  - **Financial Supervisor**: Orchestrates financial analysis tasks
- **UI Components**:
  - **Stock Chart Component**: Interactive stock chart visualization
  - **Data Visualization Component**: Comprehensive charting capabilities
  - **Research Paper Component**: Academic paper search and visualization
- **Dynamic Agent Discovery**: Automatically discovers and registers both regular agents and supervisors
- **Database-Driven Agent Metadata**: Store and manage agent definitions, tools, and capabilities in the database
- **JSON Template Integration**: Convert between JSON templates and database records for agent definitions
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

4. For authentication, create a `.env.local` file in the frontend directory:
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
   ```
   
   You can get these keys by creating a Clerk account at https://clerk.dev and setting up a new application.

### Testing the System

#### Calculator Agent Test

The simplest way to test the agent system is to run the calculator agent test script:

```bash
python -m mosaic.backend.tests.test_calculator
```

This will start an interactive session where you can test the calculator agent's capabilities.

#### Research Supervisor Test

To test the more advanced research supervisor that orchestrates multiple agents:

```bash
python -m mosaic.backend.tests.test_research_supervisor
```

This will start an interactive session where you can test the research supervisor's capabilities, including:
- Web search and content retrieval
- Browser interaction with JavaScript-heavy sites
- Data extraction and normalization
- Academic literature search

Example queries you can try:
- "Research the latest iPhone model and its features"
- "Find information about Tesla's newest electric vehicle"
- "Research academic papers on machine learning for image recognition"
- "Compare features of top gaming laptops"

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

#### Option 3: Running with Docker

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the mosaic directory with your OpenAI API key and Clerk authentication keys:
   ```
   # OpenAI API Key
   OPENAI_API_KEY=your_api_key_here
   
   # Clerk Authentication Keys
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   ```
   
   These environment variables will be passed to the Docker containers through the docker-compose.yml configuration.

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

6. To rebuild the containers while preserving conversation history:
   ```bash
   # Stop containers but keep volumes
   docker-compose -f docker/docker-compose.yml down

   # Rebuild and start containers
   docker-compose -f docker/docker-compose.yml up --build
   ```

   The system uses a named Docker volume (`mosaic-db-data`) to persist the database across container rebuilds. This ensures your conversation history is preserved even when you rebuild the containers with updated code.

   Note: Anonymous volumes (like the one used for frontend node_modules) are automatically removed when you run `docker-compose down` without the `-v` flag.

7. If you want to completely reset the database and start fresh:
   ```bash
   # Stop containers and remove ALL volumes (including database)
   docker-compose -f docker/docker-compose.yml down -v

   # Rebuild and start containers
   docker-compose -f docker/docker-compose.yml up --build
   ```

8. For development with frequent frontend package changes:
   ```bash
   # Remove only frontend container and its anonymous volumes
   docker-compose -f docker/docker-compose.yml rm -f -s -v frontend

   # Rebuild only the frontend
   docker-compose -f docker/docker-compose.yml up -d --build frontend
   ```

   This approach allows you to rebuild the frontend with fresh node_modules while preserving the database and other containers.

## Project Structure

```
mosaic/
├── docker/         # Docker configuration files
├── frontend/       # Next.js frontend application
├── backend/        # FastAPI backend application
│   ├── app/        # FastAPI application
│   ├── agents/     # Agent system
│   │   ├── base.py           # Base agent framework
│   │   ├── regular/          # Regular (specialized) agents
│   │   ├── supervisors/      # Supervisor agents
│   │   ├── sandbox/          # Sandbox environment for testing
│   │   └── templates/        # Templates for creating new agents
│   ├── database/   # Database models and operations
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── repository.py     # Repository classes for database operations
│   │   ├── database.py       # Database connection management
│   │   └── migrations/       # Database migration scripts
│   └── tests/      # Test scripts
├── database/       # SQLite database files
├── setup.py        # Package setup file
└── ROADMAP.md      # Development roadmap
```

## Development

See the [ROADMAP.md](ROADMAP.md) file for the current development status and upcoming features.

## Documentation

### Creating Agents

For detailed instructions on creating new agents, see the [Creating Agents Guide](backend/agents/CREATING_AGENTS.md). This guide covers:

- Different approaches to creating agents (JSON templates, API, Python scripts, UI)
- Agent structure and schema
- Best practices for agent design and tool implementation
- Troubleshooting common issues

### Component Documentation

- [Backend README](backend/README.md): Documentation for the backend components
  - API endpoints
  - Database models
  - Server configuration
  
- [Frontend README](frontend/README.md): Documentation for the frontend components
  - UI components
  - State management
  - Routing
  
- [Agents README](backend/agents/README.md): Documentation for the agent system
  - Agent framework
  - Tool development
  - Supervisor system

## Authentication with Clerk

MOSAIC uses [Clerk](https://clerk.dev) for user authentication and management. Clerk provides a secure, feature-rich authentication system that includes:

- User sign-up and sign-in
- Social login options
- Multi-factor authentication
- User profile management
- Session management

### Setting Up Clerk

1. Create an account at [Clerk.dev](https://clerk.dev)
2. Create a new application in the Clerk dashboard
3. Configure your application settings:
   - Set the allowed domains to include your development and production domains
   - Configure the authentication methods you want to support
   - Set up the appearance and branding options

4. Get your API keys from the Clerk dashboard:
   - Publishable Key: Used by the frontend to initialize Clerk
   - Secret Key: Used by the backend to verify authentication

5. Add these keys to your environment:
   - For local development: Add to `.env.local` in the frontend directory
   - For Docker: Add to the main `.env` file

### User Data in MOSAIC

When a user authenticates with Clerk, MOSAIC associates their user ID with:
- Chat conversations
- Agent interactions
- User preferences
- Uploaded files and attachments

This ensures that each user's data is private and only accessible to them when they're logged in.

## Troubleshooting

See the component-specific README files for troubleshooting information.

## License

[MIT License](LICENSE)
