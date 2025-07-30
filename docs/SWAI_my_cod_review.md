<!-- Verified on 2025-07-30 by Claude -->
<!-- Purpose: Python codebase review guide with human-centered approach -->

# SWAI - Python Codebase Review Guide - Human-Centered Approach

## Phase 1: Get the Lay of the Land (30-45 minutes)

### What are we trying to achieve?

Build a mental map of the project's geography - like looking at a city from a helicopter before walking its streets.

### Why this matters

You can't understand code in isolation. You need context: What problem does this solve? Who uses it? How is it deployed?

### Activities

1. **Read all documentation** (README, docs/, wiki)
   - Look for: Architecture diagrams, design decisions, problem statement
   - Take notes on: Core concepts, domain terminology, stated goals

2. **Examine configuration files** (setup.py, requirements.txt, Dockerfile, .env.example)
   - Understand: Dependencies, deployment environment, external services
   - Question: Why these specific libraries? What infrastructure is assumed?

3. **Find and run the entry points**
   - Locate: main.py, CLI commands, web server startup
   - Try: Actually run the application (even if it fails, the errors are informative)

### Definition of Done

- [ ] You can explain in one paragraph what this codebase does and why it exists
- [ ] You have a list of 3-5 core concepts/terms used in this domain
- [ ] You know how to start the application (even if you can't run it fully)
- [ ] You understand the deployment context (web app? CLI tool? library?)

### Your Notes Template

```
PROJECT PURPOSE: [one paragraph]

DOMAIN CONCEPTS:
- Term 1: [definition]
- Term 2: [definition]

DEPLOYMENT: [web/cli/library/service]
ENTRY POINT: [how to run it]
```

---

## Phase 2: Identify the Skeleton (45-60 minutes)

### What are we trying to achieve?

Find the load-bearing structures - the code that everything else hangs off of.

### Why this matters

In any codebase, 20% of the code does 80% of the work. Finding this 20% first makes everything else make sense.

### Activities

1. **Map the directory structure**
   - Draw it on paper/whiteboard
   - Mark which folders contain: core logic, tests, utilities, configuration
   - Identify naming patterns (do they use `services/`, `models/`, `handlers/`?)

2. **Find the core data structures**
   - Look for: Classes/dataclasses that appear everywhere
   - Check: Database models, API schemas, main entities
   - Ask: What are the "nouns" in this system?

3. **Trace the main workflows**
   - Pick ONE primary use case
   - Follow it from entry point to completion
   - Note every file it touches

### Definition of Done

- [ ] You have a hand-drawn diagram of the folder structure with annotations
- [ ] You can list 3-5 core classes/data structures and explain what they represent
- [ ] You can describe one complete workflow from start to finish
- [ ] You've identified which code is "core" vs "supporting"

### Your Notes Template

```
CORE STRUCTURES:
1. [ClassName] - represents [what] - found in [where]
2. [ClassName] - represents [what] - found in [where]

MAIN WORKFLOW: [User does X]
1. Request enters at: [file:function]
2. Processed by: [file:function]
3. Data stored in: [where]
4. Response sent from: [file:function]

FOLDER PURPOSES:
- /src: [what goes here]
- /tests: [test strategy]
- /lib: [what goes here]
```

---

## Phase 3: Understand the Conversations (60-90 minutes)

### What are we trying to achieve?

Understand how different parts of the code talk to each other - the interfaces and contracts.

### Why this matters

Code complexity comes from interactions, not individual functions. Understanding these interaction patterns reveals the true architecture.

### Activities

1. **Map the imports**
   - Pick 3-5 core modules
   - For each: What does it import? What imports it?
   - Look for: Circular dependencies, abstraction layers, clear boundaries

2. **Find the integration points**
   - Database connections: Where/how are they established?
   - External APIs: What services does this talk to?
   - Message queues/events: How do components communicate?

3. **Identify the contracts**
   - Look at function signatures of public APIs
   - Find interface definitions (protocols, ABCs, base classes)
   - Note data validation/transformation boundaries

### Definition of Done

- [ ] You can draw a dependency diagram showing how major modules relate
- [ ] You understand how the app connects to external services
- [ ] You can identify 2-3 key interfaces/protocols that define component boundaries
- [ ] You know where data validation happens

### Your Notes Template

```
MODULE DEPENDENCIES:
- [ModuleA] depends on → [ModuleB, ModuleC]
- [ModuleB] depends on → [ModuleD]

EXTERNAL INTEGRATIONS:
- Database: [type] connected in [where]
- APIs: [which ones] called from [where]
- Files: [what types] processed in [where]

KEY INTERFACES:
1. [InterfaceName]: Defines contract for [what]
2. [InterfaceName]: Used by [who] to [do what]
```

---

## Phase 4: Learn the Patterns and Conventions (45-60 minutes)

### What are we trying to achieve?

Understand the "house style" - the patterns, conventions, and idioms this codebase uses.

### Why this matters

Every codebase has its own personality. Understanding the local conventions helps you read code faster and write code that fits in.

### Activities

1. **Identify coding patterns**
   - Error handling: Try/except patterns, custom exceptions?
   - Logging: How and where do they log?
   - Configuration: Environment variables? Config files? How are settings managed?

2. **Understand the testing philosophy**
   - Test structure: Unit? Integration? E2E?
   - Mocking strategy: What gets mocked and how?
   - Test data: Fixtures? Factories? Hard-coded?

3. **Find the utilities and helpers**
   - Common operations wrapped in utilities?
   - Domain-specific helpers?
   - Decorators used frequently?

### Definition of Done

- [ ] You can write a new function that "looks like it belongs"
- [ ] You understand the error handling strategy
- [ ] You know how to add a new test that follows existing patterns
- [ ] You can identify 3-5 project-specific conventions

### Your Notes Template

```
CODING CONVENTIONS:
- Errors: [how they handle errors]
- Logging: [what gets logged where]
- Naming: [function/variable naming patterns]

TESTING APPROACH:
- Structure: [how tests are organized]
- Style: [unittest/pytest/other]
- Coverage: [what's tested, what isn't]

COMMON PATTERNS:
1. [Pattern]: Used for [what] - example: [where]
2. [Pattern]: Used for [what] - example: [where]
```

---

## Phase 5: Deep Dive on Critical Paths (2-3 hours)

### What are we trying to achieve?

Truly understand the most important workflows at a detailed level.

### Why this matters

This is where you move from "I know where things are" to "I understand how things work."

### Activities

1. **Choose 2-3 critical workflows**
   - The most common user path
   - The most complex business logic
   - The most performance-critical operation

2. **For each workflow, trace in detail**
   - Start with a specific user action/API call
   - Follow every function call
   - Understand every transformation
   - Note every side effect

3. **Question everything**
   - Why is this designed this way?
   - What edge cases are handled?
   - What assumptions are made?
   - What could go wrong?

### Definition of Done

- [ ] You could implement a similar feature following the same patterns
- [ ] You understand not just WHAT the code does but WHY
- [ ] You've identified potential issues or improvements
- [ ] You could debug issues in these workflows

### Your Notes Template

```
WORKFLOW: [Name]
Purpose: [What user need does this serve?]

DETAILED FLOW:
1. Entry: [function] receives [what data]
   - Validates: [what]
   - Transforms: [how]
   
2. Processing: [function] does [what]
   - Business rule: [explain]
   - Edge case handling: [what cases]
   
3. Storage: [where/how]
   - Transaction boundaries: [where]
   - Consistency guarantees: [what]

QUESTIONS/CONCERNS:
- [Why does it...?]
- [What happens if...?]
- [Could be improved by...?]
```

---

## Phase 6: Build Your Mental Model (1-2 hours)

### What are we trying to achieve?

Synthesize everything into a coherent mental model you can use for future work.

### Why this matters

Knowledge isn't useful until it's organized. This phase turns information into understanding.

### Activities

1. **Create your own documentation**
   - One-page architecture overview
   - Glossary of project-specific terms
   - "How to add a new feature" guide
   - Common gotchas and their solutions

2. **Identify knowledge gaps**
   - What still confuses you?
   - What seems unnecessarily complex?
   - What would you need to learn to contribute?

3. **Plan your first contribution**
   - Find a small bug or improvement
   - Understand what you'd need to change
   - Identify who you'd need to talk to

### Definition of Done

- [ ] You have a one-page "elevator pitch" for the codebase
- [ ] You've created personal reference documentation
- [ ] You have a list of specific questions for the team
- [ ] You've identified your first potential contribution

### Your Notes Template

```
ELEVATOR PITCH:
[One paragraph that explains this codebase to a new developer]

KEY INSIGHTS:
1. [Something non-obvious you learned]
2. [A clever design decision you noticed]
3. [A pattern that makes sense now]

REMAINING QUESTIONS:
1. [Specific question]: Need to ask [who]
2. [Specific question]: Need to investigate [what]

FIRST CONTRIBUTION IDEAS:
1. [What]: Because [why it matters]
2. [What]: Because [why it matters]
```

---

## Meta-Learning: Track Your Progress

### Daily Review Questions

At the end of each day, ask yourself:

1. What surprised me today?
2. What patterns am I starting to see?
3. What should I focus on tomorrow?

### Signs You're Making Progress

- You can navigate to code without searching
- You predict what you'll find before opening files
- You understand the "why" not just the "what"
- You see opportunities for improvement
- You can explain the codebase to others

### When You're Stuck

- Pick a smaller scope (one file, one function)
- Run the code and add print statements
- Draw diagrams by hand
- Take a break and come back fresh
- Ask specific questions to the team

Remember: Understanding a codebase is like learning a new city. First you learn the main streets, then the neighborhoods, then the shortcuts and hidden gems. Be patient with yourself and celebrate small victories.