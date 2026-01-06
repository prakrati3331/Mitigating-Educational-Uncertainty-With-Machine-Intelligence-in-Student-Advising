from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS
import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

# Add parent directory to path to import existing services
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import existing services
from Arts_dataset.flask_app import ArtsCourseRecommender
from Commerce_dataset.flask_app import CommerceCourseRecommender
from pcb_dataset.flask_app import PCBCourseRecommender
from pcm_dataset.flask_app import PCMCourseRecommender
from Vocational_dataset.flask_app import VocationalCourseRecommender
from Career_Mapping.career_service import CareerService
from Interest_and_quizzes.quiz_service import QuizService
from Dropout_risk_factor.imp.dropout_risk_service import DropoutRiskService

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
arts_recommender = ArtsCourseRecommender()
commerce_recommender = CommerceCourseRecommender()
pcb_recommender = PCBCourseRecommender()
pcm_recommender = PCMCourseRecommender()
vocational_recommender = VocationalCourseRecommender()
career_service = CareerService()
quiz_service = QuizService()
dropout_risk_service = DropoutRiskService()

# In-memory storage for user data (in production, use a database)
user_data_store = {}

class DashboardService:
    """Service to aggregate all user data for the dashboard"""
    
    def __init__(self):
        self.user_data = user_data_store
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        try:
            user_data = self.user_data.get(user_id, {})
            
            # Get stream recommendation data
            stream_data = self._get_stream_recommendation(user_id)
            
            # Get course recommendations
            course_recommendations = self._get_course_recommendations(user_id)
            
            # Get career guidance data
            career_data = self._get_career_data(user_id)
            
            # Get quiz results
            quiz_data = self._get_quiz_data(user_id)
            
            # Get dropout risk data
            risk_data = self._get_dropout_risk_data(user_id)
            
            # Calculate overall stats
            stats = self._calculate_user_stats(user_id, stream_data, course_recommendations, quiz_data, risk_data)
            
            # Get recent activities
            activities = self._get_recent_activities(user_id)
            
            return {
                'user_id': user_id,
                'stats': stats,
                'stream_recommendation': stream_data,
                'course_recommendations': course_recommendations,
                'career_guidance': career_data,
                'quiz_results': quiz_data,
                'dropout_risk': risk_data,
                'recent_activities': activities,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {str(e)}")
            return {'error': str(e)}
    
    def _get_stream_recommendation(self, user_id: str) -> Dict[str, Any]:
        """Get stream recommendation for user"""
        try:
            user_data = self.user_data.get(user_id, {})
            if 'stream_prediction' in user_data:
                return user_data['stream_prediction']
            return None
        except Exception as e:
            logger.error(f"Error getting stream recommendation: {str(e)}")
            return None
    
    def _get_course_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get course recommendations for user"""
        try:
            user_data = self.user_data.get(user_id, {})
            recommendations = {}
            
            stream = user_data.get('stream', '').lower()
            
            if stream == 'arts' and 'arts_recommendations' in user_data:
                recommendations['arts'] = user_data['arts_recommendations']
            elif stream == 'commerce' and 'commerce_recommendations' in user_data:
                recommendations['commerce'] = user_data['commerce_recommendations']
            elif stream == 'pcm' and 'pcm_recommendations' in user_data:
                recommendations['pcm'] = user_data['pcm_recommendations']
            elif stream == 'pcb' and 'pcb_recommendations' in user_data:
                recommendations['pcb'] = user_data['pcb_recommendations']
            elif stream == 'vocational' and 'vocational_recommendations' in user_data:
                recommendations['vocational'] = user_data['vocational_recommendations']
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting course recommendations: {str(e)}")
            return {}
    
    def _get_career_data(self, user_id: str) -> Dict[str, Any]:
        """Get career guidance data for user"""
        try:
            assessment = career_service.get_latest_assessment(user_id)
            if assessment:
                return {
                    'assessment': assessment,
                    'career_paths': self._get_career_paths_for_stream(assessment.get('stream', ''))
                }
            return None
        except Exception as e:
            logger.error(f"Error getting career data: {str(e)}")
            return None
    
    def _get_career_paths_for_stream(self, stream: str) -> list:
        """Get career paths for a specific stream"""
        try:
            career_data = career_service.get_career_data(stream)
            if career_data.get('status') == 'success':
                return career_data.get('careers', [])
            return []
        except Exception as e:
            logger.error(f"Error getting career paths: {str(e)}")
            return []
    
    def _get_quiz_data(self, user_id: str) -> Dict[str, Any]:
        """Get quiz results for user"""
        try:
            user_quizzes = {k: v for k, v in quiz_service.quiz_results.items() if v.get('user_id') == user_id}
            
            if user_quizzes:
                # Calculate analytics
                total_quizzes = len(user_quizzes)
                average_score = sum(q.get('score', 0) for q in user_quizzes.values()) / total_quizzes if total_quizzes > 0 else 0
                quiz_types = list(set(q.get('quiz_type', 'Unknown') for q in user_quizzes.values()))
                
                return {
                    'total_quizzes': total_quizzes,
                    'average_score': round(average_score, 2),
                    'quiz_types': quiz_types,
                    'recent_quizzes': list(user_quizzes.values())[:5]  # Last 5 quizzes
                }
            return None
        except Exception as e:
            logger.error(f"Error getting quiz data: {str(e)}")
            return None
    
    def _get_dropout_risk_data(self, user_id: str) -> Dict[str, Any]:
        """Get dropout risk assessment for user"""
        try:
            user_data = self.user_data.get(user_id, {})
            if 'dropout_assessment' in user_data:
                return user_data['dropout_assessment']
            return None
        except Exception as e:
            logger.error(f"Error getting dropout risk data: {str(e)}")
            return None
    
    def _calculate_user_stats(self, user_id: str, stream_data: Any, course_data: Any, quiz_data: Any, risk_data: Any) -> Dict[str, Any]:
        """Calculate overall user statistics"""
        try:
            profile_completion = 0
            
            # Stream recommendation (25%)
            if stream_data:
                profile_completion += 25
            
            # Course recommendations (25%)
            if course_data and len(course_data) > 0:
                profile_completion += 25
            
            # Quiz participation (25%)
            if quiz_data:
                profile_completion += 25
            
            # Career assessment (25%)
            if risk_data or (stream_data and stream_data.get('best_stream')):
                profile_completion += 25
            
            # Calculate skills mastered based on quiz scores
            skills_mastered = 0
            total_skills = 10
            if quiz_data:
                skills_mastered = min(int(quiz_data.get('average_score', 0) / 10), total_skills)
            
            # Active courses count
            active_courses = len(course_data) if course_data else 0
            
            # Achievements (based on various activities)
            achievements = 0
            if quiz_data and quiz_data.get('total_quizzes', 0) > 0:
                achievements += 1
            if stream_data:
                achievements += 1
            if course_data and len(course_data) > 0:
                achievements += 1
            
            return {
                'profile_completion': profile_completion,
                'skills_mastered': f"{skills_mastered}/{total_skills}",
                'active_courses': active_courses,
                'achievements': achievements
            }
            
        except Exception as e:
            logger.error(f"Error calculating user stats: {str(e)}")
            return {
                'profile_completion': 0,
                'skills_mastered': "0/10",
                'active_courses': 0,
                'achievements': 0
            }
    
    def _get_recent_activities(self, user_id: str) -> list:
        """Get recent user activities"""
        try:
            activities = []
            user_data = self.user_data.get(user_id, {})
            
            # Stream recommendation activity
            if 'stream_prediction' in user_data:
                activities.append({
                    'type': 'stream_recommendation',
                    'title': f"Stream recommended: {user_data['stream_prediction'].get('best_stream', 'Unknown')}",
                    'description': "Based on your assessment scores",
                    'timestamp': user_data.get('stream_prediction', {}).get('timestamp', datetime.now().isoformat()),
                    'icon': 'fas fa-chart-line'
                })
            
            # Quiz activities
            user_quizzes = {k: v for k, v in quiz_service.quiz_results.items() if v.get('user_id') == user_id}
            for quiz_id, quiz_result in list(user_quizzes.items())[:3]:
                activities.append({
                    'type': 'quiz_completed',
                    'title': f"Completed {quiz_result.get('quiz_type', 'Quiz')}",
                    'description': f"Score: {quiz_result.get('score', 0)}%",
                    'timestamp': quiz_result.get('timestamp', datetime.now().isoformat()),
                    'icon': 'fas fa-clipboard-check'
                })
            
            # Course recommendation activities
            for stream, recommendations in user_data.items():
                if 'recommendations' in stream and recommendations:
                    activities.append({
                        'type': 'course_recommendation',
                        'title': f"Course recommendations available",
                        'description': f"{len(recommendations)} courses recommended",
                        'timestamp': datetime.now().isoformat(),
                        'icon': 'fas fa-graduation-cap'
                    })
            
            # Sort by timestamp (most recent first)
            activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return activities[:5]  # Return last 5 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []

# Initialize dashboard service
dashboard_service = DashboardService(user_data_store)

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/stream_selection.html')
def stream_selection():
    """Serve stream selection page - redirect to main app"""
    return redirect('http://localhost:5006/stream_selection.html')

@app.route('/favicon.ico')
def favicon():
    """Return empty response for favicon"""
    return '', 204

@app.route('/api/dashboard/<user_id>')
def get_dashboard_data(user_id):
    """Get dashboard data for a specific user"""
    try:
        data = dashboard_service.get_user_dashboard_data(user_id)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in get_dashboard_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/overview/<user_id>')
def get_dashboard_overview(user_id):
    """Get dashboard overview (summary stats)"""
    try:
        data = dashboard_service.get_user_dashboard_data(user_id)
        if 'error' in data:
            return jsonify(data), 500
        
        overview = {
            'stats': data.get('stats', {}),
            'best_stream': data.get('stream_recommendation', {}).get('best_stream'),
            'total_recommendations': len(data.get('course_recommendations', {})),
            'recent_activities': data.get('recent_activities', [])[:3]
        }
        
        return jsonify(overview)
    except Exception as e:
        logger.error(f"Error in get_dashboard_overview: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Stream Recommendation Endpoints
@app.route('/api/stream/predict', methods=['POST'])
def predict_stream():
    """Predict stream for user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        
        # Store user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        
        # Here you would integrate with your existing stream prediction logic
        # For now, returning mock data
        prediction = {
            'best_stream': 'PCM',
            'predictions': [
                {'stream': 'PCM', 'probability': 85.5},
                {'stream': 'PCB', 'probability': 72.3},
                {'stream': 'Commerce', 'probability': 65.1}
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        user_data_store[user_id]['stream_prediction'] = prediction
        user_data_store[user_id]['stream'] = prediction['best_stream']
        
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error in predict_stream: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Course Recommendation Endpoints
@app.route('/api/courses/recommend/<stream>', methods=['POST'])
def recommend_courses(stream):
    """Get course recommendations for a stream"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        user_profile = data.get('user_profile', {})
        
        # Store user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        
        recommendations = []
        
        # Get recommendations based on stream
        if stream.lower() == 'arts':
            user_profile_list = [user_profile.get(feature, 50) for feature in arts_recommender.feature_columns]
            recommendations = arts_recommender.recommend_courses(user_profile_list)
            user_data_store[user_id]['arts_recommendations'] = recommendations
            
        elif stream.lower() == 'commerce':
            user_profile_list = [user_profile.get(feature, 50) for feature in commerce_recommender.feature_columns]
            recommendations = commerce_recommender.recommend_courses(user_profile_list)
            user_data_store[user_id]['commerce_recommendations'] = recommendations
            
        elif stream.lower() == 'pcm':
            user_profile_list = [user_profile.get(feature, 50) for feature in pcm_recommender.feature_columns]
            best_course = pcm_recommender.predict_course(user_profile_list)
            recommendations = pcm_recommender.recommend_courses(user_profile_list, top_n=5)
            user_data_store[user_id]['pcm_recommendations'] = recommendations
            
        elif stream.lower() == 'pcb':
            user_profile_list = [user_profile.get(feature, 50) for feature in pcb_recommender.feature_columns]
            recommendations = pcb_recommender.recommend_courses(user_profile_list)
            user_data_store[user_id]['pcb_recommendations'] = recommendations
            
        elif stream.lower() == 'vocational':
            user_profile_list = [user_profile.get(feature, 50) for feature in vocational_recommender.feature_columns]
            recommendations = vocational_recommender.recommend_courses(user_profile_list)
            user_data_store[user_id]['vocational_recommendations'] = recommendations
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        logger.error(f"Error in recommend_courses: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Career Assessment Endpoints
@app.route('/api/career/assess', methods=['POST'])
def assess_career():
    """Process career assessment"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        
        # Process assessment using career service
        result = career_service.process_assessment(data)
        
        # Store in user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        
        user_data_store[user_id]['career_assessment'] = result
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in assess_career: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Quiz Endpoints
@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz results"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        
        # Store quiz result
        quiz_result = {
            'user_id': user_id,
            'quiz_type': data.get('quiz_type', 'General'),
            'score': data.get('score', 0),
            'total_questions': data.get('total_questions', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        quiz_id = f"{user_id}_{data.get('quiz_type', 'general')}_{int(datetime.now().timestamp())}"
        quiz_service.quiz_results[quiz_id] = quiz_result
        
        return jsonify({'status': 'success', 'quiz_id': quiz_id})
        
    except Exception as e:
        logger.error(f"Error in submit_quiz: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Dropout Risk Assessment Endpoints
@app.route('/api/dropout-risk/assess', methods=['POST'])
def assess_dropout_risk():
    """Assess dropout risk"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        
        # Map field names to match the service's expected format
        mapped_data = {
            'grades': data.get('grades', 0),
            'attendance': data.get('attendance', 0),
            'assignments': data.get('assignments', 0),
            'exams': data.get('exams', 0),
            'participation': data.get('participation', 0),
            'absences': data.get('absences', 0),
            'tardiness': data.get('tardiness', 0),
            'behavioralIssues': data.get('behavioral_issues', 0),
            'financialStress': data.get('financial_stress', 0),
            'workHours': data.get('work_hours', 0),
            'familySupport': data.get('family_support', 0),
            'healthStatus': data.get('health_status', 0),
            'courseLoad': data.get('course_load', 0),
            'majorFit': data.get('major_fit', 0),
            'facultyInteraction': data.get('faculty_interaction', 0),
            'campusInvolvement': data.get('campus_involvement', 0),
            'peerNetwork': data.get('peer_network', 0),
            'mentorship': data.get('mentorship', 0),
            'bullying': data.get('bullying', 0),
            'commuteTime': data.get('commute_time', 0),
            'familyResponsibilities': data.get('family_responsibilities', 0),
            'workLifeBalance': data.get('work_life_balance', 0),
            'motivation': data.get('motivation', 0),
            'selfEfficacy': data.get('self_efficacy', 0),
            'stressLevel': data.get('stress_level', 0),
            'previousDropout': data.get('previous_dropout', 0),
            'gradeRetention': data.get('grade_retention', 0),
            'schoolChanges': data.get('school_changes', 0),
            'lmsActivity': data.get('lms_activity', 0),
            'onlineEngagement': data.get('online_engagement', 0),
            'warningSigns': data.get('warning_signs', 0),
            'earlyAlerts': data.get('early_alerts', 0)
        }
        
        # Get risk assessment
        result = dropout_risk_service.assess_risk(mapped_data)
        
        # Store in user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        
        user_data_store[user_id]['dropout_assessment'] = result
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in assess_dropout_risk: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('DASHBOARD_PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=True)
