from flask import Flask, render_template, request, jsonify, send_from_directory
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
from functools import wraps
import time

# Subject organization
SUBJECT_CATEGORIES = {
    'core': {
        'title': '📘 Core Subjects',
        'subjects': [
            'Physics', 'Chemistry', 'Biology', 
            'Mathematics', 'English', 'Hindi'
        ],
        'icon': 'atom',
        'description': 'Fundamental subjects that form the core of the PCB stream'
    },
    'elective': {
        'title': '📙 Elective Subjects',
        'subjects': [
            'Psychology', 'Computer Science', 'Research Skills'
        ],
        'icon': 'flask',
        'description': 'Complementary subjects that enhance your scientific knowledge'
    },
    'aptitude': {
        'title': '🎯 Aptitudes & Skills',
        'subjects': [
            'Logical Reasoning', 'Analytical Thinking', 'Critical Thinking',
            'Problem-Solving', 'Communication', 'Creativity',
            'Numerical Aptitude', 'Empathy', 'Attention to Detail'
        ],
        'icon': 'brain',
        'description': 'Essential skills for success in scientific careers'
    }
}

class PCBCourseRecommender:
    def __init__(self):
        # Load the pre-trained models and data
        self.scaler = self._load_pickle("pcb_scaler.pkl")
        self.clf = self._load_pickle("pcb_course_classifier.pkl")
        self.le_course = self._load_pickle("pcb_label_encoder.pkl")
        self.feature_columns = self._load_pickle("pcb_feature_columns.pkl")
        self.df = self._load_pickle("pcb_dataset.pkl")
        print("All model files loaded successfully!")
        print(f"Feature columns: {self.feature_columns}")
        print(f"Dataset columns: {self.df.columns.tolist()}")
        print(f"Sample career options: {self.df['Career Option'].head().tolist()}")

    def _load_pickle(self, filename):
        """Helper to load pickle files"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, filename), "rb") as f:
            return pickle.load(f)

    def recommend_courses(self, user_profile, top_n=5):
        """
        Recommend courses based on user profile
        """
        try:
            # Convert user profile to list if it's a dictionary
            if isinstance(user_profile, dict):
                user_profile = [user_profile.get(feature, 50) for feature in self.feature_columns]

            # Ensure we have the right number of features
            if len(user_profile) != len(self.feature_columns):
                raise ValueError(f"Expected {len(self.feature_columns)} features, got {len(user_profile)}")

            # Scale the input
            user_scaled = self.scaler.transform([user_profile])

            # Calculate similarity with all courses
            sims = cosine_similarity(user_scaled, self.scaler.transform(self.df[self.feature_columns]))[0]
            df_temp = self.df.copy()
            df_temp["similarity"] = sims

            # Aggregate similarity per course
            course_scores = df_temp.groupby("Course")["similarity"].mean().reset_index()
            top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)

            recommendations = []
            for _, row in top_courses.iterrows():
                course = row["Course"]
                sim = row["similarity"]

                # Get career options (handle different column names)
                career_col = next((col for col in ['Career Option', 'Career_Options', 'CareerOptions', 'Career']
                                 if col in df_temp.columns), None)

                if career_col is None:
                    careers = ["Various careers in this field"]
                else:
                    career_data = df_temp[df_temp["Course"] == course][career_col].iloc[0]
                    if pd.isna(career_data):
                        careers = ["Various careers in this field"]
                    elif isinstance(career_data, str):
                        careers = [c.strip() for c in career_data.split(',')]
                    elif isinstance(career_data, (list, np.ndarray)):
                        careers = list(career_data)
                    else:
                        careers = [str(career_data)]

                # Find top contributing skills (most aligned with user's strengths)
                course_avg = df_temp[df_temp["Course"] == course][self.feature_columns].mean().values
                diffs = np.array(user_profile) - course_avg
                top_features_idx = diffs.argsort()[::-1][:3]  # Top 3 strengths
                top_features = [self.feature_columns[i] for i in top_features_idx if i < len(self.feature_columns)]

                recommendations.append({
                    "Course": str(course),
                    "Similarity": float(round(sim, 3)),
                    "Career Options": ", ".join(careers[:3]) if careers else "Various career options available",
                    "Top Supporting Skills": ", ".join(top_features) if top_features else "Various skills"
                })

            return recommendations

        except Exception as e:
            import traceback
            print(f"Error in recommend_courses: {str(e)}")
            print(traceback.format_exc())
            return []

# Initialize the recommender instance
recommender = PCBCourseRecommender()

app = Flask(__name__)

@app.route('/Dataset/pcb_dataset/templates/pcb_recommendation.html')
def redirect_old_template():
    """Redirect old template URL to main page"""
    return render_template('pcb_recommendation.html', categories=SUBJECT_CATEGORIES)

@app.route('/')
def home():
    """Render the main page with subject sliders"""
    # Check for any missing features in the dataset
    all_subjects = []
    for category in SUBJECT_CATEGORIES.values():
        all_subjects.extend(category['subjects'])
    
    missing_features = [subj for subj in all_subjects if subj not in recommender.feature_columns]
    if missing_features:
        print(f"Warning: The following subjects are not in the feature columns: {missing_features}")
    
    return render_template(
        'pcb_recommendation.html',
        categories=SUBJECT_CATEGORIES,
        all_subjects=all_subjects,
        missing_features=missing_features
    )

@app.route('/get_features', methods=['GET'])
def get_features():
    """Return the list of all features in order"""
    return jsonify({
        'features': recommender.feature_columns,
        'subjects': [subj for cat in SUBJECT_CATEGORIES.values() for subj in cat['subjects']]
    })

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Handle recommendation requests"""
    try:
        data = request.get_json()
        if not data or 'scores' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No scores provided'
            }), 400
        
        # Convert scores to list in the correct order
        scores = data['scores']
        if isinstance(scores, dict):
            # Ensure all required features are present
            for feature in recommender.feature_columns:
                if feature not in scores:
                    scores[feature] = 50  # Default value
            # Convert to list in correct order
            scores = [scores[feature] for feature in recommender.feature_columns]
        
        print(f"Getting recommendations for scores: {scores}")
        
        # Get recommendations
        recommendations = recommender.recommend_courses(scores)
        
        print(f"Generated {len(recommendations)} recommendations")
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f"An error occurred: {str(e)}"
        }), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"success": False, "error": "No input data provided"}), 400
        
        # Create a list of values in the same order as feature_columns
        user_input = []
        for feature in recommender.feature_columns:
            value = data.get(feature, 0)
            # Ensure the value is within 0-100 range
            value = max(0, min(100, int(value)))
            user_input.append(value)
        
        # Get recommendations
        recommendations = recommender.recommend_courses(user_input)
        
        if not recommendations:
            return jsonify({
                "success": False, 
                "error": "No recommendations could be generated"
            }), 400
            
        return jsonify({
            "success": True, 
            "recommendations": recommendations,
            "timestamp": time.time()
        })
        
    except Exception as e:
        print(f"Error in recommend endpoint: {str(e)}")
        return jsonify({
            "success": False, 
            "error": f"An error occurred: {str(e)}"
        }), 500

# Error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

# Error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Print server info
    print("\n" + "="*50)
    print("PCB Course & Career Recommendation System")
    print("="*50)
    print(f"Loaded {len(recommender.df)} courses with {len(recommender.feature_columns)} features")
    print(f"Available courses: {len(recommender.df['Course'].unique())}")
    print("\nStarting server... (Press Ctrl+C to stop)")
    print("="*50 + "\n")
    
    # Run the app
    app.run(debug=True, port=5002, threaded=True)