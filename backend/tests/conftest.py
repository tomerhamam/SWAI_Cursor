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
  - name: OtherModule
    required: true
""" 