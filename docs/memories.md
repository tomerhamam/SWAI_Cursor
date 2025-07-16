# Project Memories

## Server Startup Issues - RESOLVED

### Problem: Flask Backend Won't Start
**Issue encountered**: Multiple times during milestone verification
**Date**: July 16, 2025
**Status**: RESOLVED

**Common Errors:**
```bash
bash: venv/bin/activate: No such file or directory
Error: Could not locate a Flask application. Use the 'flask --app' option
```

**Root Cause:**
- Users assume Flask app is in `backend/` directory
- Users look for virtual environment in `backend/venv/`
- Users expect standard Flask app discovery

**CORRECT Solution:**
1. **Flask app location**: Main `app.py` is in **PROJECT ROOT**, not in `backend/`
2. **Virtual environment**: Use `.venv/` in **PROJECT ROOT** (already activated)
3. **Command**: `python -m flask --app app.py run --debug` from project root
4. **Frontend**: Uses port 3001 (configured in vite.config.ts), not default 5173

**Working Commands:**
```bash
# From project root directory (/home/thh3/work/SWAI_Cursor)
python -m flask --app app.py run --debug &
cd frontend && npm run dev &

# Verify servers:
# Backend: http://localhost:5000/api/modules
# Frontend: http://localhost:3001
```

**Never Try Again:**
- `cd backend && source venv/bin/activate` ❌
- Running Flask from backend directory ❌
- Looking for app.py in backend/ ❌

---

## Project Structure Notes
- Backend logic is in `backend/` but main Flask app is in root
- Virtual environment `.venv/` is in project root
- Frontend configured for port 3001 via vite.config.ts proxy setup
