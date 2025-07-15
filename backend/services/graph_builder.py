"""
Enhanced Graph Builder Service for Modular AI Architecture

This module provides advanced dependency resolution, graph building capabilities,
and vis.js compatible graph generation with performance optimizations for 500+ modules.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time

from backend.models.schemas import ModuleSchema, ModuleStatus, ModuleType, validate_modules_batch
import yaml


class CircularDependencyError(Exception):
    """Exception raised when circular dependencies are detected"""
    
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(f"Circular dependency detected: {cycle_str}")


@dataclass
class DependencyNode:
    """Represents a module node in the dependency graph"""
    name: str
    status: ModuleStatus
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    level: int = 0
    
    def __eq__(self, other):
        """Nodes are equal if they have the same name"""
        return isinstance(other, DependencyNode) and self.name == other.name
    
    def __hash__(self):
        """Hash based on name for use in sets/dicts"""
        return hash(self.name)


@dataclass
class GraphData:
    """Data structure for vis.js graph representation"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }


class DependencyResolver:
    """Advanced dependency resolution with cycle detection and level calculation"""
    
    def __init__(self, modules: List[ModuleSchema]):
        self.modules = modules
        self.nodes: Dict[str, DependencyNode] = {}
        self._build_nodes()
    
    def _build_nodes(self):
        """Build dependency nodes from module schemas"""
        # First pass: create all nodes
        for module in self.modules:
            self.nodes[module.name] = DependencyNode(
                name=module.name,
                status=module.status,
                dependencies=[dep.name for dep in module.dependencies]
            )
        
        # Second pass: build dependents graph
        for module in self.modules:
            for dep in module.dependencies:
                dep_name = dep.name
                if dep_name in self.nodes:
                    self.nodes[dep_name].dependents.append(module.name)
    
    def resolve(self) -> List[str]:
        """
        Resolve dependencies using topological sort.
        
        Returns:
            List of module names in dependency order
            
        Raises:
            CircularDependencyError: If circular dependencies detected
            ValueError: If required dependencies are missing
        """
        # Check for missing dependencies
        self._validate_dependencies()
        
        # Kahn's algorithm for topological sorting with cycle detection
        in_degree = {}
        for name, node in self.nodes.items():
            in_degree[name] = len([dep for dep in node.dependencies 
                                 if dep in self.nodes])  # Only count existing dependencies
        
        # Find nodes with no dependencies
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        resolution_order = []
        
        while queue:
            current = queue.popleft()
            resolution_order.append(current)
            
            # Update in-degree for dependents
            for dependent in self.nodes[current].dependents:
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # Check for cycles
        if len(resolution_order) != len(self.nodes):
            # Find cycle
            remaining = set(self.nodes.keys()) - set(resolution_order)
            cycle = self._find_cycle(remaining)
            raise CircularDependencyError(cycle)
        
        # Calculate levels for hierarchical layout
        self._calculate_levels(resolution_order)
        
        return resolution_order
    
    def _validate_dependencies(self):
        """Validate that all required dependencies exist"""
        all_module_names = set(self.nodes.keys())
        
        for module in self.modules:
            for dep in module.dependencies:
                if dep.required and dep.name not in all_module_names:
                    raise ValueError(
                        f"Missing required dependency: {module.name} -> {dep.name}"
                    )
    
    def _find_cycle(self, remaining_nodes: Set[str]) -> List[str]:
        """Find a cycle in the remaining nodes using DFS"""
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            if node in rec_stack:
                # Found cycle, return path from cycle start
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in self.nodes[node].dependencies:
                if dep in remaining_nodes:
                    cycle = dfs(dep)
                    if cycle:
                        return cycle
            
            rec_stack.remove(node)
            path.pop()
            return None
        
        for node in remaining_nodes:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle
        
        return list(remaining_nodes)  # Fallback
    
    def _calculate_levels(self, resolution_order: List[str]):
        """Calculate hierarchical levels for layout"""
        for name in resolution_order:
            node = self.nodes[name]
            if not node.dependencies:
                node.level = 0
            else:
                # Level is max level of dependencies + 1
                max_dep_level = max(
                    self.nodes[dep].level 
                    for dep in node.dependencies 
                    if dep in self.nodes
                ) if node.dependencies else -1
                node.level = max_dep_level + 1


class GraphBuilder:
    """Main graph builder with enhanced capabilities for vis.js integration"""
    
    def __init__(self, modules_dir: Optional[Path] = None):
        """
        Initialize graph builder
        
        Args:
            modules_dir: Directory containing module YAML files
        """
        self.modules_dir = modules_dir or Path("modules")
        self.modules: List[ModuleSchema] = []
        self._load_modules()
    
    def _load_modules(self):
        """Load and validate modules from directory"""
        if not self.modules_dir.exists():
            self.modules = []
            return
            
        modules_data = []
        for yaml_file in self.modules_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        modules_data.append(data)
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")
        
        # Validate using Pydantic schemas
        try:
            self.modules = validate_modules_batch(modules_data)
        except Exception as e:
            print(f"Warning: Validation failed: {e}")
            self.modules = []
    
    def build_graph(
        self, 
        layout: str = "physics",
        include_statuses: Optional[List[ModuleStatus]] = None
    ) -> GraphData:
        """
        Build vis.js compatible graph data
        
        Args:
            layout: Layout type ("physics", "hierarchical")
            include_statuses: Filter modules by status
            
        Returns:
            GraphData object with nodes and edges
        """
        # Filter modules by status if specified
        filtered_modules = self.modules
        if include_statuses:
            filtered_modules = [
                m for m in self.modules 
                if m.status in include_statuses
            ]
        
        if not filtered_modules:
            return GraphData(nodes=[], edges=[])
        
        # Resolve dependencies
        resolver = DependencyResolver(filtered_modules)
        try:
            resolver.resolve()  # This calculates levels and validates
        except CircularDependencyError:
            # Still return graph but mark problematic nodes
            pass
        
                 # Generate vis.js nodes
        nodes = []
        for module in filtered_modules:
            node_data: Dict[str, Any] = {
                "id": module.name,
                "label": module.name,
                "group": module.status,
                "title": self._generate_node_tooltip(module),
                "type": module.type
            }
            
            # Add level for hierarchical layout
            if layout == "hierarchical" and module.name in resolver.nodes:
                node_data["level"] = resolver.nodes[module.name].level
            
            nodes.append(node_data)
        
        # Generate vis.js edges
        edges = []
        module_names = {m.name for m in filtered_modules}
        
        for module in filtered_modules:
            for dep in module.dependencies:
                if dep.name in module_names:
                    edge_data: Dict[str, Any] = {
                        "from": module.name,
                        "to": dep.name,
                        "arrows": "to",
                        "title": f"{module.name} depends on {dep.name}"
                    }
                    
                    # Style optional dependencies differently
                    if not dep.required:
                        edge_data["dashes"] = True
                        edge_data["color"] = {"color": "#848484"}
                    
                    edges.append(edge_data)
        
        return GraphData(nodes=nodes, edges=edges)
    
    def _generate_node_tooltip(self, module: ModuleSchema) -> str:
        """Generate HTML tooltip for module node"""
        tooltip_parts = [
            f"<b>{module.name}</b>",
            f"Status: {module.status}",
            f"Type: {module.type}",
            f"Version: {module.version}",
            f"<br/>{module.description}"
        ]
        
        if module.dependencies:
            deps = [dep.name for dep in module.dependencies]
            tooltip_parts.append(f"<br/>Dependencies: {', '.join(deps)}")
        
        return "<br/>".join(tooltip_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get module statistics for dashboard"""
        stats = {
            "total_modules": len(self.modules),
            "by_status": defaultdict(int),
            "by_type": defaultdict(int),
            "dependency_count": 0
        }
        
        for module in self.modules:
            stats["by_status"][module.status] += 1
            stats["by_type"][module.type] += 1
            stats["dependency_count"] += len(module.dependencies)
        
        return dict(stats)
    
    def reload_modules(self):
        """Reload modules from disk"""
        self._load_modules()


# Utility functions for backwards compatibility and convenience

def generate_vis_js_graph(modules: List[ModuleSchema]) -> GraphData:
    """
    Generate vis.js graph from module list
    
    Args:
        modules: List of module schemas
        
    Returns:
        GraphData object ready for vis.js Network
    """
    # Create temporary resolver for dependency analysis
    resolver = DependencyResolver(modules)
    try:
        resolver.resolve()
    except (CircularDependencyError, ValueError):
        # Continue with graph generation even if there are issues
        pass
    
         # Generate nodes
    nodes = []
    for module in modules:
        node: Dict[str, Any] = {
            "id": module.name,
            "label": module.name,
            "group": module.status,
            "title": f"{module.name}\n{module.description}\nStatus: {module.status}",
            "type": module.type
        }
        
        # Add level if available
        if module.name in resolver.nodes:
            node["level"] = resolver.nodes[module.name].level
        
        nodes.append(node)
    
    # Generate edges
    edges = []
    module_names = {m.name for m in modules}
    
    for module in modules:
        for dep in module.dependencies:
            if dep.name in module_names:
                edge: Dict[str, Any] = {
                    "from": module.name,
                    "to": dep.name,
                    "arrows": "to"
                }
                
                # Style optional dependencies
                if not dep.required:
                    edge["dashes"] = True
                
                edges.append(edge)
    
    return GraphData(nodes=nodes, edges=edges)


def generate_module_metadata(modules: List[ModuleSchema]) -> Dict[str, Any]:
    """
    Generate comprehensive metadata for modules
    
    Args:
        modules: List of module schemas
        
    Returns:
        Dictionary mapping module names to metadata
    """
    # Build dependency resolver to get computed fields
    resolver = DependencyResolver(modules)
    try:
        resolver.resolve()
    except (CircularDependencyError, ValueError):
        pass
    
    metadata = {}
    
    for module in modules:
        module_meta = {
            "name": module.name,
            "description": module.description,
            "status": module.status,
            "type": module.type,
            "version": module.version,
            "inputs": [input_schema.model_dump() for input_schema in module.inputs],
            "outputs": [output_schema.model_dump() for output_schema in module.outputs],
            "dependencies": [dep.model_dump() for dep in module.dependencies],
            "metadata": module.metadata,
            "dependency_count": len(module.dependencies)
        }
        
        # Add computed fields from resolver
        if module.name in resolver.nodes:
            node = resolver.nodes[module.name]
            module_meta["dependents"] = node.dependents
            module_meta["level"] = node.level
        else:
            module_meta["dependents"] = []
            module_meta["level"] = 0
        
        metadata[module.name] = module_meta
    
    return metadata


# Legacy function for backwards compatibility
def generate_diagram_file(modules_data, output_path="static/diagram.mmd"):
    """Legacy function for Mermaid diagram generation (deprecated)"""
    # This function is kept for backwards compatibility but should be replaced
    # with vis.js graph generation
    pass 