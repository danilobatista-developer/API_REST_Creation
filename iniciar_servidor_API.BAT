@echo off
call venv\Scripts\activate
pip install -r requirements.txt
cmd /k "uvicorn app.main:app --reload"
