# Milestone 5 Testing Script: Advanced Features

**Duration**: 30 minutes  
**Focus**: Hierarchical management, bulk operations, and advanced UI features

## Pre-Testing Setup

```bash
# Start both servers
cd backend && source venv/bin/activate && python -m flask run --debug &
cd frontend && npm run dev &

# Open browser to http://localhost:5173
# Have keyboard shortcuts reference available
```

## Test Scenarios

### 1. Hierarchical Expand/Collapse (10 minutes)

**Create hierarchical structure:**
- Create parent module "SystemCore"
- Create child modules "Authentication", "Storage", "API"
- Nest children under parent
- Create sub-children under "Authentication"

**Expected Results:**
- [ ] Parent/child relationships visible in graph
- [ ] Hierarchical layout is logical
- [ ] Parent modules show child count indicator
- [ ] Nesting levels are visually distinct

**Expand/collapse operations:**
- Click expand/collapse icons on parent modules
- Test keyboard shortcuts for expand/collapse
- Test "expand all" and "collapse all" options

**Expected Results:**
- [ ] Expand/collapse animations are smooth
- [ ] Collapsed children are hidden but not deleted
- [ ] Expand state persists during pan/zoom
- [ ] Keyboard shortcuts work consistently

**Root node selection:**
- Select different modules as root
- Test view reorganization
- Verify subtree isolation

**Expected Results:**
- [ ] Root selection changes graph perspective
- [ ] Only selected subtree and dependencies show
- [ ] Root selection UI is intuitive
- [ ] Performance remains good with large hierarchies

### 2. Multi-Select Operations (8 minutes)

**Selection mechanisms:**
- Click + Ctrl/Cmd for multi-select
- Drag rectangle for area selection
- Select all with Ctrl/Cmd + A
- Test keyboard navigation with Shift+arrows

**Expected Results:**
- [ ] Multi-select visual feedback is clear
- [ ] Selection methods work consistently
- [ ] Selected items remain highlighted
- [ ] Selection state persists during operations

**Bulk operations:**
- Select multiple modules
- Test bulk status change
- Test bulk delete
- Test bulk property editing

**Expected Results:**
- [ ] Bulk operations work on all selected items
- [ ] Confirmation dialogs show item count
- [ ] Operations are atomic (all or none)
- [ ] Undo covers entire bulk operation

**Bulk dependency management:**
- Select multiple modules
- Add dependency to all selected
- Remove common dependencies
- Test dependency validation

**Expected Results:**
- [ ] Dependencies apply to all selected modules
- [ ] Circular dependency checking works
- [ ] Bulk dependency removal is safe
- [ ] Visual feedback shows progress

### 3. Undo/Redo Functionality (7 minutes)

**Single operations:**
- Create module → Undo → Redo
- Edit module → Undo → Redo
- Delete module → Undo → Redo
- Create dependency → Undo → Redo

**Expected Results:**
- [ ] Undo reverses each operation completely
- [ ] Redo restores the exact previous state
- [ ] Undo/redo buttons update appropriately
- [ ] Keyboard shortcuts (Ctrl/Cmd+Z, Ctrl/Cmd+Y) work

**Complex operations:**
- Perform sequence of operations
- Test undo/redo through the sequence
- Test branching (undo, new operation, redo)
- Test bulk operation undo/redo

**Expected Results:**
- [ ] Complex operation sequences undo correctly
- [ ] Undo history is maintained properly
- [ ] Branching creates new undo path
- [ ] Bulk operations undo as single unit

**State persistence:**
- Perform operations
- Refresh page
- Test undo/redo after refresh

**Expected Results:**
- [ ] Undo history persists across page refreshes
- [ ] State consistency maintained
- [ ] No orphaned undo states
- [ ] History limit respected

### 4. Keyboard Shortcuts (3 minutes)

**Navigation shortcuts:**
- Arrow keys for node navigation
- Tab for element focus
- Enter/Space for activation
- Escape for cancel/close

**Expected Results:**
- [ ] Keyboard navigation is intuitive
- [ ] Focus indicators are visible
- [ ] All interactive elements accessible
- [ ] Tab order is logical

**Operation shortcuts:**
- Ctrl/Cmd+N for new module
- Ctrl/Cmd+S for save
- Ctrl/Cmd+A for select all
- Delete key for delete

**Expected Results:**
- [ ] Shortcuts work consistently
- [ ] No conflicts with browser shortcuts
- [ ] Shortcuts are discoverable (tooltips)
- [ ] Context-appropriate shortcuts only

### 5. Advanced Filtering (2 minutes)

**Filter types:**
- Filter by status (multiple)
- Filter by tag/category
- Filter by dependency depth
- Filter by search term

**Expected Results:**
- [ ] Multiple filters work together
- [ ] Filter results update immediately
- [ ] Filter state is visually clear
- [ ] Filter reset works properly

**Saved filters:**
- Create custom filter combinations
- Save filter presets
- Load saved filters
- Share filter configurations

**Expected Results:**
- [ ] Custom filters save correctly
- [ ] Saved filters load accurately
- [ ] Filter sharing works (if implemented)
- [ ] Filter management is intuitive

## Performance Testing

### Hierarchical Performance
- Create deep hierarchy (5+ levels)
- Test expand/collapse performance
- Monitor memory usage
- Test with 100+ modules

**Expected Results:**
- [ ] Deep hierarchies remain responsive
- [ ] Expand/collapse is smooth
- [ ] Memory usage stays reasonable
- [ ] Performance scales with complexity

### Bulk Operation Performance
- Select 50+ modules
- Test bulk operations
- Monitor execution time
- Test undo performance

**Expected Results:**
- [ ] Bulk operations complete reasonably fast
- [ ] UI remains responsive during operations
- [ ] Progress feedback for long operations
- [ ] Undo performance is acceptable

## Accessibility Testing

### Keyboard Navigation
- Navigate entire interface with keyboard only
- Test all shortcuts
- Verify focus management
- Test screen reader compatibility

**Expected Results:**
- [ ] Complete keyboard accessibility
- [ ] Logical tab order
- [ ] Clear focus indicators
- [ ] Screen reader announcements

### Visual Accessibility
- Test with high contrast mode
- Verify color blindness compatibility
- Test with different font sizes
- Check minimum contrast ratios

**Expected Results:**
- [ ] High contrast mode works
- [ ] Color is not only differentiator
- [ ] Text scales appropriately
- [ ] Meets WCAG 2.1 AA standards

## Test Completion Checklist

### Core Functionality
- [ ] Hierarchical expand/collapse works smoothly
- [ ] Multi-select operations function correctly
- [ ] Undo/redo covers all operations
- [ ] Keyboard shortcuts are comprehensive
- [ ] Advanced filtering is effective

### User Experience
- [ ] All features are discoverable
- [ ] Interactions feel natural and intuitive
- [ ] Performance remains good with complex data
- [ ] Error handling is graceful
- [ ] Help/documentation is available

### Technical Quality
- [ ] No memory leaks with complex operations
- [ ] State management is robust
- [ ] Browser compatibility confirmed
- [ ] Accessibility standards met
- [ ] Code follows established patterns

## Common Issues and Solutions

**Issue: Hierarchy becomes confusing**
- Improve visual hierarchy indicators
- Add breadcrumb navigation
- Implement hierarchy overview

**Issue: Multi-select is unclear**
- Enhance selection visual feedback
- Add selection counter
- Improve bulk operation dialogs

**Issue: Undo/redo is slow**
- Optimize state diffing
- Implement incremental snapshots
- Add progress indicators

## Post-Testing Actions

If all tests pass:
```bash
git add .
git commit -m "Milestone 5 complete: Advanced features fully functional"
git tag milestone-5-complete
echo "✅ Milestone 5 testing complete - Ready for Milestone 6"
```

If tests fail:
```bash
echo "❌ Milestone 5 testing failed - Review issues before proceeding"
# Document specific UX issues
# Create improvement recommendations
```

## Next Steps

After successful completion:
1. Document advanced feature usage
2. Create user guide for complex operations
3. Plan production deployment
4. Prepare for final testing
5. Begin Phase 7 development

---

**Testing completed by**: _______________  
**Date**: _______________  
**Issues found**: _______________  
**Ready for Milestone 6**: [ ] Yes [ ] No 