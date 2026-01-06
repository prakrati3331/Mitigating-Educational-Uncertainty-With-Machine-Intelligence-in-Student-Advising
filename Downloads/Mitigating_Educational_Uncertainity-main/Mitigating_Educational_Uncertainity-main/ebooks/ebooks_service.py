"""
E-books Service - Backend for managing educational e-books library
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import os

# Setup logging
logger = logging.getLogger(__name__)

class EbooksService:
    """Service to manage e-books library functionality"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'data')
        self.ebooks_file = os.path.join(self.data_dir, 'ebooks.json')
        self.categories_file = os.path.join(self.data_dir, 'categories.json')
        self.user_progress_file = os.path.join(self.data_dir, 'user_progress.json')
        
        # Initialize data files
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize ebooks data
        if not os.path.exists(self.ebooks_file):
            default_ebooks = self._get_default_ebooks()
            with open(self.ebooks_file, 'w', encoding='utf-8') as f:
                json.dump(default_ebooks, f, indent=2, ensure_ascii=False)
        
        # Initialize categories data
        if not os.path.exists(self.categories_file):
            default_categories = self._get_default_categories()
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_categories, f, indent=2, ensure_ascii=False)
        
        # Initialize user progress data
        if not os.path.exists(self.user_progress_file):
            with open(self.user_progress_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
    
    def _get_default_ebooks(self) -> List[Dict[str, Any]]:
        """Get default e-books collection"""
        return [
            {
                "id": "math_fundamentals",
                "title": "Mathematics Fundamentals for Class 10",
                "author": "Dr. Rajesh Kumar",
                "category": "Mathematics",
                "stream": ["PCM", "Commerce", "Arts"],
                "description": "Comprehensive guide to mathematical concepts including algebra, geometry, and trigonometry.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 450,
                "language": "English",
                "rating": 4.5,
                "downloads": 1250,
                "tags": ["algebra", "geometry", "trigonometry", "class10"],
                "difficulty": "Intermediate",
                "added_date": "2024-01-15",
                "last_updated": "2024-03-20"
            },
            {
                "id": "physics_concepts",
                "title": "Physics Concepts Simplified",
                "author": "Prof. Anita Sharma",
                "category": "Physics",
                "stream": ["PCM", "PCB"],
                "description": "Easy-to-understand explanations of fundamental physics concepts including mechanics, thermodynamics, and modern physics.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 380,
                "language": "English",
                "rating": 4.7,
                "downloads": 980,
                "tags": ["mechanics", "thermodynamics", "modern_physics", "class12"],
                "difficulty": "Advanced",
                "added_date": "2024-02-10",
                "last_updated": "2024-04-05"
            },
            {
                "id": "chemistry_basics",
                "title": "Chemistry Basics for Beginners",
                "author": "Dr. Suresh Patel",
                "category": "Chemistry",
                "stream": ["PCM", "PCB"],
                "description": "Introduction to basic chemistry concepts including organic, inorganic, and physical chemistry.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 320,
                "language": "English",
                "rating": 4.3,
                "downloads": 750,
                "tags": ["organic", "inorganic", "physical_chemistry", "basics"],
                "difficulty": "Beginner",
                "added_date": "2024-01-20",
                "last_updated": "2024-03-15"
            },
            {
                "id": "biology_life_sciences",
                "title": "Biology and Life Sciences",
                "author": "Dr. Meera Reddy",
                "category": "Biology",
                "stream": ["PCB"],
                "description": "Complete guide to biology including cell biology, genetics, ecology, and human anatomy.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 520,
                "language": "English",
                "rating": 4.6,
                "downloads": 1100,
                "tags": ["cell_biology", "genetics", "ecology", "human_anatomy"],
                "difficulty": "Intermediate",
                "added_date": "2024-01-25",
                "last_updated": "2024-04-10"
            },
            {
                "id": "commerce_fundamentals",
                "title": "Commerce Fundamentals",
                "author": "CA. Ramesh Gupta",
                "category": "Commerce",
                "stream": ["Commerce"],
                "description": "Essential concepts of accountancy, business studies, and economics for commerce students.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 410,
                "language": "English",
                "rating": 4.4,
                "downloads": 890,
                "tags": ["accountancy", "business_studies", "economics", "commerce"],
                "difficulty": "Intermediate",
                "added_date": "2024-02-05",
                "last_updated": "2024-03-25"
            },
            {
                "id": "history_civilization",
                "title": "World History and Civilization",
                "author": "Dr. Priya Singh",
                "category": "History",
                "stream": ["Arts"],
                "description": "Comprehensive overview of world history from ancient civilizations to modern times.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 480,
                "language": "English",
                "rating": 4.8,
                "downloads": 650,
                "tags": ["world_history", "civilization", "ancient", "modern"],
                "difficulty": "Intermediate",
                "added_date": "2024-02-15",
                "last_updated": "2024-04-01"
            },
            {
                "id": "computer_science_basics",
                "title": "Computer Science Fundamentals",
                "author": "Tech Expert Team",
                "category": "Computer Science",
                "stream": ["PCM", "Vocational"],
                "description": "Introduction to programming, algorithms, data structures, and computer basics.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 350,
                "language": "English",
                "rating": 4.6,
                "downloads": 1420,
                "tags": ["programming", "algorithms", "data_structures", "basics"],
                "difficulty": "Beginner",
                "added_date": "2024-01-10",
                "last_updated": "2024-03-30"
            },
            {
                "id": "vocational_skills",
                "title": "Vocational Skills Development",
                "author": "Skills Council",
                "category": "Vocational",
                "stream": ["Vocational"],
                "description": "Practical guide to developing vocational skills for various trades and professions.",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
                "file_url": "#",
                "pages": 280,
                "language": "English",
                "rating": 4.2,
                "downloads": 520,
                "tags": ["skills", "trades", "professions", "practical"],
                "difficulty": "Beginner",
                "added_date": "2024-02-20",
                "last_updated": "2024-04-08"
            }
        ]
    
    def _get_default_categories(self) -> List[Dict[str, Any]]:
        """Get default e-book categories"""
        return [
            {
                "id": "mathematics",
                "name": "Mathematics",
                "icon": "fas fa-calculator",
                "description": "Mathematical concepts and problem-solving",
                "color": "#4361ee",
                "count": 0
            },
            {
                "id": "physics",
                "name": "Physics",
                "icon": "fas fa-atom",
                "description": "Physical sciences and natural laws",
                "color": "#00bcd4",
                "count": 0
            },
            {
                "id": "chemistry",
                "name": "Chemistry",
                "icon": "fas fa-flask",
                "description": "Chemical sciences and reactions",
                "color": "#4caf50",
                "count": 0
            },
            {
                "id": "biology",
                "name": "Biology",
                "icon": "fas fa-dna",
                "description": "Life sciences and organisms",
                "color": "#ff9800",
                "count": 0
            },
            {
                "id": "commerce",
                "name": "Commerce",
                "icon": "fas fa-chart-line",
                "description": "Business and economics",
                "color": "#9c27b0",
                "count": 0
            },
            {
                "id": "history",
                "name": "History",
                "icon": "fas fa-landmark",
                "description": "Historical events and civilizations",
                "color": "#f44336",
                "count": 0
            },
            {
                "id": "computer_science",
                "name": "Computer Science",
                "icon": "fas fa-laptop-code",
                "description": "Programming and technology",
                "color": "#607d8b",
                "count": 0
            },
            {
                "id": "vocational",
                "name": "Vocational",
                "icon": "fas fa-tools",
                "description": "Skills and trades",
                "color": "#795548",
                "count": 0
            }
        ]
    
    def get_all_ebooks(self) -> Dict[str, Any]:
        """Get all e-books with optional filtering"""
        try:
            with open(self.ebooks_file, 'r', encoding='utf-8') as f:
                ebooks = json.load(f)
            
            # Update category counts
            categories = self.get_categories()
            category_counts = {}
            for ebook in ebooks:
                for category in categories:
                    if category['name'].lower() == ebook.get('category', '').lower():
                        category_counts[category['id']] = category_counts.get(category['id'], 0) + 1
            
            for category in categories:
                category['count'] = category_counts.get(category['id'], 0)
            
            return {
                'status': 'success',
                'ebooks': ebooks,
                'categories': categories,
                'total_count': len(ebooks)
            }
        except Exception as e:
            logger.error(f"Error getting e-books: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_ebooks_by_category(self, category: str) -> Dict[str, Any]:
        """Get e-books filtered by category"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            filtered_ebooks = [ebook for ebook in result['ebooks'] 
                             if ebook.get('category', '').lower() == category.lower()]
            
            return {
                'status': 'success',
                'ebooks': filtered_ebooks,
                'category': category,
                'count': len(filtered_ebooks)
            }
        except Exception as e:
            logger.error(f"Error getting e-books by category: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_ebooks_by_stream(self, stream: str) -> Dict[str, Any]:
        """Get e-books filtered by academic stream"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            filtered_ebooks = [ebook for ebook in result['ebooks'] 
                             if stream.lower() in [s.lower() for s in ebook.get('stream', [])]]
            
            return {
                'status': 'success',
                'ebooks': filtered_ebooks,
                'stream': stream,
                'count': len(filtered_ebooks)
            }
        except Exception as e:
            logger.error(f"Error getting e-books by stream: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_ebook_details(self, ebook_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific e-book"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            ebook = next((ebook for ebook in result['ebooks'] if ebook.get('id') == ebook_id), None)
            
            if not ebook:
                return {'status': 'error', 'message': 'E-book not found'}
            
            return {
                'status': 'success',
                'ebook': ebook
            }
        except Exception as e:
            logger.error(f"Error getting e-book details: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def search_ebooks(self, query: str) -> Dict[str, Any]:
        """Search e-books by title, author, description, or tags"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            query_lower = query.lower()
            filtered_ebooks = []
            
            for ebook in result['ebooks']:
                # Search in title, author, description, and tags
                if (query_lower in ebook.get('title', '').lower() or
                    query_lower in ebook.get('author', '').lower() or
                    query_lower in ebook.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in ebook.get('tags', []))):
                    filtered_ebooks.append(ebook)
            
            return {
                'status': 'success',
                'ebooks': filtered_ebooks,
                'query': query,
                'count': len(filtered_ebooks)
            }
        except Exception as e:
            logger.error(f"Error searching e-books: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all e-book categories"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []
    
    def update_user_progress(self, user_id: str, ebook_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user reading progress for an e-book"""
        try:
            with open(self.user_progress_file, 'r', encoding='utf-8') as f:
                user_progress = json.load(f)
            
            if user_id not in user_progress:
                user_progress[user_id] = {}
            
            if ebook_id not in user_progress[user_id]:
                user_progress[user_id][ebook_id] = {
                    'started_date': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'progress_percentage': 0,
                    'pages_read': 0,
                    'bookmarks': [],
                    'notes': []
                }
            
            # Update progress data
            user_progress[user_id][ebook_id].update(progress_data)
            user_progress[user_id][ebook_id]['last_accessed'] = datetime.now().isoformat()
            
            with open(self.user_progress_file, 'w', encoding='utf-8') as f:
                json.dump(user_progress, f, indent=2)
            
            return {
                'status': 'success',
                'message': 'Progress updated successfully',
                'progress': user_progress[user_id][ebook_id]
            }
        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's reading progress for all e-books"""
        try:
            with open(self.user_progress_file, 'r', encoding='utf-8') as f:
                user_progress = json.load(f)
            
            return {
                'status': 'success',
                'progress': user_progress.get(user_id, {}),
                'total_books_reading': len(user_progress.get(user_id, {}))
            }
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_popular_ebooks(self, limit: int = 10) -> Dict[str, Any]:
        """Get most popular e-books based on downloads and ratings"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            # Sort by downloads and rating
            sorted_ebooks = sorted(result['ebooks'], 
                                 key=lambda x: (x.get('downloads', 0), x.get('rating', 0)), 
                                 reverse=True)
            
            return {
                'status': 'success',
                'ebooks': sorted_ebooks[:limit],
                'count': len(sorted_ebooks[:limit])
            }
        except Exception as e:
            logger.error(f"Error getting popular e-books: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_recent_ebooks(self, limit: int = 10) -> Dict[str, Any]:
        """Get most recently added e-books"""
        try:
            result = self.get_all_ebooks()
            if result['status'] != 'success':
                return result
            
            # Sort by added_date
            sorted_ebooks = sorted(result['ebooks'], 
                                 key=lambda x: x.get('added_date', ''), 
                                 reverse=True)
            
            return {
                'status': 'success',
                'ebooks': sorted_ebooks[:limit],
                'count': len(sorted_ebooks[:limit])
            }
        except Exception as e:
            logger.error(f"Error getting recent e-books: {str(e)}")
            return {'status': 'error', 'message': str(e)}
