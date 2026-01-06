import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class QuizService:
    def __init__(self, data_file: str = None):
        """Initialize the QuizService with quiz data and storage paths."""
        # Initialize quiz data (moved from QUIZ_DATA in flask_app.py)
        self.QUIZ_DATA = {
            'creativity': [
                {
                    'question': "Alternate Uses: You're given a plain brick. Which use is the most original and useful?",
                    'options': ["A) Doorstop", "B) Garden marker with painted labels", "C) Modular bookend system (stack & interlock)", "D) Paperweight"],
                    'answer': "C) Modular bookend system (stack & interlock)",
                    'explanation': "This option transforms the brick into a new, reusable product with modular functionality, combining originality and practicality."
                },
                # ... (other quiz questions would be added here)
            ],
            'logical': [
                {
                    'question': "Pattern completion: What is the next number in the sequence? 2, 6, 12, 20, 30, ?",
                    'options': ["A) 36", "B) 40", "C) 42", "D) 48"],
                    'answer': "C) 42",
                    'explanation': "This sequence is formed by adding 4, 6, 8, 10, ... to the previous term. The next difference should be 12, so the next number in the sequence is 30 + 12 = 42."
                },
                # ... (other quiz questions would be added here)
            ],
            # ... (other quiz types would be added here)
        }
        
        # Initialize storage
        self.quiz_results = {}  # type: Dict[str, Dict]
        self.quiz_progress = {}  # type: Dict[str, Dict]
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), 'quiz_data.json')
        
        # Load existing data if file exists
        self._load_data()

    def _load_data(self) -> None:
        """Load quiz data from file if it exists."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.quiz_results = data.get('results', {})
                    self.quiz_progress = data.get('progress', {})
        except Exception as e:
            print(f"Error loading quiz data: {e}")

    def _save_data(self) -> None:
        """Save quiz data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    'results': self.quiz_results,
                    'progress': self.quiz_progress
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving quiz data: {e}")

    def get_quiz(self, quiz_type: str) -> Dict[str, Any]:
        """Get quiz questions for a specific type."""
        if quiz_type not in self.QUIZ_DATA:
            return {'error': f'Quiz type "{quiz_type}" not found'}, 404

        questions = self.QUIZ_DATA[quiz_type]
        shuffled_questions = random.sample(questions, min(len(questions), 10))
        
        return {
            'quiz_type': quiz_type,
            'questions': shuffled_questions,
            'total_questions': len(shuffled_questions)
        }

    def submit_quiz(self, quiz_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit quiz answers and calculate score."""
        try:
            user_answers = data.get('answers', {})
            completed_locally = data.get('completed_locally', False)
            client_score = data.get('client_score')
            client_total = data.get('client_total')

            if quiz_type not in self.QUIZ_DATA:
                return {'error': f'Quiz type "{quiz_type}" not found'}, 404

            questions = self.QUIZ_DATA[quiz_type]

            if completed_locally and client_score is not None and client_total is not None:
                # Use client's calculation
                score = client_score
                total_questions = client_total
                percentage = (score / total_questions) * 100 if total_questions > 0 else 0
                results = self._create_client_results(questions, user_answers)
            else:
                # Server-side calculation
                score, total_questions, results = self._calculate_score(questions, user_answers)
                percentage = (score / total_questions) * 100 if total_questions > 0 else 0

            # Store result
            result_id = self._store_quiz_result(
                quiz_type, score, total_questions, 
                percentage, results, completed_locally
            )

            return {
                'result_id': result_id,
                'quiz_type': quiz_type,
                'score': score,
                'total_questions': total_questions,
                'percentage': round(percentage, 1),
                'results': results
            }

        except Exception as e:
            return {'error': str(e)}, 500

    def _create_client_results(self, questions: List[Dict], user_answers: Dict) -> List[Dict]:
        """Create results using client's calculation."""
        results = []
        for i, (question_key, user_answer) in enumerate(user_answers.items()):
            if i < len(questions):
                question = questions[i]
                results.append({
                    'question': question['question'],
                    'user_answer': user_answer,
                    'correct_answer': question['answer'],
                    'is_correct': True,  # Trust client's calculation
                    'explanation': question['explanation']
                })
        return results

    def _calculate_score(self, questions: List[Dict], user_answers: Dict) -> Tuple[int, int, List[Dict]]:
        """Calculate score and generate results server-side."""
        score = 0
        total_questions = len(user_answers)
        results = []

        for i, (question_key, user_answer) in enumerate(user_answers.items()):
            if i < len(questions):
                question = questions[i]
                correct_answer = question['answer']
                is_correct = user_answer == correct_answer

                if is_correct:
                    score += 10  # 10 points per correct answer

                results.append({
                    'question': question['question'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'explanation': question['explanation']
                })

        return score, total_questions, results

    def _store_quiz_result(self, quiz_type: str, score: int, total_questions: int,
                         percentage: float, results: List[Dict], completed_locally: bool) -> str:
        """Store quiz result and return result ID."""
        result_id = f"{quiz_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.quiz_results[result_id] = {
            'quiz_type': quiz_type,
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'completed_locally': completed_locally
        }
        self._save_data()
        return result_id

    def get_quiz_result(self, result_id: str) -> Dict:
        """Get a specific quiz result by ID."""
        return self.quiz_results.get(result_id)

    def get_all_results(self) -> Dict[str, Any]:
        """Get all quiz results."""
        return {
            'results': list(self.quiz_results.values()),
            'total_results': len(self.quiz_results)
        }

    def get_score_analytics(self) -> Dict[str, Any]:
        """Get comprehensive score analytics across all quiz types."""
        try:
            all_results = list(self.quiz_results.values())
            progress_data = list(self.quiz_progress.values())

            analytics = {
                'total_quizzes_completed': len(all_results),
                'total_progress_sessions': len(progress_data),
                'quiz_type_breakdown': {},
                'average_scores': {},
                'improvement_tracking': {},
                'recent_activity': []
            }

            # Analyze by quiz type
            for result in all_results:
                quiz_type = result['quiz_type']
                if quiz_type not in analytics['quiz_type_breakdown']:
                    analytics['quiz_type_breakdown'][quiz_type] = {
                        'count': 0,
                        'total_score': 0,
                        'best_score': 0,
                        'average_score': 0
                    }

                quiz_stats = analytics['quiz_type_breakdown'][quiz_type]
                quiz_stats['count'] += 1
                quiz_stats['total_score'] += result['score']
                quiz_stats['best_score'] = max(quiz_stats['best_score'], result['score'])
                quiz_stats['average_score'] = round(quiz_stats['total_score'] / quiz_stats['count'], 2)

            # Calculate overall averages
            for quiz_type, stats in analytics['quiz_type_breakdown'].items():
                analytics['average_scores'][quiz_type] = stats['average_score']

            # Recent activity (last 10 results)
            recent_results = sorted(all_results, key=lambda x: x['timestamp'], reverse=True)[:10]
            analytics['recent_activity'] = [
                {
                    'quiz_type': r['quiz_type'],
                    'score': r['score'],
                    'percentage': r['percentage'],
                    'timestamp': r['timestamp']
                }
                for r in recent_results
            ]

            return analytics

        except Exception as e:
            return {'error': str(e)}

    def get_user_progress(self, quiz_type: str) -> Dict[str, Any]:
        """Get detailed progress for a specific quiz type."""
        try:
            progress_id = f"{quiz_type}_progress"

            if progress_id in self.quiz_progress:
                progress = self.quiz_progress[progress_id]
                completed_results = [r for r in self.quiz_results.values() 
                                   if r['quiz_type'] == quiz_type]

                return {
                    'current_progress': progress,
                    'completed_attempts': len(completed_results),
                    'best_score': max([r['score'] for r in completed_results], default=0),
                    'average_score': round(sum([r['score'] for r in completed_results]) / 
                                         len(completed_results), 2) if completed_results else 0,
                    'improvement_suggestions': self._generate_improvement_suggestions(
                        quiz_type, progress, completed_results)
                }
            else:
                return {
                    'current_progress': None,
                    'completed_attempts': 0,
                    'best_score': 0,
                    'average_score': 0,
                    'improvement_suggestions': []
                }

        except Exception as e:
            return {'error': str(e)}

    def _generate_improvement_suggestions(self, quiz_type: str, progress: Dict, 
                                        completed_results: List[Dict]) -> List[str]:
        """Generate personalized improvement suggestions."""
        suggestions = []

        if not progress or progress.get('questions_answered', 0) == 0:
            suggestions.append("Start the quiz to begin tracking your progress!")
            return suggestions

        # Progress-based suggestions
        progress_pct = progress.get('progress_percentage', 0)
        if progress_pct < 50:
            suggestions.append("Focus on completing more questions to build confidence.")
        elif progress_pct < 80:
            suggestions.append("You're making good progress! Try to complete the full quiz.")
        else:
            suggestions.append("Great progress! Consider taking the full quiz to get a complete assessment.")

        # Score-based suggestions
        if completed_results:
            avg_score = sum([r['score'] for r in completed_results]) / len(completed_results)
            if avg_score < 60:
                suggestions.append("Review the explanations for incorrect answers to improve your understanding.")
            elif avg_score < 80:
                suggestions.append("You're doing well! Focus on the questions you missed to reach mastery.")
            else:
                suggestions.append("Excellent performance! You're mastering this quiz type.")

        return suggestions

    def save_quiz_progress(self, quiz_type: str, progress_data: Dict) -> bool:
        """Save user's quiz progress."""
        try:
            progress_id = f"{quiz_type}_progress"
            self.quiz_progress[progress_id] = progress_data
            self._save_data()
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False

    def load_quiz_progress(self, quiz_type: str) -> Optional[Dict]:
        """Load user's quiz progress."""
        progress_id = f"{quiz_type}_progress"
        return self.quiz_progress.get(progress_id)

    def clear_quiz_progress(self, quiz_type: str) -> bool:
        """Clear user's quiz progress."""
        try:
            progress_id = f"{quiz_type}_progress"
            if progress_id in self.quiz_progress:
                del self.quiz_progress[progress_id]
                self._save_data()
            return True
        except Exception as e:
            print(f"Error clearing progress: {e}")
            return False
