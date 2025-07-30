<!-- Verified on 2025-07-30 by Claude -->
<!-- Purpose: AI assistant guidance for working with this codebase -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Modular AI Architecture Visualization System** - a full-stack web application that provides visual modeling and management of AI-enhanced software systems using YAML-based module definitions and interactive network graphs.

## Key Commands

### Development Startup
```bash
# From project root (/home/thh3/work/SWAI_Cursor)
./start_servers.sh  # Automated startup with port conflict handling

# Manual startup if needed
python -m flask --app app.py run --debug &
cd frontend && npm run dev
```

### Running Tests
```bash
# Backend tests (85% coverage required)
cd backend && pytest
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest --cov-report=html  # Generate HTML coverage report

# Frontend tests (90% coverage required)
cd frontend
npm run test           # Run tests in watch mode
npm run test:run       # Run tests once
npm run test:coverage  # Run with coverage report
npm run test:e2e       # Run Playwright E2E tests
```

### Code Quality
```bash
# Python linting and formatting
cd backend
black .                # Format code
ruff check .          # Lint code
mypy .                # Type checking

# TypeScript/Vue linting
cd frontend
npm run lint          # ESLint with auto-fix
npm run type-check    # TypeScript type checking
```

### Building
```bash
cd frontend && npm run build  # Production build
```

## Architecture Overview

### Backend Structure (Flask/Python)
- **app.py**: Main Flask application in project root (NOT in backend/)
- **backend/models/**: Pydantic schemas for module validation
- **backend/services/**:
  - `loader.py`: YAML module loading and validation
  - `graph_builder.py`: Converts modules to vis.js network data
  - `surrogate.py`: Pluggable module execution system
  - `watcher.py`: File system monitoring for hot reload
- **backend/tests/**: Organized by test type (unit, integration, e2e)

### Frontend Structure (Vue 3/TypeScript)
- **src/components/**:
  - `GraphView.vue`: Main network visualization using vis.js
  - `ModulePanel.vue`: Module details sidebar
  - `ModuleCreationDialog.vue`: Module creation interface
  - `ModulePalette.vue`: Drag & drop module library
- **src/stores/**: Pinia state management for reactive data
- **src/services/**: Axios-based API communication layer
- **vite.config.ts**: Dev server on port 3001 with proxy to backend

### Module System
- **modules/**: YAML module definitions following schema in `docs/schema.md`
- **Validation**: Strict Pydantic validation with required fields
- **Hot Reload**: Automatic detection of YAML file changes
- **Surrogates**: Static and mock-LLM execution modes

## Important Notes from Project Memories

### Flask App Location
- Main `app.py` is in **PROJECT ROOT**, not in `backend/`
- Virtual environment `.venv/` is in **PROJECT ROOT**
- Never try: `cd backend && source venv/bin/activate`

### Port Configuration
- Backend: Port 5000 (Flask default)
- Frontend: Port 3001 (configured in vite.config.ts)
- NOT the Vite default of 5173

### Server Management
- Use `./start_servers.sh` for automated startup
- Use `./kill_ports.sh` to clear port conflicts
- Check server health:
  - Backend: `http://localhost:5000/api/modules`
  - Frontend: `http://localhost:3001`

## Current Development Status

- **Version**: Pre-release (0.1.0 planned)
- **Latest Milestone**: Milestone 3 completed (Core Interactivity)
- **Features Implemented**:
  - Interactive vis.js network visualization
  - Drag & drop module creation
  - Context menus and dependency drawing
  - Status-based filtering
  - Module details panel
  - Real-time YAML validation

## Testing Strategy

- **Frontend**: Vitest for unit tests, Playwright for E2E
- **Backend**: Pytest with markers for test categories
- **Coverage Requirements**: Frontend 90%, Backend 85%
- Always run E2E tests before milestone completion