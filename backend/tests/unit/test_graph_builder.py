import pytest
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import yaml

from backend.services.graph_builder import (
    GraphBuilder,
    DependencyResolver,
    CircularDependencyError,
    DependencyNode,
    GraphData,
    generate_vis_js_graph,
    generate_module_metadata
)
from backend.models.schemas import ModuleSchema, ModuleStatus, ModuleType


class TestDependencyNode:
    """Test the DependencyNode data structure"""
    
    def test_create_node(self):
        """Test creating a basic dependency node"""
        node = DependencyNode(
            name="TestModule",
            status=ModuleStatus.implemented,
            dependencies=["ModuleA", "ModuleB"]
        )
        
        assert node.name == "TestModule"
        assert node.status == ModuleStatus.implemented
        assert node.dependencies == ["ModuleA", "ModuleB"]
        assert node.dependents == []
        assert node.level == 0
    
    def test_node_equality(self):
        """Test node equality comparison"""
        node1 = DependencyNode("Test", ModuleStatus.placeholder, [])
        node2 = DependencyNode("Test", ModuleStatus.implemented, ["Other"])
        node3 = DependencyNode("Different", ModuleStatus.placeholder, [])
        
        assert node1 == node2  # Same name = equal
        assert node1 != node3  # Different name = not equal
    
    def test_node_hash(self):
        """Test nodes can be used in sets/dicts"""
        node1 = DependencyNode("Test", ModuleStatus.placeholder, [])
        node2 = DependencyNode("Test", ModuleStatus.implemented, [])
        
        nodes = {node1, node2}
        assert len(nodes) == 1  # Should be deduplicated by name


class TestCircularDependencyError:
    """Test circular dependency error handling"""
    
    def test_error_message(self):
        """Test error contains cycle information"""
        cycle = ["A", "B", "C", "A"]
        error = CircularDependencyError(cycle)
        
        assert "A -> B -> C -> A" in str(error)
        assert error.cycle == cycle


class TestDependencyResolver:
    """Test dependency resolution algorithms"""
    
    @pytest.fixture
    def sample_modules(self):
        """Sample module data for testing"""
        return [
            ModuleSchema(
                name="Root",
                description="Root module",
                status="implemented",
                dependencies=[]
            ),
            ModuleSchema(
                name="ChildA",
                description="Child A",
                status="placeholder",
                dependencies=[{"name": "Root", "required": True}]
            ),
            ModuleSchema(
                name="ChildB", 
                description="Child B",
                status="stub",
                dependencies=[{"name": "Root", "required": True}]
            ),
            ModuleSchema(
                name="GrandChild",
                description="Grand child",
                status="surrogate",
                dependencies=[
                    {"name": "ChildA", "required": True},
                    {"name": "ChildB", "required": False}
                ]
            )
        ]
    
    def test_create_resolver(self, sample_modules):
        """Test creating dependency resolver"""
        resolver = DependencyResolver(sample_modules)
        
        assert len(resolver.nodes) == 4
        assert "Root" in resolver.nodes
        assert "ChildA" in resolver.nodes
        assert "GrandChild" in resolver.nodes
        
        # Check node properties
        root = resolver.nodes["Root"]
        assert root.status == ModuleStatus.implemented
        assert root.dependencies == []
        
        child_a = resolver.nodes["ChildA"]
        assert child_a.dependencies == ["Root"]
        assert child_a.status == ModuleStatus.placeholder
    
    def test_resolve_dependencies(self, sample_modules):
        """Test basic dependency resolution"""
        resolver = DependencyResolver(sample_modules)
        resolution_order = resolver.resolve()
        
        # Root should come first (no dependencies)
        assert resolution_order[0] == "Root"
        
        # ChildA and ChildB should come before GrandChild
        root_idx = resolution_order.index("Root")
        child_a_idx = resolution_order.index("ChildA")
        child_b_idx = resolution_order.index("ChildB")
        grandchild_idx = resolution_order.index("GrandChild")
        
        assert root_idx < child_a_idx
        assert root_idx < child_b_idx
        assert child_a_idx < grandchild_idx
        # Note: ChildB is optional dependency, so order vs GrandChild may vary
    
    def test_resolve_missing_dependency(self):
        """Test handling missing dependencies"""
        modules = [
            ModuleSchema(
                name="TestModule",
                description="Test",
                status="placeholder",
                dependencies=[{"name": "MissingModule", "required": True}]
            )
        ]
        
        resolver = DependencyResolver(modules)
        
        with pytest.raises(ValueError, match="Missing required dependency"):
            resolver.resolve()
    
    def test_detect_circular_dependency(self):
        """Test circular dependency detection"""
        modules = [
            ModuleSchema(
                name="A",
                description="Module A",
                status="placeholder",
                dependencies=[{"name": "B", "required": True}]
            ),
            ModuleSchema(
                name="B",
                description="Module B", 
                status="placeholder",
                dependencies=[{"name": "C", "required": True}]
            ),
            ModuleSchema(
                name="C",
                description="Module C",
                status="placeholder", 
                dependencies=[{"name": "A", "required": True}]  # Creates cycle
            )
        ]
        
        resolver = DependencyResolver(modules)
        
        with pytest.raises(CircularDependencyError) as exc_info:
            resolver.resolve()
        
        # Should detect the cycle A -> B -> C -> A
        cycle = exc_info.value.cycle
        assert "A" in cycle
        assert "B" in cycle
        assert "C" in cycle
    
    def test_calculate_levels(self, sample_modules):
        """Test level calculation for hierarchical layout"""
        resolver = DependencyResolver(sample_modules)
        resolver.resolve()
        
        # Root should be level 0
        assert resolver.nodes["Root"].level == 0
        
        # ChildA and ChildB should be level 1
        assert resolver.nodes["ChildA"].level == 1
        assert resolver.nodes["ChildB"].level == 1
        
        # GrandChild should be level 2
        assert resolver.nodes["GrandChild"].level == 2
    
    def test_build_dependents_graph(self, sample_modules):
        """Test building reverse dependency graph"""
        resolver = DependencyResolver(sample_modules)
        resolver.resolve()
        
        # Root should have ChildA and ChildB as dependents
        root_dependents = resolver.nodes["Root"].dependents
        assert "ChildA" in root_dependents
        assert "ChildB" in root_dependents
        
        # ChildA should have GrandChild as dependent
        child_a_dependents = resolver.nodes["ChildA"].dependents
        assert "GrandChild" in child_a_dependents
    
    def test_optional_dependencies(self):
        """Test handling of optional dependencies"""
        modules = [
            ModuleSchema(
                name="Core",
                description="Core module",
                status="implemented",
                dependencies=[]
            ),
            ModuleSchema(
                name="Plugin",
                description="Optional plugin",
                status="placeholder",
                dependencies=[{"name": "Core", "required": False}]
            )
        ]
        
        resolver = DependencyResolver(modules)
        resolution_order = resolver.resolve()
        
        # Should work even with optional dependencies
        assert "Core" in resolution_order
        assert "Plugin" in resolution_order


class TestGraphData:
    """Test graph data structure for vis.js"""
    
    def test_create_graph_data(self):
        """Test creating vis.js graph data structure"""
        nodes = [
            {"id": "A", "label": "Module A", "group": "implemented"},
            {"id": "B", "label": "Module B", "group": "placeholder"}
        ]
        edges = [
            {"from": "B", "to": "A", "arrows": "to"}
        ]
        
        graph_data = GraphData(nodes=nodes, edges=edges)
        
        assert len(graph_data.nodes) == 2
        assert len(graph_data.edges) == 1
        assert graph_data.nodes[0]["id"] == "A"
        assert graph_data.edges[0]["from"] == "B"
    
    def test_to_dict(self):
        """Test converting graph data to dictionary"""
        nodes = [{"id": "test", "label": "Test"}]
        edges = [{"from": "test", "to": "other"}]
        
        graph_data = GraphData(nodes=nodes, edges=edges)
        result = graph_data.to_dict()
        
        assert "nodes" in result
        assert "edges" in result
        assert result["nodes"] == nodes
        assert result["edges"] == edges


class TestGraphBuilder:
    """Test the main GraphBuilder class"""
    
    @pytest.fixture
    def temp_modules_dir(self):
        """Create temporary directory with sample modules"""
        temp_dir = tempfile.mkdtemp()
        modules_dir = Path(temp_dir) / "modules"
        modules_dir.mkdir()
        
        # Create sample module files
        sample_modules = {
            "moduleA.yaml": {
                "name": "ModuleA",
                "description": "Test module A",
                "status": "implemented",
                "type": "service",
                "dependencies": []
            },
            "moduleB.yaml": {
                "name": "ModuleB", 
                "description": "Test module B",
                "status": "placeholder",
                "type": "component",
                "dependencies": [{"name": "ModuleA", "required": True}]
            },
            "moduleC.yaml": {
                "name": "ModuleC",
                "description": "Test module C", 
                "status": "stub",
                "type": "utility",
                "dependencies": [
                    {"name": "ModuleA", "required": True},
                    {"name": "ModuleB", "required": False}
                ]
            }
        }
        
        for filename, module_data in sample_modules.items():
            module_file = modules_dir / filename
            with open(module_file, 'w') as f:
                yaml.dump(module_data, f)
        
        yield modules_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_create_graph_builder(self, temp_modules_dir):
        """Test creating graph builder with module directory"""
        builder = GraphBuilder(temp_modules_dir)
        
        assert builder.modules_dir == temp_modules_dir
        assert len(builder.modules) == 3
        assert "ModuleA" in [m.name for m in builder.modules]
        assert "ModuleB" in [m.name for m in builder.modules]
        assert "ModuleC" in [m.name for m in builder.modules]
    
    def test_build_dependency_graph(self, temp_modules_dir):
        """Test building dependency graph"""
        builder = GraphBuilder(temp_modules_dir)
        graph_data = builder.build_graph()
        
        assert isinstance(graph_data, GraphData)
        
        # Should have 3 nodes
        assert len(graph_data.nodes) == 3
        
        # Should have edges for dependencies
        assert len(graph_data.edges) >= 2  # B->A, C->A, maybe C->B
        
        # Check node properties
        node_ids = [node["id"] for node in graph_data.nodes]
        assert "ModuleA" in node_ids
        assert "ModuleB" in node_ids
        assert "ModuleC" in node_ids
        
        # Check node has proper vis.js properties
        module_a_node = next(n for n in graph_data.nodes if n["id"] == "ModuleA")
        assert "label" in module_a_node
        assert "group" in module_a_node
        assert module_a_node["group"] == "implemented"  # Based on status
        
    def test_build_with_hierarchical_layout(self, temp_modules_dir):
        """Test building graph with hierarchical layout"""
        builder = GraphBuilder(temp_modules_dir)
        graph_data = builder.build_graph(layout="hierarchical")
        
        # Should have level information for hierarchical layout
        for node in graph_data.nodes:
            assert "level" in node
            assert isinstance(node["level"], int)
            assert node["level"] >= 0
        
        # ModuleA (no deps) should be level 0
        module_a = next(n for n in graph_data.nodes if n["id"] == "ModuleA")
        assert module_a["level"] == 0
        
        # ModuleB (depends on A) should be level 1  
        module_b = next(n for n in graph_data.nodes if n["id"] == "ModuleB")
        assert module_b["level"] == 1
    
    def test_build_with_status_filtering(self, temp_modules_dir):
        """Test building graph with status filtering"""
        builder = GraphBuilder(temp_modules_dir)
        
        # Filter to only implemented modules
        graph_data = builder.build_graph(include_statuses=[ModuleStatus.implemented])
        
        # Should only have ModuleA
        assert len(graph_data.nodes) == 1
        assert graph_data.nodes[0]["id"] == "ModuleA"
        
        # Should have no edges since only one node
        assert len(graph_data.edges) == 0
    
    def test_performance_with_many_modules(self):
        """Test performance with large number of modules"""
        # Create many modules programmatically
        modules = []
        for i in range(100):
            deps = []
            if i > 0:
                # Each module depends on previous module
                deps = [{"name": f"Module{i-1}", "required": True}]
            
            module = ModuleSchema(
                name=f"Module{i}",
                description=f"Generated module {i}",
                status="placeholder",
                dependencies=deps
            )
            modules.append(module)
        
        # Test resolver can handle 100 modules in reasonable time
        import time
        start_time = time.time()
        
        resolver = DependencyResolver(modules)
        resolution_order = resolver.resolve()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in under 1 second
        assert execution_time < 1.0
        assert len(resolution_order) == 100
        assert resolution_order[0] == "Module0"  # First module (no deps)
        assert resolution_order[-1] == "Module99"  # Last module (most deps)
    
    def test_get_module_statistics(self, temp_modules_dir):
        """Test getting module statistics"""
        builder = GraphBuilder(temp_modules_dir)
        stats = builder.get_statistics()
        
        assert "total_modules" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "dependency_count" in stats
        
        assert stats["total_modules"] == 3
        assert stats["by_status"]["implemented"] == 1
        assert stats["by_status"]["placeholder"] == 1
        assert stats["by_status"]["stub"] == 1
        
        assert stats["by_type"]["service"] == 1
        assert stats["by_type"]["component"] == 1
        assert stats["by_type"]["utility"] == 1


class TestVisJsGeneration:
    """Test vis.js specific graph generation functions"""
    
    def test_generate_vis_js_graph(self):
        """Test generating vis.js compatible graph format"""
        modules = [
            ModuleSchema(
                name="ServiceA",
                description="Service module A",
                status="implemented",
                type="service",
                dependencies=[]
            ),
            ModuleSchema(
                name="ComponentB",
                description="Component B",
                status="placeholder", 
                type="component",
                dependencies=[{"name": "ServiceA", "required": True}]
            )
        ]
        
        graph_data = generate_vis_js_graph(modules)
        
        # Check nodes have vis.js properties
        assert len(graph_data.nodes) == 2
        
        service_node = next(n for n in graph_data.nodes if n["id"] == "ServiceA")
        assert service_node["label"] == "ServiceA"
        assert service_node["group"] == "implemented"
        assert service_node["title"]  # Tooltip text
        
        # Check edges have vis.js properties
        assert len(graph_data.edges) == 1
        edge = graph_data.edges[0]
        assert edge["from"] == "ComponentB"
        assert edge["to"] == "ServiceA"
        assert edge["arrows"] == "to"
    
    def test_node_styling_by_status(self):
        """Test node styling based on module status"""
        modules = [
            ModuleSchema(name="Impl", description="Test", status="implemented"),
            ModuleSchema(name="Place", description="Test", status="placeholder"),
            ModuleSchema(name="Stub", description="Test", status="stub"),
            ModuleSchema(name="Surr", description="Test", status="surrogate")
        ]
        
        graph_data = generate_vis_js_graph(modules)
        
        # Each status should have different group
        groups = {node["group"] for node in graph_data.nodes}
        assert "implemented" in groups
        assert "placeholder" in groups
        assert "stub" in groups
        assert "surrogate" in groups
    
    def test_edge_styling(self):
        """Test edge styling for different dependency types"""
        modules = [
            ModuleSchema(name="A", description="Test", status="implemented"),
            ModuleSchema(
                name="B", 
                description="Test", 
                status="placeholder",
                dependencies=[
                    {"name": "A", "required": True},
                ]
            ),
            ModuleSchema(
                name="C",
                description="Test",
                status="placeholder", 
                dependencies=[
                    {"name": "A", "required": False}  # Optional dependency
                ]
            )
        ]
        
        graph_data = generate_vis_js_graph(modules)
        
        # Should have 2 edges
        assert len(graph_data.edges) == 2
        
        # Find required vs optional edges
        required_edge = next(e for e in graph_data.edges if e["from"] == "B")
        optional_edge = next(e for e in graph_data.edges if e["from"] == "C")
        
        # Required edge should be solid, optional should be dashed
        assert required_edge.get("dashes") is None or required_edge.get("dashes") == False
        assert optional_edge.get("dashes") == True


class TestModuleMetadata:
    """Test module metadata generation"""
    
    def test_generate_module_metadata(self):
        """Test generating metadata for modules"""
        modules = [
            ModuleSchema(
                name="TestModule",
                description="A test module",
                status="implemented",
                type="service",
                version="2.0.0",
                inputs=[{"type": "string", "description": "Input text"}],
                outputs=[{"type": "json", "description": "Output data"}],
                dependencies=[{"name": "OtherModule", "required": True}],
                metadata={"author": "Test Author", "created": "2024-01-01"}
            )
        ]
        
        metadata = generate_module_metadata(modules)
        
        assert "TestModule" in metadata
        module_meta = metadata["TestModule"]
        
        assert module_meta["name"] == "TestModule"
        assert module_meta["description"] == "A test module"
        assert module_meta["status"] == "implemented"
        assert module_meta["type"] == "service"
        assert module_meta["version"] == "2.0.0"
        assert len(module_meta["inputs"]) == 1
        assert len(module_meta["outputs"]) == 1
        assert len(module_meta["dependencies"]) == 1
        assert module_meta["metadata"]["author"] == "Test Author"
    
    def test_metadata_includes_computed_fields(self):
        """Test metadata includes computed dependency information"""
        modules = [
            ModuleSchema(name="A", description="Module A", status="implemented"),
            ModuleSchema(
                name="B", 
                description="Module B",
                status="placeholder",
                dependencies=[{"name": "A", "required": True}]
            )
        ]
        
        metadata = generate_module_metadata(modules)
        
        # Module A should show B as a dependent
        assert "dependents" in metadata["A"]
        assert "B" in metadata["A"]["dependents"]
        
        # Module B should show dependency info
        assert "dependency_count" in metadata["B"]
        assert metadata["B"]["dependency_count"] == 1 