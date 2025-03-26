# MOSAIC Quickstart Guide

Welcome to MOSAIC! This guide will help you get up and running quickly, even if you're new to programming or don't have development tools installed yet.

## What is MOSAIC?

MOSAIC is a platform that lets you interact with intelligent agents through chat and build custom applications. You can:

- Chat with intelligent agents for various tasks
- Build custom applications using our framework
- Create new agents for specific use cases
- Integrate with external services and APIs

## Getting Started

### Step 1: Install Required Software

Before you can run MOSAIC, you'll need to install a few things:

#### Python (Required)

1. Visit [python.org](https://www.python.org/downloads/) and download the latest version (3.11 or higher)
2. Run the installer and make sure to check "Add Python to PATH" during installation
3. Verify installation by opening a terminal/command prompt and typing:
   ```
   python --version
   ```

#### Node.js (Required for Frontend)

1. Visit [nodejs.org](https://nodejs.org/) and download the LTS version
2. Run the installer with default settings
3. Verify installation by opening a terminal/command prompt and typing:
   ```
   node --version
   npm --version
   ```

#### Docker (Optional - for containerized deployment)

If you want to run MOSAIC in containers (recommended for advanced users):
1. Visit [docker.com](https://www.docker.com/products/docker-desktop/) and download Docker Desktop
2. Install and start Docker Desktop
3. Verify installation by opening a terminal/command prompt and typing:
   ```
   docker --version
   ```

### Step 2: Get an OpenAI API Key

MOSAIC uses OpenAI's language models, so you'll need an API key:

1. Visit [OpenAI's website](https://platform.openai.com/signup) and create an account
2. Go to the [API keys page](https://platform.openai.com/api-keys)
3. Click "Create new secret key" and save it somewhere safe (you'll need it later)

### Step 3: Set Up MOSAIC

1. Open a terminal/command prompt
2. Navigate to the MOSAIC directory (where you cloned the repository)
3. Create a virtual environment (this keeps MOSAIC's dependencies separate from other Python projects):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
5. Install MOSAIC and its dependencies:
   ```
   pip install -e .
   ```
6. Create a `.env` file in the mosaic directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with the API key you got from OpenAI.

7. (Optional) Set up authentication:
   - By default, MOSAIC will run without authentication for local development
   - If you want to enable user authentication, you'll need to set up Clerk:
     1. Create an account at [Clerk.dev](https://clerk.dev)
     2. Create a new application in the Clerk dashboard
     3. Get your API keys from the dashboard
     4. Create a `.env.local` file in the frontend directory with:
        ```
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key
        CLERK_SECRET_KEY=your_secret_key
        NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
        NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
        NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
        NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
        ```

### Step 4: Start MOSAIC

#### Option 1: Using the Startup Script (Easiest)

1. Make sure you're in the mosaic directory
2. Run the startup script:
   - On Windows:
     ```
     startup.bat
     ```
   - On macOS/Linux:
     ```
     ./startup.sh
     ```
3. Open your web browser and go to http://localhost:3000

#### Option 2: Starting Services Manually

If the startup script doesn't work for you, you can start the services manually:

1. Start the backend server:
   - Make sure your virtual environment is activated
   - Run:
     ```
     python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
     ```

2. In a new terminal window, start the frontend:
   - Navigate to the frontend directory:
     ```
     cd mosaic/frontend
     ```
   - Install frontend dependencies:
     ```
     npm install
     ```
   - Start the frontend server:
     ```
     npm run dev
     ```

3. Open your web browser and go to http://localhost:3000

## Using MOSAIC

Once MOSAIC is running, you can:

1. **Chat with Agents**: Select an agent from the sidebar and start chatting
2. **Build Applications**: Create custom applications using our framework
3. **Create Agents**: Develop new agents for specific use cases
4. **Integrate Services**: Connect with external APIs and services

## Development Guides

MOSAIC provides comprehensive guides for development:

1. **Custom Applications**
   - Follow the [Custom Application Guide](frontend/app/apps/CREATING_A_CUSTOM_APPLICATION.md)
   - Learn about the application framework
   - See examples of complex applications
   - Understand best practices

2. **Agent Development**
   - Check out the [Agent Creation Guide](backend/agents/CREATING_A_NEW_AGENT.md)
   - Learn about agent capabilities
   - Understand the agent lifecycle
   - Implement custom tools

## Troubleshooting

### Common Issues

- **"Command not found" errors**: Make sure Python and Node.js are installed and added to your PATH
- **Backend won't start**: Check that you've activated the virtual environment and installed dependencies
- **Frontend won't start**: Make sure you've installed the frontend dependencies with `npm install`
- **API errors**: Verify your OpenAI API key is correct and has sufficient credits

### Getting Help

If you encounter problems:

1. Check the terminal output for error messages
2. Look at the browser console for frontend errors (press F12 in most browsers)
3. Restart both the backend and frontend services
4. Check the [GitHub repository](https://github.com/yourusername/mosaic) for updates or issues

## Next Steps

Once you're comfortable with the basics:

- Explore different agents and their capabilities
- Check out the [documentation](README.md) for more detailed information
- Learn how to [create your own agents](backend/agents/CREATING_A_NEW_AGENT.md)
- Learn how to [create custom applications](frontend/app/apps/CREATING_A_CUSTOM_APPLICATION.md)
- Explore the [example applications](frontend/app/apps) in the codebase

Happy exploring!
