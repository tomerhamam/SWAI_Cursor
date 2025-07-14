# Milestone 4 Testing Script: Real-time Collaboration

**Duration**: 30 minutes  
**Focus**: Server-Sent Events (SSE) and multi-user synchronization

## Pre-Testing Setup

```bash
# Start backend server
cd backend && source venv/bin/activate && python -m flask run --debug &

# Start frontend development server
cd frontend && npm run dev &

# Open TWO browser windows/tabs to http://localhost:5173
# Label them as "Client A" and "Client B" for testing
```

## Test Scenarios

### 1. SSE Connection Establishment (5 minutes)

**Connection testing:**
- Open browser developer tools in both clients
- Check Network tab for SSE connection
- Verify connection status in application

**Expected Results:**
- [ ] SSE connection shows in Network tab as "EventSource"
- [ ] Connection status indicator shows "Connected"
- [ ] No connection errors in console
- [ ] Connection establishes within 1 second

**Connection monitoring:**
```bash
# In separate terminal, monitor SSE endpoint
curl -N http://localhost:5000/api/stream
```

**Expected Results:**
- [ ] Curl command shows active SSE stream
- [ ] Heartbeat/ping messages received periodically
- [ ] Connection remains stable

### 2. Multi-User Module Operations (12 minutes)

**Create module in Client A:**
- Right-click → Add Module
- Name: "RealtimeTest1"
- Description: "Testing real-time sync"
- Status: "placeholder"

**Expected Results:**
- [ ] Module appears in Client A immediately
- [ ] Module appears in Client B within 500ms
- [ ] Module has same properties in both clients
- [ ] No conflicts or duplicates

**Update module in Client B:**
- Select "RealtimeTest1"
- Change description to "Updated from Client B"
- Change status to "implemented"

**Expected Results:**
- [ ] Changes appear in Client B immediately
- [ ] Changes appear in Client A within 500ms
- [ ] Both clients show updated properties
- [ ] No version conflicts

**Delete module in Client A:**
- Right-click "RealtimeTest1" → Delete
- Confirm deletion

**Expected Results:**
- [ ] Module disappears from Client A immediately
- [ ] Module disappears from Client B within 500ms
- [ ] No orphaned references remain
- [ ] Clean removal from both UIs

### 3. Dependency Synchronization (8 minutes)

**Create dependency chain:**
- In Client A: Create "Module1" → "Module2" dependency
- In Client B: Create "Module2" → "Module3" dependency
- Verify chain appears in both clients

**Expected Results:**
- [ ] Dependencies appear in both clients
- [ ] Dependency lines render correctly
- [ ] No circular dependency warnings
- [ ] Graph layout updates appropriately

**Conflict resolution:**
- Simultaneously create same dependency in both clients
- Verify conflict handling

**Expected Results:**
- [ ] No duplicate dependencies created
- [ ] Conflict resolution is transparent
- [ ] Final state is consistent
- [ ] No error messages for normal race conditions

### 4. Network Resilience (5 minutes)

**Connection interruption:**
- Disable network in Client A (airplane mode or disconnect)
- Make changes in Client B
- Re-enable network in Client A

**Expected Results:**
- [ ] Client A shows "Disconnected" status
- [ ] Client A queues changes locally
- [ ] Reconnection happens automatically
- [ ] Changes sync when reconnected
- [ ] No data loss occurs

**Server restart:**
- Stop backend server
- Make changes in both clients
- Restart backend server

**Expected Results:**
- [ ] Clients show connection loss gracefully
- [ ] Auto-reconnection attempts visible
- [ ] Changes sync after server restart
- [ ] No data corruption

## Performance Testing

### Update Latency
- Create rapid changes in one client
- Measure time to appear in other client
- Test with increasing module count

**Expected Results:**
- [ ] Updates appear within 500ms
- [ ] Latency doesn't increase with more modules
- [ ] No dropped updates
- [ ] Smooth update animations

### Concurrent Users
- Simulate 5+ simultaneous users (multiple tabs)
- Test rapid concurrent operations
- Monitor server performance

**Expected Results:**
- [ ] All clients receive updates
- [ ] Server handles concurrent load
- [ ] No performance degradation
- [ ] Memory usage stays reasonable

## Edge Cases and Error Handling

### Race Conditions
- Both clients edit same module simultaneously
- Both clients delete same module
- Conflicting dependency creation

**Expected Results:**
- [ ] Last-write-wins or merge strategy works
- [ ] No system crashes or errors
- [ ] Consistent final state
- [ ] Graceful conflict resolution

### Invalid Operations
- Client A creates module, Client B immediately deletes it
- Rapid create/delete cycles
- Malformed update messages

**Expected Results:**
- [ ] Invalid operations fail gracefully
- [ ] No system instability
- [ ] Clear error messages where appropriate
- [ ] Automatic state recovery

## Browser Compatibility Testing

### Chrome
- [ ] SSE connection works reliably
- [ ] Updates sync properly
- [ ] No console errors
- [ ] Performance is acceptable

### Firefox
- [ ] SSE connection works reliably
- [ ] Updates sync properly
- [ ] No console errors
- [ ] Performance is acceptable

### Safari (if available)
- [ ] SSE connection works reliably
- [ ] Updates sync properly
- [ ] No console errors
- [ ] Performance is acceptable

## Test Completion Checklist

### Core Functionality
- [ ] SSE connections establish reliably
- [ ] Multi-user operations sync correctly
- [ ] Update latency meets <500ms target
- [ ] Network resilience works properly
- [ ] Conflict resolution handles edge cases

### User Experience
- [ ] Connection status is visible
- [ ] Updates feel immediate and smooth
- [ ] Error handling is graceful
- [ ] No data loss during network issues
- [ ] Interface remains responsive

### Technical Quality
- [ ] No memory leaks in long-running sessions
- [ ] Server handles concurrent users well
- [ ] Browser compatibility confirmed
- [ ] Error logging is comprehensive
- [ ] Performance scales with user count

## Common Issues and Solutions

**Issue: SSE connection fails**
- Check CORS configuration
- Verify server SSE endpoint
- Check firewall/proxy settings

**Issue: Updates don't sync**
- Verify event handling in frontend
- Check server-side event broadcasting
- Monitor network traffic

**Issue: Conflicts cause errors**
- Implement optimistic locking
- Add conflict resolution strategy
- Improve error handling

## Post-Testing Actions

If all tests pass:
```bash
git add .
git commit -m "Milestone 4 complete: Real-time collaboration working"
git tag milestone-4-complete
echo "✅ Milestone 4 testing complete - Ready for Milestone 5"
```

If tests fail:
```bash
echo "❌ Milestone 4 testing failed - Review issues before proceeding"
# Document specific sync issues
# Check server logs for errors
```

## Next Steps

After successful completion:
1. Document collaboration patterns
2. Note any performance bottlenecks
3. Plan advanced user features
4. Prepare for Milestone 5 testing
5. Begin Phase 6 development

---

**Testing completed by**: _______________  
**Date**: _______________  
**Issues found**: _______________  
**Ready for Milestone 5**: [ ] Yes [ ] No 