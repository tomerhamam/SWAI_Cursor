# Agent Memory Rule - ALWAYS FOLLOW

## MANDATORY: Check Project Memories First

**RULE**: On EVERY new user interaction, the agent MUST:

1. **Read `docs/memories.md`** before taking any action
2. **Check for relevant past issues** that match the current request
3. **Apply documented solutions** instead of rediscovering problems
4. **Update memories** when new issues or solutions are found

## When to Check Memories

✅ **ALWAYS check before:**
- Starting servers (Flask, npm, etc.)
- Troubleshooting common errors
- Setting up development environment
- Running tests or deployments
- Making configuration changes

✅ **ESPECIALLY check for:**
- Server startup procedures
- Port configurations
- Virtual environment locations
- Common error patterns
- Project structure assumptions

## Agent Behavior Requirements

### DO:
- Read memories.md at start of interaction
- Reference documented solutions
- Follow "CORRECT Solution" sections precisely
- Avoid "Never Try Again" approaches
- Update memories when learning new information

### DON'T:
- Ignore documented solutions
- Repeat failed approaches from memories
- Assume standard configurations without checking
- Waste time rediscovering known issues

## Memory Update Protocol

When encountering new issues or solutions:
1. Document the problem clearly
2. Include error messages and symptoms
3. Provide step-by-step resolution
4. Mark old approaches to avoid
5. Add date and status information

## Example Usage

```
User: "Start the backend server"
Agent: 
1. ✅ Check docs/memories.md first
2. ✅ Find "Server Startup Issues - RESOLVED"
3. ✅ Use documented solution: python -m flask --app app.py run --debug
4. ✅ Avoid backend/ directory approach (marked as "Never Try Again")
```

---

**This rule applies globally to ALL agent interactions with this project.**
**Ignoring documented memories wastes time and frustrates users.**
**When in doubt, check memories.md first.** 