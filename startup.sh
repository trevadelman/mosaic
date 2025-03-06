#!/bin/bash

# Startup script for Mosaic project
# This script starts both the frontend and backend services

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Mosaic Startup Script ===${NC}"
echo -e "${YELLOW}Starting both frontend and backend services...${NC}"

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        echo -e "${YELLOW}Loading OPENAI_API_KEY from .env file...${NC}"
        export $(grep -v '^#' .env | xargs)
    else
        echo -e "${YELLOW}Warning: OPENAI_API_KEY not set. Please set it in your environment or .env file.${NC}"
    fi
fi

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start the backend
echo -e "${GREEN}Starting backend service...${NC}"
cd backend
# Add the parent directory to the Python path
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to initialize
sleep 2

# Start the frontend
echo -e "${GREEN}Starting frontend service...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}Services started:${NC}"
echo -e "  Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "  Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for both processes
wait $FRONTEND_PID $BACKEND_PID
