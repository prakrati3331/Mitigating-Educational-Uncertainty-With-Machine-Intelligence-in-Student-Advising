from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import pandas as pd
import numpy as np
import pickle
import json
import os
import traceback
from sklearn.metrics.pairwise import cosine_similarity
from functools import wraps
from flask_cors import CORS
import logging

# Subject organization for Vocational
SUBJECT_CATEGORIES = {
    'core': {
        'title': '🎨 Core Creative Subjects',
        'subjects': [
            'Fine Arts', 'Creativity', 'Communication', 'Empathy', 'English'
        ],
        'icon': 'palette',
        'description': 'Fundamental creative and communication skills for vocational careers'
    },
    'academic': {
        'title': '📚 Academic Subjects',
        'subjects': [
            'Sociology', 'Memory', 'Computer Science', 'Mathematics', 'Statistics',
            'Accountancy', 'Business Studies', 'Economics', 'Psychology', 'Hindi',
            'Geography', 'Biology', 'Chemistry'
        ],
        'icon': 'book',
        'description': 'Academic knowledge that supports vocational training and practice'
    },
    'aptitude': {
        'title': '🧠 Aptitudes & Skills',
        'subjects': [
            'Logical Reasoning', 'Critical Thinking', 'Numerical Aptitude'
        ],
        'icon': 'brain',
        'description': 'Essential cognitive skills for vocational success and problem-solving'
    }
}

class VocationalCourseRecommender:
    def __init__(self):
        # Load the pre-trained models and data
        self.scaler = self._load_pickle("vocational_scaler.pkl")
        self.clf = self._load_pickle("vocational_course_classifier.pkl")
        self.le_course = self._load_pickle("vocational_label_encoder.pkl")
        self.feature_columns = [
            'Fine Arts', 'Creativity', 'Communication', 'Empathy', 'English',
            'Sociology', 'Memory', 'Computer Science', 'Mathematics', 'Statistics',
            'Accountancy', 'Business Studies', 'Economics', 'Psychology', 'Hindi',
            'Geography', 'Biology', 'Chemistry', 'Logical Reasoning', 'Critical Thinking',
            'Numerical Aptitude'
        ]
        self.df = self._load_pickle("vocational_dataset.pkl")

        # Ensure the dataset has all required columns
        for col in self.feature_columns:
            if col not in self.df.columns:
                self.df[col] = 0  # Initialize missing columns with 0

        print("Vocational models loaded successfully!")

    def _load_pickle(self, filename):
        """Helper to load pickle files"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, filename), "rb") as f:
            return pickle.load(f)

    def recommend_courses(self, user_profile, top_n=5):
        """Recommend courses based on user profile"""
        try:
            # Ensure user_profile is a list with the correct number of features
            if len(user_profile) != len(self.feature_columns):
                raise ValueError(f"Expected {len(self.feature_columns)} features, got {len(user_profile)}")

            # Create a DataFrame with proper feature names for scaling
            user_df = pd.DataFrame([user_profile], columns=self.feature_columns)

            # Convert all values to numeric, handling any potential non-numeric values
            for col in self.feature_columns:
                user_df[col] = pd.to_numeric(user_df[col], errors='coerce').fillna(0)

            # Scale user input
            user_scaled = self.scaler.transform(user_df[self.feature_columns])

            # Scale the dataset for comparison
            X = self.df[self.feature_columns].copy()
            for col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
            X_scaled = self.scaler.transform(X)

            # Calculate similarity with all courses
            sims = cosine_similarity(user_scaled, X_scaled)[0]

            # Add similarity scores to dataframe
            df_temp = self.df.copy()
            df_temp["similarity"] = sims

            # Group by course and get mean similarity
            course_scores = df_temp.groupby("Course")["similarity"].mean().reset_index()

            # Get top N courses
            top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)

            # Add career options for each course
            recommendations = []
            for _, row in top_courses.iterrows():
                course = row["Course"]
                sim = row["similarity"]

                # Get all career options for this course
                careers = df_temp[df_temp["Course"] == course]["Career Options"].unique()

                recommendations.append({
                    "Course": course,
                    "Similarity": round(sim, 3),
                    "Career Options": ", ".join(careers)
                })

            return pd.DataFrame(recommendations)
        except Exception as e:
            print(f"Error in recommend_courses: {str(e)}")
            # Return empty dataframe with expected columns
            empty_df = pd.DataFrame(columns=["Course", "Similarity", "Career Options"])
            print("Returning empty recommendations due to error")
            return empty_df

    def predict_course(self, user_profile):
        """Predict the best fit course for the user"""
        try:
            # Create a DataFrame with proper feature names for prediction
            user_df = pd.DataFrame([user_profile], columns=self.feature_columns)
            user_scaled = self.scaler.transform(user_df)
            pred = self.clf.predict(user_scaled)
            course = self.le_course.inverse_transform(pred)[0]
            return course
        except Exception as e:
            print(f"Error in predict_course: {str(e)}")
            return "Unknown"

    def get_features_by_category(self):
        """Get features organized by category"""
        all_features = list(self.feature_columns) if self.feature_columns else []

        categories = {}
        for cat_id, cat_data in SUBJECT_CATEGORIES.items():
            valid_subjects = [s for s in cat_data['subjects'] if s in all_features]
            if valid_subjects:
                categories[cat_id] = {
                    'title': cat_data['title'],
                    'subjects': valid_subjects,
                    'icon': cat_data['icon']
                }

        return categories

# Initialize the recommender instance
recommender = VocationalCourseRecommender()

# Get the directory where this script is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app with template folder path
app = Flask(__name__)
# Configure CORS to allow requests from FastAPI frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5006"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Routes
@app.route('/')
def index():
    return render_template('vocational_recommendation.html')

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def get_recommendations():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5006')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        logger.info("Received recommendation request")
        
        # Log raw request data
        raw_data = request.get_data()
        logger.debug(f"Raw request data: {raw_data}")
        
        data = request.get_json()
        logger.debug(f"Parsed JSON data: {data}")
        
        if not data:
            error_msg = 'No JSON data received in request'
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
            
        if 'user_profile' not in data:
            error_msg = f"Missing 'user_profile' in request data. Received keys: {list(data.keys())}"
            logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'received_data': data
            }), 400
            
        user_profile = data.get('user_profile', {})
        logger.debug(f"User profile: {user_profile}")
        
        # Log feature columns for debugging
        logger.debug(f"Expected feature columns: {recommender.feature_columns}")
        logger.debug(f"Received profile keys: {list(user_profile.keys())}")
        
        # Check for missing features
        missing_features = [f for f in recommender.feature_columns if f not in user_profile]
        if missing_features:
            logger.warning(f"Missing features in profile, using default value (50): {missing_features}")
        
        # Convert to list in the correct order with default value 50 for missing features
        user_input = [user_profile.get(feature, 50) for feature in recommender.feature_columns]
        
        logger.debug(f"Processed user input (first 5): {user_input[:5]}...")
        
        try:
            # Get recommendations
            recommendations = recommender.recommend_courses(user_input)
            logger.debug(f"Recommendations type: {type(recommendations)}")
            logger.debug(f"Recommendations sample: {recommendations[:2] if hasattr(recommendations, '__getitem__') else recommendations}")
            
            # Convert numpy types to native Python types for JSON serialization
            if hasattr(recommendations, 'to_dict'):
                recommendations = recommendations.to_dict(orient='records')
            elif hasattr(recommendations, 'tolist'):
                recommendations = recommendations.tolist()
            
            logger.debug(f"Serialized recommendations: {recommendations[:2] if isinstance(recommendations, list) else recommendations}")
            
            response_data = {
                'status': 'success',
                'recommendations': recommendations
            }
            
            response = jsonify(response_data)
            
        except Exception as e:
            error_msg = f"Error generating recommendations: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response = jsonify({
                'status': 'error',
                'message': error_msg,
                'error_type': type(e).__name__
            })
            response.status_code = 500
        
        # Set CORS headers for the response
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5006')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        response = jsonify({
            'status': 'error',
            'message': error_msg,
            'error_type': type(e).__name__
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5006')
        return response

# Run the app
# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting Flask server...")
    print(f"Templates directory: {os.path.join(basedir, 'templates')}")
    print(f"Static directory: {os.path.join(basedir, 'static')}")
    
    app.run(host='0.0.0.0', port=5005, debug=True)
