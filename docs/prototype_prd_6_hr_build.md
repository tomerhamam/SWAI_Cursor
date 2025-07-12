# Prototype PRD: 6-Hour Build for Modular AI Architecture Demo

---

## 1. Executive Summary

This document defines the scope, features, and deliverables of a focused prototype intended for completion within 6 hours. The goal is to validate the core principles of the Modular AI Architecture via a functional demo that ingests block schemas, renders visual module hierarchies, and supports placeholder logic execution.

This prototype will serve as the base for iterative development, Codex scripting, and early user feedback. It is designed to be **minimal, testable, and extensible**.

---

## 2. Prototype Objectives

- ✅ Ingest simple block definitions from YAML.
- ✅ Render the block structure as a visual interactive graph.
- ✅ Show per-block details on click (schema contents).
- ✅ Support placeholder behavior simulation for 1–2 types of blocks.
- ✅ Use file-based storage and zero external dependencies beyond core libraries.

---

## 3. Key Features in Scope (Must-Have)

### 3.1 Block Definition Loader
- Load up to 5 modules defined in simple YAML files.
- Validate against a basic schema (module_name, inputs, outputs, status, implementation).

### 3.2 Interactive Visualization (Graph View)
- Render a collapsible block diagram (D3.js or Mermaid).
- Edges reflect defined `dependencies` field.
- On-click: reveal module schema as side panel.

### 3.3 Surrogate Execution Mode
- Provide two surrogate implementations:
  - Static function stub (e.g., return fixed dummy value).
  - LLM call (mocked, simulated with print/log message).

### 3.4 Local State Management
- Track file updates using polling or manual refresh.
- Basic change detection to re-render graph or module panel.

---

## 4. Technical Stack (Minimum Viable)

| Layer       | Tech                     |
|-------------|--------------------------|
| Frontend    | HTML + JavaScript + Mermaid (or D3.js) |
| Backend     | Python Flask (or Static) |
| Data Format | YAML for module input    |
| Deployment  | Single-folder static prototype + Python runner |

---

## 5. Success Criteria

| Criterion                              | Target         |
|----------------------------------------|----------------|
| Working visual block diagram            | ✅             |
| Schema viewer popup or sidebar          | ✅             |
| Load 5 modules from YAML                | ✅             |
| Simulated surrogate behavior            | ✅             |
| Built, tested, and documented in 6 hrs  | ✅             |

---

## 6. Deliverables

- `/modules/` folder with YAML block definitions.
- `index.html` with embedded or linked visualizer code.
- `app.py` (if Flask is used) or JS-only event logic.
- `/static/schema_viewer.js` for block schema rendering.
- `README.md` with build + run instructions.

---

## 7. Optional Stretch Goals (Nice-to-Have)

- Search or filter blocks by name/status.
- Export JSON view of full module graph.
- Save manual edits to block schemas via UI.

---

## 8. Suggested Breakdown for Codex Agents

### Phase 1: Setup & I/O (1.5 hrs)
- [ ] Write YAML loader with schema validation.
- [ ] Define 5 example block YAML files.

### Phase 2: Graph Visualization (2 hrs)
- [ ] Build visual diagram with Mermaid or D3.js.
- [ ] Create mouse events to show side panel.

### Phase 3: Surrogate Logic Mocking (1 hr)
- [ ] Define callable surrogates (dummy + mock-LLM).
- [ ] Hook logic into UI simulation triggers.

### Phase 4: Polish + Docs (1.5 hrs)
- [ ] Test manual file change detection.
- [ ] Write basic README.md.

---

## 9. Timeboxed Constraints

- ⏱ Total max time: 6 hours
- 🛠️ No persistent DB, cloud hosting, or package bloat.
- ⚠️ Prioritize visual flow, interactivity, and file-driven logic over full backend.

---

## 10. Authors

**Lead Developer**: Tomer  
**Prototype Co-Designer**: GPT-4o (OpenAI)

---

