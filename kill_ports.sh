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

# kill_port terminates all processes found listening on the specified port, displaying status messages for success, failure, or if the port is already free.
kill_port() {
    local port=$1
    
    # Try lsof first
    local process_info=$(lsof -i :$port 2>/dev/null | grep LISTEN | awk '{print $2, $1}')
    
    # If lsof didn't find anything, try netstat (works better for some Node.js processes)
    if [ -z "$process_info" ]; then
        local netstat_result=$(netstat -tlnp 2>/dev/null | grep ":$port ")
        if [ -n "$netstat_result" ]; then
            local pid_program=$(echo "$netstat_result" | awk '{print $7}' | head -1)
            if [ "$pid_program" != "-" ] && [ -n "$pid_program" ]; then
                local pid=$(echo "$pid_program" | cut -d'/' -f1)
                local name=$(echo "$pid_program" | cut -d'/' -f2)
                process_info="$pid $name"
            fi
        fi
    fi
    
    if [ -n "$process_info" ]; then
        # Kill all processes found on this port
        echo "$process_info" | while read -r pid name; do
            if [ -n "$pid" ] && [ "$pid" -ne 0 ] 2>/dev/null; then
                echo -e "${YELLOW}🔍 Found process on port $port: $name (PID: $pid)${NC}"
                
                if kill -9 "$pid" 2>/dev/null; then
                    echo -e "${GREEN}✅ Killed process $name (PID: $pid) on port $port${NC}"
                else
                    echo -e "${RED}❌ Failed to kill process $pid on port $port${NC}"
                fi
            fi
        done
        
        # Give processes time to terminate
        sleep 1
        
        # Verify port is now free
        if lsof -i :$port >/dev/null 2>&1; then
            echo -e "${RED}⚠️  Port $port may still be in use${NC}"
        else
            echo -e "${GREEN}✅ Port $port is now free${NC}"
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