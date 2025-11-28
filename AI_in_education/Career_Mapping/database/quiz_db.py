"""
Database operations for quizzes and interests
"""
from pymongo import ReturnDocument
from datetime import datetime
import logging
from .db import get_db
from ..data.quizzes import get_quiz, get_interest_questions, get_career_interest

logger = logging.getLogger(__name__)

class QuizDB:
    """Handles quiz and interest assessment data operations"""
    
    def __init__(self):
        self.db = get_db()
        # Get the database instance and then the collections
        self.quizzes = self.db.db.quizzes
        self.quiz_responses = self.db.db.quiz_responses
        self.user_interests = self.db.db.user_interests
        
    def get_quiz(self, quiz_type):
        """Get quiz by type"""
        return get_quiz(quiz_type)
    
    def get_interest_questions(self):
        """Get all interest assessment questions"""
        return get_interest_questions()
    
    def save_quiz_response(self, user_id, quiz_type, responses, result):
        """Save user's quiz response"""
        try:
            doc = {
                'user_id': user_id,
                'quiz_type': quiz_type,
                'responses': responses,
                'result': result,
                'completed_at': datetime.utcnow()
            }
            
            result = self.quiz_responses.insert_one(doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving quiz response: {e}")
            raise
    
    def save_user_interests(self, user_id, interests):
        """Save or update user's interest assessment"""
        try:
            doc = {
                'user_id': user_id,
                'interests': interests,
                'updated_at': datetime.utcnow()
            }
            
            result = self.user_interests.find_one_and_update(
                {'user_id': user_id},
                {'$set': doc},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            
            return str(result['_id'])
            
        except Exception as e:
            logger.error(f"Error saving user interests: {e}")
            raise
    
    def get_user_quiz_history(self, user_id, quiz_type=None, limit=10):
        """Get user's quiz history"""
        try:
            query = {'user_id': user_id}
            if quiz_type:
                query['quiz_type'] = quiz_type
                
            return list(self.quiz_responses
                       .find(query)
                       .sort('completed_at', -1)
                       .limit(limit))
            
        except Exception as e:
            logger.error(f"Error fetching quiz history: {e}")
            return []
    
    def get_user_interests(self, user_id):
        """Get user's saved interests"""
        try:
            return self.user_interests.find_one(
                {'user_id': user_id},
                sort=[('updated_at', -1)]
            )
        except Exception as e:
            logger.error(f"Error fetching user interests: {e}")
            return None

# Create a singleton instance
quiz_db = QuizDB()

def get_quiz_db():
    """Get the quiz database instance"""
    return quiz_db
