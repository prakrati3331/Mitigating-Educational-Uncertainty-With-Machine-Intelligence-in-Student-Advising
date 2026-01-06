from flask import Flask, request, jsonify, render_template, send_from_directory
import pickle
# import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

class ArtsCourseRecommender:
    # Subject organization for Arts
    SUBJECT_CATEGORIES = {
        'core': {
            'title': '📘 Core Subjects',
            'subjects': [
                'History', 'Political Science', 'Sociology', 'English'
            ],
            'icon': 'book-open'
        },
        'elective': {
            'title': '📙 Elective Subjects',
            'subjects': [
                'Psychology', 'Economics', 'Philosophy', 'Geography',
                'Hindi', 'Sanskrit', 'Fine Arts'
            ],
            'icon': 'book'
        },
        'aptitude': {
            'title': '🎯 Aptitudes & Skills',
            'subjects': [
                'Logical Reasoning', 'Memory', 'Communication', 'Empathy', 'Creativity',
                'Critical Thinking', 'Problem Solving', 'Leadership', 'Teamwork', 'Time Management'
            ],
            'icon': 'brain'
        }
    }

    def __init__(self):
        # Load the pre-trained models and data
        self.scaler = self._load_pickle("scaler.pkl")
        self.clf = self._load_pickle("course_classifier.pkl")
        self.le_course = self._load_pickle("label_encoder.pkl")
        self.feature_columns = self._load_pickle("feature_columns.pkl")
        self.df = self._load_pickle("dataset.pkl")

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
            # Ensure user_profile is a numpy array
            user_profile = np.array(user_profile, dtype=float).reshape(1, -1)

            # Scale input
            user_scaled = self.scaler.transform(user_profile)

            # Calculate similarity with dataset
            sims = cosine_similarity(user_scaled, self.scaler.transform(self.df[self.feature_columns]))[0]
            df_copy = self.df.copy()
            df_copy["similarity"] = sims

            # Aggregate similarity per course
            course_scores = df_copy.groupby("Course")["similarity"].mean().reset_index()
            top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)

            # Collect career options + top skills
            recommendations = []
            for _, row in top_courses.iterrows():
                course = row["Course"]
                sim = row["similarity"]

                # Get career options, handle potential missing column
                if "Career Options" in self.df.columns:
                    career_data = self.df[self.df["Course"] == course]["Career Options"]
                    if not career_data.empty:
                        careers = career_data.dropna().unique()
                        career_str = ", ".join(careers) if len(careers) > 0 else "Various career options available"
                    else:
                        career_str = "Various career options available"
                else:
                    career_str = "Career information not available"

                # Find top supporting skills
                if all(f in self.df.columns for f in self.feature_columns):
                    course_data = self.df[self.df["Course"] == course][self.feature_columns]
                    if not course_data.empty:
                        course_avg = course_data.mean().values
                        diffs = user_profile.flatten() - course_avg
                        top_features_idx = diffs.argsort()[::-1][:3]  # top 3 strengths
                        top_features = [self.feature_columns[i] for i in top_features_idx if i < len(self.feature_columns)]
                        top_skills = ", ".join(top_features) if top_features else "Various skills"
                    else:
                        top_skills = "Various skills"
                else:
                    top_skills = "Skill information not available"

                recommendations.append({
                    "Course": str(course),
                    "Similarity": float(round(sim, 3)),
                    "Career Options": career_str,
                    "Top Supporting Skills": top_skills
                })

            return recommendations

        except Exception as e:
            import traceback
            print(f"Error in recommend_courses: {str(e)}")
            print(traceback.format_exc())
            return []

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
recommender = ArtsCourseRecommender()

app = Flask(__name__)

@app.route('/')
def home():
    """Serve the main HTML page"""
    return app.send_static_file('arts_course_recommendation.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint for getting recommendations"""
    try:
        data = request.get_json()
        user_profile_dict = data.get('user_profile', {})
        
        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in recommender.feature_columns]
        
        if len(user_profile) != len(recommender.feature_columns):
            return jsonify({
                'error': f'Expected {len(recommender.feature_columns)} features, got {len(user_profile)}',
                'features': recommender.feature_columns
            }), 400
            
        recommendations = recommender.recommend_courses(user_profile)
        return jsonify(recommendations)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/features', methods=['GET'])
def get_features():
    """Get the list of feature columns"""
    return jsonify({
        'features': recommender.feature_columns,
        'description': 'These are the features used for recommendations',
        'count': len(recommender.feature_columns)
    })

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Move the HTML file to static directory if it exists
    if os.path.exists('arts_course_recommendation.html'):
        import shutil
        shutil.move('arts_course_recommendation.html', 'static/arts_course_recommendation.html')
    
    # Run the app
    app.run(debug=True, port=5000)


