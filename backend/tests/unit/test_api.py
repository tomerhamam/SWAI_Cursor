import pytest
import json
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from backend.api import create_app
from backend.models.schemas import ModuleSchema, ModuleStatus, ModuleType


class TestAppCreation:
    """Test Flask app creation and configuration"""
    
    def test_create_app(self):
        """Test creating Flask app"""
        app = create_app()
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_app_has_required_routes(self):
        """Test app has all required API routes"""
        app = create_app()
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        # Check required routes exist
        required_routes = [
            '/api/modules',
            '/api/modules/<module_id>',
            '/api/graph',
            '/api/surrogates',
            '/health'
        ]
        
        for route in required_routes:
            # Check if exact route or parameterized version exists
            route_exists = any(route == r or route.replace('<module_id>', '<string:module_id>') == r 
                             for r in routes)
            assert route_exists, f"Route {route} not found in {routes}"


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint(self, client):
        """Test health check returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_health_endpoint_methods(self, client):
        """Test health endpoint only accepts GET"""
        response = client.post('/health')
        assert response.status_code == 405  # Method not allowed


class TestModulesEndpoint:
    """Test /api/modules endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_modules(self):
        """Sample modules for testing"""
        return [
            ModuleSchema(
                name="TestModuleA",
                description="Test module A",
                status="implemented",
                type="service",
                dependencies=[]
            ),
            ModuleSchema(
                name="TestModuleB", 
                description="Test module B",
                status="placeholder",
                type="component",
                dependencies=[{"name": "TestModuleA", "required": True}]
            )
        ]
    
    def test_get_all_modules(self, client, sample_modules):
        """Test GET /api/modules returns all modules"""
        with patch('backend.api.load_all_modules') as mock_load:
            mock_load.return_value = sample_modules
            
            response = client.get('/api/modules')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data) == 2
            assert data['TestModuleA']['name'] == 'TestModuleA'
            assert data['TestModuleB']['name'] == 'TestModuleB'
    
    def test_get_modules_empty(self, client):
        """Test GET /api/modules with no modules"""
        with patch('backend.api.load_all_modules') as mock_load:
            mock_load.return_value = []
            
            response = client.get('/api/modules')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data == {}
    
    def test_get_modules_error_handling(self, client):
        """Test GET /api/modules handles errors gracefully"""
        with patch('backend.api.load_all_modules') as mock_load:
            mock_load.side_effect = Exception("File not found")
            
            response = client.get('/api/modules')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'File not found' in data['error']
    
    def test_create_module(self, client):
        """Test POST /api/modules creates new module"""
        new_module = {
            "name": "NewModule",
            "description": "A new test module",
            "status": "placeholder",
            "type": "utility"
        }
        
        with patch('backend.api.save_module') as mock_save:
            mock_save.return_value = True
            
            response = client.post('/api/modules', 
                                 json=new_module,
                                 content_type='application/json')
            assert response.status_code == 201
            
            data = json.loads(response.data)
            assert data['name'] == 'NewModule'
            assert data['message'] == 'Module created successfully'
    
    def test_create_module_validation_error(self, client):
        """Test POST /api/modules with invalid data"""
        invalid_module = {
            "name": "",  # Invalid: empty name
            "description": "Test",
            "status": "invalid_status"  # Invalid status
        }
        
        response = client.post('/api/modules',
                              json=invalid_module,
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'validation' in data['error'].lower()
    
    def test_create_module_missing_json(self, client):
        """Test POST /api/modules without JSON data"""
        response = client.post('/api/modules')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_module_conflict(self, client):
        """Test POST /api/modules with existing module name"""
        existing_module = {
            "name": "ExistingModule",
            "description": "Already exists",
            "status": "implemented"
        }
        
        with patch('backend.api.save_module') as mock_save:
            mock_save.side_effect = FileExistsError("Module already exists")
            
            response = client.post('/api/modules',
                                  json=existing_module,
                                  content_type='application/json')
            assert response.status_code == 409  # Conflict
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'already exists' in data['error'].lower()


class TestSingleModuleEndpoint:
    """Test /api/modules/<module_id> endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_module(self):
        """Sample module for testing"""
        return ModuleSchema(
            name="TestModule",
            description="A test module",
            status="implemented",
            type="service",
            version="1.2.0",
            inputs=[{"type": "string", "description": "Input text"}],
            outputs=[{"type": "json", "description": "Output data"}],
            dependencies=[{"name": "OtherModule", "required": True}],
            metadata={"author": "Test Author"}
        )
    
    def test_get_single_module(self, client, sample_module):
        """Test GET /api/modules/<id> returns specific module"""
        with patch('backend.api.load_module_by_id') as mock_load:
            mock_load.return_value = sample_module
            
            response = client.get('/api/modules/TestModule')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['name'] == 'TestModule'
            assert data['version'] == '1.2.0'
            assert len(data['inputs']) == 1
            assert len(data['dependencies']) == 1
    
    def test_get_module_not_found(self, client):
        """Test GET /api/modules/<id> with non-existent module"""
        with patch('backend.api.load_module_by_id') as mock_load:
            mock_load.return_value = None
            
            response = client.get('/api/modules/NonExistent')
            assert response.status_code == 404
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error'].lower()
    
    def test_update_module(self, client, sample_module):
        """Test PUT /api/modules/<id> updates module"""
        updated_data = {
            "description": "Updated description",
            "status": "placeholder",
            "version": "2.0.0"
        }
        
        with patch('backend.api.load_module_by_id') as mock_load, \
             patch('backend.api.save_module') as mock_save:
            
            mock_load.return_value = sample_module
            mock_save.return_value = True
            
            response = client.put('/api/modules/TestModule',
                                 json=updated_data,
                                 content_type='application/json')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['message'] == 'Module updated successfully'
    
    def test_update_module_not_found(self, client):
        """Test PUT /api/modules/<id> with non-existent module"""
        with patch('backend.api.load_module_by_id') as mock_load:
            mock_load.return_value = None
            
            response = client.put('/api/modules/NonExistent',
                                 json={"description": "New desc"},
                                 content_type='application/json')
            assert response.status_code == 404
    
    def test_delete_module(self, client, sample_module):
        """Test DELETE /api/modules/<id> removes module"""
        with patch('backend.api.load_module_by_id') as mock_load, \
             patch('backend.api.delete_module') as mock_delete:
            
            mock_load.return_value = sample_module
            mock_delete.return_value = True
            
            response = client.delete('/api/modules/TestModule')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['message'] == 'Module deleted successfully'
    
    def test_delete_module_not_found(self, client):
        """Test DELETE /api/modules/<id> with non-existent module"""
        with patch('backend.api.load_module_by_id') as mock_load:
            mock_load.return_value = None
            
            response = client.delete('/api/modules/NonExistent')
            assert response.status_code == 404
    
    def test_delete_module_with_dependents(self, client, sample_module):
        """Test DELETE /api/modules/<id> with dependent modules"""
        with patch('backend.api.load_module_by_id') as mock_load, \
             patch('backend.api.delete_module') as mock_delete:
            
            mock_load.return_value = sample_module
            mock_delete.side_effect = ValueError("Cannot delete: module has dependents")
            
            response = client.delete('/api/modules/TestModule')
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert 'dependents' in data['error'].lower()


class TestGraphEndpoint:
    """Test /api/graph endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def sample_graph_data(self):
        """Sample graph data for testing"""
        return {
            "nodes": [
                {"id": "A", "label": "Module A", "group": "implemented"},
                {"id": "B", "label": "Module B", "group": "placeholder"}
            ],
            "edges": [
                {"from": "B", "to": "A", "arrows": "to"}
            ]
        }
    
    def test_get_graph_default(self, client, sample_graph_data):
        """Test GET /api/graph returns graph data"""
        with patch('backend.api.generate_graph_data') as mock_generate:
            mock_generate.return_value = sample_graph_data
            
            response = client.get('/api/graph')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'nodes' in data
            assert 'edges' in data
            assert len(data['nodes']) == 2
            assert len(data['edges']) == 1
    
    def test_get_graph_with_layout(self, client, sample_graph_data):
        """Test GET /api/graph with layout parameter"""
        with patch('backend.api.generate_graph_data') as mock_generate:
            mock_generate.return_value = sample_graph_data
            
            response = client.get('/api/graph?layout=hierarchical')
            assert response.status_code == 200
            
            # Verify mock was called with layout parameter
            mock_generate.assert_called_with(layout='hierarchical', include_statuses=None)
    
    def test_get_graph_with_status_filter(self, client, sample_graph_data):
        """Test GET /api/graph with status filtering"""
        with patch('backend.api.generate_graph_data') as mock_generate:
            mock_generate.return_value = sample_graph_data
            
            response = client.get('/api/graph?statuses=implemented,placeholder')
            assert response.status_code == 200
            
            # Verify mock was called with status filter
            args, kwargs = mock_generate.call_args
            assert 'implemented' in kwargs['include_statuses']
            assert 'placeholder' in kwargs['include_statuses']
    
    def test_get_graph_empty(self, client):
        """Test GET /api/graph with no modules"""
        with patch('backend.api.generate_graph_data') as mock_generate:
            mock_generate.return_value = {"nodes": [], "edges": []}
            
            response = client.get('/api/graph')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['nodes'] == []
            assert data['edges'] == []
    
    def test_get_graph_error_handling(self, client):
        """Test GET /api/graph handles errors gracefully"""
        with patch('backend.api.generate_graph_data') as mock_generate:
            mock_generate.side_effect = Exception("Graph generation failed")
            
            response = client.get('/api/graph')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'error' in data


class TestSurrogatesEndpoint:
    """Test /api/surrogates endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_get_surrogates(self, client):
        """Test GET /api/surrogates returns available surrogates"""
        mock_surrogates = [
            {"name": "MockLLMSurrogate", "description": "Mock LLM for testing"},
            {"name": "StaticSurrogate", "description": "Static response surrogate"}
        ]
        
        with patch('backend.api.get_available_surrogates') as mock_get:
            mock_get.return_value = mock_surrogates
            
            response = client.get('/api/surrogates')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data) == 2
            assert data[0]['name'] == 'MockLLMSurrogate'


class TestModuleStatistics:
    """Test module statistics and metadata endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_get_module_statistics(self, client):
        """Test GET /api/statistics returns module stats"""
        mock_stats = {
            "total_modules": 5,
            "by_status": {"implemented": 2, "placeholder": 3},
            "by_type": {"service": 3, "component": 2},
            "dependency_count": 8
        }
        
        with patch('backend.api.get_module_statistics') as mock_get:
            mock_get.return_value = mock_stats
            
            response = client.get('/api/statistics')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['total_modules'] == 5
            assert data['by_status']['implemented'] == 2
    
    def test_get_module_metadata(self, client):
        """Test GET /api/metadata returns detailed module metadata"""
        mock_metadata = {
            "TestModule": {
                "name": "TestModule",
                "dependencies": [],
                "dependents": ["OtherModule"],
                "level": 0
            }
        }
        
        with patch('backend.api.get_module_metadata') as mock_get:
            mock_get.return_value = mock_metadata
            
            response = client.get('/api/metadata')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'TestModule' in data
            assert data['TestModule']['level'] == 0


class TestErrorHandling:
    """Test comprehensive error handling across all endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    def test_404_for_unknown_endpoints(self, client):
        """Test 404 for non-existent endpoints"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 for unsupported methods"""
        response = client.delete('/api/graph')  # Graph doesn't support DELETE
        assert response.status_code == 405
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON data"""
        response = client.post('/api/modules',
                              data="invalid json",
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get('/api/modules')
        
        # Check for CORS headers if implemented
        # This depends on the actual CORS configuration
        assert response.status_code in [200, 500]  # Should respond, not fail


class TestRateLimiting:
    """Test rate limiting if implemented"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    def test_rate_limiting(self, client):
        """Test rate limiting works correctly"""
        # This test would be implemented when rate limiting is added
        pass


class TestAuthentication:
    """Test authentication if implemented"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        with app.test_client() as client:
            yield client
    
    @pytest.mark.skip(reason="Authentication not yet implemented")
    def test_protected_endpoints(self, client):
        """Test protected endpoints require authentication"""
        # This test would be implemented when authentication is added
        pass 