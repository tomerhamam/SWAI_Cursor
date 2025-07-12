# MVP Agent-Ready Task Breakdown – Modular AI Architecture Prototype (6-Hour Build)

**Style note:** All breakdowns in this project are prepared in an explicit, agent-ready format: clear inputs/outputs, explicit DoD, test requirements, dependencies, sample code/data, and escalation instructions. Use this as the baseline for all future LLM-driven task handoff.

---

## T0.1 – Initialize Git Repository

**Background:** Initialize a new git repository with clean VCS and licensing. Prepares the codebase for team collaboration and CI/CD.

- **Inputs:** Empty or fresh project folder.

- **Outputs:**

  - `.git` directory
  - `LICENSE` (MIT)
  - `.gitignore` supporting Python, Node, VSCode, macOS
  - First commit with message: `chore(repo): bootstrap repo with license & gitignore`

- **Steps:**

  1. Run `git init` in project root.
  2. Add MIT LICENSE (`https://choosealicense.com/licenses/mit/`).
  3. Generate `.gitignore` using [gitignore.io](https://gitignore.io/?templates=python,node,macos,visualstudiocode).
  4. `git add LICENSE .gitignore && git commit -m "chore(repo): bootstrap repo with license & gitignore"`
  5. If remote is provided, `git remote add origin ... && git push`.

- **Definition of Done:**

  - `.git` exists; `LICENSE` and `.gitignore` present and committed.
  - `git status` clean.

- **Test/Validation:**

  - Run `git log` and confirm first commit exists with correct files.

- **Escalation:**

  - If repo exists, confirm no history is overwritten. If permissions error, document in `BLOCKERS.md`.

---

## T0.2 – Set Up Python Environment

**Background:** Ensure deterministic package management and reproducible environment for all contributors and CI runners.

- **Inputs:** Project root (ideally after T0.1).

- **Outputs:**

  - `.venv` directory (Python virtualenv)
  - `requirements.txt` (frozen pip state)

- **Steps:**

  1. Run `python3 -m venv .venv`
  2. `source .venv/bin/activate`
  3. Upgrade pip tooling: `pip install --upgrade pip wheel setuptools`
  4. Install core packages:
     - `pydantic`, `PyYAML`, `watchdog`, `pytest`, `ruff`, `black`, `mypy`
  5. `pip freeze > requirements.txt`
  6. `git add requirements.txt && git commit -m "chore(env): add virtualenv and requirements"`

- **Definition of Done:**

  - `.venv/` exists, `requirements.txt` present, can be recreated with `pip install -r requirements.txt`.

- **Test/Validation:**

  - `python -c "import pydantic, yaml, watchdog, pytest, ruff, black, mypy"` returns no error.

- **Escalation:**

  - If any install fails, document and suggest fix in `BLOCKERS.md`.

---

## T0.3 – Scaffold Folder Layout

**Background:** Prepare project directory structure for modular growth, CI scripts, tests, and documentation.

- **Inputs:** Project root with repo and `.venv`.

- **Outputs:**

  - Folders: `/modules`, `/static`, `/tests`, `/docs`, `/build_logs`
  - Files: `index.html`, `README.md`, `CHANGELOG.md`, `BLOCKERS.md`

- **Steps:**

  1. Create folders with `mkdir -p modules static tests docs build_logs`
  2. Create files: `touch index.html README.md CHANGELOG.md BLOCKERS.md`
  3. `git add ... && git commit -m "chore(structure): scaffold project layout"`

- **Definition of Done:**

  - `ls` lists all required dirs/files.
  - All present in version control.

- **Test/Validation:**

  - Run `tree -L 1` or `ls` and compare to:
    ```
    modules/
    static/
    tests/
    docs/
    build_logs/
    index.html
    README.md
    CHANGELOG.md
    BLOCKERS.md
    ```

- **Escalation:**

  - If any directory cannot be created, explain in `BLOCKERS.md`.

---

## T1.1 – Design YAML Module Schema

**Background:** Defines the contract for how every AI module in the pipeline is described, loaded, and visualized.

- **Inputs:** `docs/` directory (from T0.3).

- **Outputs:**

  - `docs/schema.md` (YAML schema doc)
  - At least two valid YAML example snippets

- **Steps:**

  1. Create `docs/schema.md` with a table or list defining these fields:
     - `name` (string, required, unique)
     - `description` (string, required)
     - `inputs` (list[string], required)
     - `outputs` (list[string], required)
     - `status` (enum: implemented, placeholder, error)
     - `implementation` (string: path/uri)
     - `dependencies` (list[string], optional)
  2. Document field types, required/optional status, allowed enum values, and semantic meaning.
  3. Add at least two valid YAML module examples and one invalid (for validator testing).
  4. Link to the JSON Schema definition (if available).

- **Definition of Done:**

  - `schema.md` explains all fields and provides real YAML examples.
  - All team members can understand how to write a module YAML after reading the doc.

- **Test/Validation:**

  - Run sample YAMLs through a validator or linter (if not available, spot-check for valid YAML syntax).

- **Escalation:**

  - If there are questions on field meaning, annotate with TODO and flag for review.

---

## T1.2 – Implement Loader & Validator

**Background:** Converts YAML module files into Python objects and validates schema correctness; enables graph building and UI.

- **Inputs:** `/modules/` folder with at least two valid YAMLs and `docs/schema.md` (from T1.1, T1.3).

- **Outputs:**

  - `loader.py` (core loader/validator)
  - `ModuleNode` Pydantic model
  - CLI: `python -m loader modules/`

- **Steps:**

  1. Create `loader.py` in root.
  2. Define a `ModuleNode` class (pydantic.BaseModel) with fields as per `docs/schema.md`.
  3. Write `load_modules(directory: str) -> list[ModuleNode]` that:
     - Loads all `.yaml` in `directory`.
     - Validates with pydantic. For errors, print message and exit(1).
     - Checks for duplicate names and field presence.
  4. Add CLI: `python -m loader modules/` → prints summary of loaded module names, errors exit(1).
  5. Add help: `python -m loader --help` prints basic usage.

- **Definition of Done:**

  - CLI loads all valid YAMLs, lists module names.
  - Invalid YAMLs print error, exit(1).
  - Code is type-hinted, passes `black`, `ruff`, `mypy`.

- **Test/Validation:**

  - Add 3 valid, 2 invalid YAMLs and test both scenarios.
  - Save output in `build_logs/phase_1.log`.

- **Escalation:**

  - If schema doc unclear, assume minimal field types or escalate in `BLOCKERS.md`.

---

## T1.3 – Create Sample Module YAMLs

**Background:** Provide real and edge-case YAML modules for loader and UI testing.

- **Inputs:** `docs/schema.md` (from T1.1)

- **Outputs:**

  - Five sample YAMLs in `/modules/` (e.g., `input_parser.yaml`, `planner.yaml`...)

- **Steps:**

  1. Write five YAML files, each using all required fields, unique `name`.
  2. Use variety of statuses: implemented, placeholder, error.
  3. Add one invalid YAML (missing field, bad status) for loader test.

- **Definition of Done:**

  - All valid YAMLs are accepted by loader.
  - Invalid one triggers proper error.

- **Test/Validation:**

  - Run loader CLI to test both valid and error cases.

- **Escalation:**

  - If field meaning is unclear, use the sample in schema doc; otherwise flag for review.

---

## T1.4 – Unit Tests for Loader

**Background:** Regression-proof the loader for future schema changes or refactors.

- **Inputs:** `loader.py` and `/modules/` with valid+invalid YAMLs.

- **Outputs:**

  - `tests/test_loader.py` (pytest)

- **Steps:**

  1. Write pytest covering:
     - All valid YAMLs load without error.
     - Invalid YAML triggers exception.
     - Duplicate names or missing fields raise error.
  2. Achieve ≥80% coverage of loader code.
  3. Commit and add test badge if possible.

- **Definition of Done:**

  - `pytest` passes; coverage report ≥80% for loader.

- **Test/Validation:**

  - CI run (or local `pytest --cov=loader`); log report in `build_logs/phase_1.log`.

- **Escalation:**

  - If coverage goal missed, add one more test or annotate why not feasible.

---

## [Add remaining T2.x, T3.x, T4.x, T5.x tasks in same format...]

(Ask to continue for the full set!)

