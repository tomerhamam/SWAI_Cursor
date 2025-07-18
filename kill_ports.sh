#!/bin/bash

# Quick Port Cleanup Script for SWAI Cursor
# Kills processes on ports 5000 and 3001

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 SWAI Cursor Port Cleanup${NC}"
echo "============================"

# kill_port terminates the first process found listening on the specified port, displaying status messages for success, failure, or if the port is already free.
kill_port() {
    local port=$1
    local process_info=$(lsof -i :$port 2>/dev/null | grep LISTEN | awk '{print $2, $1}' | head -1)
    
    if [ -n "$process_info" ]; then
        local pid=$(echo $process_info | awk '{print $1}')
        local name=$(echo $process_info | awk '{print $2}')
        
        echo -e "${YELLOW}🔍 Found process on port $port: $name (PID: $pid)${NC}"
        
        if kill -9 $pid 2>/dev/null; then
            echo -e "${GREEN}✅ Killed process $name (PID: $pid) on port $port${NC}"
        else
            echo -e "${RED}❌ Failed to kill process on port $port${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port $port is already free${NC}"
    fi
}

# Kill common development ports
echo -e "${BLUE}🔍 Checking port 5000 (Flask backend)...${NC}"
kill_port 5000

echo -e "${BLUE}🔍 Checking port 3001 (Vue frontend)...${NC}"
kill_port 3001

echo
echo -e "${GREEN}🎉 Port cleanup complete!${NC}"
echo -e "${YELLOW}💡 You can now run: ./start_servers.sh${NC}" 