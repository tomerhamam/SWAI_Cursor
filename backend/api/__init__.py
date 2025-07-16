"""
Enhanced REST API for Modular AI Architecture

This module provides comprehensive CRUD operations for modules, graph generation,
and advanced features with proper error handling and validation.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import BadRequest
from pydantic import ValidationError

from backend.models.schemas import (
    ModuleSchema, ModuleStatus, ModuleType, 
    validate_module_yaml, validate_modules_batch
)
from backend.services.graph_builder import (
    GraphBuilder, generate_vis_js_graph, generate_module_metadata
)
from backend.services.surrogate import registry


def create_app(config=None):
    """
    Create and configure Flask application
    
    Args:
        config: Optional configuration object
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config.update({
        'TESTING': True,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True
    })
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    # Initialize graph builder
    modules_dir = Path("modules")
    graph_builder = GraphBuilder(modules_dir)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'error': 'Bad request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The request method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # Modules endpoints
    @app.route('/api/modules', methods=['GET'])
    def get_all_modules():
        """Get all modules"""
        try:
            modules = load_all_modules()
            
            # Convert to dictionary format for JSON response
            modules_dict = {}
            for module in modules:
                modules_dict[module.name] = module.model_dump()
            
            return jsonify(modules_dict)
            
        except Exception as e:
            return jsonify({'error': f'Failed to load modules: {str(e)}'}), 500
    
    @app.route('/api/modules', methods=['POST'])
    def create_module():
        """Create a new module"""
        try:
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            try:
                module_data = request.get_json()
            except Exception:
                return jsonify({'error': 'Invalid JSON data'}), 400
                
            if not module_data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate module data
            try:
                module = validate_module_yaml(module_data)
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation failed',
                    'details': str(e)
                }), 400
            
            # Save module
            try:
                save_module(module)
                graph_builder.reload_modules()  # Refresh graph builder
                
                return jsonify({
                    'message': 'Module created successfully',
                    'name': module.name
                }), 201
                
            except FileExistsError as e:
                return jsonify({'error': f'Module already exists: {str(e)}'}), 409
                
        except Exception as e:
            return jsonify({'error': f'Failed to create module: {str(e)}'}), 500
    
    @app.route('/api/modules/<string:module_id>', methods=['GET'])
    def get_single_module(module_id):
        """Get a specific module by ID"""
        try:
            module = load_module_by_id(module_id)
            if not module:
                return jsonify({'error': f'Module {module_id} not found'}), 404
            
            return jsonify(module.model_dump())
            
        except Exception as e:
            return jsonify({'error': f'Failed to load module: {str(e)}'}), 500
    
    @app.route('/api/modules/<string:module_id>', methods=['PUT'])
    def update_module(module_id):
        """Update an existing module"""
        try:
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            # Check if module exists
            existing_module = load_module_by_id(module_id)
            if not existing_module:
                return jsonify({'error': f'Module {module_id} not found'}), 404
            
            try:
                update_data = request.get_json()
            except Exception:
                return jsonify({'error': 'Invalid JSON data'}), 400
                
            if not update_data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Merge update data with existing module
            module_dict = existing_module.model_dump()
            module_dict.update(update_data)
            
            # Validate updated module
            try:
                updated_module = validate_module_yaml(module_dict)
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation failed',
                    'details': str(e)
                }), 400
            
            # Save updated module
            save_module(updated_module)
            graph_builder.reload_modules()  # Refresh graph builder
            
            return jsonify({'message': 'Module updated successfully'})
            
        except Exception as e:
            return jsonify({'error': f'Failed to update module: {str(e)}'}), 500
    
    @app.route('/api/modules/<string:module_id>', methods=['DELETE'])
    def delete_single_module(module_id):
        """Delete a specific module"""
        try:
            # Check if module exists
            module = load_module_by_id(module_id)
            if not module:
                return jsonify({'error': f'Module {module_id} not found'}), 404
            
            # Delete module
            try:
                delete_module(module_id)
                graph_builder.reload_modules()  # Refresh graph builder
                
                return jsonify({'message': 'Module deleted successfully'})
                
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
                
        except Exception as e:
            return jsonify({'error': f'Failed to delete module: {str(e)}'}), 500
    
    # Graph endpoints
    @app.route('/api/graph', methods=['GET'])
    def get_graph():
        """Get graph data for visualization"""
        try:
            # Parse query parameters
            layout = request.args.get('layout', 'physics')
            statuses_param = request.args.get('statuses')
            
            include_statuses = None
            if statuses_param:
                status_strings = [s.strip() for s in statuses_param.split(',')]
                include_statuses = []
                for status_str in status_strings:
                    try:
                        include_statuses.append(ModuleStatus(status_str))
                    except ValueError:
                        return jsonify({'error': f'Invalid status: {status_str}'}), 400
            
            graph_data = generate_graph_data(layout=layout, include_statuses=include_statuses)
            return jsonify(graph_data)
            
        except Exception as e:
            return jsonify({'error': f'Failed to generate graph: {str(e)}'}), 500
    
    # Surrogates endpoint  
    @app.route('/api/surrogates', methods=['GET'])
    def get_surrogates():
        """Get available surrogates"""
        try:
            surrogates = get_available_surrogates()
            return jsonify(surrogates)
        except Exception as e:
            return jsonify({'error': f'Failed to get surrogates: {str(e)}'}), 500
    
    # Statistics endpoint
    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        """Get module statistics"""
        try:
            stats = get_module_statistics()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500
    
    # Metadata endpoint
    @app.route('/api/metadata', methods=['GET'])
    def get_metadata():
        """Get detailed module metadata"""
        try:
            metadata = get_module_metadata()
            return jsonify(metadata)
        except Exception as e:
            return jsonify({'error': f'Failed to get metadata: {str(e)}'}), 500
    
    return app


# Helper functions for module operations

def load_all_modules() -> List[ModuleSchema]:
    """Load all modules from the modules directory"""
    modules_dir = Path("modules")
    if not modules_dir.exists():
        return []
    
    modules_data = []
    for yaml_file in modules_dir.glob("*.yaml"):
        try:
            import yaml
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                if data:
                    modules_data.append(data)
        except Exception as e:
            print(f"Warning: Could not load {yaml_file}: {e}")
    
    # Validate using Pydantic schemas
    try:
        return validate_modules_batch(modules_data)
    except Exception:
        return []


def load_module_by_id(module_id: str) -> Optional[ModuleSchema]:
    """Load a specific module by ID"""
    modules = load_all_modules()
    for module in modules:
        if module.name == module_id:
            return module
    return None


def save_module(module: ModuleSchema) -> bool:
    """Save a module to disk"""
    modules_dir = Path("modules")
    modules_dir.mkdir(exist_ok=True)
    
    module_file = modules_dir / f"{module.name}.yaml"
    
    # Check if module already exists for new modules
    if module_file.exists():
        # For updates, this is fine, for new modules, it's an error
        # This could be improved with better context about create vs update
        pass
    
    import yaml
    with open(module_file, 'w') as f:
        # Convert to dict and write as YAML
        module_dict = module.model_dump()
        yaml.dump(module_dict, f, default_flow_style=False)
    
    return True


def delete_module(module_id: str) -> bool:
    """Delete a module from disk"""
    # Check for dependencies first
    modules = load_all_modules()
    dependents = []
    
    for module in modules:
        for dep in module.dependencies:
            if dep.name == module_id:
                dependents.append(module.name)
    
    if dependents:
        raise ValueError(f"Cannot delete: module has dependents: {', '.join(dependents)}")
    
    # Delete the file
    modules_dir = Path("modules")
    module_file = modules_dir / f"{module_id}.yaml"
    
    if module_file.exists():
        module_file.unlink()
        return True
    
    return False


def generate_graph_data(layout: str = "physics", include_statuses: Optional[List[ModuleStatus]] = None) -> Dict[str, Any]:
    """Generate graph data using the GraphBuilder"""
    graph_builder = GraphBuilder(Path("modules"))
    graph_data = graph_builder.build_graph(layout=layout, include_statuses=include_statuses)
    return graph_data.to_dict()


def get_available_surrogates() -> List[Dict[str, Any]]:
    """Get list of available surrogates"""
    # This would typically query the surrogate registry
    # For now, return a basic list
    return [
        {"name": "MockLLMSurrogate", "description": "Mock LLM for testing"},
        {"name": "StaticSurrogate", "description": "Static response surrogate"}
    ]


def get_module_statistics() -> Dict[str, Any]:
    """Get module statistics"""
    graph_builder = GraphBuilder(Path("modules"))
    return graph_builder.get_statistics()


def get_module_metadata() -> Dict[str, Any]:
    """Get detailed module metadata"""
    modules = load_all_modules()
    return generate_module_metadata(modules)


# Legacy variables for backwards compatibility
app = create_app()

if __name__ == '__main__':
    import os
    app = create_app({'TESTING': False})
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=debug_mode, host=host, port=port)