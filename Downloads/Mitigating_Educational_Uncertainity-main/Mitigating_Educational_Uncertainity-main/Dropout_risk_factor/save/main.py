from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure session
app.secret_key = 'dev-key-123'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Simple risk assessment model (will be replaced with trained model)
def assess_risk(data):
    """Calculate dropout risk based on multiple factors."""
    # Convert grades from 0-10 scale to 0-100 scale for consistency
    grades = (data['grades'] / 10) * 100
    
    # Calculate weighted scores for each category
    # Academic Performance (25% weight)
    academic_score = (
        ((10 - data['grades']) * 4) +  # Convert GPA to risk (higher GPA = lower risk)
        ((100 - data['attendance']) * 0.2) + 
        ((100 - data['assignments']) * 0.2) +
        ((100 - data['exams']) * 0.2)
    )
    
    # Behavioral Indicators (15% weight)
    behavioral_score = (
        ((100 - data['participation']) * 0.3) +  # Lower participation = higher risk
        (data['absences'] * 5 * 0.3) +           # Scale 0-10 to 0-50
        (data['tardiness'] * 5 * 0.2) +          # Scale 0-10 to 0-50
        (data['behavioralIssues'] * 4 * 0.2)      # Scale 0-10 to 0-40
    )
    
    # Personal Factors (10% weight)
    personal_score = (
        (data['financialStress'] * 0.4) +
        ((data['workHours'] / 40 * 100) * 0.2) +  # Scale 0-40 to 0-100
        ((100 - data['familySupport']) * 0.2) +   # Lower support = higher risk
        ((100 - data['healthStatus']) * 0.2)      # Worse health = higher risk
    )
    
    # Institutional Factors (10% weight)
    institutional_score = (
        ((data['courseLoad'] / 24 * 100) * 0.3) +  # Higher course load = higher risk
        ((100 - data['majorFit']) * 0.4) +        # Lower fit = higher risk
        ((100 - min(data['facultyInteraction'] * 10, 100)) * 0.2) +  # Less interaction = higher risk
        ((100 - min(data['campusInvolvement'] * 5, 100)) * 0.1)      # Less involvement = higher risk
    )
    
    # Social Factors (8% weight)
    social_score = (
        ((100 - data['peerNetwork']) * 0.4) +  # Weaker network = higher risk
        ((100 - data['mentorship']) * 0.4) +   # Less mentorship = higher risk
        (data['bullying'] * 0.2)               # More bullying = higher risk
    )
    
    # External Factors (7% weight)
    external_score = (
        (min(data['commuteTime'] / 1.8, 100) * 0.4) +  # Longer commute = higher risk (max 3 hours = 100%)
        (min(data['familyResponsibilities'] * 2, 100) * 0.3) +  # More responsibilities = higher risk
        ((100 - data['workLifeBalance']) * 0.3)        # Worse balance = higher risk
    )
    
    # Psychological Factors (10% weight)
    psychological_score = (
        (100 - data['motivation']) * 0.4 +  # Lower motivation = higher risk
        (100 - data['selfEfficacy']) * 0.4 +  # Lower self-efficacy = higher risk
        data['stressLevel'] * 0.2  # Higher stress = higher risk
    )
    
    # Historical Data (8% weight)
    historical_score = (
        data['previousDropout'] * 0.4 +  # Previous dropout = higher risk
        data['gradeRetention'] * 0.4 +   # Grade retention = higher risk
        min(data['schoolChanges'] * 10, 100) * 0.2  # More school changes = higher risk (max 10 changes = 100%)
    )
    
    # Digital Footprint (5% weight)
    digital_score = (
        (100 - min(data['lmsActivity'] * 5, 100)) * 0.6 +  # Less LMS activity = higher risk
        (100 - data['onlineEngagement']) * 0.4  # Less online engagement = higher risk
    )
    
    # Early Warning Indicators (12% weight)
    warning_score = (
        data['warningSigns'] * 0.7 +  # More warning signs = higher risk
        data['earlyAlerts'] * 0.3     # More faculty concerns = higher risk
    )
    
    # Calculate total risk score (0-100)
    total_score = (
        (academic_score * 0.25) +
        (behavioral_score * 0.15) +
        (personal_score * 0.1) +
        (institutional_score * 0.1) +
        (social_score * 0.08) +
        (external_score * 0.07) +
        (psychological_score * 0.1) +
        (historical_score * 0.08) +
        (digital_score * 0.05) +
        (warning_score * 0.12)
    )
    risk_score = min(100, max(0, total_score))  # Ensure score is between 0-100
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = 'High Risk'
    elif risk_score >= 30:
        risk_level = 'Moderate Risk'
    else:
        risk_level = 'Low Risk'
    
    return {
        'risk_score': round(risk_score, 1),
        'risk_level': risk_level,
        'factors': {
            'academic': academic_score,
            'behavioral': behavioral_score,
            'personal': personal_score,
            'institutional': institutional_score,
            'social': social_score,
            'external': external_score,
            'psychological': psychological_score,
            'historical': historical_score,
            'digital': digital_score,
            'warning': warning_score,
            'details': {
                # Academic
                'grades': data['grades'],
                'attendance': data['attendance'],
                'assignments': data['assignments'],
                'exams': data['exams'],
                # Behavioral
                'participation': data['participation'],
                'absences': data['absences'],
                'tardiness': data['tardiness'],
                'behavioral_issues': data['behavioralIssues'],
                # Personal
                'financial_stress': data['financialStress'],
                'work_hours': data['workHours'],
                'family_support': data['familySupport'],
                'health_status': data['healthStatus'],
                # Institutional
                'course_load': data['courseLoad'],
                'major_fit': data['majorFit'],
                'faculty_interaction': data['facultyInteraction'],
                'campus_involvement': data['campusInvolvement'],
                # Social
                'peer_network': data['peerNetwork'],
                'mentorship': data['mentorship'],
                'bullying': data['bullying'],
                # External
                'commute_time': data['commuteTime'],
                'family_responsibilities': data['familyResponsibilities'],
                'work_life_balance': data['workLifeBalance'],
                # Psychological
                'motivation': data['motivation'],
                'self_efficacy': data['selfEfficacy'],
                'stress_level': data['stressLevel'],
                # Historical
                'previous_dropout': data['previousDropout'],
                'grade_retention': data['gradeRetention'],
                'school_changes': data['schoolChanges'],
                # Digital
                'lms_activity': data['lmsActivity'],
                'online_engagement': data['onlineEngagement'],
                # Early Warning
                'warning_signs': data['warningSigns'],
                'early_alerts': data['earlyAlerts']
            }
        }
    }

def generate_sample_trends(student_id):
    """Generate more realistic trend data based on the latest assessment with 6 months of historical data."""
    try:
        import random
        import numpy as np
        from datetime import datetime, timedelta
        
        # Get the latest assessment data from session
        assessment_data = session.get('last_assessment', {})
        
        if not assessment_data:
            return {
                'dates': ['No Data'],
                'grades': [0],
                'attendance': [0],
                'assignments': [0],
                'participation': [0],
                'message': 'Complete a risk assessment to see performance trends'
            }
        
        # Normalize and prepare current values
        current_values = {
            'grades': min(100, (assessment_data.get('grades', 5) / 10) * 100),
            'attendance': min(100, assessment_data.get('attendance', 75)),
            'assignments': min(100, assessment_data.get('assignments', 75)),
            'participation': min(100, assessment_data.get('participation', 65)),
            'exams': min(100, assessment_data.get('exams', 70)),
            'behavioral_issues': min(100, assessment_data.get('behavioralIssues', 0) * 10),
            'motivation': min(100, assessment_data.get('motivation', 70)),
            'self_efficacy': min(100, assessment_data.get('selfEfficacy', 70))
        }
        
        # Generate dates for the last 6 months (current month + 5 previous months)
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=30*(5-i))).strftime('%b %Y') for i in range(6)]
        
        # Function to generate realistic trend data
        def generate_trend(current, metric_name, is_positive=True, volatility=8):
            # Set baseline and target based on metric type
            if is_positive:
                # For positive metrics, start lower and trend up
                base = max(20, current * random.uniform(0.6, 0.9))  # Start between 60-90% of current
            else:
                # For negative metrics (like behavioral issues), start higher and trend down
                base = min(100, current * random.uniform(1.1, 1.5))
            
            # Generate smooth trend using cubic interpolation
            x = np.linspace(0, 1, 6)
            if is_positive:
                # S-curve for positive trends (start slow, accelerate, then slow down)
                y = [base + (current - base) * (x**0.7) for x in x]
            else:
                # Inverted S-curve for negative trends
                y = [base - (base - current) * (x**0.7) for x in x]
            
            # Add some random noise (less noise for more stable metrics like attendance)
            if metric_name in ['attendance', 'grades']:
                noise = np.random.normal(0, volatility/3, 6)
            else:
                noise = np.random.normal(0, volatility, 6)
            
            # Apply noise and ensure values are within bounds
            y = [max(0, min(100, y[i] + noise[i])) for i in range(6)]
            
            # Ensure the last value matches the current assessment
            y[-1] = current
            
            return [round(val, 1) for val in y]
        
        # Generate trends for each metric with appropriate parameters
        trends = {
            'dates': dates,
            'grades': generate_trend(current_values['grades'], 'grades', is_positive=True, volatility=5),
            'attendance': generate_trend(current_values['attendance'], 'attendance', is_positive=True, volatility=3),
            'assignments': generate_trend(current_values['assignments'], 'assignments', is_positive=True, volatility=7),
            'participation': generate_trend(current_values['participation'], 'participation', is_positive=True, volatility=8),
            'exams': generate_trend(current_values['exams'], 'exams', is_positive=True, volatility=6),
            'behavioral_issues': generate_trend(current_values['behavioral_issues'], 'behavioral_issues', is_positive=False, volatility=10),
            'motivation': generate_trend(current_values['motivation'], 'motivation', is_positive=True, volatility=9),
            'self_efficacy': generate_trend(current_values['self_efficacy'], 'self_efficacy', is_positive=True, volatility=7),
            'risk_score': assessment_data.get('risk_score', 0),
            'risk_level': assessment_data.get('risk_level', 'Not Assessed'),
            'current_values': current_values  # Include current values for reference
        }
        
        return trends
        
    except Exception as e:
        app.logger.error(f"Error in generate_sample_trends: {str(e)}")
        return {
            'dates': ['Error'],
            'grades': [0],
            'attendance': [0],
            'assignments': [0],
            'participation': [0],
            'error': str(e)
        }
    except Exception as e:
        app.logger.error(f"Error in generate_sample_trends: {str(e)}")
        # Return some fallback data if there's an error
        return {
            'dates': ['2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11'],
            'grades': [75, 78, 82, 80, 85, 88],
            'attendance': [85, 82, 88, 90, 92, 95],
            'assignments': [80, 82, 78, 85, 88, 90],
            'participation': [70, 72, 75, 78, 82, 85]
        }

def get_category_progress(student_data):
    """Calculate progress for each category."""
    if not student_data:
        return {}
        
    return {
        'academic': {
            'score': student_data.get('grades', 0) * 0.4 + 
                    student_data.get('assignments', 0) * 0.3 +
                    student_data.get('exams', 0) * 0.3,
            'target': 85
        },
        'behavioral': {
            'score': 100 - (
                (100 - student_data.get('participation', 0)) * 0.4 +
                student_data.get('absences', 0) * 0.3 +
                student_data.get('tardiness', 0) * 0.2 +
                student_data.get('behavioralIssues', 0) * 0.1
            ),
            'target': 80
        },
        'personal': {
            'score': (
                (100 - student_data.get('financialStress', 0)) * 0.4 +
                (100 - min(student_data.get('workHours', 0) * 2.5, 100)) * 0.2 +
                student_data.get('familySupport', 0) * 0.2 +
                student_data.get('healthStatus', 0) * 0.2
            ),
            'target': 75
        },
        'institutional': {
            'score': (
                (100 - min(student_data.get('courseLoad', 0) * 4.17, 100)) * 0.3 +
                student_data.get('majorFit', 0) * 0.4 +
                student_data.get('facultyInteraction', 0) * 10 * 0.2 +
                student_data.get('campusInvolvement', 0) * 20 * 0.1
            ),
            'target': 70
        },
        'social': {
            'score': (
                student_data.get('peerNetwork', 0) * 0.4 +
                student_data.get('mentorship', 0) * 0.4 +
                (100 - student_data.get('bullying', 0)) * 0.2
            ),
            'target': 80
        },
        'external': {
            'score': (
                (100 - min(student_data.get('commuteTime', 0) / 1.8, 100)) * 0.4 +
                (100 - min(student_data.get('familyResponsibilities', 0) * 2, 100)) * 0.3 +
                student_data.get('workLifeBalance', 0) * 0.3
            ),
            'target': 75
        },
        'psychological': {
            'score': (
                student_data.get('motivation', 0) * 0.4 +
                student_data.get('selfEfficacy', 0) * 0.4 +
                (100 - student_data.get('stressLevel', 0)) * 0.2
            ),
            'target': 80
        },
        'historical': {
            'score': 100 - (
                student_data.get('previousDropout', 0) * 0.4 +
                student_data.get('gradeRetention', 0) * 0.4 +
                min(student_data.get('schoolChanges', 0) * 10, 100) * 0.2
            ),
            'target': 90
        },
        'digital': {
            'score': (
                min(student_data.get('lmsActivity', 0) * 5, 100) * 0.6 +
                student_data.get('onlineEngagement', 0) * 0.4
            ),
            'target': 70
        },
        'warning': {
            'score': 100 - (
                student_data.get('warningSigns', 0) * 0.7 +
                student_data.get('earlyAlerts', 0) * 0.3
            ),
            'target': 90
        }
    }

@app.route('/')
def home():
    """Render the home page with default tab."""
    return redirect(url_for('dashboard', tab='risk-assessment'))

@app.route('/dashboard/<tab>')
def dashboard(tab='risk-assessment'):
    """Render the dashboard with the specified tab active."""
    return render_template('index.html', active_tab=tab)

@app.route('/api/trends/<student_id>')
def get_trends(student_id):
    """API endpoint to get trend data for a student."""
    try:
        # In a real app, this would fetch from a database
        data = generate_sample_trends(student_id)
        response = jsonify(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        app.logger.error(f"Error in get_trends: {str(e)}")
        return jsonify({"error": "Failed to load trends data"}), 500

@app.route('/api/progress')
def get_progress():
    """API endpoint to get category progress."""
    try:
        print("Session data:", dict(session))  # Debug: Print session data
        student_data = session.get('last_assessment', {})
        print("Student data from session:", student_data)  # Debug: Print student data
        progress = get_category_progress(student_data)
        print("Generated progress data:", progress)  # Debug: Print progress data
        return jsonify(progress)
    except Exception as e:
        print(f"Error in get_progress: {str(e)}")  # Debug: Print any errors
        return jsonify({"error": str(e)})

@app.route('/api/assess', methods=['POST'])
def assess_risk_api():
    """API endpoint for risk assessment."""
    try:
        data = request.get_json()
        print("Received assessment data:", data)  # Debug: Print received data
        
        # Validate required fields
        required_fields = [
            'grades', 'attendance', 'assignments', 'exams',
            'participation', 'absences', 'tardiness', 'behavioralIssues',
            'financialStress', 'workHours', 'familySupport', 'healthStatus',
            'courseLoad', 'majorFit', 'facultyInteraction', 'campusInvolvement',
            'peerNetwork', 'mentorship', 'bullying', 'commuteTime',
            'familyResponsibilities', 'workLifeBalance', 'motivation',
            'selfEfficacy', 'stressLevel', 'previousDropout', 'gradeRetention',
            'schoolChanges', 'lmsActivity', 'onlineEngagement', 'warningSigns',
            'earlyAlerts'
        ]
        
        # Set default values for missing fields and ensure they're numbers
        processed_data = {}
        for field in required_fields:
            value = data.get(field, 0.0)
            try:
                processed_data[field] = float(value) if value is not None and value != '' else 0.0
            except (ValueError, TypeError):
                processed_data[field] = 0.0
        
        # Calculate risk
        result = assess_risk(processed_data)
        
        # Store the assessment in session
        session['last_assessment'] = processed_data
        session.permanent = True
        session.modified = True
        
        # Calculate category progress
        progress = get_category_progress(processed_data)
        
        # Add progress data to the response
        result['progress'] = progress
        
        # Debug output
        print("Assessment result:", result)
        print("Session data after save:", dict(session))
        
        return jsonify({
            'success': True,
            'risk_score': result['risk_score'],
            'risk_level': result['risk_level'],
            'progress': progress,
            'factors': result.get('factors', {})
        })
        
    except Exception as e:
        app.logger.error(f'Error in assess_risk_api: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'details': str(e) if app.debug else None
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    
    # Run the app
    app.logger.info('Starting Dropout Risk Predictor application')
    app.run(debug=True, port=5000, host='0.0.0.0')
