# Modular AI Architecture

A modular, visual AI system architecture that enables hierarchical modeling of AI-enhanced software systems with YAML-based module definitions, interactive visualization, and surrogate execution capabilities.

## Features

- **Interactive Vue 3 + vis.js Visualization**: Network graph with hierarchical layout and smooth interactions
- **Module Definition System**: YAML-based schemas with validation
- **Surrogate Execution**: Pluggable placeholder behaviors (static + mock-LLM)
- **Real-time Interactions**: Node selection, module details panel, dependency navigation
- **Responsive Design**: Modern UI with proper accessibility and error handling

## Technology Stack

### Frontend: Vue 3 + vis.js

**Decision**: Vue 3 with vis.js was chosen for the interactive visualization.

**Rationale**:
- **Vue 3 Composition API**: Modern reactive framework with excellent TypeScript support
- **vis.js Network**: Mature library specifically designed for network graph visualization
- **Component Architecture**: Clean separation of concerns with reusable components
- **State Management**: Pinia store for reactive state across components
- **Performance**: Optimized rendering with physics simulation controls

### Backend: Flask + Python

**Decision**: Flask provides a lightweight API layer for the Python-based module system.

**Benefits**:
- **Simple Integration**: Easy integration with existing Python module loading system
- **YAML Processing**: Native Python support for YAML module definitions
- **RESTful API**: Clean API endpoints for frontend integration
- **Development Tools**: Built-in debugging and development server

## Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   # Backend dependencies (virtual environment .venv should already exist)
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Start the development servers:**
   ```bash
   # Automated startup (recommended)
   ./start_servers.sh
   
   # Manual startup (if needed)
   python -m flask --app app.py run --debug &
   cd frontend && npm run dev
   ```

4. **Open the application:**
   - **Frontend**: http://localhost:3001
   - **Backend API**: http://localhost:5000

## Usage

- **Navigate**: Use mouse wheel to zoom, drag to pan the network graph
- **Select Modules**: Click any module node to view detailed information in the side panel
- **View Dependencies**: See module relationships and dependencies in the details panel
- **Status Visualization**: Modules are color-coded by status (green=implemented, yellow=placeholder, red=error)
- **Live Editing**: Modify YAML files in the `/modules/` directory - changes are reflected on page refresh


## Server Management

### Quick Commands
```bash
# Start both servers with port conflict handling
./start_servers.sh

# Kill processes on development ports (5000, 3001)
./kill_ports.sh
```

### Manual Management
```bash
# Check what's using ports
lsof -i :5000  # Backend
lsof -i :3001  # Frontend

# Stop servers by PID (shown in start_servers.sh output)
kill <backend_pid> <frontend_pid>
```

### Troubleshooting
```bash
# If you get "Address already in use" errors
./kill_ports.sh
./start_servers.sh

# Check server status
curl http://localhost:5000/api/modules  # Backend health check
curl http://localhost:3001              # Frontend health check
```


## Architecture

The system consists of:

### Backend Components
- **Module Loader**: Validates and loads YAML module definitions from `/modules/` directory
- **Graph Builder**: Converts modules into network visualization data
- **Flask API**: RESTful endpoints for module data and operations (`/api/modules`, `/api/surrogates`)
- **Surrogate Registry**: Pluggable execution engine for module testing

### Frontend Components
- **Vue 3 Application**: Modern reactive UI framework with TypeScript support
- **vis.js Network**: Interactive graph visualization with physics simulation
- **Module Store**: Pinia-based state management for module data
- **Component Library**: Reusable UI components (GraphView, ModulePanel, etc.)
- **API Service**: Axios-based HTTP client for backend communication

## Contributing

All modules are defined in YAML format in the `/modules/` directory. See `docs/schema.md` for the complete schema specification. 