"""
Pydantic schemas for module validation and serialization.

This module defines the data structures for validating YAML module definitions
and ensuring consistent data formats throughout the system.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class ModuleStatus(str, Enum):
    """Valid module implementation statuses"""
    placeholder = "placeholder"
    stub = "stub"
    surrogate = "surrogate"
    implemented = "implemented"


class ModuleType(str, Enum):
    """Valid module types for categorization"""
    service = "service"
    component = "component"
    utility = "utility"
    interface = "interface"
    data = "data"


class InputSchema(BaseModel):
    """Schema for module input definition"""
    type: str = Field(..., description="The input data type")
    description: str = Field(..., description="Human readable description of the input")
    required: bool = Field(default=False, description="Whether this input is required")
    
    model_config = ConfigDict(extra="forbid")


class OutputSchema(BaseModel):
    """Schema for module output definition"""
    type: str = Field(..., description="The output data type")
    description: str = Field(..., description="Human readable description of the output")
    format: Optional[str] = Field(default=None, description="Optional format specification")
    
    model_config = ConfigDict(extra="forbid")


class DependencySchema(BaseModel):
    """Schema for module dependency definition"""
    name: str = Field(..., description="Name of the dependent module")
    required: bool = Field(default=False, description="Whether this dependency is required")
    description: Optional[str] = Field(default=None, description="Description of the dependency relationship")
    
    model_config = ConfigDict(extra="forbid")


class ModuleSchema(BaseModel):
    """
    Main schema for module validation.
    
    This schema validates the complete structure of a module definition,
    ensuring all required fields are present and properly formatted.
    """
    
    # Required fields
    name: str = Field(..., description="Unique module name")
    description: str = Field(..., description="Human readable description")
    status: ModuleStatus = Field(..., description="Current implementation status")
    
    # Optional fields with defaults
    type: ModuleType = Field(default=ModuleType.service, description="Module type category")
    version: str = Field(default="1.0.0", description="Module version")
    
    # Collections
    inputs: List[InputSchema] = Field(default_factory=list, description="Module input definitions")
    outputs: List[OutputSchema] = Field(default_factory=list, description="Module output definitions")
    dependencies: List[DependencySchema] = Field(default_factory=list, description="Module dependencies")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate module name format"""
        if not v:
            raise ValueError("Module name cannot be empty")
        
        # Module names should be valid identifiers (no spaces, special chars except underscore)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                "Module name must start with a letter and contain only letters, numbers, and underscores"
            )
        
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description is not empty"""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


# Validation helper functions

def validate_module_yaml(yaml_data: Dict[str, Any]) -> ModuleSchema:
    """
    Validate a module definition from YAML data.
    
    Args:
        yaml_data: Dictionary containing module definition from YAML
        
    Returns:
        ModuleSchema: Validated module schema
        
    Raises:
        ValidationError: If the module definition is invalid
    """
    return ModuleSchema(**yaml_data)


def validate_modules_batch(modules_data: List[Dict[str, Any]]) -> List[ModuleSchema]:
    """
    Validate multiple module definitions.
    
    Args:
        modules_data: List of dictionaries containing module definitions
        
    Returns:
        List[ModuleSchema]: List of validated module schemas
        
    Raises:
        ValidationError: If any module definition is invalid
    """
    return [ModuleSchema(**module_data) for module_data in modules_data]


# Export all schemas for easy importing
__all__ = [
    'ModuleSchema',
    'InputSchema', 
    'OutputSchema',
    'DependencySchema',
    'ModuleStatus',
    'ModuleType',
    'validate_module_yaml',
    'validate_modules_batch'
] 