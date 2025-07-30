# Hierarchical System Composer PRD v2.0

## 1. Introduction & Vision

The Hierarchical System Composer is a web-based tool for creating system architecture diagrams and data flow visualizations. It enables software architects and developers to design high-level system structures through interconnected blocks with navigable hierarchy levels.

**Primary Use Cases:**
- System architecture diagrams
- Data flow diagrams  
- High-level software planning
- Documentation for LLM-assisted development

**Current Version:** v0.3 (based on iterative development and user feedback)

## 2. User Stories

### Core Stories (Implemented ✅)
- As a system designer, I want to create and name blocks on a canvas to represent system components
- As a system designer, I want to draw connections between blocks to represent data flow or dependencies
- As a system designer, I want to group blocks into "Subsystem" blocks to manage complexity
- As a system designer, I want to navigate into subsystems and back up through the hierarchy
- As a system designer, I want to delete blocks and undo deletions
- As a system designer, I want to persist my diagrams and reload them later
- As a system designer, I want to indicate block status (active, warning, error, disabled)
- As a system designer, I want to move blocks between different subsystems
- As a system designer, I want to label connections to describe data flows
- As a system designer, I want to export diagrams as text for LLM consumption

### Discovered Needs (In Progress 🚧)
- As a system designer, I need multiple connections to feed into a single block
- As a system designer, I want to view diagrams on mobile devices

## 3. Functional Requirements

### FR-1: Canvas & Navigation ✅
- **FR-1.1**: Infinite canvas with pan and zoom
- **FR-1.2**: Hierarchical breadcrumbs showing current path
- **FR-1.3**: "Go Up" button when inside subsystems
- **FR-1.4**: Visual indicator (▶ icon) on subsystem blocks

### FR-2: Blocks ✅
- **FR-2.1**: Create "Block" or "Subsystem" via toolbar
- **FR-2.2**: Editable block names (click to edit)
- **FR-2.3**: Drag blocks to reposition
- **FR-2.4**: Status indicators (active, warning, error, disabled)
- **FR-2.5**: Cut/paste blocks between subsystems

### FR-3: Connections ✅
- **FR-3.1**: Single input/output ports per block
- **FR-3.2**: Drag from output to input to create connections
- **FR-3.3**: Connections follow blocks when moved
- **FR-3.4**: Connection labels (double-click to edit)
- **FR-3.5**: Multiple outputs from single port ✅
- **FR-3.6**: Multiple inputs to single port 🚧 (discovered as critical need)

### FR-4: Data Management ✅
- **FR-4.1**: Auto-save to localStorage
- **FR-4.2**: Import/export as JSON
- **FR-4.3**: Export as structured text for LLMs
- **FR-4.4**: Single-level undo for deletions

## 4. Technical Implementation

### Technology Stack
- **Framework**: React 18+ with TypeScript
- **Canvas Library**: React Flow
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Persistence**: localStorage
- **Build Tool**: Vite

### Data Model
```typescript
interface Block {
  id: string;
  type: 'block' | 'subsystem';
  name: string;
  position: { x: number; y: number };
  status?: 'active' | 'warning' | 'error' | 'disabled';
}

interface Connection {
  id: string;
  source: string;
  target: string;
  label?: string;
}

interface Diagram {
  id: string;
  name: string;
  parentId?: string;
  blocks: Record<string, Block>;
  connections: Connection[];
}

interface AppState {
  diagrams: Record<string, Diagram>;
  currentDiagramId: string;
  selectedBlockId: string | null;
  clipboard: {
    block: Block | null;
    sourceDiagramId: string;
  } | null;
  lastAction: UndoState | null;
}
```

### Export Formats

**JSON Export**: Complete state for re-import

**Text Export** (for LLMs):
```
=== SYSTEM ARCHITECTURE ===

BLOCKS:
Main/AuthService [block]
Main/Database [block]
Main/APIGateway [subsystem]
Main/APIGateway/RateLimiter [block]
Main/APIGateway/RequestHandler [block]

CONNECTIONS:
Main/AuthService -> Main/Database (UserData)
Main/APIGateway/RateLimiter -> Main/APIGateway/RequestHandler (ValidatedRequest)

HIERARCHY:
Main
  ├─ AuthService
  ├─ Database
  └─ APIGateway
      ├─ RateLimiter
      └─ RequestHandler
```

## 5. UI/UX Specifications

### Visual Design
- **Blocks**: 150x60px rectangles
- **Regular blocks**: White background, gray border
- **Subsystem blocks**: Light blue background (#E0F2FE), blue border (#3B82F6), ▶ icon
- **Status colors**: 
  - Active: Green border (#10B981)
  - Warning: Yellow border (#F59E0B)
  - Error: Red border (#EF4444)
  - Disabled: Gray background with 50% opacity
- **Connections**: 2px black lines with arrowheads
- **Connection labels**: White pills with gray border

### Interactions
- **Single-click**: Select block
- **Double-click block name**: Edit name
- **Double-click subsystem**: Navigate into it
- **Double-click connection**: Edit label
- **Drag**: Move blocks
- **Ctrl+X/C/V**: Cut/copy/paste
- **Delete key**: Delete selected block
- **Ctrl+Z**: Undo last delete

## 6. Mobile Considerations

### Current State
- Desktop-optimized interface
- "Desktop only" message on mobile

### Planned Mobile Support
- View-only mode on mobile
- Touch navigation (pan, pinch-zoom)
- Long-press for subsystem navigation
- No connection editing on mobile

## 7. Known Limitations & Future Considerations

### Current Limitations
- Single input port restriction (being addressed)
- No wire shorting or bus functionality
- No multi-select operations
- Basic undo (single action only)

### Considered but Deferred (YAGNI)
- Multiple ports per block
- Port type definitions
- Wire shorting by name
- Bus/multi-signal connections
- Advanced styling options
- Collaborative editing
- Version control
- Simulation capabilities

## 8. Success Metrics

- Can create 50+ block diagrams without performance issues
- Can navigate 3+ levels deep in hierarchy
- Can refactor architecture by moving blocks between subsystems
- Can export clear documentation for LLM consumption
- Can round-trip diagrams through export/import

## 9. Development Philosophy

This project follows strict YAGNI (You Aren't Gonna Need It) principles:
- Build only what's needed for immediate use cases
- Validate through actual usage before adding features
- Prefer simple solutions over complex ones
- Question every feature request against real needs

## 10. Next Steps

### Immediate (v0.4)
1. Fix multiple input connections support
2. Improve connection label visibility
3. Basic mobile viewing support

### Future (When Needed)
- Only add features discovered through real usage pain points
- Evaluate each request against actual architectural diagrams being created
- Maintain focus on core use case: software architecture documentation