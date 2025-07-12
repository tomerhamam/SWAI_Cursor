# Modular AI Architecture

A system for hierarchical modeling of AI-enhanced software systems with interactive visualization and surrogate execution capabilities.

## Overview

This MVP implementation provides a complete workflow for defining, visualizing, and executing AI-enhanced software modules using a YAML-based configuration system. The system features real-time visualization, surrogate execution capabilities, and live file monitoring for rapid development cycles.

## Getting Started

### Prerequisites
- Python 3.11+
- Git

### Installation
1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start
```bash
# 1. Load and validate modules
python -m loader modules/ --validate-deps

# 2. Start the full application with live updates
python app.py

# 3. Open http://localhost:5000 in browser
```

### Command Line Interface

**Module Loading and Validation:**
```bash
# Load and validate all modules
python -m loader modules/

# Validate with dependency checking
python -m loader modules/ --validate-deps

# Validate specific module
python -m loader modules/auth_service.yaml
```

**Manual Visualization Generation:**
```bash
# Generate Mermaid diagram and JSON data
python graph_builder.py modules/

# Output: static/diagram.mmd and static/modules.json
```

**Development Servers:**
```bash
# Full application server with surrogate execution
python app.py
# → http://localhost:5000

# Static file server (diagram only)
python -m http.server 8000
# → http://localhost:8000

# Live file watcher (auto-regenerates on changes)
python watcher.py modules/
```

### Web Interface

The web interface provides a complete interactive experience:

1. **Interactive Diagram**
   - Pan and zoom to navigate the module hierarchy
   - Click any module node to view detailed information
   - Status-based color coding: Green (implemented), Yellow (placeholder), Red (error)
   - Dependency arrows show module relationships

2. **Side Panel Details**
   - Complete module information: name, description, inputs, outputs, status
   - Dependency lists with clickable links
   - Surrogate execution controls

3. **Surrogate Execution**
   - Click "Run Surrogate" to execute placeholder behaviors
   - Real-time execution with loading states
   - JSON output display for results
   - Choose between Static Stub and Mock LLM surrogates

4. **Live Updates**
   - Toggle auto-refresh to monitor file changes
   - Visual refresh indicators
   - Automatic diagram regeneration on YAML modifications

### Module Definition Format

Create YAML files in the `modules/` directory with the following structure:

```yaml
name: "example_module"
description: "Example module demonstrating the YAML format"
inputs:
  - name: "input_data"
    type: "string"
    description: "Input data description"
outputs:
  - name: "output_result"
    type: "object"
    description: "Output result description"
dependencies:
  - "dependency_module_name"
status: "placeholder"  # implemented, placeholder, or error
```

### Examples

The `modules/` directory contains sample modules demonstrating various patterns:

- **auth_service.yaml**: Authentication service with multiple outputs
- **user_interface.yaml**: UI component with dependency on auth service
- **data_processor.yaml**: Data processing module with complex inputs
- **ai_model.yaml**: AI model component with specific requirements
- **orchestrator.yaml**: Main orchestrator depending on all other modules

## Features

### ✅ Completed Features

- **Module Loading**: YAML-based module definitions with Pydantic validation
- **Interactive Visualization**: Mermaid.js diagram with clickable nodes and zoom controls
- **Status Highlighting**: Color-coded modules by implementation status
- **Side Panel Details**: Complete module information display on click
- **Dependency Visualization**: Arrows showing module relationships
- **Surrogate Execution**: Static stub and mock LLM surrogates with UI integration
- **Flask Backend**: REST API for module data and surrogate execution
- **Live Updates**: File watcher with auto-refresh capabilities
- **Professional UI**: Modern, responsive design with controls and indicators

### API Endpoints

The Flask backend provides the following REST endpoints:

- `GET /api/modules` - Retrieve all module data
- `POST /api/surrogate/<module_name>` - Execute surrogate for specific module
- `GET /api/surrogates` - List available surrogate types

### File Structure

```
.
├── app.py                 # Flask application server
├── graph_builder.py       # Mermaid diagram generation
├── loader.py             # Module loading and validation
├── surrogate.py          # Surrogate execution engine
├── watcher.py            # File monitoring and live updates
├── index.html            # Web interface
├── modules/              # YAML module definitions
│   ├── auth_service.yaml
│   ├── user_interface.yaml
│   ├── data_processor.yaml
│   ├── ai_model.yaml
│   └── orchestrator.yaml
├── static/               # Generated files
│   ├── diagram.mmd
│   └── modules.json
├── build_logs/           # Execution logs
│   └── llm_prompts.log
└── tests/                # Unit tests
    └── test_loader.py
```

### Development Workflow

1. **Edit YAML modules** in the `modules/` directory
2. **Run validation** with `python -m loader modules/ --validate-deps`
3. **Start live development** with `python app.py`
4. **Enable auto-refresh** in the web interface
5. **Make changes** to YAML files and see updates in real-time

### Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Current test coverage includes:
- Module loading and validation
- Dependency resolution
- YAML schema validation
- Error handling

## Architecture

Based on the Modular AI Architecture PRD - see `docs/` for detailed specifications.

### Tech Stack

- **Backend**: Python, Flask, Pydantic, Watchdog
- **Frontend**: HTML, CSS, JavaScript, Mermaid.js
- **Data**: YAML configuration files
- **Testing**: pytest

### Design Decisions

**Rendering Library: Mermaid.js**
- **Decision**: Mermaid.js chosen over D3.js for MVP
- **Rationale**: 
  - Faster development time (critical for 6-hour constraint)
  - Built-in styling and layout algorithms
  - Simpler syntax for rapid prototyping
  - Good enough interactivity for MVP requirements
  - Can upgrade to D3.js later if needed
- **Tradeoffs**: Less customization control, but sufficient for validation phase

**Surrogate Architecture**
- Abstract base class with registry pattern
- Pluggable surrogate implementations
- Extensible for future AI integrations

## Contributing

This is an active development project. See `docs/sw_plan.md` for implementation roadmap.

### Development Setup

1. Follow installation instructions above
2. Run tests to verify setup: `python -m pytest tests/`
3. Start development server: `python app.py`
4. Make changes and test in real-time

## License

MIT License - see LICENSE file for details. 