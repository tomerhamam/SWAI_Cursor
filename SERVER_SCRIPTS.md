# Server Management Scripts

## Quick Start

**To start both servers with automatic port conflict resolution:**
```bash
./start_servers.sh
```

**To just clear port conflicts:**
```bash
./kill_ports.sh
```

## Scripts Overview

### `start_servers.sh` - Complete Server Startup
- **Purpose**: Handles port conflicts and starts both backend and frontend servers
- **Features**:
  - Automatically detects port conflicts (5000, 3001)
  - Offers to kill conflicting processes or finds alternative ports
  - Starts Flask backend with correct command: `python -m flask --app app.py run --debug`
  - Starts Vue frontend on port 3001
  - Provides server URLs and PIDs for easy management
  - Allows Ctrl+C to stop both servers

### `kill_ports.sh` - Port Cleanup
- **Purpose**: Quickly kills processes on ports 5000 and 3001
- **Use case**: When you get "Address already in use" errors
- **Safe**: Only affects the specific ports used by this project

## Common Usage Patterns

**Normal development startup:**
```bash
./start_servers.sh
# Opens browser to http://localhost:3001
```

**When getting port conflicts:**
```bash
./kill_ports.sh
./start_servers.sh
```

**Manual startup (if needed):**
```bash
# Backend
python -m flask --app app.py run --debug

# Frontend (in separate terminal)
cd frontend && npm run dev
```

## Troubleshooting

**If scripts don't run:**
```bash
chmod +x start_servers.sh kill_ports.sh
```

**If lsof command not found:**
```bash
# Ubuntu/Debian
sudo apt install lsof

# macOS
brew install lsof
```

**Check what's using a port:**
```bash
lsof -i :5000  # Check port 5000
lsof -i :3001  # Check port 3001
``` 