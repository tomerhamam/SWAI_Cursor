# Modular AI Architecture

A modular, visual AI system architecture that enables hierarchical modeling of AI-enhanced software systems with YAML-based module definitions, interactive visualization, and surrogate execution capabilities.

## Features

- **Interactive D3.js Visualization**: Force-directed diagram with smooth animations
- **Module Definition System**: YAML-based schemas with validation
- **Surrogate Execution**: Pluggable placeholder behaviors (static + mock-LLM)
- **Real-time Interactions**: Zoom, pan, drag, and click handling
- **Live Updates**: File watching and auto-refresh capabilities

## Technology Choices

### Visualization Library: D3.js

**Decision**: D3.js was chosen over Mermaid.js for the visualization layer.

**Rationale**:
- **Superior Interactivity**: D3.js provides much better support for complex user interactions like drag-and-drop, smooth zooming, and custom click handlers
- **Flexible Styling**: More control over visual appearance and animations
- **Force-Directed Layout**: Natural arrangement of nodes with physics simulation
- **Extensibility**: Easier to add advanced features like multi-select, custom layouts, and complex animations

**Trade-offs**:
- **Complexity**: More complex implementation than Mermaid.js
- **Bundle Size**: Larger JavaScript footprint
- **Learning Curve**: Steeper learning curve for contributors

The decision favors rich interactivity over simplicity, as this type of system visualization benefits significantly from smooth, responsive user interactions.

## Setup

1. Clone the repository
2. Set up Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open http://localhost:5000 in your browser

## Usage

- **Navigate**: Use mouse wheel to zoom, drag to pan the diagram
- **Interact**: Click any module node to view detailed information
- **Execute**: Use the "Run Surrogate" button to test module functionality
- **Live Edit**: Modify YAML files in the `/modules/` directory to see real-time updates


## To manage the server:
### Check if server is running
jobs -l

### Stop the server
kill %1

### View server logs
tail -f server.log

### Check what's using port 5000
lsof -i :5000


## Architecture

The system consists of:
- **Module Loader**: Validates and loads YAML module definitions
- **Graph Builder**: Converts modules into visualization data
- **Web Interface**: D3.js-powered interactive diagram
- **Surrogate Registry**: Pluggable execution engine
- **File Watcher**: Live reload system

## Contributing

All modules are defined in YAML format in the `/modules/` directory. See `docs/schema.md` for the complete schema specification. 