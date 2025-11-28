@echo off
REM Create templates directory if it doesn't exist
if not exist "templates" mkdir templates

REM Move HTML file to templates directory if it's not already there
if exist "commerce_course_recommendation_.html" (
    if not exist "templates\commerce_course_recommendation_.html" (
        move "commerce_course_recommendation_.html" "templates\"
    )
)

REM Install required packages if not already installed
pip install flask pandas scikit-learn numpy

REM Start the Flask application
echo Starting Flask server...
set FLASK_APP=flask_app.py
set FLASK_ENV=development
flask run --port=5001
