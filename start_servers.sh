#!/bin/bash

# SWAI Cursor Server Startup Script
# Handles port conflicts and starts both backend and frontend servers

set -e  # Exit on any error

PROJECT_ROOT="/home/thh3/work/SWAI_Cursor"
BACKEND_PORT=5000
FRONTEND_PORT=3001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SWAI Cursor Server Startup Script${NC}"
echo "======================================"

# check_port checks if the specified TCP port is currently in use by any process. Returns 0 if in use, 1 if free.
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# get_port_process outputs the PID and process name of the process listening on the specified port.
get_port_process() {
    local port=$1
    lsof -i :$port | grep LISTEN | awk '{print $2, $1}' | head -1
}

# kill_port_process attempts to terminate the process occupying the specified port, prompting the user for confirmation, and returns success if the port is freed or was already free.
kill_port_process() {
    local port=$1
    echo -e "${YELLOW}🔍 Finding process on port $port...${NC}"
    
    local process_info=$(get_port_process $port)
    if [ -n "$process_info" ]; then
        local pid=$(echo $process_info | awk '{print $1}')
        local name=$(echo $process_info | awk '{print $2}')
        
        echo -e "${RED}⚠️  Port $port is in use by: $name (PID: $pid)${NC}"
        
        read -p "Kill this process? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $pid 2>/dev/null || true
            sleep 1
            if check_port $port; then
                echo -e "${RED}❌ Failed to kill process on port $port${NC}"
                return 1
            else
                echo -e "${GREEN}✅ Successfully killed process on port $port${NC}"
                return 0
            fi
        else
            echo -e "${YELLOW}⚠️  Skipping port $port cleanup${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✅ Port $port is free${NC}"
        return 0
    fi
}

# find_available_port searches for a free TCP port starting from the given port and returns the first available one within a range of 11 ports; exits with an error if none are found.
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while check_port $port; do
        ((port++))
        if [ $port -gt $((start_port + 10)) ]; then
            echo -e "${RED}❌ Could not find available port near $start_port${NC}"
            exit 1
        fi
    done
    
    echo $port
}

# Navigate to project root
echo -e "${BLUE}📁 Navigating to project root...${NC}"
cd "$PROJECT_ROOT" || {
    echo -e "${RED}❌ Failed to navigate to $PROJECT_ROOT${NC}"
    exit 1
}

# Check backend port
echo -e "${BLUE}🔍 Checking backend port $BACKEND_PORT...${NC}"
if check_port $BACKEND_PORT; then
    if ! kill_port_process $BACKEND_PORT; then
        echo -e "${YELLOW}🔄 Finding alternative port for backend...${NC}"
        BACKEND_PORT=$(find_available_port $BACKEND_PORT)
        echo -e "${GREEN}✅ Using port $BACKEND_PORT for backend${NC}"
    fi
else
    echo -e "${GREEN}✅ Port $BACKEND_PORT is available for backend${NC}"
fi

# Check frontend port
echo -e "${BLUE}🔍 Checking frontend port $FRONTEND_PORT...${NC}"
if check_port $FRONTEND_PORT; then
    if ! kill_port_process $FRONTEND_PORT; then
        echo -e "${YELLOW}🔄 Finding alternative port for frontend...${NC}"
        FRONTEND_PORT=$(find_available_port $FRONTEND_PORT)
        echo -e "${GREEN}✅ Using port $FRONTEND_PORT for frontend${NC}"
    fi
else
    echo -e "${GREEN}✅ Port $FRONTEND_PORT is available for frontend${NC}"
fi

# Start backend server
echo -e "${BLUE}🐍 Starting Flask backend server...${NC}"
if [ $BACKEND_PORT -eq 5000 ]; then
    python -m flask --app app.py run --debug &
else
    python -m flask --app app.py run --debug --port $BACKEND_PORT &
fi

BACKEND_PID=$!
sleep 2

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}❌ Backend server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID, Port: $BACKEND_PORT)${NC}"

# Start frontend server
echo -e "${BLUE}⚛️  Starting Vue frontend server...${NC}"
cd frontend || {
    echo -e "${RED}❌ Failed to navigate to frontend directory${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
}

if [ $FRONTEND_PORT -eq 3001 ]; then
    npm run dev &
else
    npx vite --port $FRONTEND_PORT &
fi

FRONTEND_PID=$!
sleep 3

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}❌ Frontend server failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID, Port: $FRONTEND_PORT)${NC}"

# Display server information
echo
echo -e "${GREEN}🎉 Both servers started successfully!${NC}"
echo "========================================"
echo -e "${BLUE}Backend:${NC}  http://localhost:$BACKEND_PORT"
echo -e "${BLUE}Frontend:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${BLUE}API Test:${NC} http://localhost:$BACKEND_PORT/api/modules"
echo
echo -e "${YELLOW}📝 Server PIDs:${NC}"
echo -e "   Backend:  $BACKEND_PID"
echo -e "   Frontend: $FRONTEND_PID"
echo
echo -e "${YELLOW}🛑 To stop servers:${NC}"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   OR press Ctrl+C in this terminal"

# Wait for servers (allows Ctrl+C to kill both)
wait 