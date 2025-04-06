@echo off
call .venv\Scripts\activate
start /B python app.py
start http://localhost:5000
pause