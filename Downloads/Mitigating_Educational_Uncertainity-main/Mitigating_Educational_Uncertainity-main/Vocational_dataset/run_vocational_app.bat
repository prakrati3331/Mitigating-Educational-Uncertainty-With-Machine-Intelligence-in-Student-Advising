@echo off
echo Starting Vocational Career Guidance System...
echo Installing required packages...
pip install flask pandas numpy scikit-learn flask-cors

echo Starting Flask server...
set FLASK_APP=flask_app.py
set FLASK_ENV=development
flask run --port=5000 --host=0.0.0.0

pause
