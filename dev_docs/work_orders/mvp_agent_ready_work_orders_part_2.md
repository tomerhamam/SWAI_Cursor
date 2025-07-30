# MVP Agent-Ready Task Breakdown (Part 2)

## T2.1 – Choose Rendering Library

**Background:** The rendering library is used to visualize the module dependency graph in the browser. This choice impacts client-side bundle size, interactivity, and maintainability.

- **Inputs:**
  - Output from T1.1 (`docs/schema.md`), as field list determines what needs to be shown in the node detail panel.
  - Awareness of project browser requirements (vanilla JS, no heavy frameworks).

- **Outputs:**
  - `README.md#tech-choices` section updated with rationale and decision (Mermaid v10 or D3.js).

- **Steps:**
  1. Compare Mermaid v10 (embedded via CDN) and D3.js for:
      - Learning curve, setup complexity
      - Interactivity (zoom, pan, click handlers)
      - Ability to customize node appearance/status
      - Performance and bundle size
  2. Record pros/cons for both options in `README.md` (bullet list).
  3. Make final decision. Clearly mark the chosen library and why.
  4. Commit README changes.

- **Definition of Done:**
  - README contains a clearly explained decision and rationale, with at least three pros/cons per option.

- **Test/Validation:**
  - Reviewer can read README and understand why the chosen library fits the project’s needs.

- **Escalation:**
  - If both libraries are inadequate, suggest a fallback or flag for review in `BLOCKERS.md`.

---

## T2.2 – Build Graph Builder

**Background:** The graph builder converts loaded module objects into the node/edge data format needed by the rendering library (Mermaid or D3). It encodes dependencies, module status, and output shape for use in the front-end visualization.

- **Inputs:**
  - `loader.py` (T1.2)
  - Rendering library choice and its input format (T2.1)
  - At least three sample modules (T1.3)

- **Outputs:**
  - `graph_builder.py` (Python script/function)
  - For Mermaid: string with Mermaid flowchart syntax
  - For D3: JSON file with nodes/edges and node metadata

- **Steps:**
  1. Create `graph_builder.py` in root.
  2. Accept output of `load_modules` as input.
  3. Transform loaded modules into the diagram format:
      - For Mermaid: output directed graph in text format
      - For D3: output JSON `{"nodes": [...], "edges": [...]}`
      - Encode module status as a class/tag for styling
      - Ensure that module dependencies map to edges
  4. CLI: `python -m graph_builder modules/` writes output to `static/diagram.mmd` or `static/graph.json` as appropriate.
  5. Document the function signature and CLI usage in a top-level docstring.

- **Definition of Done:**
  - Running the script produces a valid diagram spec with at least five nodes and correct dependency edges.

- **Test/Validation:**
  - Sample output renders in a live Mermaid/D3 playground, with clear node status color/tags.

- **Escalation:**
  - If format is unclear, mimic the default example in the library’s documentation, note as TODO for later refactor.

---

## T2.3 – Embed Diagram in HTML

**Background:** The interactive diagram is the main UI for viewing and exploring the module graph. This task connects backend data to browser display.

- **Inputs:**
  - Diagram data file (`static/diagram.mmd` or `static/graph.json`) from T2.2
  - `index.html` file from T0.3
  - CDN or local scripts for rendering library (from T2.1)

- **Outputs:**
  - Updated `index.html` with rendering code
  - If needed, new file: `static/diagram.js` or similar
  - Basic CSS for responsive diagram area

- **Steps:**
  1. Load rendering library (Mermaid or D3) in `index.html` via CDN.
  2. Add HTML/JS to read the diagram data file and render into the page.
  3. Implement zoom, pan, and fit-to-screen.
  4. Style diagram for full-window use; add minimum padding and a clear background.
  5. Document any local JS in comments.

- **Definition of Done:**
  - Running a local dev server (e.g., `python -m http.server`) and opening `index.html` shows the interactive diagram, fits window, and is navigable.

- **Test/Validation:**
  - Diagram displays all modules, status is visually encoded.
  - UI can zoom/pan and stays readable at any window size.

- **Escalation:**
  - If rendering fails, add fallback static image or error message, document in `BLOCKERS.md`.

---

## T2.4 – Node Side-Panel Details

**Background:** Clicking a diagram node brings up a detail panel showing YAML schema fields for the selected module. This is essential for quick inspection and debugging.

- **Inputs:**
  - `index.html` and diagram code (from T2.3)
  - Schema field list from `docs/schema.md` (T1.1)
  - Loaded modules from `loader.py` (T1.2)

- **Outputs:**
  - JS code (`static/schema_viewer.js` or inline)
  - Side-panel UI elements (can use vanilla JS or Alpine.js ≤ 5kB if desired)
  - Minimal CSS for side panel

- **Steps:**
  1. Add event listeners for diagram node clicks.
  2. Populate side panel with a table or card showing all YAML fields for the selected module.
  3. Ensure keyboard accessibility and close/dismiss option.
  4. (Optional) Style using Tailwind via CDN or minimal custom CSS.
  5. Document the function signature and usage.

- **Definition of Done:**
  - Clicking any node brings up a panel with the correct module’s fields and values.
  - No errors or unhandled exceptions on interaction.

- **Test/Validation:**
  - Manual UI test: open several modules, check panel accuracy.
  - Code passes linter/formatter checks.

- **Escalation:**
  - If unable to match a node to YAML, log error to console and explain in `BLOCKERS.md`.

---

## T2.5 – Status-Based Highlighting

**Background:** Node color or appearance should change based on module `status` (implemented, placeholder, error) for fast scanning.

- **Inputs:**
  - Graph builder output (T2.2)
  - Diagram rendering code (T2.3)
  - Status field enum from `docs/schema.md` (T1.1)

- **Outputs:**
  - Updated JS and/or CSS
  - Visual legend in the UI

- **Steps:**
  1. Add CSS classes or D3/Mermaid tags for each status type.
  2. Update graph builder and/or JS to assign class/tags based on module status.
  3. Add a color legend (e.g., green=implemented, yellow=placeholder, red=error) to UI corner.
  4. Document any mappings in code comments.

- **Definition of Done:**
  - Node color/appearance reflects status for all modules.
  - Legend is visible and matches actual colors.

- **Test/Validation:**
  - Manual test: change a YAML’s status, reload diagram, see color update.

- **Escalation:**
  - If status cannot be styled, fall back to shape or icon, explain in `BLOCKERS.md`.

---

## [Continue for T3.x, T4.x, T5.x...]

(Ask to keep going for full coverage!)

