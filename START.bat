@echo off
cd backend
start cmd /k "pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8001"
timeout /t 3
cd ..\frontend
start http://localhost:3001
start cmd /k "python -m http.server 3001"
echo Server started! Open http://localhost:3001
pause