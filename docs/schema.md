<!-- Verified on 2025-07-30 by Claude -->
<!-- Purpose: YAML module schema specification and validation rules -->

# YAML Module Schema Documentation

This document defines the structure and validation rules for YAML module definitions in the Modular AI Architecture system.

## Schema Definition

Each module must be defined in a separate YAML file with the following structure:

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the module |
| `description` | string | Brief description of module purpose |
| `inputs` | list[dict] | List of input specifications |
| `outputs` | list[dict] | List of output specifications |
| `status` | enum | Current implementation status |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `implementation` | string | Implementation type or file path |
| `dependencies` | list[string] | List of module names this module depends on |

## Field Specifications

### Status Field
Allowed values:
- `implemented` - Module is fully implemented and functional
- `placeholder` - Module exists but uses surrogate/stub behavior
- `error` - Module has known issues or implementation failures

### Input/Output Specifications
Each input and output must have:
- `type`: Data type (string, required)
- `description`: Human-readable description (string, required)

## Valid Example

```yaml
name: "TrajectoryPlanner"
description: "Plans optimal vehicle trajectory from current pose to goal"
inputs:
  - type: "Pose"
    description: "Current vehicle position and orientation"
  - type: "Goal"
    description: "Target destination coordinates"
outputs:
  - type: "Trajectory"
    description: "Sequence of waypoints to follow"
status: "placeholder"
implementation: "rule-based"
dependencies:
  - "MapService"
  - "ObstacleDetector"
```

## Additional Valid Example

```yaml
name: "SensorFusion"
description: "Combines multiple sensor inputs into unified world model"
inputs:
  - type: "LidarData"
    description: "3D point cloud from LiDAR sensor"
  - type: "CameraImage"
    description: "RGB image from front camera"
  - type: "IMUData"
    description: "Inertial measurement unit readings"
outputs:
  - type: "WorldModel"
    description: "Unified representation of environment"
status: "implemented"
implementation: "deep_learning"
dependencies: []
```

## Invalid Example (for testing)

```yaml
name: "InvalidModule"
description: "This module has invalid status"
inputs:
  - type: "SomeInput"
    description: "Input description"
outputs:
  - type: "SomeOutput"
    description: "Output description"
status: "invalid_status"  # This will cause validation error
```

## Validation Rules

1. **Name Uniqueness**: Each module name must be unique across all YAML files
2. **Required Fields**: All required fields must be present
3. **Status Values**: Status must be one of the allowed enum values
4. **Dependencies**: Referenced dependencies should exist as other modules
5. **Input/Output Structure**: Each input/output must have both type and description

## File Naming Convention

- Use lowercase with underscores: `trajectory_planner.yaml`
- File name should relate to module name for clarity
- Place all module YAML files in the `/modules/` directory 