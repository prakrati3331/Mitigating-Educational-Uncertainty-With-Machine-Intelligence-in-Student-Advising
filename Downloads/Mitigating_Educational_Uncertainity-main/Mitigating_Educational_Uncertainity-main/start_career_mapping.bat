@echo off
echo Starting Career Mapping Service...
echo.
echo This will start the career assessment service on port 5000
echo The dashboard will link to this service for career assessments
echo.
cd /d "%~dp0Career_Mapping"
python flask_app.py
pause
