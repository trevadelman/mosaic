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
   # API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   
   # Clerk Authentication Keys
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   
   # Clerk URLs
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
   ```
   
   You can get the Clerk keys by creating an account at [Clerk.dev](https://clerk.dev) and setting up a new application.

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
- **Auth Pages**: Sign-in and sign-up pages for user authentication

### Authentication

The frontend uses [Clerk](https://clerk.dev) for user authentication and management. This provides:

- User sign-up and sign-in functionality
- Social login options
- User profile management
- Session management
- Protected routes

The authentication flow is handled by Clerk components and hooks:

- `<ClerkProvider>`: Wraps the application to provide authentication context
- `<SignInButton>` and `<SignOutButton>`: UI components for authentication actions
- `useAuth()` and `useUser()`: Hooks to access authentication state and user data

User authentication state is used throughout the application to:
- Show/hide authenticated content
- Associate chat conversations with specific users
- Personalize the user experience
- Secure API requests with user tokens

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
