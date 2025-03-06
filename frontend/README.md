# MOSAIC Frontend

This directory contains the frontend components of the MOSAIC system, built with Next.js, TypeScript, and shadcn/ui.

## System Architecture

The MOSAIC frontend consists of several key components:

1. **Next.js Application**: Provides the core framework for the frontend
2. **UI Components**: Reusable components built with shadcn/ui
3. **API Client**: Communicates with the backend API
4. **WebSocket Client**: Handles real-time communication with the backend

## Directory Structure

The frontend is organized into the following directories:

- **app/**: Next.js app directory containing pages and routes
  - **agents/**: Agent listing page
  - **chat/**: Chat interface for interacting with agents
  - **community/**: Community page
  - **settings/**: Settings page
- **components/**: Reusable UI components
  - **agents/**: Agent-related components
  - **chat/**: Chat interface components
  - **sidebar/**: Navigation sidebar
  - **ui/**: Base UI components from shadcn/ui
- **lib/**: Utility functions and API clients
  - **contexts/**: React context providers
  - **hooks/**: Custom React hooks

## How to Test the Frontend

### Prerequisites

1. Node.js 18 or higher
2. npm or yarn

### Setting Up the Environment

1. Install dependencies:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms/mosaic/frontend
   npm install
   ```

2. Create a `.env.local` file in the frontend directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Running the Development Server

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms/mosaic/frontend
npm run dev
```

This will start the Next.js development server on http://localhost:3000.

## Integration with Backend

The frontend communicates with the backend through:

1. **REST API Calls**:
   - `GET /api/agents`: Get a list of all available agents
   - `GET /api/agents/{agent_id}`: Get information about a specific agent
   - `POST /api/agents/{agent_id}/messages`: Send a message to an agent
   - `GET /api/agents/{agent_id}/messages`: Get all messages for a specific agent

2. **WebSocket Connection**:
   - `/ws/chat/{agent_id}`: Real-time communication for agent responses and logs

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
   npm run dev
   ```

3. Open your browser to http://localhost:3000 to access the MOSAIC interface.

## Key Components

### Pages

- **Home Page**: Landing page with introduction to MOSAIC
- **Chat Page**: Interface for interacting with agents
- **Agents Page**: Overview of available agents
- **Settings Page**: Configuration options for the application

### Components

- **Sidebar**: Navigation sidebar for the application
- **Chat Interface**: Components for the chat interface
- **Agent Visualization**: Components for visualizing agent responses
- **Theme Provider**: Handles dark/light theme switching

## Development Guidelines

1. **Component Structure**: Follow the shadcn/ui component structure
2. **State Management**: Use React hooks for state management
3. **API Calls**: Use the API client for all backend communication
4. **WebSocket**: Use the WebSocket client for real-time communication
5. **Styling**: Use Tailwind CSS for styling components

## Troubleshooting

### API Connection Issues

If you encounter issues connecting to the backend API, make sure the backend server is running and that the `NEXT_PUBLIC_API_URL` environment variable is set correctly.

### WebSocket Connection Issues

If the WebSocket connection fails, make sure the backend server is running and that there are no network restrictions blocking WebSocket connections.

### Build Errors

If you encounter build errors, try cleaning the Next.js cache:

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms/mosaic/frontend
rm -rf .next
npm run dev
```
