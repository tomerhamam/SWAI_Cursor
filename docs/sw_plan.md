# Software Implementation Plan: Modular AI Architecture MVP

## Executive Summary

This plan outlines the implementation of a modular, visual AI system architecture based on the provided PRD and detailed work orders. The system will enable hierarchical modeling of AI-enhanced software systems with YAML-based module definitions, interactive visualization, and surrogate execution capabilities.

**Target Timeline**: 6-hour focused prototype with extensible architecture  
**Primary Goal**: Validate core principles through functional demo  
**Success Criteria**: Interactive block diagram + schema viewer + surrogate execution

---

## Architecture Overview

### Core Components
1. **Module Definition System** - YAML-based block schemas with validation
2. **Graph Processing Layer** - Dependency resolution and visualization data preparation  
3. **Interactive Visualization** - Web-based diagram with zoom/pan/click interactions
4. **Surrogate Execution Engine** - Pluggable placeholder behaviors (static + mock-LLM)
5. **Live Update System** - File watching and auto-refresh capabilities

### Data Flow
```
YAML Modules → Loader/Validator → Graph Builder → Visualization → User Interaction → Surrogate Execution
     ↑                                                                          ↓
File Watcher ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

---

## Implementation Phases

### Phase 1: Foundation & Data Layer (1.5 hours)
**Goal**: Establish project structure and core data processing

#### Tasks:
- **T0.1-T0.3**: Project bootstrap (git repo, Python env, folder structure)
- **T1.1**: Define YAML schema specification
- **T1.2**: Implement `loader.py` with Pydantic validation
- **T1.3**: Create 5 sample module YAML files
- **T1.4**: Add unit tests for loader

#### Key Technical Decisions:
- **Python Environment**: Use `venv` with `requirements.txt`
- **Validation**: Pydantic for schema validation and type safety
- **File Structure**: Separate `/modules/`, `/static/`, `/tests/` directories

#### Deliverables:
- Working Python loader that validates and loads YAML modules
- Sample modules covering different statuses (implemented, placeholder, error)
- CLI tool: `python -m loader modules/`

#### Dependencies:
- None (foundation layer)

---

### Phase 2: Visualization & UI (2 hours)
**Goal**: Create interactive web-based module diagram

#### Tasks:
- **T2.1**: Choose rendering library (Mermaid vs D3.js)
- **T2.2**: Build graph builder (modules → diagram format)
- **T2.3**: Embed diagram in HTML with interaction
- **T2.4**: Add node click → side panel details
- **T2.5**: Implement status-based visual highlighting

#### Key Technical Decisions:
- **Rendering Library**: Mermaid (lighter weight, easier setup) vs D3.js (more flexibility)
- **Frontend Stack**: Vanilla JS + HTML (no heavy frameworks)
- **Layout**: Full-window diagram with collapsible side panel

#### Deliverables:
- Interactive web interface at `index.html`
- Graph builder producing Mermaid/D3 format
- Clickable nodes showing module details
- Color-coded status visualization

#### Dependencies:
- Phase 1 (loader and sample modules)

---

### Phase 3: Surrogate Execution (1 hour)
**Goal**: Enable placeholder behavior simulation

#### Tasks:
- **T3.1**: Define surrogate interface (ABC base class)
- **T3.2**: Implement static stub surrogate
- **T3.3**: Add mock LLM surrogate with logging
- **T3.4**: UI integration (run button + output display)

#### Key Technical Decisions:
- **Interface Design**: Abstract base class with `run(inputs) -> outputs`
- **Registry Pattern**: Dynamic surrogate lookup by type
- **Backend**: Simple Flask endpoint for surrogate execution

#### Deliverables:
- Pluggable surrogate execution system
- Two surrogate implementations (static + mock-LLM)
- UI button to trigger execution and view results

#### Dependencies:
- Phase 2 (UI framework for integration)

---

### Phase 4: Live Updates & Polish (1 hour)
**Goal**: File watching and user experience improvements

#### Tasks:
- **T4.1**: File watcher for live module reload
- **T4.2**: Frontend auto-refresh on data changes
- **T5.1**: End-to-end smoke test + demo recording
- **T5.2**: Documentation (README, usage instructions)

#### Key Technical Decisions:
- **File Watching**: Python `watchdog` library
- **Auto-refresh**: JavaScript polling vs WebSocket (choose polling for simplicity)
- **Demo Format**: GIF/MP4 screencast

#### Deliverables:
- Live-reloading development experience
- Comprehensive README with setup/usage
- Working demo recording

#### Dependencies:
- Phase 3 (complete feature set)

---

### Phase 5: Quality & Release (30 minutes)
**Goal**: Code quality, testing, and release preparation

#### Tasks:
- **T5.3**: Code quality pass (linting, type checking)
- **T5.4**: Tag v0.1 release

#### Deliverables:
- Clean, PEP8-compliant codebase
- Git tag for MVP release
- Updated CHANGELOG.md

---

## Technical Stack & Dependencies

### Core Dependencies
```python
# requirements.txt
pydantic>=1.10.0      # Schema validation
PyYAML>=6.0           # YAML parsing
watchdog>=2.1.0       # File watching
flask>=2.3.0          # Web backend (optional)
pytest>=7.0.0         # Testing
black>=22.0.0         # Code formatting
ruff>=0.0.250         # Linting
mypy>=1.0.0           # Type checking
```

### Frontend Stack
- **HTML5** + **Vanilla JavaScript** (no build process)
- **Mermaid.js** (CDN) for diagram rendering
- **Minimal CSS** for responsive layout

### File Structure
```
/
├── modules/              # YAML module definitions
├── static/               # Web assets, generated diagrams
├── tests/                # Unit tests
├── docs/                 # Documentation
├── build_logs/           # Build/execution logs
├── loader.py             # Core module loader
├── graph_builder.py      # Visualization data prep
├── surrogate.py          # Execution engine
├── watcher.py            # File monitoring
├── index.html            # Main UI
└── requirements.txt      # Dependencies
```

---

## Key Design Decisions

### 1. YAML Schema Design
```yaml
# Example module structure
name: "ExamplePlanner"
description: "Plans vehicle trajectory"
inputs:
  - type: "Pose"
    description: "Current vehicle state"
outputs:
  - type: "Trajectory"
    description: "Planned path"
status: "placeholder"  # implemented | placeholder | error
implementation: "rule-based"
dependencies:
  - "MapService"
  - "GoalSelector"
```

### 2. Surrogate Interface
```python
class Surrogate(ABC):
    @abstractmethod
    def run(self, inputs: dict) -> dict:
        """Execute surrogate behavior"""
        pass
```

### 3. Visualization Approach
- **Mermaid.js** for rapid prototyping (can upgrade to D3.js later)
- **Dependency arrows** showing module relationships
- **Color coding** for status (green=implemented, yellow=placeholder, red=error)
- **Side panel** for detailed schema inspection

---

## Risk Assessment & Mitigation

### High-Risk Items
1. **Rendering Library Choice**: Mermaid may be too limited for complex interactions
   - *Mitigation*: Start with Mermaid, design graph builder to be renderer-agnostic

2. **File Watching Reliability**: Cross-platform file watching can be flaky
   - *Mitigation*: Fall back to manual refresh, add polling option

3. **6-Hour Timeline**: Ambitious scope for prototype
   - *Mitigation*: Prioritize core features, defer polish items

### Medium-Risk Items
1. **Schema Evolution**: YAML schema may need frequent changes
   - *Mitigation*: Use Pydantic for flexible validation, version the schema

2. **Browser Compatibility**: Modern JS features may not work everywhere
   - *Mitigation*: Target modern browsers, test on Chrome/Firefox

---

## Testing Strategy

### Unit Tests
- **Loader validation** (valid/invalid YAML handling)
- **Graph builder** (correct node/edge generation)
- **Surrogate execution** (interface compliance)

### Integration Tests
- **End-to-end workflow**: YAML → visualization → surrogate execution
- **File watching**: Edit YAML → auto-refresh

### Manual Tests
- **UI interaction**: Click nodes, view panels, run surrogates
- **Cross-browser**: Chrome, Firefox, Safari
- **Demo recording**: Full workflow documentation

---

## Success Metrics

| Metric | Target | Validation |
|--------|---------|------------|
| Module loading | 5 YAML files | CLI tool lists all modules |
| Visualization | Interactive diagram | Click/zoom/pan works |
| Schema viewing | Per-module details | Side panel shows all fields |
| Surrogate execution | 2 implementations | Button triggers, output displayed |
| Live updates | File save → UI refresh | Edit YAML, see changes |
| Code quality | Zero lint errors | `ruff`, `black`, `mypy` pass |
| Documentation | Complete README | New user can run demo |

---

## Post-MVP Roadmap

### Phase 6: Advanced Features (Future)
- **Live code editor** per module (Monaco integration)
- **Real LLM integration** (OpenAI, Claude APIs)
- **Export capabilities** (JSON, Docker, CI/CD hooks)
- **Module marketplace** (common patterns library)
- **Version control** (schema evolution tracking)

### Phase 7: Production Features (Future)
- **Authentication/authorization** for team usage
- **Database persistence** (beyond file system)
- **API gateway** for external module execution
- **Monitoring/telemetry** for production deployments

---

## Conclusion

This implementation plan provides a structured approach to building the Modular AI Architecture MVP within the 6-hour constraint. The phased approach ensures each component builds upon the previous while maintaining flexibility for future enhancements.

The key success factors are:
1. **Rapid prototyping** with minimal dependencies
2. **Extensible architecture** for future growth
3. **User-focused design** with immediate visual feedback
4. **Agent-ready structure** for continued development

The plan prioritizes core functionality over polish, ensuring a working demo that validates the architectural concepts while providing a solid foundation for iterative improvement. 