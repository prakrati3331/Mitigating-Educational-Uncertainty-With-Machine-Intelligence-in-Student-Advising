from flask import Flask, render_template, request, jsonify, send_from_directory
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# Subject organization
SUBJECT_CATEGORIES = {
    'core': {
        'title': '📘 Core Subjects',
        'subjects': [
            'Accountancy', 'Business Studies', 'Economics',
            'Mathematics', 'English', 'Hindi'
        ],
        'icon': 'book-open'
    },
    'elective': {
        'title': '📙 Elective Subjects',
        'subjects': [
            'Statistics', 'Computer Science', 'Psychology', 'Sociology'
        ],
        'icon': 'book'
    },
    'aptitude': {
        'title': '🎯 Aptitudes & Skills',
        'subjects': [
            'Logical Reasoning', 'Numerical Aptitude', 'Critical Thinking',
            'Empathy', 'Memory', 'Communication', 'Creativity'
        ],
        'icon': 'brain'
    }
}

class CommerceCourseRecommender:
    """Class to handle all commerce course recommendation functionality"""

    def __init__(self):
        # Load the pre-trained models and data
        self.scaler = None
        self.clf = None
        self.le_course = None
        self.feature_columns = None
        self.df = None
        self._load_models()

    def _load_models(self):
        """Load the ML models and encoders"""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))

            with open(os.path.join(script_dir, "commerce_scaler.pkl"), "rb") as f:
                self.scaler = pickle.load(f)
            with open(os.path.join(script_dir, "commerce_course_classifier.pkl"), "rb") as f:
                self.clf = pickle.load(f)
            with open(os.path.join(script_dir, "commerce_label_encoder.pkl"), "rb") as f:
                self.le_course = pickle.load(f)
            with open(os.path.join(script_dir, "commerce_feature_columns.pkl"), "rb") as f:
                self.feature_columns = pickle.load(f)
            with open(os.path.join(script_dir, "commerce_dataset.pkl"), "rb") as f:
                self.df = pickle.load(f)
            print("Commerce models loaded successfully!")
        except Exception as e:
            print(f"Error loading commerce models: {str(e)}")
            raise

    def recommend_courses(self, user_profile, top_n=5):
        """
        Recommend courses based on user profile
        """
        try:
            # Ensure user_profile is in the correct order matching feature_columns
            if isinstance(user_profile, dict):
                # If user_profile is a dict, convert to list in correct order
                user_profile = [user_profile.get(feature, 50) for feature in self.feature_columns]

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

                # Get career options (handle both string and list types)
                career_data = df_temp[df_temp["Course"] == course]["Career Options"].iloc[0]
                if isinstance(career_data, str):
                    careers = [c.strip() for c in career_data.split(',')]
                elif isinstance(career_data, (list, np.ndarray)):
                    careers = list(career_data)
                else:
                    careers = [str(career_data)]

                # Find top contributing skills
                course_avg = df_temp[df_temp["Course"] == course][self.feature_columns].mean().values
                diff = np.abs(np.array(user_profile) - course_avg)
                top_features_idx = diff.argsort()[:3]  # 3 most aligned skills
                top_features = [self.feature_columns[i] for i in top_features_idx if i < len(self.feature_columns)]

                recommendations.append({
                    "course": course,
                    "similarity": round(float(sim), 3),
                    "career_options": careers,
                    "top_skills": top_features
                })

            return {"status": "success", "recommendations": recommendations}

        except Exception as e:
            import traceback
            print(f"Error in recommend_courses: {str(e)}")
            print(traceback.format_exc())
            return {"status": "error", "message": str(e)}

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
commerce_recommender = CommerceCourseRecommender()

app = Flask(__name__)

@app.route('/')
def home():
    # Get features organized by category
    categories = commerce_recommender.get_features_by_category()
    return render_template('commerce_course_recommendation_.html', categories=categories)

@app.route('/api/features', methods=['GET'])
def get_features():
    """Get the list of feature columns organized by category"""
    categories = commerce_recommender.get_features_by_category()
    return jsonify({
        "status": "success",
        "categories": categories
    })

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """API endpoint for getting commerce course recommendations"""
    try:
        data = request.get_json()
        user_profile = [data.get(feature, 50) for feature in commerce_recommender.feature_columns]
        result = commerce_recommender.recommend_courses(user_profile)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Move HTML file to templates directory if it exists in the root
    html_file = 'commerce_course_recommendation_.html'
    if os.path.exists(html_file) and not os.path.exists(f'templates/{html_file}'):
        import shutil
        shutil.move(html_file, 'templates/')

    print("Starting Commerce Flask server...")
    print("Available routes:")
    print("- http://127.0.0.1:5001/ (Main application)")
    print("- http://127.0.0.1:5001/api/features (API endpoint for features)")
    print("- http://127.0.0.1:5001/api/recommend (API endpoint for recommendations)")

    app.run(debug=True, port=5001)
