import pytest
from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import ValidationError

# Import the schemas we'll be creating
from backend.models.schemas import (
    ModuleSchema, 
    InputSchema, 
    OutputSchema, 
    DependencySchema,
    ModuleStatus,
    ModuleType
)


class TestModuleStatus:
    """Test the ModuleStatus enum"""
    
    def test_valid_statuses(self):
        """Test all valid module statuses"""
        valid_statuses = ['placeholder', 'stub', 'surrogate', 'implemented']
        for status in valid_statuses:
            assert ModuleStatus(status) == status
    
    def test_invalid_status(self):
        """Test invalid status raises error"""
        with pytest.raises(ValueError):
            ModuleStatus('invalid')


class TestModuleType:
    """Test the ModuleType enum"""
    
    def test_valid_types(self):
        """Test all valid module types"""
        valid_types = ['service', 'component', 'utility', 'interface', 'data']
        for module_type in valid_types:
            assert ModuleType(module_type) == module_type
    
    def test_invalid_type(self):
        """Test invalid type raises error"""
        with pytest.raises(ValueError):
            ModuleType('invalid')


class TestInputSchema:
    """Test input schema validation"""
    
    def test_valid_input(self):
        """Test valid input creation"""
        input_data = {
            'type': 'string',
            'description': 'User input text',
            'required': True
        }
        input_schema = InputSchema(**input_data)
        assert input_schema.type == 'string'
        assert input_schema.description == 'User input text'
        assert input_schema.required is True
    
    def test_optional_fields_defaults(self):
        """Test optional fields have correct defaults"""
        input_data = {'type': 'string', 'description': 'Test input'}
        input_schema = InputSchema(**input_data)
        assert input_schema.required is False  # Default should be False
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields"""
        with pytest.raises(ValidationError):
            InputSchema(type='string')  # Missing description
        
        with pytest.raises(ValidationError):
            InputSchema(description='Test')  # Missing type


class TestOutputSchema:
    """Test output schema validation"""
    
    def test_valid_output(self):
        """Test valid output creation"""
        output_data = {
            'type': 'json',
            'description': 'Processed result',
            'format': 'application/json'
        }
        output_schema = OutputSchema(**output_data)
        assert output_schema.type == 'json'
        assert output_schema.description == 'Processed result'
        assert output_schema.format == 'application/json'
    
    def test_optional_format_field(self):
        """Test format field is optional"""
        output_data = {'type': 'string', 'description': 'Simple output'}
        output_schema = OutputSchema(**output_data)
        assert output_schema.format is None
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields"""
        with pytest.raises(ValidationError):
            OutputSchema(type='string')  # Missing description


class TestDependencySchema:
    """Test dependency schema validation"""
    
    def test_valid_dependency(self):
        """Test valid dependency creation"""
        dep_data = {
            'name': 'UserService',
            'required': True,
            'description': 'Handles user authentication'
        }
        dependency = DependencySchema(**dep_data)
        assert dependency.name == 'UserService'
        assert dependency.required is True
        assert dependency.description == 'Handles user authentication'
    
    def test_optional_fields_defaults(self):
        """Test optional fields have correct defaults"""
        dep_data = {'name': 'OptionalService'}
        dependency = DependencySchema(**dep_data)
        assert dependency.required is False
        assert dependency.description is None
    
    def test_missing_required_name(self):
        """Test validation fails for missing name"""
        with pytest.raises(ValidationError):
            DependencySchema(required=True)


class TestModuleSchema:
    """Test the main module schema validation"""
    
    def test_valid_complete_module(self):
        """Test valid module with all fields"""
        module_data = {
            'name': 'TestModule',
            'description': 'A test module for validation',
            'status': 'implemented',
            'type': 'service',
            'version': '1.0.0',
            'inputs': [
                {'type': 'string', 'description': 'Input text', 'required': True}
            ],
            'outputs': [
                {'type': 'json', 'description': 'Processed result'}
            ],
            'dependencies': [
                {'name': 'UtilityModule', 'required': True}
            ],
            'metadata': {
                'author': 'Test Author',
                'created': '2024-01-01'
            }
        }
        
        module = ModuleSchema(**module_data)
        assert module.name == 'TestModule'
        assert module.status == ModuleStatus.implemented
        assert module.type == ModuleType.service
        assert len(module.inputs) == 1
        assert len(module.outputs) == 1
        assert len(module.dependencies) == 1
        assert module.metadata['author'] == 'Test Author'
    
    def test_minimal_valid_module(self):
        """Test module with only required fields"""
        module_data = {
            'name': 'MinimalModule',
            'description': 'Minimal module',
            'status': 'placeholder'
        }
        
        module = ModuleSchema(**module_data)
        assert module.name == 'MinimalModule'
        assert module.status == ModuleStatus.placeholder
        assert module.type == ModuleType.service  # Default value
        assert module.version == '1.0.0'  # Default value
        assert module.inputs == []
        assert module.outputs == []
        assert module.dependencies == []
        assert module.metadata == {}
    
    def test_invalid_module_name(self):
        """Test validation fails for invalid module names"""
        # Empty name
        with pytest.raises(ValidationError):
            ModuleSchema(name='', description='Test', status='placeholder')
        
        # Name with spaces
        with pytest.raises(ValidationError):
            ModuleSchema(name='Invalid Name', description='Test', status='placeholder')
        
        # Name with special characters
        with pytest.raises(ValidationError):
            ModuleSchema(name='Invalid@Name', description='Test', status='placeholder')
    
    def test_invalid_status(self):
        """Test validation fails for invalid status"""
        with pytest.raises(ValidationError):
            ModuleSchema(
                name='TestModule',
                description='Test',
                status='invalid_status'
            )
    
    def test_invalid_type(self):
        """Test validation fails for invalid type"""
        with pytest.raises(ValidationError):
            ModuleSchema(
                name='TestModule',
                description='Test',
                status='placeholder',
                type='invalid_type'
            )
    
    def test_nested_validation_errors(self):
        """Test validation fails for invalid nested objects"""
        # Invalid input
        module_data = {
            'name': 'TestModule',
            'description': 'Test',
            'status': 'placeholder',
            'inputs': [{'type': 'string'}]  # Missing description
        }
        
        with pytest.raises(ValidationError):
            ModuleSchema(**module_data)
        
        # Invalid dependency
        module_data = {
            'name': 'TestModule',
            'description': 'Test',
            'status': 'placeholder',
            'dependencies': [{'required': True}]  # Missing name
        }
        
        with pytest.raises(ValidationError):
            ModuleSchema(**module_data)
    
    def test_version_validation(self):
        """Test version field validation"""
        # Valid semantic version
        module_data = {
            'name': 'TestModule',
            'description': 'Test',
            'status': 'placeholder',
            'version': '2.1.3'
        }
        module = ModuleSchema(**module_data)
        assert module.version == '2.1.3'
        
        # Invalid version format should still work (we'll validate format separately if needed)
        module_data['version'] = 'v1.0'
        module = ModuleSchema(**module_data)
        assert module.version == 'v1.0'


class TestYAMLIntegration:
    """Test integration with YAML loading"""
    
    def test_load_from_yaml_string(self, sample_module_yaml):
        """Test loading module from YAML string"""
        yaml_data = yaml.safe_load(sample_module_yaml)
        module = ModuleSchema(**yaml_data)
        
        assert module.name is not None
        assert module.description is not None
        assert module.status is not None
    
    def test_load_invalid_yaml_structure(self):
        """Test loading invalid YAML structure"""
        invalid_yaml = """
        name: TestModule
        invalid_field: true
        missing_required_fields: true
        """
        
        yaml_data = yaml.safe_load(invalid_yaml)
        
        # Should fail due to missing required fields
        with pytest.raises(ValidationError):
            ModuleSchema(**yaml_data)
    
    def test_export_to_dict(self):
        """Test exporting module back to dict format"""
        module_data = {
            'name': 'ExportTest',
            'description': 'Test export functionality',
            'status': 'implemented',
            'type': 'component'
        }
        
        module = ModuleSchema(**module_data)
        exported = module.model_dump()
        
        assert exported['name'] == 'ExportTest'
        assert exported['status'] == 'implemented'
        assert exported['type'] == 'component'
        
        # Should be able to recreate from exported data
        module2 = ModuleSchema(**exported)
        assert module2.name == module.name
        assert module2.status == module.status


class TestModuleValidationEdgeCases:
    """Test edge cases and complex validation scenarios"""
    
    def test_circular_dependency_detection_data_structure(self):
        """Test that we can represent potential circular dependencies in data"""
        # This tests the data structure can handle the case, actual circular detection
        # will be in the graph builder service
        module_data = {
            'name': 'ModuleA',
            'description': 'Module A',
            'status': 'placeholder',
            'dependencies': [
                {'name': 'ModuleB', 'required': True},
                {'name': 'ModuleC', 'required': False}
            ]
        }
        
        module = ModuleSchema(**module_data)
        assert len(module.dependencies) == 2
        assert module.dependencies[0].name == 'ModuleB'
        assert module.dependencies[1].name == 'ModuleC'
    
    def test_large_module_data(self):
        """Test module with large amounts of data"""
        # Create a module with many inputs, outputs, and dependencies
        large_module_data = {
            'name': 'LargeModule',
            'description': 'Module with many connections',
            'status': 'implemented',
            'inputs': [
                {'type': f'input_type_{i}', 'description': f'Input {i}'}
                for i in range(50)
            ],
            'outputs': [
                {'type': f'output_type_{i}', 'description': f'Output {i}'}
                for i in range(30)
            ],
            'dependencies': [
                {'name': f'Dependency_{i}', 'required': i % 2 == 0}
                for i in range(100)
            ]
        }
        
        module = ModuleSchema(**large_module_data)
        assert len(module.inputs) == 50
        assert len(module.outputs) == 30
        assert len(module.dependencies) == 100
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters in descriptions"""
        module_data = {
            'name': 'UnicodeModule',
            'description': 'Module with émojis 🚀 and ünicode çharacters',
            'status': 'placeholder',
            'inputs': [
                {
                    'type': 'string',
                    'description': 'Input with 中文 and русский text'
                }
            ]
        }
        
        module = ModuleSchema(**module_data)
        assert '🚀' in module.description
        assert '中文' in module.inputs[0].description
    
    def test_empty_collections(self):
        """Test behavior with empty collections"""
        module_data = {
            'name': 'EmptyCollections',
            'description': 'Test empty collections',
            'status': 'placeholder',
            'inputs': [],
            'outputs': [],
            'dependencies': [],
            'metadata': {}
        }
        
        module = ModuleSchema(**module_data)
        assert module.inputs == []
        assert module.outputs == []
        assert module.dependencies == []
        assert module.metadata == {} 