"""
Dashboard Service - Centralized aggregation service for AI education modules
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd

# Import existing services
from Arts_dataset.flask_app import ArtsCourseRecommender
from Commerce_dataset.flask_app import CommerceCourseRecommender
from pcb_dataset.flask_app import PCBCourseRecommender
from pcm_dataset.flask_app import PCMCourseRecommender
from Vocational_dataset.flask_app import VocationalCourseRecommender
from Career_Mapping.career_service import CareerService
from Interest_and_quizzes.quiz_service import QuizService
from Dropout_risk_factor.imp.dropout_risk_service import DropoutRiskService

# Setup logging
logger = logging.getLogger(__name__)

class DashboardService:
    """Service to aggregate all user data for the dashboard"""
    
    def __init__(self, user_data_store: Dict[str, Any]):
        self.user_data = user_data_store
        
        # Initialize services
        self.arts_recommender = ArtsCourseRecommender()
        self.commerce_recommender = CommerceCourseRecommender()
        self.pcb_recommender = PCBCourseRecommender()
        self.pcm_recommender = PCMCourseRecommender()
        self.vocational_recommender = VocationalCourseRecommender()
        self.career_service = CareerService()
        self.quiz_service = QuizService()
        self.dropout_risk_service = DropoutRiskService()
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        try:
            logger.info(f"Getting dashboard data for user {user_id}")
            
            # Initialize user data if not exists
            if user_id not in self.user_data:
                self.user_data[user_id] = {
                    'activities': [],
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            
            # Ensure all required fields exist and are populated
            user_data = self.user_data[user_id]
            
            # 1. Extract stream from career_data if not set
            if not user_data.get('stream') and 'career_data' in user_data:
                career_data = user_data['career_data']
                if isinstance(career_data, dict) and career_data.get('stream'):
                    user_data['stream'] = career_data['stream']
                    logger.info(f"Set stream from career_data: {career_data['stream']}")
            
            # 2. Extract quiz scores from tracking_scores if not set
            if not user_data.get('scores') and 'tracking_scores' in user_data:
                tracking_scores = user_data['tracking_scores']
                if isinstance(tracking_scores, dict) and tracking_scores.get('quiz_breakdown'):
                    quiz_breakdown = tracking_scores['quiz_breakdown']
                    scores = {}
                    for quiz_name, score_data in quiz_breakdown.items():
                        if score_data and isinstance(score_data, dict):
                            scores[quiz_name] = {
                                'score': score_data.get('score', 0),
                                'total': score_data.get('total', 0),
                                'percentage': score_data.get('percentage', 0),
                                'date': score_data.get('date', datetime.now().isoformat())
                            }
                    if scores:
                        user_data['scores'] = scores
                        logger.info(f"Extracted {len(scores)} quiz scores from tracking_scores")
            
            # 3. Ensure activities exist and add missing assessment activities
            if not user_data.get('activities'):
                user_data['activities'] = []
            
            activities = user_data['activities']
            
            # Add stream assessment activity if missing
            if user_data.get('stream'):
                stream_assessments = [a for a in activities if a.get('type') == 'stream_assessment']
                if not stream_assessments:
                    stream_activity = {
                        'id': f"stream_assessment_{user_id}_{int(datetime.now().timestamp())}",
                        'type': 'stream_assessment',
                        'title': 'Stream Assessment',
                        'timestamp': datetime.now().isoformat(),
                        'data': {
                            'recommended_stream': user_data['stream'],
                            'assessment_date': datetime.now().isoformat()
                        }
                    }
                    activities.append(stream_activity)
                    logger.info(f"Added stream assessment activity for stream: {user_data['stream']}")
            
            # Add career assessment activity if missing
            if 'career_data' in user_data and user_data['career_data'].get('assessment'):
                career_assessments = [a for a in activities if a.get('type') == 'career_assessment']
                if not career_assessments:
                    career_activity = {
                        'id': f"career_assessment_{user_id}_{int(datetime.now().timestamp())}",
                        'type': 'career_assessment',
                        'title': 'Career Assessment',
                        'timestamp': datetime.now().isoformat(),
                        'data': user_data['career_data']
                    }
                    activities.append(career_activity)
                    logger.info("Added career assessment activity")
            
            # 4. Add dropout assessment if missing AND user has real activities
            if not user_data.get('dropout_assessment') and 'engagement_metrics' in user_data:
                engagement = user_data['engagement_metrics']
                if isinstance(engagement, dict) and engagement.get('has_real_activities', False):
                    # Check if user has real activities (not dummy data)
                    real_activities = [act for act in user_data.get('activities', []) 
                                     if not act.get('data', {}).get('is_dummy', False)]
                    
                    # Only generate dropout assessment if user has real activities
                    if len(real_activities) > 0:
                        risk_score = max(0, 100 - engagement.get('engagement_score', 0))
                        
                        user_data['dropout_assessment'] = {
                            'risk_level': 'Low' if risk_score < 30 else 'Medium' if risk_score < 60 else 'High',
                            'risk_score': risk_score,
                            'factors': {
                                'engagement_score': engagement.get('engagement_score', 0),
                                'streak_days': engagement.get('streak_days', 0),
                                'total_activities': engagement.get('total_activities', 0)
                            },
                            'recommendations': [],
                            'assessment_date': datetime.now().isoformat(),
                            'based_on_real_data': True
                        }
                        logger.info(f"Added dropout assessment based on real activities (Risk: {user_data['dropout_assessment']['risk_level']})")
                    else:
                        logger.info("Skipping dropout assessment generation - no real user activities found")
                else:
                    logger.info("Skipping dropout assessment generation - no real activities flag")
            
            # 5. Add form_data if missing
            if not user_data.get('form_data') and 'career_data' in user_data:
                career_data = user_data['career_data']
                if isinstance(career_data, dict) and 'assessment' in career_data:
                    assessment = career_data['assessment']
                    if isinstance(assessment, dict) and 'scores' in assessment:
                        user_data['form_data'] = {
                            'stream': career_data.get('stream'),
                            'scores': assessment['scores'],
                            'submission_date': assessment.get('date', datetime.now().isoformat())
                        }
                        logger.info("Added form_data from career assessment")
            
            # Update last_updated
            user_data['last_updated'] = datetime.now().isoformat()
            
            # Get engagement metrics
            engagement_metrics = self._get_engagement_metrics(user_id)
            
            # Get tracking scores (including quiz scores)
            tracking_scores = self._get_tracking_scores(user_id)
            
            # Get career data
            career_data = self._get_career_data(user_id)
            
            # Get course recommendations
            course_recommendations = self._get_course_recommendations(user_id)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(user_id)
            
            # Get dropout risk data
            dropout_assessment = self._get_dropout_risk_data(user_id)
            
            # Get form data
            form_data = self.user_data.get(user_id, {}).get('form_data', None)
            
            # Get stream data
            stream_data = self._get_stream_data(user_id)
            
            # Update last updated
            self.user_data[user_id]['last_updated'] = datetime.now().isoformat()
            
            return {
                'user_id': user_id,
                'engagement_metrics': engagement_metrics,
                'tracking_scores': tracking_scores,
                'career_data': career_data,
                'course_recommendations': course_recommendations,
                'recommendations': recommendations,
                'dropout_assessment': dropout_assessment,
                'form_data': form_data,
                'stream': stream_data.get('stream'),
                'scores': stream_data.get('scores'),
                'predictions': stream_data.get('predictions'),
                'activities': user_data.get('activities', []),
                'last_updated': self.user_data[user_id]['last_updated']
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {str(e)}")
            return {'error': str(e)}
    
    def _get_stream_data(self, user_id: str) -> Dict[str, Any]:
        """Get stream data for user from user_data_store"""
        try:
            # Check user_data_store first (this is where set-recommended-stream stores data)
            if user_id in self.user_data:
                user_data = self.user_data[user_id]
                logger.info(f"User data keys: {list(user_data.keys())}")
                
                # Check if stream is directly in user data
                if 'stream' in user_data and user_data['stream']:
                    logger.info(f"Found stream data in user_data_store: {user_data['stream']}")
                    return {
                        'stream': user_data.get('stream'),
                        'scores': user_data.get('scores'),
                        'predictions': user_data.get('predictions')
                    }
                
                # Check career_data for stream information
                if 'career_data' in user_data and isinstance(user_data['career_data'], dict):
                    career_data = user_data['career_data']
                    if 'stream' in career_data and career_data['stream']:
                        logger.info(f"Found stream in career_data: {career_data['stream']}")
                        return {
                            'stream': career_data['stream'],
                            'scores': user_data.get('scores'),
                            'predictions': user_data.get('predictions')
                        }
                
                # Check activities for stream assessment data
                activities = user_data.get('activities', [])
                stream_activities = [
                    activity for activity in activities 
                    if activity.get('type') == 'stream_assessment' or 
                       activity.get('title', '').lower().find('stream assessment') != -1
                ]
                
                if stream_activities:
                    # Sort by timestamp to get latest
                    stream_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    latest_activity = stream_activities[0]
                    
                    if 'data' in latest_activity and latest_activity['data'].get('recommended_stream'):
                        logger.info(f"Found stream data in activity: {latest_activity['data']['recommended_stream']}")
                        return {
                            'stream': latest_activity['data'].get('recommended_stream'),
                            'scores': latest_activity['data'].get('scores'),
                            'predictions': latest_activity['data'].get('predictions')
                        }
            
            logger.info("No stream data found")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting stream data: {str(e)}")
            return {}
    
    def _get_stream_recommendation(self, user_id: str) -> Dict[str, Any]:
        """Get stream recommendation for user"""
        try:
            user_data = self.user_data.get(user_id, {})
            
            # Check if stream is already stored
            if 'stream_prediction' in user_data:
                return user_data['stream_prediction']
            
            # Extract stream from activities (use most recent)
            activities = user_data.get('activities', [])
            stream_predictions = []
            
            for activity in activities:
                if activity.get('type') == 'stream_prediction' and activity.get('data'):
                    stream_data = activity['data']
                    if 'best_stream' in stream_data:
                        stream_predictions.append(stream_data)
            
            if stream_predictions:
                # Use the most recent stream prediction (last in list)
                latest_stream_data = stream_predictions[-1]
                # Store the stream prediction for future use
                self.user_data[user_id]['stream_prediction'] = latest_stream_data
                self.user_data[user_id]['stream'] = latest_stream_data['best_stream']
                
                # Automatically generate course recommendations for the recommended stream
                stream = latest_stream_data['best_stream'].lower()
                if stream and not any(key in user_data for key in ['arts_recommendations', 'commerce_recommendations', 'pcm_recommendations', 'pcb_recommendations', 'vocational_recommendations']):
                    self._generate_sample_course_recommendations(user_id, stream)
                    logger.info(f"Generated course recommendations for {stream} stream for user {user_id}")
                
                return latest_stream_data
            
            return None
        except Exception as e:
            logger.error(f"Error getting stream recommendation: {str(e)}")
            return None
    
    def _get_engagement_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement metrics based on real activities only"""
        try:
            # Get only real activities (no dummy data)
            user_data = self.user_data.get(user_id, {})
            real_activities = [act for act in user_data.get('activities', []) 
                             if not act.get('data', {}).get('is_dummy', False)]
            
            # Time-based analysis
            now = datetime.now()
            total_activities = len(real_activities)
            
            # Only calculate meaningful metrics if there are real activities
            if total_activities == 0:
                return {
                    'total_sessions': 0,
                    'avg_session_duration': 0,
                    'most_active_hour': 0,
                    'most_active_day': '-',
                    'streak_days': 0,
                    'last_activity': None,
                    'total_activities': 0,
                    'engagement_score': 0,
                    'has_real_activities': False
                }
            
            engagement_metrics = {
                'total_sessions': max(len(set(a.get('session_id', '') for a in real_activities if a.get('session_id'))), 1),
                'avg_session_duration': 25,  # Default estimate
                'most_active_hour': 14,  # Default estimate
                'most_active_day': 'Tuesday',  # Default estimate
                'streak_days': min(total_activities, 30),  # Calculate based on real activities
                'last_activity': real_activities[-1].get('timestamp') if real_activities else None,
                'total_activities': total_activities,
                'engagement_score': min(total_activities * 8, 100),  # Based on real activities only
                'has_real_activities': True
            }
            
            return engagement_metrics
            
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {str(e)}")
            return {
                'total_sessions': 0,
                'avg_session_duration': 0,
                'most_active_hour': 0,
                'most_active_day': '-',
                'streak_days': 0,
                'last_activity': None,
                'total_activities': 0,
                'engagement_score': 0,
                'has_real_activities': False
            }
    
    def _generate_dummy_activities(self, user_id: str) -> list:
        """Generate dummy activities for the user"""
        import random
        from datetime import timedelta
        
        dummy_activities = []
        activity_types = [
            {'type': 'stream_prediction', 'title': 'Stream Prediction Completed', 'description': 'Recommended: PCM', 'icon': 'fas fa-graduation-cap', 'duration': 10},
            {'type': 'quiz', 'title': 'Mathematics Quiz', 'description': 'Score: 85/100', 'icon': 'fas fa-brain', 'duration': 15},
            {'type': 'course_recommendation', 'title': 'Course Recommendations Viewed', 'description': '5 courses recommended', 'icon': 'fas fa-book', 'duration': 12},
            {'type': 'career_assessment', 'title': 'Career Assessment Started', 'description': 'Stream: PCM', 'icon': 'fas fa-route', 'duration': 20},
            {'type': 'risk_analysis', 'title': 'Risk Analysis Completed', 'description': 'Low risk detected', 'icon': 'fas fa-shield-alt', 'duration': 8},
            {'type': 'quiz', 'title': 'Science Quiz', 'description': 'Score: 92/100', 'icon': 'fas fa-flask', 'duration': 18},
            {'type': 'course_recommendation', 'title': 'Engineering Courses Explored', 'description': 'Computer Science focus', 'icon': 'fas fa-laptop-code', 'duration': 15},
            {'type': 'stream_prediction', 'title': 'Career Path Analysis', 'description': 'Software Engineering', 'icon': 'fas fa-code', 'duration': 25}
        ]
        
        now = datetime.now()
        for i, activity in enumerate(activity_types[:8]):  # Generate 8 dummy activities
            activity_time = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            dummy_activities.append({
                'id': f'dummy_{i}_{user_id}',
                'timestamp': activity_time.isoformat(),
                **activity
            })
        
        return dummy_activities
    
    def _get_course_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get course recommendations for a user"""
        try:
            user_data = self.user_data.get(user_id, {})
            
            print(f"🔥 DEBUG: Getting course recommendations for user {user_id}")
            print(f"🔥 DEBUG: User data keys: {list(user_data.keys())}")
            
            logger.info(f"Getting course recommendations for user {user_id}")
            logger.info(f"User data keys: {list(user_data.keys())}")
            
            # Get stream from various possible locations
            stream = user_data.get('stream', '').lower()
            
            # If no stream in user_data, check career_data
            if not stream and 'career_data' in user_data and isinstance(user_data['career_data'], dict):
                career_data = user_data['career_data']
                if 'stream' in career_data and career_data['stream']:
                    stream = career_data['stream'].lower()
                    print(f"🔥 DEBUG: Found stream in career_data: {stream}")
            
            # Check what recommendation keys exist
            recommendation_keys = ['arts_recommendations', 'commerce_recommendations', 'pcm_recommendations', 'pcb_recommendations', 'vocational_recommendations']
            existing_keys = [key for key in recommendation_keys if key in user_data]
            
            print(f"🔥 DEBUG: Existing recommendation keys: {existing_keys}")
            logger.info(f"Existing recommendation keys: {existing_keys}")
            
            # Special handling for PCB recommendations from career_data
            if stream == 'pcb' and 'pcb_recommendations' not in existing_keys:
                if 'career_data' in user_data and isinstance(user_data['career_data'], dict):
                    career_data = user_data['career_data']
                    if 'assessment' in career_data and isinstance(career_data['assessment'], dict):
                        assessment = career_data['assessment']
                        if 'pcb_recommendations' in assessment:
                            # Copy PCB recommendations from career_data to user_data
                            user_data['pcb_recommendations'] = assessment['pcb_recommendations']
                            existing_keys.append('pcb_recommendations')
                            print(f"🔥 DEBUG: Copied PCB recommendations from career_data")
                            logger.info(f"Copied PCB recommendations from career_data to user_data")
            
            # Generate sample recommendations ONLY if user has stream but no stored recommendations
            if stream and not existing_keys:
                logger.info(f"No existing recommendations found for stream {stream}, generating sample recommendations")
                self._generate_sample_course_recommendations(user_id, stream)
                user_data = self.user_data.get(user_id, {})
                existing_keys = [key for key in recommendation_keys if key in user_data]
            else:
                logger.info(f"Found existing recommendations, skipping sample generation")
            
            # Collect all available recommendations across all streams
            all_recommendations = {}
            current_stream_recs = {}
            
            # Check for each stream's recommendations and convert format
            if 'arts_recommendations' in user_data:
                arts_data = user_data['arts_recommendations']
                # Convert to the format expected by frontend
                converted_arts = []
                if 'recommendations' in arts_data:
                    for rec in arts_data['recommendations']:
                        converted_arts.append({
                            'course': rec.get('Course', rec.get('course', 'Unknown')),
                            'probability': rec.get('Similarity', rec.get('probability', 0)) * 100,  # Convert to percentage
                            'careers': rec.get('Career Options', rec.get('careers', '')),
                            'skills': rec.get('Top Supporting Skills', rec.get('skills', ''))
                        })
                all_recommendations['arts'] = converted_arts
                logger.info(f"Found arts recommendations: {arts_data}")
                print(f"🔥 DEBUG: Converted arts recommendations: {converted_arts}")
                
            if 'commerce_recommendations' in user_data:
                commerce_data = user_data['commerce_recommendations']
                converted_commerce = []
                if 'recommendations' in commerce_data:
                    for rec in commerce_data['recommendations']:
                        converted_commerce.append({
                            'course': rec.get('Course', rec.get('course', 'Unknown')),
                            'probability': rec.get('Similarity', rec.get('probability', 0)) * 100,
                            'careers': rec.get('Career Options', rec.get('careers', '')),
                            'skills': rec.get('Top Supporting Skills', rec.get('skills', ''))
                        })
                all_recommendations['commerce'] = converted_commerce
                logger.info(f"Found commerce recommendations: {commerce_data}")
                
            if 'pcm_recommendations' in user_data:
                pcm_data = user_data['pcm_recommendations']
                converted_pcm = []
                if 'recommendations' in pcm_data:
                    for rec in pcm_data['recommendations']:
                        converted_pcm.append({
                            'course': rec.get('Course', rec.get('course', 'Unknown')),
                            'probability': rec.get('Similarity', rec.get('probability', 0)) * 100,
                            'careers': rec.get('Career Options', rec.get('careers', '')),
                            'skills': rec.get('Top Supporting Skills', rec.get('skills', ''))
                        })
                all_recommendations['pcm'] = converted_pcm
                logger.info(f"Found pcm recommendations: {pcm_data}")
                
            if 'pcb_recommendations' in user_data:
                pcb_data = user_data['pcb_recommendations']
                converted_pcb = []
                if isinstance(pcb_data, dict) and 'recommendations' in pcb_data:
                    # Handle the case where recommendations is a list of strings
                    if pcb_data['recommendations'] and isinstance(pcb_data['recommendations'][0], str):
                        careers = pcb_data.get('careers', [''] * len(pcb_data['recommendations']))
                        for i, rec in enumerate(pcb_data['recommendations']):
                            converted_pcb.append({
                                'course': rec,
                                'probability': 100,  # Default high probability for direct recommendations
                                'careers': careers[i] if i < len(careers) else '',
                                'skills': ''
                            })
                    # Handle the case where recommendations is a list of dicts
                    else:
                        for rec in pcb_data['recommendations']:
                            if isinstance(rec, dict):
                                converted_pcb.append({
                                    'course': rec.get('Course', rec.get('course', 'Unknown')),
                                    'probability': rec.get('Similarity', rec.get('probability', 0)) * 100,
                                    'careers': rec.get('Career Options', rec.get('careers', '')),
                                    'skills': rec.get('Top Supporting Skills', rec.get('skills', ''))
                                })
                all_recommendations['pcb'] = converted_pcb
                logger.info(f"Found pcb recommendations: {pcb_data}")
                print(f"🔥 DEBUG: Converted PCB recommendations: {converted_pcb}")
                
            if 'vocational_recommendations' in user_data:
                vocational_data = user_data['vocational_recommendations']
                converted_vocational = []
                if 'recommendations' in vocational_data:
                    for rec in vocational_data['recommendations']:
                        converted_vocational.append({
                            'course': rec.get('Course', rec.get('course', 'Unknown')),
                            'probability': rec.get('Similarity', rec.get('probability', 0)) * 100,
                            'careers': rec.get('Career Options', rec.get('careers', '')),
                            'skills': rec.get('Top Supporting Skills', rec.get('skills', ''))
                        })
                all_recommendations['vocational'] = converted_vocational
                logger.info(f"Found vocational recommendations: {vocational_data}")
            
            print(f"🔥 DEBUG: Final all_recommendations: {all_recommendations}")
            
            # Try exact match first
            if stream in all_recommendations:
                current_stream_recs = all_recommendations[stream]
            else:
                # Try case-insensitive match
                for stream_key in all_recommendations:
                    if stream_key.lower() == stream.lower():
                        current_stream_recs = all_recommendations[stream_key]
                        break
            
            logger.info(f"Current stream recommendations found: {bool(current_stream_recs)}")
            
            return {
                'current_stream': stream,
                'current_stream_recommendations': current_stream_recs,
                'all_stream_recommendations': all_recommendations,
                'total_courses': sum(len(recs) for recs in all_recommendations.values()),
                'available_streams': list(all_recommendations.keys())
            }
            
        except Exception as e:
            logger.error(f"Error getting course recommendations: {str(e)}")
            return {
                'current_stream': '',
                'current_stream_recommendations': {},
                'all_stream_recommendations': {},
                'total_courses': 0,
                'available_streams': []
            }
    
    def _generate_sample_course_recommendations(self, user_id: str, stream: str):
        """Generate sample course recommendations for user based on stream"""
        try:
            logger.info(f"Generating sample course recommendations for {stream} stream for user {user_id}")
            sample_recommendations = {
                'arts': {
                    'best_course': 'Literature',
                    'recommendations': ['Literature', 'History', 'Philosophy', 'Fine Arts', 'Political Science'],
                    'careers': ['Writer', 'Historian', 'Philosopher', 'Artist', 'Politician']
                },
                'commerce': {
                    'best_course': 'Accounting',
                    'recommendations': ['Accounting', 'Business Administration', 'Finance', 'Marketing', 'Economics'],
                    'careers': ['Accountant', 'Business Manager', 'Financial Analyst', 'Marketing Manager', 'Economist']
                },
                'pcm': {
                    'best_course': 'Engineering',
                    'recommendations': ['Engineering', 'Computer Science', 'Physics', 'Mathematics', 'Architecture'],
                    'careers': ['Engineer', 'Software Developer', 'Physicist', 'Mathematician', 'Architect']
                },
                'pcb': {
                    'best_course': 'Medicine',
                    'recommendations': ['Medicine', 'Biotechnology', 'Pharmacy', 'Nursing', 'Life Sciences'],
                    'careers': ['Doctor', 'Medical Researcher', 'Pharmacist', 'Nurse', 'Lab Technician']
                },
                'vocational': {
                    'best_course': 'Digital Marketing',
                    'recommendations': ['Digital Marketing', 'Web Development', 'Graphic Design', 'Photography', 'Culinary Arts'],
                    'careers': ['Digital Marketer', 'Web Developer', 'Graphic Designer', 'Photographer', 'Chef']
                }
            }
            
            if stream in sample_recommendations:
                recommendation_key = f"{stream}_recommendations"
                self.user_data[user_id][recommendation_key] = sample_recommendations[stream]
                logger.info(f"Generated sample course recommendations for {stream} stream: {sample_recommendations[stream]}")
            else:
                logger.warning(f"No sample recommendations found for stream: {stream}")
            
        except Exception as e:
            logger.error(f"Error generating sample course recommendations: {str(e)}")
    
    def _get_career_data(self, user_id: str) -> Dict[str, Any]:
        """Get career guidance data for user"""
        try:
            # First try to get the latest assessment from career service
            assessment = self.career_service.get_latest_assessment(user_id)
            
            # Also check if there's a career assessment stored in user data
            user_data = self.user_data.get(user_id, {})
            stored_assessment = user_data.get('career_assessment')
            
            # Use the most recent assessment
            latest_assessment = None
            if assessment and stored_assessment:
                # Compare timestamps and use the most recent
                assessment_time = assessment.get('created_at', '')
                stored_time = stored_assessment.get('timestamp', '')
                if assessment_time > stored_time:
                    latest_assessment = assessment
                else:
                    latest_assessment = stored_assessment
            elif assessment:
                latest_assessment = assessment
            elif stored_assessment:
                latest_assessment = stored_assessment
            
            if latest_assessment:
                # Use the actual recommendations from the assessment
                stream = latest_assessment.get('stream', '')
                recommendations = latest_assessment.get('recommendations', [])
                
                return {
                    'assessment': latest_assessment,
                    'career_paths': recommendations,  # Direct use of recommendations
                    'stream': stream,
                    'has_data': True
                }
            
            return {'has_data': False, 'message': 'No career assessment found'}
            
        except Exception as e:
            logger.error(f"Error getting career data: {str(e)}")
            return {'has_data': False, 'error': str(e)}
    
    def _get_career_paths_for_stream(self, stream: str) -> list:
        """Get career paths for a specific stream"""
        try:
            career_data = self.career_service.get_career_data(stream)
            if career_data.get('status') == 'success':
                return career_data.get('careers', [])
            return []
        except Exception as e:
            logger.error(f"Error getting career paths: {str(e)}")
            return []
    
    def _get_quiz_data(self, user_id: str) -> Dict[str, Any]:
        """Get quiz results for user"""
        try:
            logger.info(f"Getting quiz data for user {user_id}")
            logger.info(f"Total quiz results in storage: {len(self.quiz_service.quiz_results)}")
            
            user_quizzes = {k: v for k, v in self.quiz_service.quiz_results.items() if v.get('user_id') == user_id}
            
            logger.info(f"Found {len(user_quizzes)} quizzes for user {user_id}")
            
            if user_quizzes:
                # Calculate analytics
                total_quizzes = len(user_quizzes)
                average_score = sum(q.get('score', 0) for q in user_quizzes.values()) / total_quizzes if total_quizzes > 0 else 0
                quiz_types = list(set(q.get('quiz_type', 'Unknown') for q in user_quizzes.values()))
                
                logger.info(f"Quiz analytics: {total_quizzes} quizzes, avg score: {average_score}, types: {quiz_types}")
                
                return {
                    'total_quizzes': total_quizzes,
                    'average_score': round(average_score, 2),
                    'quiz_types': quiz_types,
                    'recent_quizzes': list(user_quizzes.values())[:5]  # Last 5 quizzes
                }
            else:
                logger.info(f"No quiz data found for user {user_id}")
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
            
            # Stream recommendation (20%)
            if stream_data and stream_data.get('best_stream'):
                profile_completion += 20
            
            # Course recommendations (20%)
            if course_data and len(course_data) > 0:
                profile_completion += 20
            
            # Quiz participation (20%)
            if quiz_data:
                profile_completion += 20
            
            # Career assessment (20%)
            user_data = self.user_data.get(user_id, {})
            if user_data.get('career_assessment'):
                profile_completion += 20
            
            # Activities/Engagement (20%)
            if user_data.get('activities') and len(user_data['activities']) > 0:
                profile_completion += 20
            
            # Calculate skills mastered based on quiz scores and career assessment
            skills_mastered = 0
            total_skills = 10
            
            if quiz_data:
                skills_mastered = min(int(quiz_data.get('average_score', 0) / 10), total_skills)
            elif user_data.get('career_assessment'):
                # Calculate skills from career assessment scores
                career_assessment = user_data['career_assessment']
                if 'scores' in career_assessment:
                    scores = career_assessment['scores']
                    avg_score = sum(scores.values()) / len(scores) if scores else 0
                    skills_mastered = min(int(avg_score / 10), total_skills)
            
            # Active courses count
            active_courses = len(course_data) if course_data else 0
            
            # Achievements (based on various activities)
            achievements = 0
            if quiz_data and quiz_data.get('total_quizzes', 0) > 0:
                achievements += 1
            if stream_data and stream_data.get('best_stream'):
                achievements += 1
            if course_data and len(course_data) > 0:
                achievements += 1
            if user_data.get('career_assessment'):
                achievements += 1
            if user_data.get('activities') and len(user_data['activities']) > 0:
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
            
            # Get all tracked activities first
            tracked_activities = user_data.get('activities', [])
            
            # Add tracked activities (page visits, assessments, etc.)
            for activity in tracked_activities:
                activities.append({
                    'type': activity.get('type', 'general'),
                    'title': activity.get('title', 'Activity'),
                    'description': activity.get('description', ''),
                    'timestamp': activity.get('timestamp', datetime.now().isoformat()),
                    'icon': activity.get('icon', 'fas fa-user')
                })
            
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
            user_quizzes = {k: v for k, v in self.quiz_service.quiz_results.items() if v.get('user_id') == user_id}
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
            
            return activities[:10]  # Return last 10 activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []
    
    def _generate_achievements(self, user_id: str, stream_data: Any, course_data: Any, quiz_data: Any, risk_data: Any) -> list:
        """Generate achievements based on user activities and progress"""
        try:
            achievements = []
            user_data = self.user_data.get(user_id, {})
            
            # First Steps Achievement
            if stream_data:
                achievements.append({
                    'title': 'Path Chosen',
                    'description': f'Stream recommendation: {stream_data.get("best_stream", "Unknown")}',
                    'icon': 'fas fa-road',
                    'date': stream_data.get('timestamp', datetime.now().isoformat()),
                    'category': 'milestone'
                })
            
            # Quiz Master Achievement
            if quiz_data and quiz_data.get('total_quizzes', 0) > 0:
                achievements.append({
                    'title': 'Quiz Participant',
                    'description': f'Completed {quiz_data.get("total_quizzes", 0)} quiz(es)',
                    'icon': 'fas fa-brain',
                    'date': datetime.now().isoformat(),
                    'category': 'badge'
                })
            
            # Course Explorer Achievement
            if course_data and isinstance(course_data, dict):
                total_courses = course_data.get('total_courses', 0)
                if total_courses > 0:
                    achievements.append({
                        'title': 'Course Explorer',
                        'description': f'Explored {total_courses} course recommendations',
                        'icon': 'fas fa-book-open',
                        'date': datetime.now().isoformat(),
                        'category': 'badge'
                    })
            
            # Risk Assessment Achievement
            if risk_data:
                achievements.append({
                    'title': 'Self-Aware',
                    'description': 'Completed dropout risk assessment',
                    'icon': 'fas fa-shield-alt',
                    'date': datetime.now().isoformat(),
                    'category': 'milestone'
                })
            
            # AI Chat Achievement
            activities = user_data.get('activities', [])
            ai_chats = [a for a in activities if a.get('type') == 'ai_chat']
            if ai_chats:
                achievements.append({
                    'title': 'AI Counselor',
                    'description': f'Had {len(ai_chats)} AI counseling session(s)',
                    'icon': 'fas fa-robot',
                    'date': datetime.now().isoformat(),
                    'category': 'badge'
                })
            
            # Active Learner Achievement (based on activity count)
            if len(activities) >= 3:
                achievements.append({
                    'title': 'Active Learner',
                    'description': f'Completed {len(activities)} platform activities',
                    'icon': 'fas fa-fire',
                    'date': datetime.now().isoformat(),
                    'category': 'milestone'
                })
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error generating achievements: {str(e)}")
            return []

    def predict_stream_for_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict stream for user using the main stream recommender"""
        try:
            user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
            
            # Store user data
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            # Here you would integrate with your existing stream prediction logic
            # For now, returning mock data - this should be replaced with actual stream prediction
            prediction = {
                'best_stream': 'PCM',
                'predictions': [
                    {'stream': 'PCM', 'probability': 85.5},
                    {'stream': 'PCB', 'probability': 72.3},
                    {'stream': 'Commerce', 'probability': 65.1}
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            self.user_data[user_id]['stream_prediction'] = prediction
            self.user_data[user_id]['stream'] = prediction['best_stream']
            
            return prediction
        except Exception as e:
            logger.error(f"Error in predict_stream_for_user: {str(e)}")
            return {'error': str(e)}

    def recommend_courses_for_user(self, stream: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get course recommendations for a stream"""
        try:
            user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
            user_profile = data.get('user_profile', {})
            
            # Store user data
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            recommendations = []
            
            # Get recommendations based on stream
            if stream.lower() == 'arts':
                try:
                    user_profile_list = [user_profile.get(feature, 50) for feature in self.arts_recommender.feature_columns]
                    recommendations = self.arts_recommender.recommend_courses(user_profile_list)
                    self.user_data[user_id]['arts_recommendations'] = recommendations
                    logger.info(f"Generated Arts recommendations for user {user_id}: {recommendations}")
                except Exception as e:
                    logger.error(f"Error generating Arts recommendations: {str(e)}")
                    # Fallback to sample recommendations
                    sample_recs = self._generate_sample_course_recommendations(user_id, 'arts')
                    logger.info(f"Used fallback Arts sample recommendations")
                
            elif stream.lower() == 'commerce':
                try:
                    user_profile_list = [user_profile.get(feature, 50) for feature in self.commerce_recommender.feature_columns]
                    recommendations = self.commerce_recommender.recommend_courses(user_profile_list)
                    self.user_data[user_id]['commerce_recommendations'] = recommendations
                    logger.info(f"Generated Commerce recommendations for user {user_id}: {recommendations}")
                except Exception as e:
                    logger.error(f"Error generating Commerce recommendations: {str(e)}")
                    # Fallback to sample recommendations
                    sample_recs = self._generate_sample_course_recommendations(user_id, 'commerce')
                    logger.info(f"Used fallback Commerce sample recommendations")
                
            elif stream.lower() == 'pcm':
                try:
                    user_profile_list = [user_profile.get(feature, 50) for feature in self.pcm_recommender.feature_columns]
                    best_course = self.pcm_recommender.predict_course(user_profile_list)
                    recommendations = self.pcm_recommender.recommend_courses(user_profile_list, top_n=5)
                    self.user_data[user_id]['pcm_recommendations'] = recommendations
                    logger.info(f"Generated PCM recommendations for user {user_id}: {recommendations}")
                except Exception as e:
                    logger.error(f"Error generating PCM recommendations: {str(e)}")
                    # Fallback to sample recommendations
                    sample_recs = self._generate_sample_course_recommendations(user_id, 'pcm')
                    logger.info(f"Used fallback PCM sample recommendations")
                
            elif stream.lower() == 'pcb':
                try:
                    user_profile_list = [user_profile.get(feature, 50) for feature in self.pcb_recommender.feature_columns]
                    recommendations = self.pcb_recommender.recommend_courses(user_profile_list)
                    self.user_data[user_id]['pcb_recommendations'] = recommendations
                    logger.info(f"Generated PCB recommendations for user {user_id}: {recommendations}")
                except Exception as e:
                    logger.error(f"Error generating PCB recommendations: {str(e)}")
                    # Fallback to sample recommendations
                    sample_recs = self._generate_sample_course_recommendations(user_id, 'pcb')
                    logger.info(f"Used fallback PCB sample recommendations")
                
            elif stream.lower() == 'vocational':
                try:
                    user_profile_list = [user_profile.get(feature, 50) for feature in self.vocational_recommender.feature_columns]
                    recommendations = self.vocational_recommender.recommend_courses(user_profile_list)
                    self.user_data[user_id]['vocational_recommendations'] = recommendations
                    logger.info(f"Generated Vocational recommendations for user {user_id}: {recommendations}")
                except Exception as e:
                    logger.error(f"Error generating Vocational recommendations: {str(e)}")
                    # Fallback to sample recommendations
                    sample_recs = self._generate_sample_course_recommendations(user_id, 'vocational')
                    logger.info(f"Used fallback Vocational sample recommendations")
            
            else:
                logger.warning(f"Unknown stream: {stream}. Using sample recommendations.")
                # Fallback to sample recommendations for unknown streams
                sample_recs = self._generate_sample_course_recommendations(user_id, stream.lower())
                logger.info(f"Used fallback sample recommendations for unknown stream: {stream}")
            
            return {'recommendations': recommendations}
            
        except Exception as e:
            logger.error(f"Error in recommend_courses_for_user: {str(e)}")
            return {'error': str(e)}

    def assess_career_for_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process career assessment"""
        try:
            user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
            
            # Process assessment using career service
            result = self.career_service.process_assessment(data)
            
            # Store in user data
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            self.user_data[user_id]['career_assessment'] = result
            
            # Track this activity
            self._track_activity(user_id, {
                'type': 'career_assessment',
                'title': 'Career Assessment Completed',
                'description': f'Stream: {data.get("stream", "Unknown")}',
                'icon': 'fas fa-route',
                'duration': 15
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in assess_career_for_user: {str(e)}")
            return {'error': str(e)}

    def submit_quiz_for_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit quiz results"""
        try:
            user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
            logger.info(f"Submitting quiz for user {user_id}: {data.get('quiz_type')} - Score: {data.get('score')}")
            
            # Store quiz result
            quiz_result = {
                'user_id': user_id,
                'quiz_type': data.get('quiz_type', 'General'),
                'score': data.get('score', 0),
                'total_questions': data.get('total_questions', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            quiz_id = f"{user_id}_{data.get('quiz_type', 'general')}_{int(datetime.now().timestamp())}"
            self.quiz_service.quiz_results[quiz_id] = quiz_result
            logger.info(f"Stored quiz result with ID: {quiz_id}")
            logger.info(f"Total quiz results in storage: {len(self.quiz_service.quiz_results)}")
            
            # Track this activity
            self._track_activity(user_id, {
                'type': 'quiz',
                'title': f'{data.get("quiz_type", "General")} Quiz Completed',
                'description': f'Score: {data.get("score", 0)}/{data.get("total_questions", 0)}',
                'icon': 'fas fa-brain',
                'duration': 10
            })
            
            return {'status': 'success', 'quiz_id': quiz_id}
            
        except Exception as e:
            logger.error(f"Error in submit_quiz_for_user: {str(e)}")
            return {'error': str(e)}

    def track_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track any user activity"""
        try:
            user_id = activity_data.get('user_id', 'anonymous')
            activity = {
                'id': f"activity_{int(datetime.now().timestamp())}_{len(self.user_data.get(user_id, {}).get('activities', []))}",
                'type': activity_data.get('type', 'general'),
                'title': activity_data.get('title', 'Activity'),
                'description': activity_data.get('description', ''),
                'timestamp': datetime.now().isoformat(),
                'icon': activity_data.get('icon', 'fas fa-user'),
                'data': activity_data.get('data', {}),
                'session_id': activity_data.get('session_id', ''),
                'duration': activity_data.get('duration', 0),
                'page': activity_data.get('page', ''),
                'action': activity_data.get('action', '')
            }
            
            # Store activity
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            if 'activities' not in self.user_data[user_id]:
                self.user_data[user_id]['activities'] = []
            
            self.user_data[user_id]['activities'].append(activity)
            
            # Keep only last 100 activities per user
            if len(self.user_data[user_id]['activities']) > 100:
                self.user_data[user_id]['activities'] = self.user_data[user_id]['activities'][-100:]
            
            return {
                'status': 'success', 
                'activity_id': activity['id'],
                'total_activities': len(self.user_data[user_id]['activities'])
            }
        except Exception as e:
            logger.error(f"Error tracking activity: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_user_activities(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """Get user's recent activities"""
        try:
            user_data = self.user_data.get(user_id, {})
            activities = user_data.get('activities', [])
            
            # Sort by timestamp (most recent first)
            activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Group activities by type
            activity_stats = {}
            for activity in activities:
                activity_type = activity.get('type', 'general')
                if activity_type not in activity_stats:
                    activity_stats[activity_type] = 0
                activity_stats[activity_type] += 1
            
            return {
                'status': 'success',
                'activities': activities[:limit],
                'total_activities': len(activities),
                'activity_stats': activity_stats,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting user activities: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_detailed_stats(self, user_id: str) -> Dict[str, Any]:
        """Get detailed user statistics"""
        try:
            # Get basic dashboard data
            basic_data = self.get_user_dashboard_data(user_id)
            
            if 'error' in basic_data:
                return {'status': 'error', 'message': basic_data['error']}
            
            # Get detailed activity analysis
            activities_data = self.get_user_activities(user_id, 100)
            
            # Calculate engagement metrics
            user_data = self.user_data.get(user_id, {})
            activities = user_data.get('activities', [])
            
            # Time-based analysis
            now = datetime.now()
            total_activities = len(activities)
            
            engagement_metrics = {
                'total_sessions': len(set(a.get('session_id', '') for a in activities if a.get('session_id'))) or 1,
                'avg_session_duration': 15,  # Default 15 minutes
                'most_active_hour': 10,  # Default 10 AM
                'most_active_day': 'Monday',  # Default
                'streak_days': 1,
                'last_activity': None,
                'total_activities': total_activities,
                'engagement_score': min(total_activities * 10, 100)  # Simple engagement score
            }
            
            # Calculate session durations and activity patterns
            session_durations = []
            hour_counts = [0] * 24
            day_counts = {}
            
            for activity in activities:
                try:
                    activity_time = datetime.fromisoformat(activity.get('timestamp', '').replace('Z', '+00:00'))
                    
                    # Hour analysis
                    hour_counts[activity_time.hour] += 1
                    
                    # Day analysis
                    day_name = activity_time.strftime('%A')
                    day_counts[day_name] = day_counts.get(day_name, 0) + 1
                    
                    # Session duration
                    if activity.get('duration', 0) > 0:
                        session_durations.append(activity['duration'])
                    
                    # Last activity
                    if not engagement_metrics['last_activity'] or activity_time > datetime.fromisoformat(engagement_metrics['last_activity'].replace('Z', '+00:00')):
                        engagement_metrics['last_activity'] = activity.get('timestamp')
                        
                except:
                    continue
            
            # Calculate averages and most common values
            if session_durations:
                engagement_metrics['avg_session_duration'] = sum(session_durations) / len(session_durations)
            
            if hour_counts:
                engagement_metrics['most_active_hour'] = hour_counts.index(max(hour_counts))
            
            if day_counts:
                engagement_metrics['most_active_day'] = max(day_counts, key=day_counts.get)
            
            # Prepare basic stats using proper calculation
            stream_data = basic_data.get('stream_recommendation')
            course_data = basic_data.get('course_recommendations', {}).get('current_stream_recommendations', [])
            quiz_data = basic_data.get('quiz_results')
            risk_data = basic_data.get('dropout_risk')
            
            logger.info(f"Stats calculation - stream_data: {bool(stream_data)}, course_data: {len(course_data)}, quiz_data: {bool(quiz_data)}, risk_data: {bool(risk_data)}")
            logger.info(f"User data keys: {list(self.user_data.get(user_id, {}).keys())}")
            
            basic_stats = self._calculate_user_stats(user_id, stream_data, course_data, quiz_data, risk_data)
            logger.info(f"Calculated basic_stats: {basic_stats}")
            
            # Prepare achievements
            achievements = []
            if basic_data.get('quiz_results'):
                achievements.append({
                    'title': 'Quiz Champion',
                    'description': f"Completed {basic_data['quiz_results'].get('total_quizzes', 0)} quizzes",
                    'icon': 'fas fa-trophy',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            
            if basic_data.get('stream_recommendation'):
                achievements.append({
                    'title': 'Stream Selected',
                    'description': f"Chosen {basic_data['stream_recommendation'].get('best_stream', 'Unknown')} stream",
                    'icon': 'fas fa-graduation-cap',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            
            # Prepare recommendations
            recommendations = []
            course_recs = basic_data.get('course_recommendations', {})
            
            # Handle new course recommendations structure
            if isinstance(course_recs, dict) and course_recs.get('all_stream_recommendations'):
                all_recs = course_recs.get('all_stream_recommendations', {})
                for stream, stream_data in all_recs.items():
                    if stream_data and isinstance(stream_data, dict):
                        rec_list = stream_data.get('recommendations', [])
                        if rec_list and len(rec_list) > 0:
                            recommendations.append({
                                'stream': stream,
                                'courses': rec_list,
                                'best_course': stream_data.get('best_course', 'Unknown'),
                                'careers': stream_data.get('careers', [])
                            })
            else:
                # Fallback for old structure
                for stream, courses in course_recs.items():
                    if courses and len(courses) > 0:
                        recommendations.append({
                            'title': f'{stream.title()} Courses',
                            'description': f"Explore {len(courses)} recommended courses",
                            'icon': 'fas fa-book',
                            'action': 'view_courses'
                        })
            
            return {
                'status': 'success',
                'basic_stats': basic_stats,
                'engagement_metrics': engagement_metrics,
                'achievements': achievements,
                'recommendations': recommendations,
                'stream_recommendation': basic_data.get('stream_recommendation'),
                'course_recommendations': basic_data.get('course_recommendations'),
                'quiz_results': basic_data.get('quiz_results'),
                'dropout_risk': basic_data.get('dropout_risk'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting detailed stats: {str(e)}")
            return {
                'status': 'success',  # Return success with default data
                'basic_stats': {
                    'profile_completion': 0,
                    'skills_mastered': 0,
                    'active_courses': 0
                },
                'engagement_metrics': {
                    'total_sessions': 0,
                    'avg_session_duration': 0,
                    'most_active_hour': 0,
                    'most_active_day': '-',
                    'streak_days': 0,
                    'last_activity': None
                },
                'achievements': [],
                'recommendations': [],
                'last_updated': datetime.now().isoformat()
            }
    
    def _analyze_skill_progression(self, user_id: str) -> Dict[str, Any]:
        """Analyze skill progression over time"""
        try:
            user_data = self.user_data.get(user_id, {})
            quiz_data = user_data.get('quiz_results', {})
            
            # Group quiz results by skill type over time
            skill_timeline = {}
            
            for quiz_id, result in quiz_data.items():
                quiz_type = result.get('quiz_type', 'General')
                score = result.get('score', 0)
                timestamp = result.get('timestamp', '')
                
                if quiz_type not in skill_timeline:
                    skill_timeline[quiz_type] = []
                
                skill_timeline[quiz_type].append({
                    'score': score,
                    'timestamp': timestamp,
                    'improvement': 0
                })
            
            # Calculate improvement for each skill
            for skill_type, results in skill_timeline.items():
                results.sort(key=lambda x: x['timestamp'])
                if len(results) > 1:
                    first_score = results[0]['score']
                    last_score = results[-1]['score']
                    improvement = last_score - first_score
                    results[-1]['improvement'] = improvement
            
            return {
                'skill_timeline': skill_timeline,
                'total_skills_tracked': len(skill_timeline),
                'average_improvement': sum(r[-1].get('improvement', 0) for r in skill_timeline.values() if r) / max(len(skill_timeline), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skill progression: {str(e)}")
            return {'skill_timeline': {}, 'total_skills_tracked': 0, 'average_improvement': 0}
    
    def _analyze_risk_trend(self, user_id: str) -> Dict[str, Any]:
        """Analyze dropout risk trend over time"""
        try:
            user_data = self.user_data.get(user_id, {})
            risk_assessments = []
            
            # Extract risk assessments from activities
            activities = user_data.get('activities', [])
            for activity in activities:
                if activity.get('type') == 'dropout_risk_assessment':
                    risk_data = activity.get('data', {})
                    if 'risk_level' in risk_data:
                        risk_assessments.append({
                            'risk_level': risk_data['risk_level'],
                            'timestamp': activity.get('timestamp'),
                            'factors': risk_data.get('risk_factors', [])
                        })
            
            # Sort by timestamp
            risk_assessments.sort(key=lambda x: x['timestamp'])
            
            # Calculate trend
            trend = 'stable'
            if len(risk_assessments) > 1:
                first_risk = risk_assessments[0]['risk_level']
                last_risk = risk_assessments[-1]['risk_level']
                
                if last_risk > first_risk:
                    trend = 'increasing'
                elif last_risk < first_risk:
                    trend = 'decreasing'
            
            return {
                'assessments': risk_assessments,
                'trend': trend,
                'total_assessments': len(risk_assessments),
                'current_risk': risk_assessments[-1]['risk_level'] if risk_assessments else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk trend: {str(e)}")
            return {'assessments': [], 'trend': 'stable', 'total_assessments': 0, 'current_risk': None}
    
    def _get_tracking_scores(self, user_id: str) -> Dict[str, Any]:
        """Get user's assessment tracking scores including quiz scores"""
        try:
            user_data = self.user_data.get(user_id, {})
            activities = user_data.get('activities', [])
            
            # Extract assessment scores from activities
            assessment_scores = []
            assessment_dates = []
            assessment_types = []
            
            # Get quiz scores from quiz service
            try:
                quiz_analytics = self.quiz_service.get_score_analytics()
                quiz_results = self.quiz_service.quiz_results
                
                # Process quiz results for this user
                for result_id, result in quiz_results.items():
                    # Check if this result belongs to the current user
                    # (Assuming user_id is stored in the result or we match by timestamp)
                    if self._is_user_quiz_result(result, user_id, activities):
                        score = result.get('score', 0) or result.get('percentage', 0)
                        assessment_scores.append(score)
                        assessment_dates.append(result.get('timestamp', ''))
                        assessment_types.append(f"Quiz: {result.get('quiz_type', 'Unknown').title()}")
            except Exception as e:
                logger.warning(f"Could not fetch quiz analytics: {str(e)}")
                quiz_analytics = {}
                quiz_results = {}
            
            # Process other assessment activities
            for activity in activities:
                if activity.get('type') in ['stream_prediction', 'course_recommendation', 'career_assessment']:
                    # Extract score from activity data
                    data = activity.get('data', {})
                    score = None
                    
                    if 'score' in data:
                        score = data['score']
                    elif 'confidence' in data:
                        # Convert confidence to percentage
                        score = data.get('confidence', 0) * 100
                    elif 'similarity_scores' in data:
                        # Use average similarity score
                        similarities = data['similarity_scores']
                        if similarities:
                            score = (sum(similarities) / len(similarities)) * 100
                    
                    if score is not None:
                        assessment_scores.append(round(score, 1))
                        assessment_dates.append(activity.get('timestamp', ''))
                        assessment_types.append(activity.get('type', 'Assessment').replace('_', ' ').title())
            
            # Sort by date to maintain chronological order
            scored_items = list(zip(assessment_scores, assessment_dates, assessment_types))
            scored_items.sort(key=lambda x: x[1] if x[1] else '')
            
            # Unsorted after sorting
            if scored_items:
                assessment_scores, assessment_dates, assessment_types = zip(*scored_items)
                assessment_scores = list(assessment_scores)
                assessment_dates = list(assessment_dates)
                assessment_types = list(assessment_types)
            
            # Calculate statistics
            highest_score = max(assessment_scores) if assessment_scores else 0
            average_score = round(sum(assessment_scores) / len(assessment_scores), 1) if assessment_scores else 0
            total_assessments = len(assessment_scores)
            
            # Calculate improvement rate (compare first half with second half)
            improvement_rate = 0
            if total_assessments >= 2:
                mid_point = total_assessments // 2
                first_half_avg = sum(assessment_scores[:mid_point]) / mid_point if mid_point > 0 else 0
                second_half_avg = sum(assessment_scores[mid_point:]) / (total_assessments - mid_point) if total_assessments - mid_point > 0 else 0
                if first_half_avg > 0:
                    improvement_rate = round(((second_half_avg - first_half_avg) / first_half_avg) * 100, 1)
            
            # Format dates for display
            formatted_dates = []
            for date_str in assessment_dates:
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            # Try to parse ISO format
                            from datetime import datetime
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            formatted_dates.append(dt.strftime('%m/%d/%Y'))
                        else:
                            # If it's already a datetime object
                            from datetime import datetime
                            dt = datetime.fromtimestamp(date_str / 1000 if isinstance(date_str, (int, float)) else date_str)
                            formatted_dates.append(dt.strftime('%m/%d/%Y'))
                    except:
                        formatted_dates.append('Unknown')
                else:
                    formatted_dates.append('Unknown')
            
            # Get quiz-specific analytics with enhanced categorization
            quiz_stats = {}
            
            # Try to get data from quiz service first
            try:
                quiz_analytics = self.quiz_service.get_score_analytics()
                quiz_results = self.quiz_service.quiz_results
                
                # Process quiz results for this user to create detailed breakdown
                user_quiz_results = {}
                for result_id, result in quiz_results.items():
                    if self._is_user_quiz_result(result, user_id, activities):
                        quiz_type = result.get('quiz_type', 'unknown')
                        score = result.get('score', 0) or result.get('percentage', 0)
                        
                        if quiz_type not in user_quiz_results:
                            user_quiz_results[quiz_type] = []
                        user_quiz_results[quiz_type].append(score)
                
                # Create enhanced quiz breakdown
                for quiz_type, scores in user_quiz_results.items():
                    if scores:
                        quiz_stats[quiz_type] = {
                            'count': len(scores),
                            'best_score': max(scores),
                            'average_score': round(sum(scores) / len(scores), 1),
                            'latest_score': scores[-1] if scores else 0,
                            'category': self._get_quiz_category(quiz_type)
                        }
                
                # Add aptitude quiz categories
                aptitude_quizzes = ['creativity', 'logical', 'analytical', 'communication', 'numerical', 'artistic', 'practical']
                subject_quizzes = ['mathematics', 'science', 'biology', 'english', 'social_studies', 'language']
                
                # Ensure aptitude quizzes are represented
                for quiz_type in aptitude_quizzes:
                    if quiz_type not in quiz_stats:
                        quiz_stats[quiz_type] = {
                            'count': 0,
                            'best_score': 0,
                            'average_score': 0,
                            'latest_score': 0,
                            'category': 'Aptitude'
                        }
                
                # Ensure subject quizzes are represented
                for quiz_type in subject_quizzes:
                    if quiz_type not in quiz_stats:
                        quiz_stats[quiz_type] = {
                            'count': 0,
                            'best_score': 0,
                            'average_score': 0,
                            'latest_score': 0,
                            'category': 'Subject'
                        }
                        
            except Exception as e:
                logger.warning(f"Could not fetch quiz analytics: {str(e)}")
                # Provide fallback data structure to prevent disruption
                quiz_stats = self._get_fallback_quiz_data()
            
            # Add summary statistics
            total_aptitude = sum(1 for q in quiz_stats.values() if q.get('category') == 'Aptitude' and q['count'] > 0)
            total_subject = sum(1 for q in quiz_stats.values() if q.get('category') == 'Subject' and q['count'] > 0)
            
            return {
                'history': assessment_scores,
                'dates': formatted_dates,
                'types': assessment_types,
                'highest': highest_score,
                'average': average_score,
                'total': total_assessments,
                'improvement': f"{improvement_rate}%" if improvement_rate != 0 else "0%",
                'quiz_breakdown': quiz_stats,
                'total_quizzes': quiz_analytics.get('total_quizzes_completed', 0) if 'quiz_analytics' in locals() else sum(q['count'] for q in quiz_stats.values()),
                'quiz_summary': {
                    'aptitude_quizzes_taken': total_aptitude,
                    'subject_quizzes_taken': total_subject,
                    'best_aptitude_score': max([q['best_score'] for q in quiz_stats.values() if q.get('category') == 'Aptitude'] + [0]),
                    'best_subject_score': max([q['best_score'] for q in quiz_stats.values() if q.get('category') == 'Subject'] + [0])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting tracking scores: {str(e)}")
            return {
                'history': [],
                'dates': [],
                'types': [],
                'highest': 0,
                'average': 0,
                'total': 0,
                'improvement': '0%',
                'quiz_breakdown': {},
                'total_quizzes': 0
            }
    
    def _get_quiz_category(self, quiz_type: str) -> str:
        """Categorize quiz type as Aptitude or Subject"""
        aptitude_quizzes = ['creativity', 'logical', 'analytical', 'communication', 'numerical', 'artistic', 'practical']
        subject_quizzes = ['mathematics', 'science', 'biology', 'english', 'social_studies', 'language']
        
        if quiz_type.lower() in aptitude_quizzes:
            return 'Aptitude'
        elif quiz_type.lower() in subject_quizzes:
            return 'Subject'
        else:
            return 'General'
    
    def _get_fallback_quiz_data(self) -> Dict[str, Any]:
        """Provide fallback quiz data structure to prevent disruption"""
        aptitude_quizzes = ['creativity', 'logical', 'analytical', 'communication', 'numerical', 'artistic', 'practical']
        subject_quizzes = ['mathematics', 'science', 'biology', 'english', 'social_studies', 'language']
        
        quiz_stats = {}
        
        # Add aptitude quizzes with zero data
        for quiz_type in aptitude_quizzes:
            quiz_stats[quiz_type] = {
                'count': 0,
                'best_score': 0,
                'average_score': 0,
                'latest_score': 0,
                'category': 'Aptitude'
            }
        
        # Add subject quizzes with zero data
        for quiz_type in subject_quizzes:
            quiz_stats[quiz_type] = {
                'count': 0,
                'best_score': 0,
                'average_score': 0,
                'latest_score': 0,
                'category': 'Subject'
            }
        
        return quiz_stats

    def _is_user_quiz_result(self, result: Dict, user_id: str, activities: List[Dict]) -> bool:
        """Check if a quiz result belongs to the user"""
        try:
            # First check if user_id is directly stored in the result
            result_user_id = result.get('user_id')
            if result_user_id:
                # Check for exact match or partial match (for generated user IDs)
                if result_user_id == user_id or user_id in result_user_id or result_user_id in user_id:
                    return True
            
            # Fallback to timestamp matching if user_id is not stored
            result_timestamp = result.get('timestamp', '')
            if not result_timestamp:
                return False
            
            # Convert timestamps to comparable format
            from datetime import datetime
            result_dt = datetime.fromisoformat(result_timestamp.replace('Z', '+00:00'))
            
            # Check if there's an activity with similar timestamp (within 1 minute)
            for activity in activities:
                if activity.get('type') == 'quiz_completed':
                    activity_timestamp = activity.get('timestamp', '')
                    if activity_timestamp:
                        activity_dt = datetime.fromisoformat(activity_timestamp.replace('Z', '+00:00'))
                        time_diff = abs((result_dt - activity_dt).total_seconds())
                        if time_diff < 60:  # Within 1 minute
                            return True
            
            # If no matching activity, accept recent quiz results (within last 24 hours)
            # This is a fallback - ideally we'd store user_id in quiz results
            from datetime import datetime, timedelta
            time_since_result = (datetime.now() - result_dt).total_seconds()
            return time_since_result < 86400  # Within last 24 hours
            
        except:
            return False
    
    def _generate_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        try:
            user_data = self.user_data.get(user_id, {})
            recommendations = {
                'academic': [],
                'career': [],
                'skill_development': [],
                'risk_intervention': []
            }
            
            # Academic recommendations
            if not user_data.get('stream_prediction'):
                recommendations['academic'].append({
                    'type': 'stream_assessment',
                    'title': 'Complete Stream Assessment',
                    'description': 'Take the stream prediction test to get personalized course recommendations',
                    'priority': 'high',
                    'action': 'Take Assessment'
                })
            
            # Quiz performance recommendations
            quiz_data = user_data.get('quiz_results', {})
            if quiz_data:
                avg_score = sum(q.get('score', 0) for q in quiz_data.values()) / len(quiz_data)
                if avg_score < 70:
                    recommendations['skill_development'].append({
                        'type': 'improve_skills',
                        'title': 'Improve Quiz Performance',
                        'description': f'Your average score is {avg_score:.1f}%. Consider studying core concepts.',
                        'priority': 'medium',
                        'action': 'Study Resources'
                    })
            
            # Risk-based recommendations
            risk_data = user_data.get('dropout_assessment', {})
            if risk_data:
                risk_score = risk_data.get('risk_score', 0)
                # Handle both numeric and string risk levels
                if isinstance(risk_score, (int, float)) and risk_score > 50:
                    recommendations['risk_intervention'].append({
                        'type': 'counseling',
                        'title': 'Schedule Counseling Session',
                        'description': 'Your risk assessment indicates need for additional support',
                        'priority': 'high',
                        'action': 'Book Appointment'
                    })
                elif isinstance(risk_score, str):
                    # Try to extract numeric value from string like "32.5%" or "Moderate Risk"
                    import re
                    numbers = re.findall(r'\d+\.?\d*', risk_score)
                    if numbers and float(numbers[0]) > 50:
                        recommendations['risk_intervention'].append({
                            'type': 'counseling',
                            'title': 'Schedule Counseling Session',
                            'description': 'Your risk assessment indicates need for additional support',
                            'priority': 'high',
                            'action': 'Book Appointment'
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {'academic': [], 'career': [], 'skill_development': [], 'risk_intervention': []}
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get overall dashboard overview for all users"""
        try:
            total_users = len(self.user_data)
            total_activities = sum(len(user.get('activities', [])) for user in self.user_data.values())
            
            # User engagement breakdown
            active_users = len([uid for uid, user in self.user_data.items() 
                              if len(user.get('activities', [])) > 0])
            
            # Module usage statistics
            module_stats = {}
            for user_data in self.user_data.values():
                activities = user_data.get('activities', [])
                for activity in activities:
                    module = activity.get('type', 'general')
                    if module not in module_stats:
                        module_stats[module] = 0
                    module_stats[module] += 1
            
            # Risk assessment overview
            risk_assessments = 0
            high_risk_users = 0
            for user_data in self.user_data.values():
                if user_data.get('dropout_assessment'):
                    risk_assessments += 1
                    if user_data['dropout_assessment'].get('risk_level', 0) > 70:
                        high_risk_users += 1
            
            return {
                'status': 'success',
                'total_users': total_users,
                'active_users': active_users,
                'total_activities': total_activities,
                'engagement_rate': (active_users / total_users * 100) if total_users > 0 else 0,
                'module_usage': module_stats,
                'risk_assessments': risk_assessments,
                'high_risk_users': high_risk_users,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting overview stats: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def assess_dropout_risk_for_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess dropout risk"""
        try:
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
            result = self.dropout_risk_service.assess_risk(mapped_data)
            
            # Store in user data
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            self.user_data[user_id]['dropout_assessment'] = result
            self.user_data[user_id]['form_data'] = data  # Store original form data
            
            # Track this activity
            self._track_activity(user_id, {
                'type': 'dropout_assessment',
                'title': 'Dropout Risk Assessment Completed',
                'description': f'Risk level: {result.get("risk_level", "Unknown")}',
                'icon': 'fas fa-exclamation-triangle',
                'duration': 5
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in assess_dropout_risk_for_user: {str(e)}")
            return {'error': str(e)}
    
    def _track_activity(self, user_id: str, activity_data: Dict[str, Any]) -> None:
        """Track user activity"""
        try:
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            if 'activities' not in self.user_data[user_id]:
                self.user_data[user_id]['activities'] = []
            
            activity = {
                'id': str(datetime.now().timestamp()),
                'timestamp': datetime.now().isoformat(),
                **activity_data
            }
            
            self.user_data[user_id]['activities'].append(activity)
            
            # Keep only last 50 activities
            if len(self.user_data[user_id]['activities']) > 50:
                self.user_data[user_id]['activities'] = self.user_data[user_id]['activities'][-50:]
                
        except Exception as e:
            logger.error(f"Error tracking activity: {str(e)}")
