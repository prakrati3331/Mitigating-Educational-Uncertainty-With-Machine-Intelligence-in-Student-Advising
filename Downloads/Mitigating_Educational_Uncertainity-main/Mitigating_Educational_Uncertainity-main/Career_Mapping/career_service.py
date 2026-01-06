import json
from datetime import datetime
import logging
from typing import Dict, Any, Optional
import importlib

from .data.career_data import CAREER_DATA
from .database.db import get_db

class CareerService:
    def __init__(self, db_connection=None):
        """Initialize the CareerService with an optional database connection."""
        self.db = db_connection or get_db()
        self.logger = logging.getLogger(__name__)
        self._career_data = None

    def _get_career_data(self):
        """Get career data, reloading if necessary."""
        if self._career_data is None:
            # Reload the career data module to get latest changes
            try:
                importlib.reload(importlib.import_module('Career_Mapping.data.career_data'))
                from .data.career_data import CAREER_DATA as updated_career_data
                self._career_data = updated_career_data
                self.logger.info(f"Reloaded career data with {len(self._career_data)} streams")
            except Exception as e:
                self.logger.error(f"Failed to reload career data: {e}")
                self._career_data = CAREER_DATA
        return self._career_data

    def calculate_career_compatibility(self, career: Dict[str, Any], scores: Dict[str, float]) -> float:
        """Calculate how well a career matches the user's scores."""
        compatibility = 0
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
            'Attention to Detail': scores.get('analytical', 0),
            'Logic': scores.get('logical', 0),
            'Leadership': (scores.get('communication', 0) + scores.get('social', 0)) / 2,
            'Conflict Resolution': scores.get('communication', 0),
            'Strategic Planning': scores.get('analytical', 0),
            'Excel': scores.get('numerical', 0),
            'Recruitment': (scores.get('communication', 0) + scores.get('social', 0)) / 2,
            'Employee Relations': scores.get('communication', 0),
            'Labor Laws': scores.get('analytical', 0),
            'Supply Chain Management': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,
            'Inventory Control': scores.get('analytical', 0),
            'Logistics': (scores.get('analytical', 0) + scores.get('practical', 0)) / 2,
            'Brand Management': (scores.get('creativity', 0) + scores.get('communication', 0)) / 2,
            'Digital Marketing': (scores.get('creativity', 0) + scores.get('communication', 0)) / 2,
            'Market Research': (scores.get('analytical', 0) + scores.get('social', 0)) / 2,
            'Scientific Method': (scores.get('analytical', 0) + scores.get('logical', 0)) / 2,
            'Laboratory Skills': (scores.get('practical', 0) + scores.get('science', 0)) / 2,
            'Technical Drawing': (scores.get('practical', 0) + scores.get('creativity', 0)) / 2,
            'Machine Learning': scores.get('analytical', 0),
            'Data Visualization': (scores.get('analytical', 0) + scores.get('creativity', 0)) / 2,
            'Environmental Science': scores.get('science', 0),
            'Policy Analysis': (scores.get('analytical', 0) + scores.get('social', 0)) / 2,
            'Field Work': (scores.get('practical', 0) + scores.get('science', 0)) / 2,
            'Design Software': (scores.get('creativity', 0) + scores.get('practical', 0)) / 2,
            'Color Theory': scores.get('creativity', 0),
            'Typography': scores.get('creativity', 0),
            'Aerodynamics': scores.get('science', 0),
            'Thermodynamics': scores.get('science', 0),
            'Physics': scores.get('science', 0)
        }

        total_possible = 0
        total_achieved = 0

        for skill in career['skills']:
            if skill in skill_score_mapping:
                total_possible += 10  # Max score per skill
                total_achieved += skill_score_mapping[skill]
            else:
                self.logger.warning(f"Skill '{skill}' not found in mapping for career '{career['title']}'")

        if total_possible > 0:
            compatibility = (total_achieved / total_possible) * 100
        else: 
            # If no skills match, use average of all scores as a fallback
            avg_score = sum(scores.values()) / len(scores) if scores else 50
            compatibility = avg_score * 10  # Scale to 0-100 range
            self.logger.warning(f"No matching skills found for career '{career['title']}', using average score: {compatibility}")

        return round(compatibility, 1)

    def get_career_data(self, stream: str) -> Dict[str, Any]:
        """Get career data for a specific stream."""
        if stream in CAREER_DATA:
            return {'status': 'success', 'data': CAREER_DATA[stream]}
        return {'status': 'error', 'message': 'Stream not found'}

    def process_assessment(self, data: Dict[str, Any], ip_address: Optional[str] = None,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process career assessment data and return recommendations."""
        try:
            self.logger.info(f"Processing assessment data: {data}")
            
            # Extract scores and stream
            stream = data.get('stream', 'Vocational')
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

            # Get career recommendations for the selected stream
            career_data = self._get_career_data()
            careers = career_data.get(stream, [])
            self.logger.info(f"Found {len(careers)} careers for stream {stream}")

            # Calculate compatibility scores for each career
            career_recommendations = []
            for career in careers:
                compatibility_score = self.calculate_career_compatibility(career, scores)
                career_recommendations.append({
                    'title': career['title'],
                    'type': career['type'],
                    'compatibility_score': round(compatibility_score, 2),
                    'skills': career.get('skills', []),
                    'courses': career.get('courses', []),
                    'exams': career.get('exams', [])
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
            result = self.db.db.assessments.insert_one(assessment_doc)
            assessment_id = str(result.inserted_id)
            self.logger.info(f"Assessment saved with ID: {assessment_id}")

            # Prepare response
            response_data = {
                'status': 'success',
                'assessment_id': assessment_id,
                'stream': stream,
                'scores': scores,
                'recommendations': career_recommendations,
                'timestamp': assessment_doc['created_at'].isoformat()
            }

            return response_data

        except Exception as e:
            self.logger.error(f"Error processing assessment: {str(e)}", exc_info=True)
            raise

    def get_latest_assessment(self, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the latest assessment for a user."""
        try:
            query = {}
            if user_id:
                query['user_id'] = user_id
                
            latest_assessment = self.db.db.assessments.find_one(
                query,
                sort=[('_id', -1)]  # Get the most recent assessment
            )
            
            if latest_assessment:
                # Convert ObjectId to string for JSON serialization
                latest_assessment['_id'] = str(latest_assessment['_id'])
                # Convert datetime to string
                latest_assessment['created_at'] = latest_assessment['created_at'].isoformat()
                if 'updated_at' in latest_assessment:
                    latest_assessment['updated_at'] = latest_assessment['updated_at'].isoformat()
                
                self.logger.info(f"Found assessment data: {latest_assessment['_id']}")
                return latest_assessment
                
            self.logger.warning("No assessment data found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving assessment data: {str(e)}", exc_info=True)
            raise
