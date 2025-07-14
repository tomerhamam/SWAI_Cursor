# Milestone 3 Testing Script: Core Interactivity

**Duration**: 30 minutes  
**Focus**: Advanced vis.js interactions and user interface features

## Pre-Testing Setup

```bash
# Start both servers
cd backend && source venv/bin/activate && python -m flask run --debug &
cd frontend && npm run dev &

# Open browser to http://localhost:5173
# Open browser developer tools for monitoring
```

## Test Scenarios

### 1. Right-Click Context Menus (8 minutes)

**Basic context menu functionality:**
- Right-click on empty graph area
- Right-click on existing module nodes
- Test menu options and actions

**Expected Results:**
- [ ] Right-click on empty space shows "Add Module" option
- [ ] Right-click on node shows module-specific options
- [ ] Menu appears at cursor position
- [ ] Menu disappears when clicking elsewhere
- [ ] Menu items are clearly labeled and functional

**Add Module workflow:**
- Right-click empty space → "Add Module"
- Fill out module creation form
- Submit and verify new module appears

**Expected Results:**
- [ ] Form appears with proper fields (name, description, status)
- [ ] Form validation works (required fields, invalid names)
- [ ] New module appears in graph immediately
- [ ] Module is saved to backend (verify via API)

### 2. Drag & Drop Module Creation (8 minutes)

**Drag from toolbar/palette:**
- Test dragging module template to graph
- Verify drop zones and visual feedback
- Test multiple module types if available

**Expected Results:**
- [ ] Drag preview shows module being dragged
- [ ] Valid drop zones are highlighted
- [ ] Invalid drop areas show appropriate feedback
- [ ] Dropped module appears at correct position
- [ ] Module creation dialog appears after drop

**Drag existing modules:**
- Test repositioning existing modules
- Verify position persistence
- Test drag boundaries

**Expected Results:**
- [ ] Existing modules can be dragged smoothly
- [ ] Position changes are visually smooth
- [ ] Modules stay within graph boundaries
- [ ] Position changes persist after refresh

### 3. Dependency Line Drawing (8 minutes)

**Create dependencies:**
- Select source module
- Drag to target module
- Verify dependency line appears
- Test bidirectional dependencies

**Expected Results:**
- [ ] Dependency creation mode is clear
- [ ] Drag line shows connection preview
- [ ] Completed dependencies show as arrows
- [ ] Dependencies are labeled if versioned
- [ ] Circular dependencies are prevented/warned

**Dependency management:**
- Right-click on existing dependency lines
- Test removing dependencies
- Verify dependency validation

**Expected Results:**
- [ ] Existing dependencies can be selected
- [ ] Context menu offers "Remove" option
- [ ] Dependency removal updates graph immediately
- [ ] Backend reflects dependency changes

### 4. Zoom and Pan Controls (3 minutes)

**Zoom functionality:**
- Test mouse wheel zoom
- Test zoom buttons (if present)
- Test keyboard zoom shortcuts
- Test zoom limits

**Expected Results:**
- [ ] Mouse wheel zooms smoothly
- [ ] Zoom maintains center focus
- [ ] Zoom limits prevent excessive scaling
- [ ] Zoom level indicator is visible

**Pan functionality:**
- Test mouse drag panning
- Test keyboard arrow panning
- Test pan boundaries

**Expected Results:**
- [ ] Dragging empty space pans the view
- [ ] Panning is smooth and responsive
- [ ] Pan boundaries prevent excessive movement
- [ ] Pan state persists during zoom

### 5. Status-Based Filtering (3 minutes)

**Filter controls:**
- Test status filter dropdown/buttons
- Verify filter combinations
- Test filter reset functionality

**Expected Results:**
- [ ] Filter controls are intuitive
- [ ] Filtering updates graph immediately
- [ ] Multiple status filters work together
- [ ] "Show All" option clears filters
- [ ] Filter state is visually indicated

## Performance Testing

### Interaction Responsiveness
- Test with 50+ modules
- Monitor frame rate during interactions
- Check for lag or stuttering

**Expected Results:**
- [ ] All interactions respond within 100ms
- [ ] No dropped frames during drag operations
- [ ] Smooth animations throughout
- [ ] No memory leaks during extended use

### Stress Testing
- Create many modules rapidly
- Test with complex dependency networks
- Monitor browser performance

**Expected Results:**
- [ ] System handles 100+ modules smoothly
- [ ] Complex dependency graphs render correctly
- [ ] No performance degradation over time
- [ ] Browser memory usage stays reasonable

## Edge Cases and Error Handling

### Invalid Operations
- Try to create circular dependencies
- Test invalid module names
- Attempt to delete modules with dependencies

**Expected Results:**
- [ ] Circular dependencies are prevented
- [ ] Helpful error messages appear
- [ ] Operations fail gracefully
- [ ] System remains stable after errors

### Network Connectivity
- Disable network temporarily
- Test offline behavior
- Re-enable network and verify recovery

**Expected Results:**
- [ ] Offline actions queue appropriately
- [ ] User receives connectivity feedback
- [ ] Changes sync when connection restored
- [ ] No data loss during connectivity issues

## Accessibility Testing

### Keyboard Navigation
- Tab through all interactive elements
- Test keyboard shortcuts for common actions
- Verify focus management

**Expected Results:**
- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are clearly visible
- [ ] Keyboard shortcuts work as expected
- [ ] Tab order is logical

### Screen Reader Support
- Test with screen reader (if available)
- Verify descriptive labels
- Check ARIA attributes

**Expected Results:**
- [ ] Screen reader can navigate interface
- [ ] All actions are announced properly
- [ ] Context menus are accessible
- [ ] Graph structure is describable

## Test Completion Checklist

### Core Interactions
- [ ] Right-click context menus work reliably
- [ ] Drag & drop module creation functions
- [ ] Dependency line drawing is intuitive
- [ ] Zoom and pan controls are smooth
- [ ] Status filtering works as expected

### User Experience
- [ ] All interactions feel responsive
- [ ] Visual feedback is immediate and clear
- [ ] Error handling is graceful
- [ ] Interface is discoverable
- [ ] Actions are reversible where appropriate

### Technical Quality
- [ ] Performance meets 60 FPS target with 100+ modules
- [ ] No memory leaks or performance degradation
- [ ] Browser compatibility confirmed
- [ ] Accessibility requirements met
- [ ] Code follows established patterns

## Common Issues and Solutions

**Issue: Context menus don't appear**
- Check event listeners on graph elements
- Verify preventDefault on right-click
- Check z-index of menu elements

**Issue: Drag & drop doesn't work**
- Verify drag event handlers
- Check drop zone detection
- Ensure proper event propagation

**Issue: Dependencies create loops**
- Implement cycle detection algorithm
- Provide clear user feedback
- Offer alternative connection suggestions

## Post-Testing Actions

If all tests pass:
```bash
git add .
git commit -m "Milestone 3 complete: Core interactivity fully functional"
git tag milestone-3-complete
echo "✅ Milestone 3 testing complete - Ready for Milestone 4"
```

If tests fail:
```bash
echo "❌ Milestone 3 testing failed - Review issues before proceeding"
# Create screenshots of failing interactions
# Document specific UX issues
```

## Next Steps

After successful completion:
1. Document interaction patterns
2. Note any UX improvements needed
3. Plan real-time collaboration features
4. Prepare for Milestone 4 testing
5. Begin Phase 5 development

---

**Testing completed by**: _______________  
**Date**: _______________  
**Issues found**: _______________  
**Ready for Milestone 4**: [ ] Yes [ ] No 