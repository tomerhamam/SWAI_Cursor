#!/usr/bin/env python3
"""
Graph builder for converting module definitions to Mermaid diagram format.

This module takes validated ModuleNode objects and generates Mermaid.js
compatible flowchart syntax for visualization.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Set

from loader import load_modules, ModuleNode, ModuleStatus


def sanitize_node_id(name: str) -> str:
    """
    Sanitize module name for use as Mermaid node ID.
    
    Args:
        name: Original module name
        
    Returns:
        Sanitized ID safe for Mermaid syntax
    """
    # Replace spaces and special characters with underscores
    sanitized = name.replace(" ", "_").replace("-", "_")
    # Remove any remaining special characters
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    return sanitized


def get_status_class(status: ModuleStatus) -> str:
    """
    Get CSS class name for module status.
    
    Args:
        status: Module status enum
        
    Returns:
        CSS class name for styling
    """
    status_map = {
        ModuleStatus.IMPLEMENTED: "implemented",
        ModuleStatus.PLACEHOLDER: "placeholder", 
        ModuleStatus.ERROR: "error"
    }
    return status_map.get(status, "unknown")


def build_mermaid_graph(modules: List[ModuleNode]) -> str:
    """
    Build Mermaid flowchart from module definitions.
    
    Args:
        modules: List of validated module nodes
        
    Returns:
        Mermaid flowchart syntax as string
    """
    lines = ["graph TD"]
    
    # Create mapping of module names to IDs
    name_to_id = {module.name: sanitize_node_id(module.name) for module in modules}
    
    # Add node definitions with styling
    for module in modules:
        node_id = name_to_id[module.name]
        status_class = get_status_class(module.status)
        
        # Create node with label and class
        node_line = f'    {node_id}["{module.name}"]'
        lines.append(node_line)
        
        # Add status class for styling
        class_line = f'    class {node_id} {status_class}'
        lines.append(class_line)
    
    # Add empty line before dependencies
    lines.append("")
    
    # Add dependency edges
    for module in modules:
        source_id = name_to_id[module.name]
        
        for dep_name in module.dependencies:
            if dep_name in name_to_id:
                target_id = name_to_id[dep_name]
                edge_line = f'    {target_id} --> {source_id}'
                lines.append(edge_line)
            else:
                # Add missing dependency as external node
                dep_id = sanitize_node_id(dep_name)
                lines.append(f'    {dep_id}["{dep_name}"]')
                lines.append(f'    class {dep_id} missing')
                lines.append(f'    {dep_id} --> {source_id}')
    
    return "\n".join(lines)


def build_mermaid_with_styling(modules: List[ModuleNode]) -> str:
    """
    Build complete Mermaid diagram with CSS styling.
    
    Args:
        modules: List of validated module nodes
        
    Returns:
        Complete Mermaid diagram with styling
    """
    graph = build_mermaid_graph(modules)
    
    # Add CSS styling
    styling = """
    
    %% Status-based styling
    classDef implemented fill:#d4edda,stroke:#c3e6cb,stroke-width:2px,color:#155724
    classDef placeholder fill:#fff3cd,stroke:#ffeaa7,stroke-width:2px,color:#856404
    classDef error fill:#f8d7da,stroke:#f5c6cb,stroke-width:2px,color:#721c24
    classDef missing fill:#f0f0f0,stroke:#999,stroke-width:1px,color:#666,stroke-dasharray: 5 5
    """
    
    return graph + styling


def generate_diagram_file(modules: List[ModuleNode], output_path: Path) -> None:
    """
    Generate Mermaid diagram file from modules.
    
    Args:
        modules: List of validated module nodes
        output_path: Path to write diagram file
    """
    diagram_content = build_mermaid_with_styling(modules)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write diagram file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(diagram_content)
    
    print(f"Generated diagram: {output_path}")


def generate_module_metadata(modules: List[ModuleNode], output_path: Path) -> None:
    """
    Generate JSON metadata file for frontend module details.
    
    Args:
        modules: List of validated module nodes
        output_path: Path to write metadata file
    """
    import json
    
    metadata = {}
    for module in modules:
        metadata[module.name] = {
            "name": module.name,
            "description": module.description,
            "status": module.status.value,
            "implementation": module.implementation,
            "inputs": [{"type": inp.type, "description": inp.description} for inp in module.inputs],
            "outputs": [{"type": out.type, "description": out.description} for out in module.outputs],
            "dependencies": module.dependencies
        }
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write metadata file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Generated metadata: {output_path}")


def main() -> None:
    """CLI entry point for graph builder."""
    parser = argparse.ArgumentParser(
        description="Build Mermaid diagram from YAML module definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python graph_builder.py modules/
  python graph_builder.py modules/ --output static/custom.mmd
  python graph_builder.py modules/ --format json
        """
    )
    
    parser.add_argument(
        "directory",
        help="Directory containing YAML module files"
    )
    
    parser.add_argument(
        "--output",
        default="static/diagram.mmd",
        help="Output file path (default: static/diagram.mmd)"
    )
    
    parser.add_argument(
        "--metadata",
        default="static/modules.json",
        help="Module metadata output path (default: static/modules.json)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load modules using the loader
        modules = load_modules(args.directory)
        
        if not modules:
            print("Warning: No modules loaded", file=sys.stderr)
            return
        
        # Generate diagram file
        output_path = Path(args.output)
        generate_diagram_file(modules, output_path)
        
        # Generate metadata file
        metadata_path = Path(args.metadata)
        generate_module_metadata(modules, metadata_path)
        
        if not args.quiet:
            print(f"Successfully generated diagram for {len(modules)} modules")
            print(f"Diagram: {output_path}")
            print(f"Metadata: {metadata_path}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 