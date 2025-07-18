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


# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')


# Global module data cache
_module_cache = {}
_modules_loaded = False


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
    """Get list of all modules."""
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
    """Create a new module."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        module_data = request.get_json()
        if not module_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if 'name' not in module_data:
            return jsonify({'error': 'Module name is required'}), 400
        
        # Set defaults for optional fields
        module_data.setdefault('description', 'Generated module')
        module_data.setdefault('status', 'placeholder')
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
        
        # Convert to plain dict with str values
        module_dict = module_node.model_dump()
        if 'status' in module_dict:
            module_dict['status'] = module_dict['status'].value if hasattr(module_dict['status'], 'value') else str(module_dict['status'])
        
        with open(module_file, 'w') as f:
            yaml.safe_dump(module_dict, f, default_flow_style=False, sort_keys=False)
        
        # Reload module cache
        load_module_cache()
        
        return jsonify(module_dict), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/surrogates')
def get_surrogates():
    """Get list of available surrogates."""
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
    """Get detailed information about a specific module."""
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
    """Update an existing module."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        module_data = request.get_json()
        if not module_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
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
        
        # Convert to plain dict with str values
        module_dict = module_node.model_dump()
        if 'status' in module_dict:
            module_dict['status'] = module_dict['status'].value if hasattr(module_dict['status'], 'value') else str(module_dict['status'])
        
        with open(module_file, 'w') as f:
            yaml.safe_dump(module_dict, f, default_flow_style=False, sort_keys=False)
        
        # Reload module cache
        load_module_cache()
        
        return jsonify(module_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/modules/<module_name>', methods=['DELETE'])
def delete_module(module_name: str):
    """Delete a module."""
    try:
        modules_dir = Path("modules")
        module_file = modules_dir / f"{module_name}.yaml"
        
        if not module_file.exists():
            return jsonify({'error': f'Module {module_name} not found'}), 404
        
        # Delete the file
        module_file.unlink()
        
        # Reload module cache
        load_module_cache()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
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