# Modular AI Architecture

A system for hierarchical modeling of AI-enhanced software systems with interactive visualization and surrogate execution capabilities.

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

### Usage

1. **Load and validate modules:**
   ```bash
   python -m loader modules/ --validate-deps
   ```

2. **Generate visualization:**
   ```bash
   python graph_builder.py modules/
   ```

3. **View interactive diagram:**
   ```bash
   python -m http.server 8000
   # Open http://localhost:8000 in browser
   ```

4. **Interact with the diagram:**
   - Click any module node to view detailed information
   - Use zoom controls to navigate the diagram
   - Status colors: Green (implemented), Yellow (placeholder), Red (error)

### Current Features
- ✅ **Module Loading**: YAML-based module definitions with Pydantic validation
- ✅ **Interactive Visualization**: Mermaid.js diagram with clickable nodes
- ✅ **Status Highlighting**: Color-coded modules by implementation status
- ✅ **Side Panel Details**: Complete module information on click
- ✅ **Dependency Visualization**: Arrows showing module relationships

## Features (In Development)
- [x] YAML-based module definitions
- [x] Interactive visualization
- [ ] Surrogate execution engine
- [ ] Live file watching and updates

## Architecture
Based on the Modular AI Architecture PRD - see `docs/` for detailed specifications.

### Tech Choices

**Rendering Library: Mermaid.js**
- **Decision**: Mermaid.js chosen over D3.js for MVP
- **Rationale**: 
  - Faster development time (critical for 6-hour constraint)
  - Built-in styling and layout algorithms
  - Simpler syntax for rapid prototyping
  - Good enough interactivity for MVP requirements
  - Can upgrade to D3.js later if needed
- **Tradeoffs**: Less customization control, but sufficient for validation phase

## Contributing
This is an active development project. See `docs/sw_plan.md` for implementation roadmap.

## License
MIT License - see LICENSE file for details. 