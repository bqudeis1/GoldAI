@echo off
start cmd /k "python live.py"
start cmd /k "uvicorn api:app --reload --port 8000"
echo KING SNIPER BACKEND NODES STARTING...