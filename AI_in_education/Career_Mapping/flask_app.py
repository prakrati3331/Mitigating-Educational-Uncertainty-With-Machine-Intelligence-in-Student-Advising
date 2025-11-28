import json
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
import logging
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from the data package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.career_data import CAREER_DATA
from database.db import get_db

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection will be handled per-request

def get_db_connection():
    """Get a database connection"""
    if 'db' not in g:
        g.db = get_db()
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    """Close the database connection when the app context is torn down"""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.client.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Career data is imported from data.career_data

@app.route('/')
def home():
    """Serve the main career assessment page"""
    return render_template('career_path_assessment.html')

@app.route('/guidance', methods=['GET', 'POST'])
def guidance():
    """Serve the career guidance page with assessment data"""
    # Get the latest assessment data from the database
    try:
        db = get_db_connection()
        latest_assessment = db.db.assessments.find_one(
            {},
            sort=[('_id', -1)]  # Get the most recent assessment
        )
        
        if latest_assessment:
            # Create a new dictionary to avoid modifying the original
            assessment_data = dict(latest_assessment)
            # Convert ObjectId to string for JSON serialization
            assessment_data['_id'] = str(assessment_data['_id'])
            # Convert datetime to string
            assessment_data['created_at'] = assessment_data['created_at'].isoformat()
            if 'updated_at' in assessment_data:
                assessment_data['updated_at'] = assessment_data['updated_at'].isoformat()
            
            logger.info(f"Found assessment data for guidance page: {assessment_data['_id']}")
            return render_template('career_guidance.html', assessment_data=json.dumps(assessment_data) if assessment_data else 'null')
        else:
            logger.warning("No assessment data found in the database")
            return render_template('career_guidance.html', assessment_data='null')
            
    except Exception as e:
        logger.error(f"Error retrieving assessment data: {str(e)}", exc_info=True)
        return render_template('career_guidance.html', assessment_data='null', error="Error loading assessment data")

@app.route('/api/career-assessment', methods=['POST'])
def process_assessment():
    """Process career assessment data, save to database, and return recommendations"""
    try:
        data = request.get_json()
        logger.info(f"Received assessment data: {data}")

        # Extract user ID (if available) and IP address
        user_id = data.get('user_id')
        ip_address = request.remote_addr

        # Extract scores and stream
        stream = data.get('stream', 'Vocational')  # Default to 'Vocational' if not specified
        scores = {
            'math': float(data.get('math', 0)),
            'science': float(data.get('science', 0)),
            'english': float(data.get('english', 0)),
            'social': float(data.get('social', 0)),
            'language': float(data.get('language', 0)),
            'artistic': float(data.get('artistic', 0)),
            'biology': float(data.get('biology', 0)),
            'logical': float(data.get('logical', 0)),
            'analytical': float(data.get('analytical', 0)),
            'numerical': float(data.get('numerical', 0)),
            'creativity': float(data.get('creativity', 0)),
            'communication': float(data.get('communication', 0)),
            'practical': float(data.get('practical', 0))
        }

        logger.info(f"Processing assessment for stream: {stream}")

        # Get career recommendations for the selected stream
        careers = CAREER_DATA.get(stream, [])
        logger.info(f"Found {len(careers)} careers for stream {stream}")

        # Calculate compatibility scores for each career
        career_recommendations = []
        for career in careers:
            compatibility_score = calculate_career_compatibility(career, scores)
            career_recommendations.append({
                'title': career['title'],
                'type': career['type'],
                'compatibility_score': round(compatibility_score, 2),
                'skills': career['skills'],
                'courses': career['courses'],
                'exams': career['exams']
            })

        # Sort by compatibility score (highest first)
        career_recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        # Prepare assessment document
        assessment_doc = {
            'user_id': user_id,
            'ip_address': ip_address,
            'stream': stream,
            'scores': scores,
            'recommendations': career_recommendations[:5],  # Save top 5 recommendations
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Save to database
        try:
            db = get_db_connection()
            result = db.db.assessments.insert_one(assessment_doc)
            assessment_doc['_id'] = str(result.inserted_id)
            logger.info(f"Assessment saved with ID: {result.inserted_id}")
        except Exception as db_error:
            logger.error(f"Error saving assessment to database: {db_error}")
            # Continue even if database save fails

        # Prepare response
        response_data = {
            'status': 'success',
            'assessment_id': str(assessment_doc.get('_id', '')),
            'stream': stream,
            'scores': {k: float(v) for k, v in scores.items()},
            'recommendations': career_recommendations,
            'timestamp': assessment_doc['created_at'].isoformat()
        }

        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error processing assessment: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your assessment',
            'error': str(e)
        }), 500

def calculate_career_compatibility(career, scores):
    """Calculate how well a career matches the user's scores"""
    compatibility = 0

    # Map skills to relevant scores
    skill_score_mapping = {
        'Mathematics': scores.get('math', 0),
        'Science': scores.get('science', 0),
        'English': scores.get('english', 0),
        'Biology Knowledge': scores.get('biology', 0),
        'Analytical Thinking': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,
        'Communication': scores.get('communication', 0),
        'Problem Solving': (scores.get('logical', 0) + scores.get('analytical', 0)) / 2,
        'Programming': scores.get('numerical', 0),
        'Creativity': scores.get('creativity', 0),
        'Research': (scores.get('analytical', 0) + scores.get('science', 0)) / 2,
        'Statistics': (scores.get('math', 0) + scores.get('analytical', 0)) / 2,
        'Data Analysis': scores.get('analytical', 0),
        'Critical Thinking': scores.get('logical', 0),
        'Accounting': scores.get('numerical', 0),
        'Financial Analysis': (scores.get('analytical', 0) + scores.get('numerical', 0)) / 2,
        'Business Acumen': (scores.get('social', 0) + scores.get('communication', 0)) / 2,
        'Taxation': scores.get('numerical', 0),
        'Financial Modeling': (scores.get('math', 0) + scores.get('analytical', 0)) / 2,
        'Valuation': scores.get('analytical', 0),
        'Negotiation': scores.get('communication', 0),
        'Market Analysis': (scores.get('analytical', 0) + scores.get('social', 0)) / 2,
        'Writing': scores.get('english', 0),
        'Interviewing': scores.get('communication', 0),
        'Legal Research': (scores.get('analytical', 0) + scores.get('english', 0)) / 2,
        'Argumentation': (scores.get('logical', 0) + scores.get('communication', 0)) / 2,
        'Empathy': scores.get('social', 0),
        'Active Listening': scores.get('communication', 0),
        'Subject Knowledge': (scores.get('english', 0) + scores.get('social', 0)) / 2,
        'Patience': scores.get('communication', 0),
        'Medical Knowledge': (scores.get('biology', 0) + scores.get('science', 0)) / 2,
        'Patient Care': scores.get('communication', 0),
        'Diagnostic Skills': (scores.get('analytical', 0) + scores.get('science', 0)) / 2,
        'Molecular Biology': scores.get('biology', 0),
        'Genetic Engineering': scores.get('biology', 0),
        'Pharmacology': (scores.get('biology', 0) + scores.get('science', 0)) / 2,
        'Chemistry': scores.get('science', 0),
        'Patient Counseling': scores.get('communication', 0),
        'Nutrition Science': (scores.get('biology', 0) + scores.get('science', 0)) / 2,
        'Diet Planning': (scores.get('analytical', 0) + scores.get('practical', 0)) / 2,
        'Design': (scores.get('creativity', 0) + scores.get('practical', 0)) / 2,
        'Financial Mathematics': (scores.get('math', 0) + scores.get('numerical', 0)) / 2,
        'Risk Management': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,
        # Missing skills from career data
        'Attention to Detail': scores.get('analytical', 0),
        'Logic': scores.get('logical', 0),
        'Leadership': (scores.get('communication', 0) + scores.get('social', 0)) / 2,
        'Conflict Resolution': scores.get('communication', 0),
        'Strategic Planning': scores.get('analytical', 0),
        # Commerce-specific skills
        'Excel': scores.get('numerical', 0),  # Excel is a numerical skill
        'Recruitment': (scores.get('communication', 0) + scores.get('social', 0)) / 2,  # Recruitment involves communication and social skills
        'Employee Relations': scores.get('communication', 0),  # Map to communication
        'Labor Laws': scores.get('analytical', 0),  # Understanding laws requires analytical skills
        'Supply Chain Management': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,  # Requires planning and analysis
        'Inventory Control': scores.get('analytical', 0),  # Managing inventory requires analytical skills
        'Logistics': (scores.get('analytical', 0) + scores.get('practical', 0)) / 2,  # Logistics requires both planning and practical skills
        'Brand Management': (scores.get('creativity', 0) + scores.get('communication', 0)) / 2,  # Brand management involves creativity and communication
        'Digital Marketing': (scores.get('creativity', 0) + scores.get('communication', 0)) / 2,  # Digital marketing involves creativity and communication
        'Market Research': (scores.get('analytical', 0) + scores.get('social', 0)) / 2,  # Market research involves analysis and social understanding
        'Scientific Method': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,  # Scientific method involves analysis and logic
        'Laboratory Skills': (scores.get('practical', 0) + scores.get('science', 0)) / 2,  # Lab skills involve practical work and science knowledge
        'Technical Drawing': (scores.get('practical', 0) + scores.get('creativity', 0)) / 2,  # Technical drawing involves practical skills and creativity
        'Machine Learning': scores.get('analytical', 0),  # ML is analytical
        'Data Visualization': (scores.get('analytical', 0) + scores.get('creativity', 0)) / 2,  # Data viz involves analysis and creativity
        'Environmental Science': scores.get('science', 0),  # Environmental science is science
        'Policy Analysis': (scores.get('analytical', 0) + scores.get('social', 0)) / 2,  # Policy analysis involves analysis and social understanding
        'Field Work': (scores.get('practical', 0) + scores.get('science', 0)) / 2,  # Field work involves practical work and science
        'Design Software': (scores.get('creativity', 0) + scores.get('practical', 0)) / 2,  # Design software involves creativity and practical skills
        'Color Theory': scores.get('creativity', 0),  # Color theory is creative
        'Typography': scores.get('creativity', 0),  # Typography is creative
        'Aerodynamics': scores.get('science', 0),  # Aerodynamics is science/physics
        'Thermodynamics': scores.get('science', 0),  # Thermodynamics is science/physics
        'Physics': scores.get('science', 0),  # Physics is science
    }

    # Calculate compatibility score
    total_possible = 0
    total_achieved = 0

    for skill in career['skills']:
        if skill in skill_score_mapping:
            total_possible += 10  # Max score per skill
            total_achieved += skill_score_mapping[skill]
        else:
            logger.warning(f"Skill '{skill}' not found in mapping for career '{career['title']}'")

    if total_possible > 0:
        compatibility = (total_achieved / total_possible) * 100
    else: 
        # If no skills match, use average of all scores as a fallback
        avg_score = sum(scores.values()) / len(scores) if scores else 50
        compatibility = avg_score * 10  # Scale to 0-100 range
        logger.warning(f"No matching skills found for career '{career['title']}', using average score: {compatibility}")

    return round(compatibility, 1)

@app.route('/api/career-data/<stream>')
def get_career_data(stream):
    """Get career data for a specific stream"""
    if stream in CAREER_DATA:
        return jsonify(CAREER_DATA[stream])
    return jsonify({'error': 'Stream not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
