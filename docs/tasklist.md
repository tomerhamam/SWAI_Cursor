# Detailed Implementation Task List

## Overview
This document provides explicit, step-by-step tasks for implementing the Modular AI Architecture system with comprehensive testing. Each task includes specific files to modify, exact commands to run, and clear definition of done criteria.

**CRITICAL**: No task is complete without corresponding tests. Every feature must be tested at unit, integration, and E2E levels.

---

# 🎯 MILESTONE 1: Foundation & Backend API
**Phases**: 0, 1, 2 (22 hours total)
**Target**: Complete backend with full test coverage

## Milestone 1 Completion Checklist
- [ ] All Phase 0, 1, 2 tasks completed
- [ ] Backend test coverage >85% (100% for critical paths)
- [ ] All API endpoints tested and working
- [ ] Performance benchmark: 500+ modules load in <100ms
- [ ] CLI tools functional
- [ ] Documentation complete

## Milestone 1 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-1-testing.md`

### Pre-Testing Commands
```bash
# Backend health check
cd backend
pytest --cov
python -c "from services.loader import ModuleLoader; print('✓ Backend ready')"

# Start test server
python -m flask run --debug

# Create milestone tag
git tag milestone-1-ready
echo "🎯 MILESTONE 1 REACHED - USER TESTING REQUIRED"
echo "⏳ Please conduct user testing before proceeding"
echo "📋 Testing checklist: docs/milestone-1-testing.md"
```

---

# 🎯 MILESTONE 2: Basic Interactive Visualization
**Phases**: 3 (8 hours)
**Target**: Working Vue 3 frontend with vis.js

## Milestone 2 Completion Checklist
- [ ] Vue 3 frontend with vis.js integration
- [ ] Basic graph rendering with status colors
- [ ] Click-to-select functionality
- [ ] Module details panel working
- [ ] Frontend test coverage >90%
- [ ] 60 FPS rendering performance

## Milestone 2 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-2-testing.md`

### Pre-Testing Commands
```bash
# Frontend health check
cd frontend
npm run test:coverage
npm run build

# Start development servers
npm run dev &
cd ../backend && python -m flask run &

# Create milestone tag
git tag milestone-2-ready
echo "🎯 MILESTONE 2 REACHED - USER TESTING REQUIRED"
echo "⏳ Please conduct user testing before proceeding"
echo "📋 Testing checklist: docs/milestone-2-testing.md"
```

---

# 🎯 MILESTONE 3: Core Interactivity
**Phases**: 4 (6 hours)
**Target**: Full vis.js interactions

## Milestone 3 Completion Checklist
- [ ] Right-click context menus
- [ ] Drag & drop module creation
- [ ] Dependency line drawing
- [ ] Zoom/pan controls
- [ ] Status-based filtering
- [ ] Performance with 100+ modules

## Milestone 3 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-3-testing.md`

### Pre-Testing Commands
```bash
# Performance test with 100+ modules
cd backend
python -c "
import time
from services.loader import ModuleLoader
start = time.time()
loader = ModuleLoader('test_modules_100')
modules = loader.load_all_modules()
print(f'✓ Loaded {len(modules)} modules in {time.time()-start:.3f}s')
"

git tag milestone-3-ready
echo "🎯 MILESTONE 3 REACHED - USER TESTING REQUIRED"
echo "⏳ Please conduct user testing before proceeding"
echo "📋 Testing checklist: docs/milestone-3-testing.md"
```

---

# 🎯 MILESTONE 4: Real-time Collaboration
**Phases**: 5 (4 hours)
**Target**: Live updates and SSE

## Milestone 4 Completion Checklist
- [ ] SSE connection established
- [ ] Multi-user synchronization
- [ ] Optimistic UI updates
- [ ] Connection recovery
- [ ] <500ms update latency

## Milestone 4 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-4-testing.md`

### Pre-Testing Commands
```bash
# SSE connection test
curl -N http://localhost:5000/api/stream &
sleep 2
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{"name":"TestSSE","description":"Test","status":"placeholder"}'

git tag milestone-4-ready
echo "🎯 MILESTONE 4 REACHED - USER TESTING REQUIRED"
echo "⏳ Please conduct user testing before proceeding"
echo "📋 Testing checklist: docs/milestone-4-testing.md"
```

---

# 🎯 MILESTONE 5: Advanced Features
**Phases**: 6 (6 hours)
**Target**: Hierarchical management and bulk operations

## Milestone 5 Completion Checklist
- [ ] Hierarchical expand/collapse
- [ ] Multi-select operations
- [ ] Undo/redo functionality
- [ ] Keyboard shortcuts
- [ ] Advanced filtering

## Milestone 5 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-5-testing.md`

### Pre-Testing Commands
```bash
# Undo/redo test
cd frontend
npm run test -- --grep "undo.*redo"

git tag milestone-5-ready
echo "🎯 MILESTONE 5 REACHED - USER TESTING REQUIRED"
echo "⏳ Please conduct user testing before proceeding"
echo "📋 Testing checklist: docs/milestone-5-testing.md"
```

---

# 🎯 MILESTONE 6: Production Ready
**Phases**: 7 (4 hours)
**Target**: Complete E2E testing and deployment

## Milestone 6 Completion Checklist
- [ ] All E2E tests passing
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Deployment pipeline ready

## Milestone 6 Testing Protocol
**Duration**: 30 minutes
**Testing Script**: `docs/milestone-6-testing.md`

### Pre-Testing Commands
```bash
# Full E2E test suite
cd frontend
npm run test:e2e

# Performance benchmark
npm run test:performance

# Security scan
npm audit
cd ../backend && pip-audit

git tag milestone-6-ready
echo "🎯 MILESTONE 6 REACHED - PRODUCTION READY!"
echo "⏳ Please conduct final user testing"
echo "📋 Testing checklist: docs/milestone-6-testing.md"
```

---

## Phase 0: Project Restructure and Migration Preparation (2 hours)

### T0.1: Backup Current Implementation
**Description**: Create a complete backup of the current D3.js implementation before migration
**Files to modify**: None
**Commands to run**:
```bash
git checkout -b backup/d3js-implementation
git add .
git commit -m "Backup: D3.js implementation before vis.js migration"
git checkout -b feature/visjs-migration
```
**Definition of Done**:
- [ ] Backup branch created with all current code
- [ ] New feature branch created for migration
- [ ] No uncommitted changes in working directory

### T0.2: Create New Project Structure
**Description**: Set up the new directory structure for backend/frontend separation
**Files to create**:
```
backend/
├── api/
│   ├── __init__.py
│   ├── modules.py
│   ├── dependencies.py
│   └── stream.py
├── services/
│   ├── __init__.py
│   ├── loader.py
│   ├── graph_builder.py
│   ├── watcher.py
│   └── surrogate.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── requirements.txt

frontend/
├── src/
├── tests/
├── public/
├── package.json
└── vite.config.ts
```
**Commands to run**:
```bash
mkdir -p backend/{api,services,models,tests/{unit,integration,fixtures}}
mkdir -p frontend/{src/{components,stores,services,utils},tests/{unit,component,e2e},public}
touch backend/{api,services,models,tests}/__init__.py
```
**Definition of Done**:
- [ ] All directories created
- [ ] All __init__.py files in place
- [ ] Directory structure matches specification

### T0.3: Move Existing Python Files
**Description**: Relocate existing Python files to new backend structure
**Files to move**:
- `loader.py` → `backend/services/loader.py`
- `graph_builder.py` → `backend/services/graph_builder.py`
- `surrogate.py` → `backend/services/surrogate.py`
- `watcher.py` → `backend/services/watcher.py`
- `app.py` → `backend/api/__init__.py` (refactor later)
**Commands to run**:
```bash
mv loader.py backend/services/
mv graph_builder.py backend/services/
mv surrogate.py backend/services/
mv watcher.py backend/services/
cp app.py backend/api/__init__.py
```
**Definition of Done**:
- [ ] All Python files moved to correct locations
- [ ] Original files no longer in root directory
- [ ] Imports still resolve (will fix in next phase)

---

## Phase 1: Test Infrastructure Setup (4 hours)

### T1.1: Python Testing Infrastructure
**Description**: Set up pytest with coverage and testing utilities
**Files to create**:
1. `backend/requirements-test.txt`:
```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.20.0
pytest-mock>=3.10.0
factory-boy>=3.2.0
faker>=15.0.0
responses>=0.22.0
pytest-flask>=1.2.0
```

2. `backend/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
    --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
```

3. `backend/tests/conftest.py`:
```python
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_module_yaml():
    """Sample YAML content for testing"""
    return """
name: TestModule
description: A test module
status: placeholder
inputs:
  - type: TestInput
    description: Test input
outputs:
  - type: TestOutput
    description: Test output
dependencies:
  - OtherModule
"""
```

**Commands to run**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt
pytest --version
```

**Write tests**:
Create `backend/tests/unit/test_setup.py`:
```python
def test_pytest_working():
    """Verify pytest is properly configured"""
    assert True

def test_coverage_working():
    """Verify coverage is working"""
    assert 1 + 1 == 2
```

**Run tests**:
```bash
pytest -v
pytest --cov
```

**Definition of Done**:
- [ ] All test dependencies installed
- [ ] pytest.ini configured with coverage requirements
- [ ] Basic test fixtures created
- [ ] Sample test passing
- [ ] Coverage report generating
- [ ] Coverage threshold enforced (85%)

### T1.2: Vue Testing Infrastructure
**Description**: Set up Vue 3 project with Vitest and testing utilities
**Files to create**:
1. `frontend/package.json`:
```json
{
  "name": "modular-ai-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.3.0",
    "pinia": "^2.1.0",
    "vis-network": "^9.1.0",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@vitejs/plugin-vue": "^4.4.0",
    "@vue/test-utils": "^2.4.0",
    "@testing-library/vue": "^7.0.0",
    "@testing-library/user-event": "^14.0.0",
    "@vitest/ui": "^0.34.0",
    "@vitest/coverage-v8": "^0.34.0",
    "vitest": "^0.34.0",
    "typescript": "^5.2.0",
    "vue-tsc": "^1.8.0",
    "vite": "^4.5.0",
    "eslint": "^8.50.0",
    "eslint-plugin-vue": "^9.17.0",
    "@typescript-eslint/parser": "^6.7.0",
    "@typescript-eslint/eslint-plugin": "^6.7.0",
    "msw": "^1.3.0",
    "jsdom": "^22.1.0"
  }
}
```

2. `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockServiceWorker.js',
      ],
      thresholds: {
        lines: 85,
        functions: 85,
        branches: 85,
        statements: 85
      }
    }
  }
})
```

3. `frontend/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts']
  }
})
```

4. `frontend/tests/setup.ts`:
```typescript
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/vue'
import matchers from '@testing-library/jest-dom/matchers'

expect.extend(matchers)

afterEach(() => {
  cleanup()
})

// Mock vis-network globally
vi.mock('vis-network', () => ({
  Network: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    setData: vi.fn(),
    destroy: vi.fn(),
    fit: vi.fn(),
    getSelectedNodes: vi.fn(() => []),
    getSelectedEdges: vi.fn(() => [])
  })),
  DataSet: vi.fn(() => ({
    add: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    get: vi.fn(),
    getIds: vi.fn(() => [])
  }))
}))
```

**Commands to run**:
```bash
cd frontend
npm install
npm run test
```

**Write tests**:
Create `frontend/tests/unit/setup.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'

describe('Test Setup', () => {
  it('should run tests', () => {
    expect(true).toBe(true)
  })

  it('should have testing utilities available', () => {
    expect(typeof expect).toBe('function')
  })
})
```

**Definition of Done**:
- [ ] Vue 3 project initialized with TypeScript
- [ ] All testing dependencies installed
- [ ] Vitest configured with coverage thresholds
- [ ] vis-network mocked globally
- [ ] Testing utilities set up
- [ ] Sample test passing
- [ ] Coverage reporting working

### T1.3: E2E Testing Framework
**Description**: Set up Playwright for end-to-end testing
**Files to create**:
1. `frontend/playwright.config.ts`:
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  use: {
    actionTimeout: 0,
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    }
  ],
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  }
})
```

2. `frontend/tests/e2e/app.spec.ts`:
```typescript
import { test, expect } from '@playwright/test'

test.describe('App Launch', () => {
  test('should load the application', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Modular AI Architecture/)
    
    // Verify main components are present
    const graphContainer = page.locator('[data-testid="graph-container"]')
    await expect(graphContainer).toBeVisible()
  })

  test('should be accessible', async ({ page }) => {
    await page.goto('/')
    
    // Basic accessibility check
    const accessibilitySnapshot = await page.accessibility.snapshot()
    expect(accessibilitySnapshot).toBeTruthy()
  })
})
```

**Commands to run**:
```bash
cd frontend
npx playwright install
npm run test:e2e
```

**Definition of Done**:
- [ ] Playwright installed with all browsers
- [ ] Configuration supports Chrome, Firefox, Safari
- [ ] Screenshots on failure enabled
- [ ] HTML reporter configured
- [ ] Sample E2E test passing
- [ ] Accessibility testing included

### T1.4: CI/CD Pipeline Setup
**Description**: Create GitHub Actions workflow with test gates
**Files to create**:
1. `.github/workflows/test.yml`:
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        cd backend
        pytest --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        fail_ci_if_error: true

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run unit tests
      run: |
        cd frontend
        npm run test:coverage
    
    - name: Run E2E tests
      run: |
        cd frontend
        npx playwright install --with-deps
        npm run test:e2e
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: frontend/test-results/
```

**Definition of Done**:
- [ ] GitHub Actions workflow created
- [ ] Backend tests run on every push/PR
- [ ] Frontend tests run on every push/PR
- [ ] Coverage reporting integrated
- [ ] Tests must pass for PR merge
- [ ] Artifacts uploaded for debugging

--- 

## Phase 2: Backend Core with TDD (6 hours)

### T2.1: Module Schema and Validation
**Description**: Create Pydantic models for module validation with comprehensive tests
**Files to create**:

1. `backend/tests/unit/test_schemas.py` (CREATE FIRST - TDD):
```python
import pytest
from pydantic import ValidationError
from models.schemas import ModuleSchema, ModuleInput, ModuleOutput, ModuleDependency

class TestModuleSchema:
    def test_valid_module_schema(self):
        """Test creating a valid module schema"""
        data = {
            "name": "TestModule",
            "description": "A test module",
            "status": "implemented",
            "version": "1.0.0",
            "inputs": [
                {"name": "input1", "type": "string", "description": "Test input", "required": True}
            ],
            "outputs": [
                {"name": "output1", "type": "string", "description": "Test output"}
            ],
            "dependencies": [
                {"name": "OtherModule", "version": ">=1.0.0"}
            ]
        }
        module = ModuleSchema(**data)
        assert module.name == "TestModule"
        assert len(module.inputs) == 1
        assert module.inputs[0].required is True

    def test_invalid_status(self):
        """Test that invalid status raises ValidationError"""
        data = {
            "name": "TestModule",
            "description": "Test",
            "status": "invalid_status"
        }
        with pytest.raises(ValidationError) as exc:
            ModuleSchema(**data)
        assert "status" in str(exc.value)

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        # Implementation in next iteration
        pass

    def test_version_compatibility(self):
        """Test semantic versioning validation"""
        dep = ModuleDependency(name="Test", version=">=1.0.0")
        assert dep.is_compatible_with("1.5.0")
        assert not dep.is_compatible_with("0.9.0")
```

2. `backend/models/schemas.py` (CREATE AFTER TESTS):
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from enum import Enum
import semver

class ModuleStatus(str, Enum):
    IMPLEMENTED = "implemented"
    PLACEHOLDER = "placeholder"
    ERROR = "error"
    TESTING = "testing"

class ModuleInput(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    validation: Optional[dict] = None

class ModuleOutput(BaseModel):
    name: str
    type: str
    description: str
    validation: Optional[dict] = None

class ModuleDependency(BaseModel):
    name: str
    version: str = "*"
    
    def is_compatible_with(self, version: str) -> bool:
        """Check if given version satisfies dependency requirement"""
        if self.version == "*":
            return True
        return semver.match(version, self.version)

class ModuleMetadata(BaseModel):
    author: Optional[str] = None
    last_modified: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    test_coverage: Optional[float] = Field(None, ge=0, le=100)

class ModuleSchema(BaseModel):
    name: str
    description: str
    status: ModuleStatus
    version: str = "1.0.0"
    inputs: List[ModuleInput] = Field(default_factory=list)
    outputs: List[ModuleOutput] = Field(default_factory=list)
    dependencies: List[ModuleDependency] = Field(default_factory=list)
    implementation: Optional[str] = None
    metadata: ModuleMetadata = Field(default_factory=ModuleMetadata)
    
    @validator('version')
    def validate_version(cls, v):
        """Validate semantic versioning"""
        try:
            semver.VersionInfo.parse(v)
        except ValueError:
            raise ValueError(f"Invalid version format: {v}")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure module names are valid identifiers"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Module name must be alphanumeric: {v}")
        return v
```

**Commands to run**:
```bash
cd backend
pip install semver
pytest tests/unit/test_schemas.py -v
```

**Definition of Done**:
- [ ] All schema tests written first (TDD)
- [ ] Pydantic models created and passing tests
- [ ] Version validation working
- [ ] Name validation enforced
- [ ] 100% test coverage for schemas
- [ ] No validation errors for valid data

### T2.2: Enhanced Module Loader Service
**Description**: Refactor loader with dependency injection and comprehensive testing
**Files to create**:

1. `backend/tests/unit/test_loader.py` (CREATE FIRST):
```python
import pytest
from pathlib import Path
import yaml
from services.loader import ModuleLoader, LoaderError
from models.schemas import ModuleSchema

class TestModuleLoader:
    @pytest.fixture
    def loader(self, temp_dir):
        """Create loader with temp directory"""
        return ModuleLoader(modules_dir=temp_dir)
    
    def test_load_valid_module(self, loader, temp_dir):
        """Test loading a valid YAML module"""
        module_content = """
name: TestModule
description: Test module
status: implemented
version: 1.0.0
inputs:
  - name: input1
    type: string
    description: Test input
"""
        module_file = temp_dir / "test_module.yaml"
        module_file.write_text(module_content)
        
        module = loader.load_module(module_file)
        assert isinstance(module, ModuleSchema)
        assert module.name == "TestModule"
        assert module.status == "implemented"
    
    def test_load_invalid_yaml(self, loader, temp_dir):
        """Test handling of invalid YAML"""
        module_file = temp_dir / "bad.yaml"
        module_file.write_text("{ invalid yaml }")
        
        with pytest.raises(LoaderError) as exc:
            loader.load_module(module_file)
        assert "Invalid YAML" in str(exc.value)
    
    def test_load_all_modules(self, loader, temp_dir):
        """Test loading multiple modules"""
        for i in range(3):
            content = f"""
name: Module{i}
description: Test module {i}
status: placeholder
"""
            (temp_dir / f"module{i}.yaml").write_text(content)
        
        modules = loader.load_all_modules()
        assert len(modules) == 3
        assert all(isinstance(m, ModuleSchema) for m in modules.values())
    
    def test_validate_dependencies(self, loader, temp_dir):
        """Test dependency validation across modules"""
        module1 = """
name: Module1
description: Module 1
status: implemented
dependencies:
  - name: Module2
    version: ">=1.0.0"
"""
        module2 = """
name: Module2
description: Module 2
status: implemented
version: 1.5.0
"""
        (temp_dir / "module1.yaml").write_text(module1)
        (temp_dir / "module2.yaml").write_text(module2)
        
        modules = loader.load_all_modules()
        errors = loader.validate_dependencies(modules)
        assert len(errors) == 0
```

2. `backend/services/loader.py` (REFACTOR AFTER TESTS):
```python
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import ValidationError
from models.schemas import ModuleSchema
import logging

logger = logging.getLogger(__name__)

class LoaderError(Exception):
    """Custom exception for loader errors"""
    pass

class ModuleLoader:
    def __init__(self, modules_dir: Path):
        self.modules_dir = Path(modules_dir)
        if not self.modules_dir.exists():
            raise LoaderError(f"Modules directory not found: {modules_dir}")
    
    def load_module(self, filepath: Path) -> ModuleSchema:
        """Load and validate a single module"""
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                raise LoaderError(f"Invalid YAML structure in {filepath}")
            
            return ModuleSchema(**data)
            
        except yaml.YAMLError as e:
            raise LoaderError(f"Invalid YAML in {filepath}: {e}")
        except ValidationError as e:
            raise LoaderError(f"Validation error in {filepath}: {e}")
        except Exception as e:
            raise LoaderError(f"Error loading {filepath}: {e}")
    
    def load_all_modules(self) -> Dict[str, ModuleSchema]:
        """Load all YAML modules from directory"""
        modules = {}
        
        for yaml_file in self.modules_dir.glob("*.yaml"):
            try:
                module = self.load_module(yaml_file)
                if module.name in modules:
                    logger.warning(f"Duplicate module name: {module.name}")
                modules[module.name] = module
            except LoaderError as e:
                logger.error(f"Failed to load {yaml_file}: {e}")
                
        return modules
    
    def validate_dependencies(self, modules: Dict[str, ModuleSchema]) -> List[str]:
        """Validate all dependencies are satisfied"""
        errors = []
        
        for name, module in modules.items():
            for dep in module.dependencies:
                if dep.name not in modules:
                    errors.append(f"{name} depends on missing module: {dep.name}")
                elif dep.version != "*":
                    dep_module = modules[dep.name]
                    if not dep.is_compatible_with(dep_module.version):
                        errors.append(
                            f"{name} requires {dep.name} {dep.version}, "
                            f"but {dep_module.version} is available"
                        )
        
        return errors
```

**Commands to run**:
```bash
cd backend
pytest tests/unit/test_loader.py -v --cov=services/loader
```

**Definition of Done**:
- [ ] Loader tests achieve 100% coverage
- [ ] Error handling for all edge cases
- [ ] Dependency validation implemented
- [ ] Logging added for debugging
- [ ] Custom exceptions for clear error messages
- [ ] All tests passing

### T2.3: Graph Builder Service
**Description**: Implement graph builder for dependency visualization
**Files to create**:

1. `backend/tests/unit/test_graph_builder.py` (CREATE FIRST):
```python
import pytest
from services.graph_builder import GraphBuilder
from models.schemas import ModuleSchema, ModuleDependency

class TestGraphBuilder:
    @pytest.fixture
    def modules(self):
        """Create test modules with dependencies"""
        return {
            "A": ModuleSchema(
                name="A",
                description="Module A",
                status="implemented",
                dependencies=[
                    ModuleDependency(name="B"),
                    ModuleDependency(name="C")
                ]
            ),
            "B": ModuleSchema(
                name="B",
                description="Module B",
                status="placeholder",
                dependencies=[ModuleDependency(name="C")]
            ),
            "C": ModuleSchema(
                name="C",
                description="Module C",
                status="implemented"
            )
        }
    
    def test_build_graph_structure(self, modules):
        """Test basic graph structure generation"""
        builder = GraphBuilder()
        graph = builder.build_graph(modules)
        
        assert len(graph["nodes"]) == 3
        assert len(graph["edges"]) == 3
        
        # Check nodes have required fields
        for node in graph["nodes"]:
            assert "id" in node
            assert "label" in node
            assert "status" in node
            assert "color" in node
    
    def test_detect_circular_dependencies(self):
        """Test circular dependency detection"""
        modules = {
            "A": ModuleSchema(
                name="A", 
                description="A",
                status="implemented",
                dependencies=[ModuleDependency(name="B")]
            ),
            "B": ModuleSchema(
                name="B",
                description="B", 
                status="implemented",
                dependencies=[ModuleDependency(name="A")]
            )
        }
        
        builder = GraphBuilder()
        with pytest.raises(ValueError) as exc:
            builder.build_graph(modules)
        assert "Circular dependency" in str(exc.value)
    
    def test_hierarchical_layout(self, modules):
        """Test hierarchical layout generation"""
        builder = GraphBuilder()
        graph = builder.build_graph(modules, layout="hierarchical")
        
        # C should be at lowest level (no dependencies)
        c_node = next(n for n in graph["nodes"] if n["id"] == "C")
        assert c_node.get("level") == 0
        
        # B depends on C, should be level 1
        b_node = next(n for n in graph["nodes"] if n["id"] == "B")
        assert b_node.get("level") == 1
    
    def test_performance_with_many_modules(self):
        """Test performance with 500+ modules"""
        import time
        
        # Generate 500 modules
        modules = {}
        for i in range(500):
            deps = []
            if i > 0:
                # Create some dependencies
                deps = [ModuleDependency(name=f"Module{j}") 
                       for j in range(max(0, i-5), i) if j % 3 == 0]
            
            modules[f"Module{i}"] = ModuleSchema(
                name=f"Module{i}",
                description=f"Module {i}",
                status="implemented",
                dependencies=deps
            )
        
        builder = GraphBuilder()
        start = time.time()
        graph = builder.build_graph(modules)
        duration = time.time() - start
        
        assert len(graph["nodes"]) == 500
        assert duration < 0.1  # Should complete in under 100ms
```

2. `backend/services/graph_builder.py` (CREATE AFTER TESTS):
```python
from typing import Dict, List, Any, Optional, Set
from models.schemas import ModuleSchema
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Build graph data structure for visualization"""
    
    # Status colors for visualization
    STATUS_COLORS = {
        "implemented": "#4CAF50",    # Green
        "placeholder": "#FFC107",    # Yellow
        "error": "#F44336",          # Red
        "testing": "#2196F3"         # Blue
    }
    
    def build_graph(self, modules: Dict[str, ModuleSchema], 
                   layout: str = "network") -> Dict[str, Any]:
        """Build graph structure for vis.js"""
        # First check for circular dependencies
        self._check_circular_dependencies(modules)
        
        nodes = []
        edges = []
        
        # Build nodes
        for name, module in modules.items():
            node = {
                "id": name,
                "label": name,
                "title": module.description,  # Tooltip
                "status": module.status.value,
                "color": self.STATUS_COLORS.get(module.status.value, "#9E9E9E"),
                "shape": "box",
                "font": {"color": "white"},
                "data": {
                    "version": module.version,
                    "inputs": len(module.inputs),
                    "outputs": len(module.outputs),
                    "test_coverage": module.metadata.test_coverage
                }
            }
            
            if layout == "hierarchical":
                node["level"] = self._calculate_level(name, modules)
            
            nodes.append(node)
        
        # Build edges
        edge_id = 0
        for name, module in modules.items():
            for dep in module.dependencies:
                if dep.name in modules:  # Only add edge if dependency exists
                    edges.append({
                        "id": f"edge_{edge_id}",
                        "from": name,
                        "to": dep.name,
                        "arrows": "to",
                        "label": dep.version if dep.version != "*" else "",
                        "color": {"color": "#666666"}
                    })
                    edge_id += 1
        
        return {
            "nodes": nodes,
            "edges": edges,
            "layout": layout
        }
    
    def _check_circular_dependencies(self, modules: Dict[str, ModuleSchema]):
        """Check for circular dependencies using DFS"""
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            if node in modules:
                for dep in modules[node].dependencies:
                    if dep.name not in visited:
                        if has_cycle(dep.name, visited, rec_stack):
                            return True
                    elif dep.name in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        rec_stack = set()
        
        for module_name in modules:
            if module_name not in visited:
                if has_cycle(module_name, visited, rec_stack):
                    raise ValueError(f"Circular dependency detected involving {module_name}")
    
    def _calculate_level(self, node: str, modules: Dict[str, ModuleSchema], 
                        _cache: Optional[Dict[str, int]] = None) -> int:
        """Calculate hierarchical level for a node"""
        if _cache is None:
            _cache = {}
        
        if node in _cache:
            return _cache[node]
        
        if node not in modules or not modules[node].dependencies:
            level = 0
        else:
            # Level is max of dependencies + 1
            dep_levels = []
            for dep in modules[node].dependencies:
                if dep.name in modules:
                    dep_levels.append(self._calculate_level(dep.name, modules, _cache))
            level = max(dep_levels) + 1 if dep_levels else 0
        
        _cache[node] = level
        return level
```

**Commands to run**:
```bash
cd backend
pytest tests/unit/test_graph_builder.py -v --cov=services/graph_builder
```

**Definition of Done**:
- [ ] Graph builder tests pass with 100% coverage
- [ ] Circular dependency detection working
- [ ] Hierarchical layout calculation correct
- [ ] Performance test passes (<100ms for 500 nodes)
- [ ] Status colors properly assigned
- [ ] Edge labels for version constraints

### T2.4: REST API Implementation
**Description**: Create Flask API endpoints with comprehensive testing
**Files to create**:

1. `backend/tests/integration/test_api.py` (CREATE FIRST):
```python
import pytest
import json
from flask import Flask
from api.modules import create_modules_api
from api.dependencies import create_dependencies_api

class TestModulesAPI:
    @pytest.fixture
    def app(self, temp_dir):
        """Create test Flask app"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['MODULES_DIR'] = str(temp_dir)
        
        # Register blueprints
        app.register_blueprint(create_modules_api(temp_dir))
        app.register_blueprint(create_dependencies_api(temp_dir))
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_get_all_modules(self, client, temp_dir):
        """Test GET /api/modules"""
        # Create test module
        module_content = """
name: TestModule
description: Test
status: implemented
"""
        (temp_dir / "test.yaml").write_text(module_content)
        
        response = client.get('/api/modules')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'TestModule'
    
    def test_get_single_module(self, client, temp_dir):
        """Test GET /api/modules/<name>"""
        module_content = """
name: TestModule
description: Test module
status: implemented
version: 1.0.0
"""
        (temp_dir / "test.yaml").write_text(module_content)
        
        response = client.get('/api/modules/TestModule')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['name'] == 'TestModule'
        assert data['version'] == '1.0.0'
    
    def test_create_module(self, client, temp_dir):
        """Test POST /api/modules"""
        new_module = {
            "name": "NewModule",
            "description": "A new module",
            "status": "placeholder"
        }
        
        response = client.post('/api/modules',
                             data=json.dumps(new_module),
                             content_type='application/json')
        
        assert response.status_code == 201
        assert (temp_dir / "NewModule.yaml").exists()
    
    def test_update_module(self, client, temp_dir):
        """Test PUT /api/modules/<name>"""
        # Create initial module
        module_content = """
name: TestModule
description: Original description
status: placeholder
"""
        (temp_dir / "TestModule.yaml").write_text(module_content)
        
        # Update it
        updated_data = {
            "description": "Updated description",
            "status": "implemented"
        }
        
        response = client.put('/api/modules/TestModule',
                            data=json.dumps(updated_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        
        # Verify update
        with open(temp_dir / "TestModule.yaml") as f:
            updated_module = yaml.safe_load(f)
        assert updated_module['description'] == "Updated description"
        assert updated_module['status'] == "implemented"
    
    def test_delete_module(self, client, temp_dir):
        """Test DELETE /api/modules/<name>"""
        # Create module
        (temp_dir / "ToDelete.yaml").write_text("name: ToDelete\ndescription: Test\nstatus: placeholder")
        
        response = client.delete('/api/modules/ToDelete')
        assert response.status_code == 204
        assert not (temp_dir / "ToDelete.yaml").exists()
    
    def test_error_handling(self, client):
        """Test API error handling"""
        response = client.get('/api/modules/NonExistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
```

2. `backend/api/modules.py` (CREATE AFTER TESTS):
```python
from flask import Blueprint, jsonify, request, current_app
from pathlib import Path
import yaml
from services.loader import ModuleLoader, LoaderError
from models.schemas import ModuleSchema
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

def create_modules_api(modules_dir: Path) -> Blueprint:
    """Create modules API blueprint"""
    bp = Blueprint('modules', __name__, url_prefix='/api/modules')
    loader = ModuleLoader(modules_dir)
    
    @bp.route('', methods=['GET'])
    def get_all_modules():
        """Get all modules"""
        try:
            modules = loader.load_all_modules()
            return jsonify([module.dict() for module in modules.values()])
        except Exception as e:
            logger.error(f"Error loading modules: {e}")
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/<string:name>', methods=['GET'])
    def get_module(name: str):
        """Get a specific module"""
        try:
            modules = loader.load_all_modules()
            if name not in modules:
                return jsonify({"error": f"Module {name} not found"}), 404
            return jsonify(modules[name].dict())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @bp.route('', methods=['POST'])
    def create_module():
        """Create a new module"""
        try:
            data = request.get_json()
            module = ModuleSchema(**data)
            
            # Save to file
            filepath = modules_dir / f"{module.name}.yaml"
            if filepath.exists():
                return jsonify({"error": f"Module {module.name} already exists"}), 409
            
            with open(filepath, 'w') as f:
                yaml.dump(module.dict(), f)
            
            return jsonify(module.dict()), 201
            
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/<string:name>', methods=['PUT'])
    def update_module(name: str):
        """Update an existing module"""
        try:
            filepath = modules_dir / f"{name}.yaml"
            if not filepath.exists():
                return jsonify({"error": f"Module {name} not found"}), 404
            
            # Load existing module
            with open(filepath) as f:
                existing_data = yaml.safe_load(f)
            
            # Update with new data
            update_data = request.get_json()
            existing_data.update(update_data)
            
            # Validate
            module = ModuleSchema(**existing_data)
            
            # Save
            with open(filepath, 'w') as f:
                yaml.dump(module.dict(), f)
            
            return jsonify(module.dict())
            
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @bp.route('/<string:name>', methods=['DELETE'])
    def delete_module(name: str):
        """Delete a module"""
        try:
            filepath = modules_dir / f"{name}.yaml"
            if not filepath.exists():
                return jsonify({"error": f"Module {name} not found"}), 404
            
            filepath.unlink()
            return '', 204
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return bp
```

**Commands to run**:
```bash
cd backend
pytest tests/integration/test_api.py -v
```

**Definition of Done**:
- [ ] All CRUD operations tested
- [ ] Error handling for all edge cases
- [ ] Proper HTTP status codes
- [ ] Request validation
- [ ] Response formatting consistent
- [ ] Integration tests passing

--- 

## Phase 3: Frontend Foundation with Component Testing (8 hours)

### T3.1: Vue 3 Project Structure
**Description**: Initialize Vue 3 project with proper structure and TypeScript
**Files to create**:

1. `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

2. `frontend/src/App.vue`:
```vue
<template>
  <div id="app" class="app-container">
    <header class="app-header">
      <h1>Modular AI Architecture</h1>
      <div class="header-actions">
        <button 
          @click="toggleTheme" 
          class="theme-toggle"
          :aria-label="`Switch to ${isDark ? 'light' : 'dark'} theme`"
        >
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </header>
    
    <main class="app-main">
      <GraphView 
        :modules="modules"
        @module-selected="handleModuleSelection"
        @module-created="handleModuleCreation"
      />
      
      <ModulePanel
        v-if="selectedModule"
        :module="selectedModule"
        @close="selectedModule = null"
        @update="handleModuleUpdate"
      />
    </main>
    
    <Toast ref="toast" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useModuleStore } from '@/stores/modules'
import GraphView from '@/components/GraphView.vue'
import ModulePanel from '@/components/ModulePanel.vue'
import Toast from '@/components/Toast.vue'
import type { Module } from '@/types/module'

const moduleStore = useModuleStore()
const modules = computed(() => moduleStore.modules)
const selectedModule = ref<Module | null>(null)
const isDark = ref(false)
const toast = ref()

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

const handleModuleSelection = (moduleId: string) => {
  selectedModule.value = moduleStore.getModuleById(moduleId) || null
}

const handleModuleCreation = async (moduleData: Partial<Module>) => {
  try {
    await moduleStore.createModule(moduleData)
    toast.value?.show('Module created successfully', 'success')
  } catch (error) {
    toast.value?.show('Failed to create module', 'error')
  }
}

const handleModuleUpdate = async (moduleData: Module) => {
  try {
    await moduleStore.updateModule(moduleData.name, moduleData)
    toast.value?.show('Module updated successfully', 'success')
  } catch (error) {
    toast.value?.show('Failed to update module', 'error')
  }
}

onMounted(() => {
  moduleStore.loadModules()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
}

.app-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
</style>
```

3. `frontend/tests/unit/App.test.ts` (CREATE FIRST):
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '@/App.vue'
import { useModuleStore } from '@/stores/modules'

// Mock child components
vi.mock('@/components/GraphView.vue', () => ({
  default: {
    name: 'GraphView',
    template: '<div data-testid="graph-view"></div>',
    props: ['modules'],
    emits: ['module-selected', 'module-created']
  }
}))

vi.mock('@/components/ModulePanel.vue', () => ({
  default: {
    name: 'ModulePanel',
    template: '<div data-testid="module-panel"></div>',
    props: ['module'],
    emits: ['close', 'update']
  }
}))

describe('App.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the application header', () => {
    const wrapper = mount(App)
    expect(wrapper.find('h1').text()).toBe('Modular AI Architecture')
  })

  it('loads modules on mount', async () => {
    const store = useModuleStore()
    const loadModulesSpy = vi.spyOn(store, 'loadModules')
    
    mount(App)
    
    expect(loadModulesSpy).toHaveBeenCalled()
  })

  it('toggles theme when button clicked', async () => {
    const wrapper = mount(App)
    const button = wrapper.find('.theme-toggle')
    
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    
    await button.trigger('click')
    
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('shows module panel when module is selected', async () => {
    const store = useModuleStore()
    store.modules = [
      { name: 'TestModule', description: 'Test', status: 'implemented' }
    ]
    
    const wrapper = mount(App)
    const graphView = wrapper.findComponent({ name: 'GraphView' })
    
    expect(wrapper.find('[data-testid="module-panel"]').exists()).toBe(false)
    
    await graphView.vm.$emit('module-selected', 'TestModule')
    
    expect(wrapper.find('[data-testid="module-panel"]').exists()).toBe(true)
  })

  it('handles module creation', async () => {
    const store = useModuleStore()
    const createModuleSpy = vi.spyOn(store, 'createModule').mockResolvedValue()
    
    const wrapper = mount(App)
    const graphView = wrapper.findComponent({ name: 'GraphView' })
    
    await graphView.vm.$emit('module-created', { name: 'NewModule' })
    
    expect(createModuleSpy).toHaveBeenCalledWith({ name: 'NewModule' })
  })
})
```

**Commands to run**:
```bash
cd frontend
npm run test tests/unit/App.test.ts
```

**Definition of Done**:
- [ ] Vue 3 app structure created
- [ ] TypeScript properly configured
- [ ] Main App component created
- [ ] App component tests passing
- [ ] Theme toggle functionality tested
- [ ] Module selection tested
- [ ] >90% test coverage for App.vue

### T3.2: Pinia Store for Module State
**Description**: Implement reactive state management with Pinia
**Files to create**:

1. `frontend/tests/unit/stores/modules.test.ts` (CREATE FIRST):
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useModuleStore } from '@/stores/modules'
import { api } from '@/services/api'

vi.mock('@/services/api')

describe('Module Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('state', () => {
    it('initializes with empty modules', () => {
      const store = useModuleStore()
      expect(store.modules).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('actions', () => {
    it('loads modules from API', async () => {
      const mockModules = [
        { name: 'Module1', status: 'implemented' },
        { name: 'Module2', status: 'placeholder' }
      ]
      
      vi.mocked(api.getModules).mockResolvedValue(mockModules)
      
      const store = useModuleStore()
      await store.loadModules()
      
      expect(store.modules).toEqual(mockModules)
      expect(store.loading).toBe(false)
    })

    it('handles load error', async () => {
      vi.mocked(api.getModules).mockRejectedValue(new Error('Network error'))
      
      const store = useModuleStore()
      await store.loadModules()
      
      expect(store.modules).toEqual([])
      expect(store.error).toBe('Failed to load modules')
    })

    it('creates a new module', async () => {
      const newModule = { name: 'NewModule', status: 'placeholder' }
      vi.mocked(api.createModule).mockResolvedValue(newModule)
      
      const store = useModuleStore()
      await store.createModule(newModule)
      
      expect(store.modules).toContainEqual(newModule)
    })

    it('updates an existing module', async () => {
      const store = useModuleStore()
      store.modules = [
        { name: 'Module1', status: 'placeholder', description: 'Old' }
      ]
      
      const updated = { name: 'Module1', status: 'implemented', description: 'New' }
      vi.mocked(api.updateModule).mockResolvedValue(updated)
      
      await store.updateModule('Module1', updated)
      
      expect(store.modules[0]).toEqual(updated)
    })

    it('deletes a module', async () => {
      const store = useModuleStore()
      store.modules = [
        { name: 'Module1', status: 'implemented' },
        { name: 'Module2', status: 'placeholder' }
      ]
      
      vi.mocked(api.deleteModule).mockResolvedValue()
      
      await store.deleteModule('Module1')
      
      expect(store.modules).toHaveLength(1)
      expect(store.modules[0].name).toBe('Module2')
    })
  })

  describe('getters', () => {
    it('gets module by ID', () => {
      const store = useModuleStore()
      store.modules = [
        { name: 'Module1', status: 'implemented' },
        { name: 'Module2', status: 'placeholder' }
      ]
      
      const module = store.getModuleById('Module1')
      expect(module?.name).toBe('Module1')
    })

    it('filters modules by status', () => {
      const store = useModuleStore()
      store.modules = [
        { name: 'Module1', status: 'implemented' },
        { name: 'Module2', status: 'placeholder' },
        { name: 'Module3', status: 'implemented' }
      ]
      
      const implemented = store.getModulesByStatus('implemented')
      expect(implemented).toHaveLength(2)
      expect(implemented.every(m => m.status === 'implemented')).toBe(true)
    })
  })

  describe('undo/redo', () => {
    it('tracks state history for undo', async () => {
      const store = useModuleStore()
      
      // Initial state
      expect(store.canUndo).toBe(false)
      
      // Make a change
      const newModule = { name: 'Module1', status: 'placeholder' }
      vi.mocked(api.createModule).mockResolvedValue(newModule)
      await store.createModule(newModule)
      
      expect(store.canUndo).toBe(true)
      
      // Undo
      store.undo()
      expect(store.modules).toEqual([])
      expect(store.canUndo).toBe(false)
      expect(store.canRedo).toBe(true)
    })

    it('supports redo after undo', async () => {
      const store = useModuleStore()
      const newModule = { name: 'Module1', status: 'placeholder' }
      
      vi.mocked(api.createModule).mockResolvedValue(newModule)
      await store.createModule(newModule)
      
      store.undo()
      expect(store.modules).toEqual([])
      
      store.redo()
      expect(store.modules).toContainEqual(newModule)
    })
  })
})
```

2. `frontend/src/stores/modules.ts` (CREATE AFTER TESTS):
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type { Module } from '@/types/module'

interface State {
  modules: Module[]
  history: Module[][]
  historyIndex: number
}

export const useModuleStore = defineStore('modules', () => {
  // State
  const modules = ref<Module[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // History for undo/redo
  const history = ref<Module[][]>([])
  const historyIndex = ref(-1)
  
  // Private: Save state to history
  const saveToHistory = () => {
    // Remove any redo history
    history.value = history.value.slice(0, historyIndex.value + 1)
    
    // Add current state
    history.value.push(JSON.parse(JSON.stringify(modules.value)))
    historyIndex.value++
    
    // Limit history size
    if (history.value.length > 50) {
      history.value.shift()
      historyIndex.value--
    }
  }
  
  // Actions
  const loadModules = async () => {
    loading.value = true
    error.value = null
    
    try {
      modules.value = await api.getModules()
    } catch (err) {
      error.value = 'Failed to load modules'
      console.error('Error loading modules:', err)
    } finally {
      loading.value = false
    }
  }
  
  const createModule = async (moduleData: Partial<Module>) => {
    try {
      saveToHistory()
      const newModule = await api.createModule(moduleData)
      modules.value.push(newModule)
    } catch (err) {
      error.value = 'Failed to create module'
      throw err
    }
  }
  
  const updateModule = async (name: string, moduleData: Partial<Module>) => {
    try {
      saveToHistory()
      const updated = await api.updateModule(name, moduleData)
      const index = modules.value.findIndex(m => m.name === name)
      if (index !== -1) {
        modules.value[index] = updated
      }
    } catch (err) {
      error.value = 'Failed to update module'
      throw err
    }
  }
  
  const deleteModule = async (name: string) => {
    try {
      saveToHistory()
      await api.deleteModule(name)
      modules.value = modules.value.filter(m => m.name !== name)
    } catch (err) {
      error.value = 'Failed to delete module'
      throw err
    }
  }
  
  // Undo/Redo
  const canUndo = computed(() => historyIndex.value >= 0)
  const canRedo = computed(() => historyIndex.value < history.value.length - 1)
  
  const undo = () => {
    if (canUndo.value) {
      if (historyIndex.value === history.value.length - 1) {
        saveToHistory()
        historyIndex.value--
      }
      historyIndex.value--
      modules.value = JSON.parse(JSON.stringify(history.value[historyIndex.value] || []))
    }
  }
  
  const redo = () => {
    if (canRedo.value) {
      historyIndex.value++
      modules.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    }
  }
  
  // Getters
  const getModuleById = (id: string) => {
    return modules.value.find(m => m.name === id)
  }
  
  const getModulesByStatus = (status: string) => {
    return modules.value.filter(m => m.status === status)
  }
  
  return {
    // State
    modules,
    loading,
    error,
    
    // Actions
    loadModules,
    createModule,
    updateModule,
    deleteModule,
    
    // Undo/Redo
    undo,
    redo,
    canUndo,
    canRedo,
    
    // Getters
    getModuleById,
    getModulesByStatus
  }
})
```

3. `frontend/src/types/module.ts`:
```typescript
export interface Module {
  name: string
  description: string
  status: 'implemented' | 'placeholder' | 'error' | 'testing'
  version?: string
  inputs?: ModuleInput[]
  outputs?: ModuleOutput[]
  dependencies?: ModuleDependency[]
  implementation?: string
  metadata?: ModuleMetadata
}

export interface ModuleInput {
  name: string
  type: string
  description: string
  required?: boolean
  validation?: Record<string, any>
}

export interface ModuleOutput {
  name: string
  type: string
  description: string
  validation?: Record<string, any>
}

export interface ModuleDependency {
  name: string
  version?: string
}

export interface ModuleMetadata {
  author?: string
  lastModified?: string
  tags?: string[]
  testCoverage?: number
}
```

**Commands to run**:
```bash
cd frontend
npm run test tests/unit/stores/modules.test.ts
```

**Definition of Done**:
- [ ] Pinia store created with TypeScript
- [ ] All CRUD operations implemented
- [ ] Undo/redo functionality working
- [ ] History management tested
- [ ] Loading and error states handled
- [ ] 100% test coverage for store
- [ ] Type definitions complete

### T3.3: API Client Service
**Description**: Create API client with proper error handling and testing
**Files to create**:

1. `frontend/tests/unit/services/api.test.ts` (CREATE FIRST):
```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { api } from '@/services/api'
import axios from 'axios'

vi.mock('axios')

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getModules', () => {
    it('fetches all modules', async () => {
      const mockModules = [{ name: 'Module1' }, { name: 'Module2' }]
      vi.mocked(axios.get).mockResolvedValue({ data: mockModules })
      
      const result = await api.getModules()
      
      expect(axios.get).toHaveBeenCalledWith('/api/modules')
      expect(result).toEqual(mockModules)
    })

    it('handles network error', async () => {
      vi.mocked(axios.get).mockRejectedValue(new Error('Network error'))
      
      await expect(api.getModules()).rejects.toThrow('Network error')
    })

    it('retries on failure', async () => {
      vi.mocked(axios.get)
        .mockRejectedValueOnce(new Error('Temporary error'))
        .mockResolvedValue({ data: [] })
      
      const result = await api.getModules()
      
      expect(axios.get).toHaveBeenCalledTimes(2)
      expect(result).toEqual([])
    })
  })

  describe('createModule', () => {
    it('creates a new module', async () => {
      const newModule = { name: 'NewModule', status: 'placeholder' }
      vi.mocked(axios.post).mockResolvedValue({ data: newModule })
      
      const result = await api.createModule(newModule)
      
      expect(axios.post).toHaveBeenCalledWith('/api/modules', newModule)
      expect(result).toEqual(newModule)
    })

    it('validates input before sending', async () => {
      const invalidModule = { name: '', status: 'invalid' }
      
      await expect(api.createModule(invalidModule)).rejects.toThrow('Invalid module data')
      expect(axios.post).not.toHaveBeenCalled()
    })
  })

  describe('SSE connection', () => {
    it('establishes SSE connection', () => {
      const mockEventSource = {
        addEventListener: vi.fn(),
        close: vi.fn()
      }
      
      global.EventSource = vi.fn(() => mockEventSource) as any
      
      const onMessage = vi.fn()
      const onError = vi.fn()
      
      const connection = api.connectSSE(onMessage, onError)
      
      expect(global.EventSource).toHaveBeenCalledWith('/api/stream')
      expect(mockEventSource.addEventListener).toHaveBeenCalledWith('message', expect.any(Function))
      expect(mockEventSource.addEventListener).toHaveBeenCalledWith('error', expect.any(Function))
    })

    it('auto-reconnects on connection loss', async () => {
      vi.useFakeTimers()
      
      const mockEventSource = {
        addEventListener: vi.fn(),
        close: vi.fn(),
        readyState: 2 // CLOSED
      }
      
      global.EventSource = vi.fn(() => mockEventSource) as any
      
      const onMessage = vi.fn()
      const onError = vi.fn()
      
      api.connectSSE(onMessage, onError)
      
      // Trigger error
      const errorHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'error')[1]
      errorHandler(new Event('error'))
      
      expect(onError).toHaveBeenCalled()
      
      // Fast-forward reconnect timer
      vi.advanceTimersByTime(5000)
      
      expect(global.EventSource).toHaveBeenCalledTimes(2)
      
      vi.useRealTimers()
    })
  })
})
```

2. `frontend/src/services/api.ts` (CREATE AFTER TESTS):
```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'
import type { Module } from '@/types/module'

class APIClient {
  private client: AxiosInstance
  private sseConnection: EventSource | null = null
  private reconnectTimer: number | null = null
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    // Request interceptor
    this.client.interceptors.request.use(
      config => {
        // Add auth token if available (future)
        return config
      },
      error => Promise.reject(error)
    )
    
    // Response interceptor
    this.client.interceptors.response.use(
      response => response,
      async error => {
        if (error.code === 'ECONNABORTED' || !error.response) {
          // Retry once on timeout/network error
          const config = error.config
          if (!config.__retryCount) {
            config.__retryCount = 1
            return this.client(config)
          }
        }
        return Promise.reject(error)
      }
    )
  }
  
  // Module endpoints
  async getModules(): Promise<Module[]> {
    const response = await this.client.get<Module[]>('/api/modules')
    return response.data
  }
  
  async getModule(name: string): Promise<Module> {
    const response = await this.client.get<Module>(`/api/modules/${name}`)
    return response.data
  }
  
  async createModule(module: Partial<Module>): Promise<Module> {
    // Client-side validation
    if (!module.name || module.name.trim() === '') {
      throw new Error('Invalid module data: name is required')
    }
    
    if (module.status && !['implemented', 'placeholder', 'error', 'testing'].includes(module.status)) {
      throw new Error('Invalid module data: invalid status')
    }
    
    const response = await this.client.post<Module>('/api/modules', module)
    return response.data
  }
  
  async updateModule(name: string, module: Partial<Module>): Promise<Module> {
    const response = await this.client.put<Module>(`/api/modules/${name}`, module)
    return response.data
  }
  
  async deleteModule(name: string): Promise<void> {
    await this.client.delete(`/api/modules/${name}`)
  }
  
  // Graph endpoint
  async getGraph(layout: string = 'network'): Promise<any> {
    const response = await this.client.get(`/api/graph?layout=${layout}`)
    return response.data
  }
  
  // SSE connection
  connectSSE(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void
  ): () => void {
    // Close existing connection
    this.disconnectSSE()
    
    const connect = () => {
      this.sseConnection = new EventSource('/api/stream')
      
      this.sseConnection.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (err) {
          console.error('Failed to parse SSE message:', err)
        }
      })
      
      this.sseConnection.addEventListener('error', (event) => {
        console.error('SSE connection error:', event)
        onError?.(event)
        
        // Auto-reconnect if connection closed
        if (this.sseConnection?.readyState === EventSource.CLOSED) {
          this.scheduleReconnect(connect)
        }
      })
      
      this.sseConnection.addEventListener('open', () => {
        console.log('SSE connection established')
        this.clearReconnectTimer()
      })
    }
    
    connect()
    
    // Return cleanup function
    return () => this.disconnectSSE()
  }
  
  private scheduleReconnect(connectFn: () => void) {
    this.clearReconnectTimer()
    this.reconnectTimer = window.setTimeout(() => {
      console.log('Attempting SSE reconnection...')
      connectFn()
    }, 5000)
  }
  
  private clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
  
  disconnectSSE() {
    this.clearReconnectTimer()
    if (this.sseConnection) {
      this.sseConnection.close()
      this.sseConnection = null
    }
  }
}

export const api = new APIClient()
```

**Commands to run**:
```bash
cd frontend
npm run test tests/unit/services/api.test.ts
```

**Definition of Done**:
- [ ] API client created with axios
- [ ] All endpoints implemented
- [ ] Error handling and retry logic
- [ ] SSE connection with auto-reconnect
- [ ] Client-side validation
- [ ] Request/response interceptors
- [ ] 100% test coverage for API service

--- 

## Summary and Key Principles

### Critical Success Factors

1. **Test-First Development**: EVERY feature must have tests written BEFORE implementation
2. **100% Coverage for Critical Paths**: No exceptions - all core functionality must be fully tested
3. **Isolated Testing**: Components should be testable without external dependencies
4. **Performance Benchmarks**: 500+ modules must render at 60 FPS
5. **Accessibility Compliance**: WCAG 2.1 AA is non-negotiable

### Testing Strategy Recap

```
Unit Tests (60%)          - Fast, isolated, comprehensive
Integration Tests (30%)   - API contracts, service interactions
E2E Tests (10%)          - User workflows, visual regression
```

### Common Pitfalls to Avoid

1. **Don't test implementation details** - Test behavior, not internals
2. **Don't skip error cases** - Error handling is critical functionality
3. **Don't ignore performance** - Test with realistic data volumes
4. **Don't forget accessibility** - Include in component tests
5. **Don't mix concerns** - Keep visualization separate from business logic

### Development Workflow

1. Write failing test
2. Implement minimal code to pass
3. Refactor for quality
4. Ensure coverage targets met
5. Run full test suite
6. Commit with descriptive message

### Key Commands Reference

```bash
# Backend
cd backend
pytest                        # Run all tests
pytest --cov                  # With coverage
pytest -k "test_name"         # Run specific test
pytest --markers              # List test markers

# Frontend
cd frontend
npm run test                  # Run all tests
npm run test:coverage         # With coverage
npm run test:ui              # Interactive UI
npm run test:e2e             # E2E tests
npm run test -- --watch      # Watch mode
```

### Architecture Decisions

1. **vis.js over D3.js**: Simpler API, better performance for our use case
2. **Vue 3 Composition API**: Better TypeScript support, more testable
3. **Pinia over Vuex**: Modern, simpler, built for Vue 3
4. **SSE over WebSockets**: One-way updates are sufficient
5. **TDD Everywhere**: Quality through comprehensive testing

### Next Steps After Implementation

1. Set up monitoring and error tracking
2. Add performance profiling
3. Implement security scanning
4. Create user documentation
5. Plan for scalability testing

### Remember

**"If it's not tested, it's broken"** - This project prioritizes reliability and quality over speed of development. Every line of code should be written with testing in mind. 