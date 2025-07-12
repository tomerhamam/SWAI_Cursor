#!/usr/bin/env python3
"""
Module loader and validator for YAML-based module definitions.

This module provides Pydantic models for validating module schemas and
a CLI interface for loading and validating module directories.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

import yaml
from pydantic import BaseModel, Field, ValidationError


class ModuleStatus(str, Enum):
    """Allowed module implementation statuses."""
    IMPLEMENTED = "implemented"
    PLACEHOLDER = "placeholder"
    ERROR = "error"


class IOSpec(BaseModel):
    """Input/Output specification model."""
    type: str = Field(..., description="Data type name")
    description: str = Field(..., description="Human-readable description")


class ModuleNode(BaseModel):
    """Pydantic model for module validation."""
    name: str = Field(..., description="Unique module identifier")
    description: str = Field(..., description="Module purpose description")
    inputs: List[IOSpec] = Field(..., description="List of input specifications")
    outputs: List[IOSpec] = Field(..., description="List of output specifications") 
    status: ModuleStatus = Field(..., description="Implementation status")
    implementation: Optional[str] = Field(None, description="Implementation type or path")
    dependencies: List[str] = Field(default_factory=list, description="Module dependencies")

    def __str__(self) -> str:
        """String representation of the module."""
        return f"Module({self.name}, status={self.status.value}, deps={len(self.dependencies)})"


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load YAML file {file_path}: {e}")


def validate_module(data: Dict[str, Any], file_path: Path) -> ModuleNode:
    """Validate module data against schema."""
    try:
        return ModuleNode(**data)
    except ValidationError as e:
        raise ValueError(f"Validation failed for {file_path}: {e}")


def load_modules(directory: str) -> List[ModuleNode]:
    """
    Load all YAML modules from a directory.
    
    Args:
        directory: Path to directory containing YAML files
        
    Returns:
        List of validated ModuleNode objects
        
    Raises:
        ValueError: If validation fails or duplicate names found
    """
    modules_dir = Path(directory)
    
    if not modules_dir.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not modules_dir.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Find all YAML files
    yaml_files = list(modules_dir.glob("*.yaml")) + list(modules_dir.glob("*.yml"))
    
    if not yaml_files:
        print(f"Warning: No YAML files found in {directory}")
        return []
    
    modules = []
    module_names = set()
    
    for yaml_file in yaml_files:
        try:
            # Load and validate YAML
            data = load_yaml_file(yaml_file)
            module = validate_module(data, yaml_file)
            
            # Check for duplicate names
            if module.name in module_names:
                raise ValueError(f"Duplicate module name '{module.name}' found in {yaml_file}")
            
            module_names.add(module.name)
            modules.append(module)
            
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    return modules


def validate_dependencies(modules: List[ModuleNode]) -> None:
    """Validate that all dependencies exist."""
    module_names = {module.name for module in modules}
    
    for module in modules:
        for dep in module.dependencies:
            if dep not in module_names:
                print(f"Warning: Module '{module.name}' depends on '{dep}' which was not found")


def main() -> None:
    """CLI entry point for module loader."""
    parser = argparse.ArgumentParser(
        description="Load and validate YAML module definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m loader modules/
  python loader.py modules/ --validate-deps
        """
    )
    
    parser.add_argument(
        "directory",
        help="Directory containing YAML module files"
    )
    
    parser.add_argument(
        "--validate-deps",
        action="store_true",
        help="Validate that all dependencies exist"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load modules
        modules = load_modules(args.directory)
        
        if not args.quiet:
            print(f"Successfully loaded {len(modules)} modules from {args.directory}")
            print("\nModules:")
            for module in modules:
                print(f"  - {module}")
        
        # Validate dependencies if requested
        if args.validate_deps:
            validate_dependencies(modules)
        
        if not args.quiet:
            print(f"\nValidation complete. All {len(modules)} modules are valid.")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 