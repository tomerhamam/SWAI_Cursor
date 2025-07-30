# MVP Agent-Ready Task Breakdown (Part 3)

## T3.1 – Define Surrogate Interface

**Background:** Establishes the Python interface/protocol for module surrogate execution (static or LLM-backed), enabling plug-and-play evaluation.

- **Inputs:**
  - Project root with `loader.py` and at least two module YAMLs (T1.2, T1.3).
  - No UI/graph code required yet.

- **Outputs:**
  - `surrogate.py` file with base interface and registration system
  - Abstract class `Surrogate` (ABC)
  - Minimal inline docstring

- **Steps:**
  1. In `surrogate.py`, define `class Surrogate(ABC)` with `run(self, inputs: dict) -> dict`.
  2. Add a registry (dict) to allow dynamic lookup/instantiation by type.
  3. Add docstrings for all public classes/methods.
  4. Commit as "feat(surrogate): define base Surrogate interface"

- **Definition of Done:**
  - Interface and registry are defined, code passes `mypy`, `black`, `ruff`.
  - `help(Surrogate)` prints correct method signature and doc.

- **Test/Validation:**
  - Add `if __name__ == "__main__":` block that instantiates a dummy subclass and shows usage.

- **Escalation:**
  - If unsure about interface, follow standard Python `abc.ABC` usage and escalate in `BLOCKERS.md`.

---

## T3.2 – Static Stub Surrogate

**Background:** Implements a test surrogate that always returns the same static output; for pipeline dry runs and early integration.

- **Inputs:**
  - `surrogate.py` base class (T3.1)

- **Outputs:**
  - Subclass: `StaticStubSurrogate`
  - Returns `{ "result": "stub" }` and echoes input to log

- **Steps:**
  1. In `surrogate.py`, implement `class StaticStubSurrogate(Surrogate)`.
  2. Register with surrogate registry.
  3. `run(inputs)` returns fixed dict and prints/logs input for visibility.
  4. Add/extend unit test to demonstrate output.
  5. Commit as "feat(surrogate): add StaticStubSurrogate"

- **Definition of Done:**
  - Calling `StaticStubSurrogate().run({"foo": 123})` returns `{ "result": "stub" }`, input is logged.
  - Covered by a unit test in `tests/`.

- **Test/Validation:**
  - Run test script or REPL example. Output and log correct.

- **Escalation:**
  - If logger setup is unclear, use `print()` and comment for future upgrade.

---

## T3.3 – Mock LLM Surrogate

**Background:** Implements a mock LLM-backed surrogate for UX wiring. Does not call a real LLM, but logs prompt and returns dummy response.

- **Inputs:**
  - `surrogate.py` with Surrogate and StaticStubSurrogate (T3.1, T3.2)

- **Outputs:**
  - Subclass: `MockLLMSurrogate`
  - Accepts `prompt_template` (str)
  - Returns `{ "response": "<mock>" }`, logs formatted prompt to `build_logs/llm_prompts.log`

- **Steps:**
  1. Implement `MockLLMSurrogate` in `surrogate.py`.
  2. Accept prompt_template; fill with inputs as `prompt_template.format(**inputs)`.
  3. Log resulting prompt to file `build_logs/llm_prompts.log` (create if needed).
  4. Return dict with a dummy key, e.g., `{ "response": "<mock>" }`.
  5. Add/extend unit test for log file write and output.

- **Definition of Done:**
  - `run()` formats prompt, writes to log, returns dummy dict.
  - Passes `mypy`, `black`, `ruff`, and test.

- **Test/Validation:**
  - Check log file is written and correct prompt appears after test run.

- **Escalation:**
  - If unsure about template formatting, use Python’s str.format and flag for review if errors occur.

---

## T3.4 – UI Integration: Surrogate Execution Button

**Background:** Connects the UI (diagram/side panel) to surrogate execution. Users can trigger a surrogate for a module and view the output.

- **Inputs:**
  - `index.html`/diagram JS from T2.3/2.4
  - Surrogate classes from `surrogate.py` (T3.1–T3.3)

- **Outputs:**
  - UI button for "Run Surrogate" in node detail side panel
  - Backend API endpoint (Flask or FastAPI, choice left to implementer) e.g., `/api/run?module=<id>`
  - Displays returned JSON in side panel

- **Steps:**
  1. Add a button to node side panel in UI.
  2. On click, send AJAX request to `/api/run?module=<id>`.
  3. Backend looks up module, instantiates corresponding surrogate, calls `run()` with sample/dummy inputs.
  4. Output JSON is displayed in expandable panel below node details.
  5. Add basic error handling for failed requests.

- **Definition of Done:**
  - Button triggers backend, runs surrogate, output shown in UI.
  - No page reload needed. Errors are handled gracefully.

- **Test/Validation:**
  - Manual test: open a module in the diagram, click Run Surrogate, confirm output.
  - Backend logs each surrogate execution.

- **Escalation:**
  - If unsure how to plumb backend, use Flask with a stub endpoint, note for refactor if project later standardizes on FastAPI.

---

## T4.1 – File Watcher: Live Module Reload

**Background:** Enables live editing of module YAML files, with instant update to the rendered diagram.

- **Inputs:**
  - `loader.py` (T1.2)
  - `/modules/` folder
  - `graph_builder.py` (T2.2)

- **Outputs:**
  - `watcher.py` using `watchdog` lib
  - Watches `/modules/` for changes, triggers graph rebuild and output to `static/diagram.mmd` or `static/graph.json`

- **Steps:**
  1. Create `watcher.py` in root.
  2. Use `watchdog.observers.Observer` to monitor `modules/` for changes.
  3. On file change, call loader and graph_builder, overwrite diagram data file.
  4. Log all reloads and errors to `build_logs/phase_4.log`.

- **Definition of Done:**
  - Editing/saving any YAML in `/modules/` triggers immediate diagram data file update.
  - All events and errors are logged.

- **Test/Validation:**
  - Manual: edit YAML, see live-reload in diagram after refresh.
  - Check logs for reload events.

- **Escalation:**
  - If unable to detect changes, suggest polling as fallback and log reason.

---

## T4.2 – Front-End Auto-Refresh

**Background:** Ensures that changes to module YAML files appear automatically in the diagram view without a manual browser reload.

- **Inputs:**
  - Updated diagram data file (from T4.1)
  - `index.html`/diagram JS (T2.3)

- **Outputs:**
  - JavaScript polling/fetch code in UI
  - Auto-refresh or redraw of diagram on data change

- **Steps:**
  1. In UI JS, poll diagram data file every second (or use WebSockets if preferred).
  2. Compare `ETag` or `lastModified` header for change detection.
  3. On change, reload or re-render the diagram without a full page refresh.
  4. (Optional) Add a brief flash/animation to indicate live update.

- **Definition of Done:**
  - Editing/saving a module YAML triggers diagram update in browser automatically.
  - No duplicate reloads; refresh is seamless.

- **Test/Validation:**
  - Manual: edit YAML, see browser auto-update.
  - Code is commented and passes linter.

- **Escalation:**
  - If unable to poll, document browser or CORS limitations and note for later.

---

## T5.1 – End-to-End Smoke Test & Demo GIF

**Background:** Validates the full workflow (module load → graph UI → surrogate run) and captures as a demonstration artifact.

- **Inputs:**
  - All implemented MVP code paths (T1.x, T2.x, T3.x, T4.x)
  - Test modules in `/modules/`

- **Outputs:**
  - Animated demo: `docs/demo.gif` or `docs/demo.mp4` (use `peek`/`asciinema`)
  - Written summary of test steps and results in `build_logs/phase_5.log`

- **Steps:**
  1. Load project in a clean virtualenv, run `python -m http.server` (or backend as needed).
  2. Go through the workflow: edit YAML, confirm live diagram update, open node, run surrogate, observe output.
  3. Record screencast/GIF of the process (full window).
  4. Save/commit demo artifact and brief log.

- **Definition of Done:**
  - GIF/MP4 clearly shows successful use of the MVP from edit to surrogate run.
  - Summary log covers observed behavior and passes/fails.

- **Test/Validation:**
  - Peer or agent reviews GIF and confirms accuracy and clarity.

- **Escalation:**
  - If screencast tool unavailable, provide sequence of screenshots as fallback.

---

## T5.2 – Write README & Documentation

**Background:** Ensures onboarding, development, and usage instructions are clear for both LLM and human contributors.

- **Inputs:**
  - All implemented features and interface specs
  - Diagram/screenshot of UI from T5.1

- **Outputs:**
  - `README.md` covering setup, usage, contribution, architecture
  - Optional: docstrings and `docs/` markdown for submodules

- **Steps:**
  1. Update README: cover environment setup, launching UI, running tests, adding modules, etc.
  2. Add architecture overview and milestone badges.
  3. Link to demo GIF and reference sample YAMLs.
  4. Ensure all new fields/APIs are documented or referenced.

- **Definition of Done:**
  - Any new contributor or LLM can onboard and use all features from README alone.

- **Test/Validation:**
  - Run `markdownlint README.md`; all links and code snippets work.
  - Peer review or doc agent feedback.

- **Escalation:**
  - If usage unclear or new feature is ambiguous, note in TODO for follow-up.

---

## T5.3 – Code Quality & Lint Pass

**Background:** Polishes and standardizes codebase for handoff, CI, or release.

- **Inputs:**
  - All source files

- **Outputs:**
  - Clean, PEP8-compliant codebase; passes `ruff`, `black`, `mypy` with no errors
  - Lint/test logs in `build_logs/phase_5.log`

- **Steps:**
  1. Run `ruff --fix .`, `black .`, `mypy .`
  2. Address any errors/warnings; add type hints or comments as needed.
  3. Save/commit log outputs.

- **Definition of Done:**
  - No lint, format, or type errors; codebase is clean and ready for release/tag.

- **Test/Validation:**
  - Logs show zero issues; CI (if present) passes.

- **Escalation:**
  - If a warning/error is unresolvable, document and explain why in `BLOCKERS.md`.

---

## T5.4 – Tag v0.1 Release

**Background:** Creates the MVP release checkpoint for handoff, demo, or downstream consumption.

- **Inputs:**
  - All prior steps complete; codebase stable and clean

- **Outputs:**
  - Git tag: `v0.1`
  - Release notes in `CHANGELOG.md`

- **Steps:**
  1. Commit any outstanding changes: `git commit -am "chore(release): v0.1"`
  2. Tag release: `git tag v0.1 && git push --tags`
  3. Update `CHANGELOG.md` with summary of MVP features and known limitations.

- **Definition of Done:**
  - GitHub/GitLab repo shows tag and release notes; code is locked at MVP state.

- **Test/Validation:**
  - Release appears in repo UI; team or bot can check out v0.1 and run demo successfully.

- **Escalation:**
  - If tag push fails, note error and retry or document in `BLOCKERS.md`.

