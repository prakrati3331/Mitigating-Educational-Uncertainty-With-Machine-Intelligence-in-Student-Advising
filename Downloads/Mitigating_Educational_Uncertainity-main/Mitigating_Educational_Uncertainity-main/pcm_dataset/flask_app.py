from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import os

# Subject organization for PCM
SUBJECT_CATEGORIES = {
    'core': {
        'title': '📘 Core Subjects',
        'subjects': [
            'Physics', 'Chemistry', 'Mathematics',
            'English', 'Hindi'
        ],
        'icon': 'atom',
        'description': 'Fundamental subjects that form the core of the PCM stream'
    },
    'elective': {
        'title': '📙 Elective Subjects',
        'subjects': [
            'Biology', 'Computer Science', 'Economics'
        ],
        'icon': 'flask',
        'description': 'Complementary subjects that enhance your technical knowledge'
    },
    'aptitude': {
        'title': '🎯 Aptitudes & Skills',
        'subjects': [
            'Logical Reasoning', 'Analytical Thinking', 'Problem Solving',
            'Numerical Ability', 'Communication', 'Creativity'
        ],
        'icon': 'brain',
        'description': 'Essential skills for success in technical careers'
    }
}

class PCMCourseRecommender:
    def __init__(self):
        # Load the pre-trained models and data
        self.scaler = self._load_pickle("pcm_scaler.pkl")
        self.clf = self._load_pickle("pcm_course_classifier.pkl")
        self.le_course = self._load_pickle("pcm_label_encoder.pkl")
        self.feature_columns = self._load_pickle("pcm_feature_columns.pkl")
        self.df = self._load_pickle("pcm_dataset.pkl")
        print("PCM models loaded successfully!")

    def _load_pickle(self, filename):
        """Helper to load pickle files"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, filename), "rb") as f:
            return pickle.load(f)

    def recommend_courses(self, user_profile, top_n=5):
        """Generate course recommendations based on user profile"""
        user_scaled = self.scaler.transform([user_profile])

        # Calculate similarity with dataset
        sims = cosine_similarity(user_scaled, self.scaler.transform(self.df[self.feature_columns]))[0]
        df_temp = self.df.copy()
        df_temp["similarity"] = sims

        # Aggregate similarity per course
        course_scores = df_temp.groupby("Suggested_Course")["similarity"].mean().reset_index()
        top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)

        # Collect career options
        recommendations = []
        for _, row in top_courses.iterrows():
            course = row["Suggested_Course"]
            sim = row["similarity"]
            careers = df_temp[df_temp["Suggested_Course"] == course]["Career Options"].unique()
            recommendations.append({
                "course": course,
                "similarity": round(float(sim), 3),
                "careers": list(careers)
            })

        return recommendations

    def predict_course(self, user_profile):
        """Predict the best fit course for the user"""
        user_scaled = self.scaler.transform([user_profile])
        pred = self.clf.predict(user_scaled)
        course = self.le_course.inverse_transform(pred)[0]
        return course

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
recommender = PCMCourseRecommender()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('pcm_recommendation.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        user_profile = [data[col] for col in recommender.feature_columns]

        # Get predictions and recommendations
        best_course = recommender.predict_course(user_profile)
        recommendations = recommender.recommend_courses(user_profile, top_n=5)

        # Get careers for the best course
        careers = recommender.df[recommender.df["Suggested_Course"] == best_course]["Career Options"].unique().tolist()

        return jsonify({
            'status': 'success',
            'best_course': best_course,
            'recommendations': recommendations,
            'careers': careers
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Move HTML file to templates directory if it's not already there
    if os.path.exists('pcm_recommendation.html') and not os.path.exists('templates/pcm_recommendation.html'):
        import shutil
        shutil.move('pcm_recommendation.html', 'templates/pcm_recommendation.html')

    print("PCM Course & Career Recommendation System")
    print(f"Loaded {len(recommender.df)} courses with {len(recommender.feature_columns)} features")
    print(f"Available courses: {len(recommender.df['Suggested_Course'].unique())}")

    app.run(debug=True, port=5004)
