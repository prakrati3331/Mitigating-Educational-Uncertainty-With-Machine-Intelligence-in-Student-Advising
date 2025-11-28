@echo off
set FLASK_APP=flask_app.py
set FLASK_ENV=development
start http://localhost:5001
python -m flask run --port=5001
