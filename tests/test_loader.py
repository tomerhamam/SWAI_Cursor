#!/usr/bin/env python3
"""
Unit tests for the loader module.
"""

import os
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any

from loader import (
    ModuleNode, 
    ModuleStatus, 
    IOSpec,
    load_yaml_file,
    validate_module,
    load_modules,
    validate_dependencies
)


class TestIOSpec:
    """Test IOSpec model."""
    
    def test_valid_io_spec(self):
        """Test valid IOSpec creation."""
        spec = IOSpec(type="TestType", description="Test description")
        assert spec.type == "TestType"
        assert spec.description == "Test description"
    
    def test_missing_required_fields(self):
        """Test IOSpec with missing required fields."""
        with pytest.raises(ValueError):
            IOSpec(type="TestType")  # Missing description
        
        with pytest.raises(ValueError):
            IOSpec(description="Test description")  # Missing type


class TestModuleNode:
    """Test ModuleNode model."""
    
    def test_valid_module_node(self):
        """Test valid ModuleNode creation."""
        module = ModuleNode(
            name="TestModule",
            description="Test module description",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.IMPLEMENTED
        )
        assert module.name == "TestModule"
        assert module.status == ModuleStatus.IMPLEMENTED
        assert len(module.inputs) == 1
        assert len(module.outputs) == 1
        assert module.dependencies == []
    
    def test_module_with_dependencies(self):
        """Test ModuleNode with dependencies."""
        module = ModuleNode(
            name="TestModule",
            description="Test module description",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.PLACEHOLDER,
            dependencies=["Dep1", "Dep2"]
        )
        assert module.dependencies == ["Dep1", "Dep2"]
    
    def test_invalid_status(self):
        """Test ModuleNode with invalid status."""
        with pytest.raises(ValueError):
            ModuleNode(
                name="TestModule",
                description="Test module description",
                inputs=[IOSpec(type="Input", description="Input desc")],
                outputs=[IOSpec(type="Output", description="Output desc")],
                status="invalid_status"
            )
    
    def test_string_representation(self):
        """Test ModuleNode string representation."""
        module = ModuleNode(
            name="TestModule",
            description="Test module description",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.ERROR,
            dependencies=["Dep1"]
        )
        str_repr = str(module)
        assert "TestModule" in str_repr
        assert "error" in str_repr
        assert "deps=1" in str_repr


class TestYAMLLoading:
    """Test YAML file loading functions."""
    
    def test_load_valid_yaml(self):
        """Test loading valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
name: "TestModule"
description: "Test description"
inputs:
  - type: "Input"
    description: "Input description"
outputs:
  - type: "Output"
    description: "Output description"
status: "implemented"
            """)
            f.flush()
            
            try:
                data = load_yaml_file(Path(f.name))
                assert data["name"] == "TestModule"
                assert data["status"] == "implemented"
            finally:
                os.unlink(f.name)
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            try:
                with pytest.raises(ValueError):
                    load_yaml_file(Path(f.name))
            finally:
                os.unlink(f.name)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        with pytest.raises(ValueError):
            load_yaml_file(Path("/nonexistent/file.yaml"))


class TestModuleValidation:
    """Test module validation functions."""
    
    def test_validate_valid_module(self):
        """Test validating valid module data."""
        data = {
            "name": "TestModule",
            "description": "Test description",
            "inputs": [{"type": "Input", "description": "Input desc"}],
            "outputs": [{"type": "Output", "description": "Output desc"}],
            "status": "implemented"
        }
        
        module = validate_module(data, Path("test.yaml"))
        assert module.name == "TestModule"
        assert module.status == ModuleStatus.IMPLEMENTED
    
    def test_validate_invalid_module(self):
        """Test validating invalid module data."""
        data = {
            "name": "TestModule",
            "description": "Test description",
            "inputs": [{"type": "Input", "description": "Input desc"}],
            "outputs": [{"type": "Output", "description": "Output desc"}],
            "status": "invalid_status"
        }
        
        with pytest.raises(ValueError):
            validate_module(data, Path("test.yaml"))
    
    def test_validate_missing_required_fields(self):
        """Test validating module with missing required fields."""
        data = {
            "name": "TestModule",
            "description": "Test description",
            # Missing inputs and outputs
            "status": "implemented"
        }
        
        with pytest.raises(ValueError):
            validate_module(data, Path("test.yaml"))


class TestModuleLoading:
    """Test module loading from directories."""
    
    def test_load_modules_from_directory(self):
        """Test loading modules from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create valid module file
            module_file = Path(temp_dir) / "test_module.yaml"
            with open(module_file, 'w') as f:
                f.write("""
name: "TestModule"
description: "Test description"
inputs:
  - type: "Input"
    description: "Input description"
outputs:
  - type: "Output"
    description: "Output description"
status: "implemented"
                """)
            
            modules = load_modules(temp_dir)
            assert len(modules) == 1
            assert modules[0].name == "TestModule"
    
    def test_load_modules_nonexistent_directory(self):
        """Test loading modules from non-existent directory."""
        with pytest.raises(ValueError):
            load_modules("/nonexistent/directory")
    
    def test_load_modules_empty_directory(self):
        """Test loading modules from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            modules = load_modules(temp_dir)
            assert len(modules) == 0
    
    def test_load_modules_duplicate_names(self):
        """Test loading modules with duplicate names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two modules with the same name
            for i in range(2):
                module_file = Path(temp_dir) / f"test_module_{i}.yaml"
                with open(module_file, 'w') as f:
                    f.write("""
name: "DuplicateModule"
description: "Test description"
inputs:
  - type: "Input"
    description: "Input description"
outputs:
  - type: "Output"
    description: "Output description"
status: "implemented"
                    """)
            
            # Should exit with error due to duplicate names
            with pytest.raises(SystemExit):
                load_modules(temp_dir)


class TestDependencyValidation:
    """Test dependency validation."""
    
    def test_validate_valid_dependencies(self):
        """Test validating modules with valid dependencies."""
        module1 = ModuleNode(
            name="Module1",
            description="Test module 1",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.IMPLEMENTED,
            dependencies=[]
        )
        
        module2 = ModuleNode(
            name="Module2",
            description="Test module 2",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.IMPLEMENTED,
            dependencies=["Module1"]
        )
        
        # Should not raise any errors
        validate_dependencies([module1, module2])
    
    def test_validate_missing_dependencies(self):
        """Test validating modules with missing dependencies."""
        module = ModuleNode(
            name="Module1",
            description="Test module 1",
            inputs=[IOSpec(type="Input", description="Input desc")],
            outputs=[IOSpec(type="Output", description="Output desc")],
            status=ModuleStatus.IMPLEMENTED,
            dependencies=["NonExistentModule"]
        )
        
        # Should warn about missing dependency (captured by capsys if needed)
        validate_dependencies([module])


class TestIntegration:
    """Integration tests using actual module files."""
    
    def test_load_sample_modules(self):
        """Test loading the actual sample modules from the modules directory."""
        # This assumes we're running from the project root
        modules_dir = Path("modules")
        
        if not modules_dir.exists():
            pytest.skip("modules directory not found")
        
        # Test loading valid modules (excluding invalid one)
        valid_modules = []
        for yaml_file in modules_dir.glob("*.yaml"):
            if yaml_file.name != "invalid_module.yaml":
                try:
                    data = load_yaml_file(yaml_file)
                    module = validate_module(data, yaml_file)
                    valid_modules.append(module)
                except Exception as e:
                    pytest.fail(f"Failed to load {yaml_file}: {e}")
        
        # Should have loaded all valid modules
        assert len(valid_modules) >= 5
        
        # Verify module names are unique
        names = [m.name for m in valid_modules]
        assert len(names) == len(set(names))
    
    def test_invalid_module_fails(self):
        """Test that invalid module fails validation."""
        invalid_file = Path("modules/invalid_module.yaml")
        
        if not invalid_file.exists():
            pytest.skip("invalid_module.yaml not found")
        
        with pytest.raises(ValueError):
            data = load_yaml_file(invalid_file)
            validate_module(data, invalid_file) 