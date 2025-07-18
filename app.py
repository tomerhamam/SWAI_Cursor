#!/usr/bin/env python3
"""
Flask backend for Modular AI Architecture visualization and surrogate execution.

Provides API endpoints for serving the frontend and executing module surrogates.
"""

import json
from pathlib import Path
from typing import Dict, Any

from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask.wrappers import Response

from backend.services.loader import load_modules, ModuleNode
from backend.services.surrogate import registry
import yaml
import re


# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')


# Global module data cache
_module_cache = {}
_modules_loaded = False


def validate_module_name(module_name: str) -> tuple[bool, str]:
    """
    Validate module name to prevent path traversal attacks and ensure proper format.
    
    Args:
        module_name: The module name to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not module_name:
        return False, "Module name cannot be empty"
    
    # Limit length to prevent abuse
    if len(module_name) > 50:
        return False, "Module name cannot exceed 50 characters"
    
    # Allow only alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', module_name):
        return False, "Module name can only contain letters, numbers, underscores, and hyphens"
    
    # Prevent path traversal patterns
    if '..' in module_name or '/' in module_name or '\\' in module_name:
        return False, "Module name cannot contain path traversal characters"
    
    return True, ""


def check_module_dependencies(module_to_delete: str) -> list[str]:
    """
    Check if any modules depend on the module being deleted.
    
    Args:
        module_to_delete: Name of the module to be deleted
        
    Returns:
        List of module names that depend on the module to be deleted
    """
    dependents = []
    
    try:
        for module_name, module_node in _module_cache.items():
            if module_name == module_to_delete:
                continue
                
            # Check if this module depends on the one being deleted
            if hasattr(module_node, 'dependencies'):
                for dep in module_node.dependencies:
                    # Handle both string dependencies and dict dependencies
                    dep_name = dep if isinstance(dep, str) else dep
                    if dep_name == module_to_delete:
                        dependents.append(module_name)
                        break
                    
    except Exception as e:
        app.logger.error(f"Error checking dependencies: {e}")
    
    return dependents


def detect_circular_dependencies(modules_cache: dict) -> list[str]:
    """
    Detect circular dependencies in the module graph using DFS.
    
    Args:
        modules_cache: Dictionary of module nodes from cache
        
    Returns:
        List representing a circular dependency path, empty if no cycles
    """
    def get_dependencies(module_name: str) -> list[str]:
        """Get dependency names for a module."""
        if module_name not in modules_cache:
            return []
        
        module_node = modules_cache[module_name]
        if not hasattr(module_node, 'dependencies'):
            return []
            
        dep_names = []
        for dep in module_node.dependencies:
            dep_names.append(dep)
        return dep_names
    
    def dfs(node: str, visited: set, rec_stack: set, path: list) -> list[str]:
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for dep in get_dependencies(node):
            if dep in modules_cache:  # Only check existing modules
                if dep in rec_stack:
                    # Found cycle - return the cycle path
                    cycle_start = path.index(dep)
                    return path[cycle_start:] + [dep]
                elif dep not in visited:
                    cycle = dfs(dep, visited, rec_stack, path)
                    if cycle:
                        return cycle
        
        rec_stack.remove(node)
        path.pop()
        return []
    
    visited = set()
    
    for module_name in modules_cache:
        if module_name not in visited:
            cycle = dfs(module_name, visited, set(), [])
            if cycle:
                return cycle
    
    return []


def load_module_cache():
    """Load module data into cache."""
    global _module_cache, _modules_loaded
    
    try:
        # Load valid modules (excluding invalid one for API)
        modules_dir = Path("modules")
        if modules_dir.exists():
            # Temporarily move invalid module
            invalid_file = modules_dir / "invalid_module.yaml"
            backup_file = modules_dir / "invalid_module.yaml.bak"
            
            invalid_exists = invalid_file.exists()
            if invalid_exists:
                invalid_file.rename(backup_file)
            
            try:
                modules = load_modules(str(modules_dir))
                _module_cache = {module.name: module for module in modules}
                _modules_loaded = True
                print(f"Loaded {len(modules)} modules into cache")
            finally:
                # Restore invalid module
                if invalid_exists and backup_file.exists():
                    backup_file.rename(invalid_file)
        
    except Exception as e:
        print(f"Error loading modules: {e}")
        _modules_loaded = False


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/api/modules')
def get_modules():
    """
    Return a JSON object containing all loaded AI modules and their attributes.
    
    Each module includes its name, description, status, implementation, input and output specifications, and dependencies.
    """
    if not _modules_loaded:
        load_module_cache()
    
    module_data = {}
    for name, module in _module_cache.items():
        module_data[name] = {
            "name": module.name,
            "description": module.description,
            "status": module.status.value,
            "implementation": module.implementation,
            "inputs": [{"type": inp.type, "description": inp.description} for inp in module.inputs],
            "outputs": [{"type": out.type, "description": out.description} for out in module.outputs],
            "dependencies": module.dependencies
        }
    
    return jsonify(module_data)


@app.route('/api/modules', methods=['POST'])
def create_module():
    """
    Handles the creation of a new AI module via a POST request.
    
    Validates the incoming JSON payload, ensures required fields are present, sets defaults for optional fields, validates the module schema, and saves the new module as a YAML file. Prevents overwriting existing modules and reloads the module cache after creation.
    
    Returns:
        Response: JSON representation of the created module with HTTP 201 status on success, or an error message with an appropriate HTTP status code on failure.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        module_data = request.get_json()
        if not module_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if 'name' not in module_data:
            return jsonify({'error': 'Module name is required'}), 400
        
        # Validate module name to prevent path traversal attacks
        module_name = module_data['name']
        is_valid, error_msg = validate_module_name(module_name)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Additional input validation
        if len(module_name) > 50:
            return jsonify({'error': 'Module name cannot exceed 50 characters'}), 400
        
        # Validate description if provided
        description = module_data.get('description', 'Generated module')
        if not isinstance(description, str) or len(description) > 500:
            return jsonify({'error': 'Description must be a string with maximum 500 characters'}), 400
        
        # Validate status if provided
        valid_statuses = ['placeholder', 'in_progress', 'completed', 'error']
        status = module_data.get('status', 'placeholder')
        if status not in valid_statuses:
            return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Validate lists (inputs, outputs, dependencies)
        for field_name in ['inputs', 'outputs', 'dependencies']:
            field_value = module_data.get(field_name, [])
            if not isinstance(field_value, list):
                return jsonify({'error': f'{field_name} must be a list'}), 400
            if len(field_value) > 20:
                return jsonify({'error': f'{field_name} cannot have more than 20 items'}), 400
        
        # Set defaults for optional fields
        module_data.setdefault('description', description)
        module_data.setdefault('status', status)
        module_data.setdefault('inputs', [])
        module_data.setdefault('outputs', [])
        module_data.setdefault('dependencies', [])
        
        # Validate using schema
        try:
            module_node = ModuleNode(**module_data)
        except Exception as e:
            return jsonify({
                'error': 'Validation failed',
                'details': str(e)
            }), 400
        
        # Save module to YAML file
        modules_dir = Path("modules")
        modules_dir.mkdir(exist_ok=True)
        
        module_file = modules_dir / f"{module_node.name}.yaml"
        if module_file.exists():
            return jsonify({'error': f'Module {module_node.name} already exists'}), 409
        
        # Check for circular dependencies before saving
        # Create a temporary cache with the new module
        temp_cache = _module_cache.copy()
        temp_cache[module_node.name] = module_node
        
        cycle = detect_circular_dependencies(temp_cache)
        if cycle:
            return jsonify({
                'error': f'Module creation would create a circular dependency: {" -> ".join(cycle)}'
            }), 409
        
        # Convert to plain dict with str values
        module_dict = module_node.model_dump()
        if 'status' in module_dict:
            module_dict['status'] = module_dict['status'].value if hasattr(module_dict['status'], 'value') else str(module_dict['status'])
        
        with open(module_file, 'w') as f:
            yaml.safe_dump(module_dict, f, default_flow_style=False, sort_keys=False)
        
        # Reload module cache
        load_module_cache()
        
        return jsonify(module_dict), 201
        
    except FileNotFoundError as e:
        return jsonify({'error': 'Module directory not accessible'}), 500
    except PermissionError as e:
        return jsonify({'error': 'Permission denied accessing module files'}), 500
    except yaml.YAMLError as e:
        return jsonify({'error': f'YAML processing error: {str(e)}'}), 500
    except Exception as e:
        # Log the full error for debugging but return sanitized message
        app.logger.error(f"Unexpected error in create_module: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/surrogates')
def get_surrogates():
    """
    Return a JSON list of all available surrogate types.
    """
    return jsonify(registry.list_surrogates())


@app.route('/api/run', methods=['POST'])
def run_surrogate():
    """
    Execute a surrogate for a given module.
    
    Expected JSON payload:
    {
        "module_name": "ModuleName",
        "surrogate_type": "static_stub" | "mock_llm",
        "inputs": { ... }  // Optional, will use dummy data if not provided
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        module_name = data.get('module_name')
        surrogate_type = data.get('surrogate_type', 'static_stub')
        user_inputs = data.get('inputs', {})
        
        if not module_name:
            return jsonify({"error": "module_name is required"}), 400
        
        # Check if module exists
        if not _modules_loaded:
            load_module_cache()
        
        if module_name not in _module_cache:
            return jsonify({"error": f"Module '{module_name}' not found"}), 404
        
        module = _module_cache[module_name]
        
        # Generate dummy inputs if not provided
        if not user_inputs:
            user_inputs = {}
            for inp in module.inputs:
                user_inputs[inp.type] = f"<dummy-{inp.type.lower()}>"
        
        # Create and run surrogate
        surrogate = registry.create(surrogate_type)
        if not surrogate:
            return jsonify({"error": f"Surrogate type '{surrogate_type}' not found"}), 400
        
        # Execute surrogate
        result = surrogate.run(user_inputs)
        
        # Return execution result
        response = {
            "module_name": module_name,
            "surrogate_type": surrogate_type,
            "inputs": user_inputs,
            "outputs": result,
            "execution_info": {
                "module_status": module.status.value,
                "module_implementation": module.implementation,
                "surrogate_info": surrogate.get_info()
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/modules/<module_name>')
def get_module_details(module_name: str):
    """
    Return detailed information about a specific module by name as a JSON response.
    
    If the module is not found, returns a 404 error with an appropriate message.
    """
    if not _modules_loaded:
        load_module_cache()
    
    if module_name not in _module_cache:
        return jsonify({"error": f"Module '{module_name}' not found"}), 404
    
    module = _module_cache[module_name]
    
    return jsonify({
        "name": module.name,
        "description": module.description,
        "status": module.status.value,
        "implementation": module.implementation,
        "inputs": [{"type": inp.type, "description": inp.description} for inp in module.inputs],
        "outputs": [{"type": out.type, "description": out.description} for out in module.outputs],
        "dependencies": module.dependencies
    })


@app.route('/api/modules/<module_name>', methods=['PUT'])
def update_module(module_name: str):
    """
    Update an existing module with new data provided in the JSON request body.
    
    Validates the input, merges updates with the existing module definition, ensures the module name remains unchanged, validates the updated data, saves it to the YAML file, reloads the module cache, and returns the updated module data as JSON. Returns appropriate error responses for invalid input, validation errors, or if the module does not exist.
    """
    try:
        # Validate module name to prevent path traversal attacks
        is_valid, error_msg = validate_module_name(module_name)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
    
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        module_data = request.get_json()
        if not module_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Input validation for update data
        if 'name' in module_data and module_data['name'] != module_name:
            return jsonify({'error': 'Module name cannot be changed during update'}), 400
        
        # Validate description if provided
        if 'description' in module_data:
            description = module_data['description']
            if not isinstance(description, str) or len(description) > 500:
                return jsonify({'error': 'Description must be a string with maximum 500 characters'}), 400
        
        # Validate status if provided
        if 'status' in module_data:
            valid_statuses = ['placeholder', 'in_progress', 'completed', 'error']
            status = module_data['status']
            if status not in valid_statuses:
                return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Validate lists if provided
        for field_name in ['inputs', 'outputs', 'dependencies']:
            if field_name in module_data:
                field_value = module_data[field_name]
                if not isinstance(field_value, list):
                    return jsonify({'error': f'{field_name} must be a list'}), 400
                if len(field_value) > 20:
                    return jsonify({'error': f'{field_name} cannot have more than 20 items'}), 400
        
        # Check if module exists
        modules_dir = Path("modules")
        module_file = modules_dir / f"{module_name}.yaml"
        if not module_file.exists():
            return jsonify({'error': f'Module {module_name} not found'}), 404
        
        # Load existing module data
        with open(module_file, 'r') as f:
            existing_data = yaml.safe_load(f)
        
        # Merge with updates (preserve existing data, override with new)
        existing_data.update(module_data)
        existing_data['name'] = module_name  # Ensure name doesn't change
        
        # Validate updated data
        try:
            module_node = ModuleNode(**existing_data)
        except Exception as e:
            return jsonify({
                'error': 'Validation failed',
                'details': str(e)
            }), 400
        
        # Check for circular dependencies before saving
        # Create a temporary cache with the updated module
        temp_cache = _module_cache.copy()
        temp_cache[module_name] = module_node
        
        cycle = detect_circular_dependencies(temp_cache)
        if cycle:
            return jsonify({
                'error': f'Update would create a circular dependency: {" -> ".join(cycle)}'
            }), 409
        
        # Convert to plain dict with str values
        module_dict = module_node.model_dump()
        if 'status' in module_dict:
            module_dict['status'] = module_dict['status'].value if hasattr(module_dict['status'], 'value') else str(module_dict['status'])
        
        with open(module_file, 'w') as f:
            yaml.safe_dump(module_dict, f, default_flow_style=False, sort_keys=False)
        
        # Reload module cache
        load_module_cache()
        
        return jsonify(module_dict), 200
        
    except FileNotFoundError as e:
        return jsonify({'error': 'Module file not accessible'}), 500
    except PermissionError as e:
        return jsonify({'error': 'Permission denied accessing module files'}), 500
    except yaml.YAMLError as e:
        return jsonify({'error': f'YAML processing error: {str(e)}'}), 500
    except Exception as e:
        # Log the full error for debugging but return sanitized message
        app.logger.error(f"Unexpected error in update_module: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/modules/<module_name>', methods=['DELETE'])
def delete_module(module_name: str):
    """
    Deletes the specified module by removing its YAML file and updating the module cache.
    
    Returns:
        An empty response with HTTP 204 status on success, or a JSON error message with appropriate HTTP status code if the module is not found or an error occurs.
    """
    try:
        # Validate module name to prevent path traversal attacks
        is_valid, error_msg = validate_module_name(module_name)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
    
        modules_dir = Path("modules")
        module_file = modules_dir / f"{module_name}.yaml"
        
        if not module_file.exists():
            return jsonify({'error': f'Module {module_name} not found'}), 404
        
        # Check for dependents
        dependents = check_module_dependencies(module_name)
        if dependents:
            return jsonify({
                'error': f'Module "{module_name}" cannot be deleted because it is a dependency for: {", ".join(dependents)}'
            }), 409

        # Detect circular dependencies
        cycle = detect_circular_dependencies(_module_cache)
        if cycle:
            return jsonify({
                'error': f'Module "{module_name}" cannot be deleted because it is part of a circular dependency: {", ".join(cycle)}'
            }), 409

        # Delete the file
        module_file.unlink()
        
        # Reload module cache
        load_module_cache()
        
        return '', 204
        
    except FileNotFoundError as e:
        return jsonify({'error': 'Module file not found'}), 404
    except PermissionError as e:
        return jsonify({'error': 'Permission denied deleting module file'}), 500
    except Exception as e:
        # Log the full error for debugging but return sanitized message
        app.logger.error(f"Unexpected error in delete_module: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """
    Handles 404 Not Found errors by returning a JSON error response with HTTP status 404.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


def main():
    """Run the Flask development server."""
    print("Starting Modular AI Architecture server...")
    print("Loading modules...")
    load_module_cache()
    
    print(f"Server starting at http://localhost:5000")
    print("Available endpoints:")
    print("  GET  /                     - Main interface")
    print("  GET  /api/modules          - List all modules")
    print("  GET  /api/modules/<name>   - Get module details")
    print("  GET  /api/surrogates       - List surrogates")
    print("  POST /api/run              - Execute surrogate")
    
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main() 