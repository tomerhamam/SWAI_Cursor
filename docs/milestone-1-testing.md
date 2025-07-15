# Milestone 1 Testing Script: Foundation & Backend API

**Duration**: 30 minutes  
**Focus**: Backend API functionality and data integrity

## Pre-Testing Setup

```bash
# Ensure virtual environment is activated (venv is in root directory)
cd /home/thh3/work/SWAI_Cursor
source .venv/bin/activate

# Start the backend Flask server
FLASK_APP=backend.api:app python -m flask run --port 5000

# Open a second terminal for testing
# New terminal:
cd /home/thh3/work/SWAI_Cursor
source .venv/bin/activate
```

**Note**: The Flask app is now located in `backend/api/__init__.py` and must be run from the project root directory.

## Test Scenarios

### 1. API Health Check (5 minutes)

**Test all endpoints are responding:**

```bash
# Test module listing
curl -s http://localhost:5000/api/modules | python -m json.tool

# Test surrogates endpoint  
curl -s http://localhost:5000/api/surrogates | python -m json.tool

# Test specific module
curl -s http://localhost:5000/api/modules/DemoScript | python -m json.tool
```

**Expected Results:**
- [ ] `/api/modules` returns object with module data (9 modules: DemoScript, FileWatcher, GraphBuilder, etc.)
- [ ] `/api/surrogates` returns array of available surrogate types
- [ ] Individual module endpoints return complete module data
- [ ] No 500 errors or timeouts

**Note**: The `/api/graph` endpoint is not yet implemented in Phase 2. It will be added in the next development phase.

### 2. Module CRUD Operations (10 minutes)

**Create a new module:**

```bash
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestModule",
    "description": "Test module for milestone 1",
    "status": "placeholder",
    "version": "1.0.0"
  }'
```

**Update the module:**

```bash
curl -X PUT http://localhost:5000/api/modules/TestModule \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "status": "implemented"
  }'
```

**Verify the update:**

```bash
curl -s http://localhost:5000/api/modules/TestModule | python -m json.tool
```

**Delete the module:**

```bash
curl -X DELETE http://localhost:5000/api/modules/TestModule
```

**Expected Results:**
- [ ] Module creation returns 201 with module data
- [ ] Module update returns 200 with updated data
- [ ] Module deletion returns 204 (no content)
- [ ] Deleted module returns 404 when queried

### 3. Data Validation (5 minutes)

**Test invalid data handling:**

```bash
# Invalid status
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BadModule",
    "description": "Test",
    "status": "invalid_status"
  }'

# Missing required fields
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Missing name"
  }'

# Invalid module name
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invalid Name!",
    "description": "Test",
    "status": "placeholder"
  }'
```

**Expected Results:**
- [ ] Invalid status returns 400 with error message
- [ ] Missing name returns 400 with validation error
- [ ] Invalid characters in name returns 400 with error

### 4. Performance Testing (5 minutes)

**Test with multiple modules:**

```bash
# Create 10 test modules quickly
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/modules \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"PerfTest$i\",
      \"description\": \"Performance test module $i\",
      \"status\": \"placeholder\"
    }" &
done
wait

# Test retrieval performance
time curl -s http://localhost:5000/api/modules > /dev/null
```

**Expected Results:**
- [ ] All 10 modules created successfully
- [ ] Module retrieval completes in <100ms
- [ ] No database locks or conflicts
- [ ] Graph endpoint handles increased load

### 5. File System Integration (5 minutes)

**Test YAML file synchronization:**

```bash
# Create module via API
curl -X POST http://localhost:5000/api/modules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FileTest",
    "description": "Test file sync",
    "status": "placeholder"
  }'

# Check if YAML file was created
ls -la ../modules/FileTest.yaml
cat ../modules/FileTest.yaml

# Edit YAML file directly
echo "name: FileTest
description: Edited directly
status: implemented
version: 1.0.0" > ../modules/FileTest.yaml

# Verify API reflects changes
curl -s http://localhost:5000/api/modules/FileTest | python -m json.tool
```

**Expected Results:**
- [ ] YAML file created when module added via API
- [ ] File contains correct YAML structure
- [ ] Direct file edits are reflected in API
- [ ] No file corruption or permissions issues

## Test Completion Checklist

### Functionality Tests
- [ ] All API endpoints respond correctly
- [ ] CRUD operations work as expected
- [ ] Data validation catches errors appropriately
- [ ] Performance meets targets (<100ms)
- [ ] File system integration works

### Quality Assurance
- [ ] No server errors in console
- [ ] All HTTP status codes are appropriate
- [ ] Error messages are informative
- [ ] Response times are acceptable
- [ ] No memory leaks or resource issues

### Edge Cases
- [ ] Large payloads handled correctly
- [ ] Concurrent requests don't cause issues
- [ ] Invalid JSON returns proper errors
- [ ] Network interruptions handled gracefully

## Common Issues and Solutions

**Issue: "Module not found" errors**
- Check if modules directory exists
- Verify YAML files are valid
- Restart Flask server

**Issue: Slow response times**
- Check database connections
- Verify no blocking operations
- Review server resource usage

**Issue: 500 Internal Server Error**
- Check Flask logs
- Verify environment variables
- Check database connectivity

## Post-Testing Actions

If all tests pass:
```bash
git add .
git commit -m "Milestone 1 complete: Backend API fully functional"
git tag milestone-1-complete
echo "✅ Milestone 1 testing complete - Ready for Milestone 2"
```

If tests fail:
```bash
echo "❌ Milestone 1 testing failed - Review issues before proceeding"
# Document issues in GitHub issues or task list
```

## Next Steps

After successful completion:
1. Archive test data
2. Document any performance notes
3. Review code coverage reports
4. Plan Milestone 2 testing environment
5. Begin Phase 3 development

---

**Testing completed by**: ___Tomer
**Date**: __15.07.2025_____________  
**Issues found**: ___setting and location of files - leftovers from DC3 -  fixes____________  
**Ready for Milestone 2**: [ X] Yes [ ] No 