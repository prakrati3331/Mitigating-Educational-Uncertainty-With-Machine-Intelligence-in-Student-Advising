import json
import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchoolBackend:
    """Backend class for managing school directory data and operations"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the school backend with data directory"""
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        else:
            self.data_dir = data_dir
        
        self.schools_file = os.path.join(self.data_dir, "schools.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        
        # Initialize data files
        self._initialize_data_files()
        logger.info(f"SchoolBackend initialized with data directory: {self.data_dir}")
    
    def _initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize schools data
        if not os.path.exists(self.schools_file):
            # Create empty schools file - data will be managed separately
            with open(self.schools_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            logger.info(f"Created empty schools file: {self.schools_file}")
        
        # Initialize categories data
        if not os.path.exists(self.categories_file):
            # Create empty categories file - data will be managed separately
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            logger.info(f"Created empty categories file: {self.categories_file}")
    
    def get_all_schools(self) -> Dict[str, Any]:
        """Get all schools with categories and counts"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            # Update category counts
            categories = self.get_categories()
            category_counts = {}
            for school in schools:
                board = school.get('board', 'Unknown')
                category_counts[board] = category_counts.get(board, 0) + 1
            
            # Update categories with counts
            for category in categories:
                category['count'] = category_counts.get(category['name'], 0)
            
            return {
                'status': 'success',
                'schools': schools,
                'categories': categories,
                'total_schools': len(schools)
            }
        except Exception as e:
            logger.error(f"Error reading schools data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading schools data: {str(e)}")
    
    def get_schools_by_board(self, board: str) -> Dict[str, Any]:
        """Get schools filtered by board"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            filtered_schools = [school for school in schools if school.get('board', '').lower() == board.lower()]
            
            return {
                'status': 'success',
                'schools': filtered_schools,
                'board': board,
                'count': len(filtered_schools)
            }
        except Exception as e:
            logger.error(f"Error filtering schools by board: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering schools by board: {str(e)}")
    
    def get_schools_by_type(self, school_type: str) -> Dict[str, Any]:
        """Get schools filtered by type"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            filtered_schools = [school for school in schools if school.get('type', '').lower() == school_type.lower()]
            
            return {
                'status': 'success',
                'schools': filtered_schools,
                'type': school_type,
                'count': len(filtered_schools)
            }
        except Exception as e:
            logger.error(f"Error filtering schools by type: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering schools by type: {str(e)}")
    
    def get_schools_by_location(self, location: str) -> Dict[str, Any]:
        """Get schools filtered by location"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            filtered_schools = [school for school in schools if location.lower() in school.get('location', '').lower()]
            
            return {
                'status': 'success',
                'schools': filtered_schools,
                'location': location,
                'count': len(filtered_schools)
            }
        except Exception as e:
            logger.error(f"Error filtering schools by location: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering schools by location: {str(e)}")
    
    def get_school_details(self, school_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific school"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            school = next((school for school in schools if school.get('id') == school_id), None)
            
            if not school:
                raise HTTPException(status_code=404, detail=f"School with ID '{school_id}' not found")
            
            return {
                'status': 'success',
                'school': school
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting school details: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting school details: {str(e)}")
    
    def search_schools(self, query: str) -> Dict[str, Any]:
        """Search schools by name, location, description, or tags"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            query = query.lower()
            filtered_schools = []
            
            for school in schools:
                # Search in name
                if query in school.get('name', '').lower():
                    filtered_schools.append(school)
                    continue
                
                # Search in location
                if query in school.get('location', '').lower():
                    filtered_schools.append(school)
                    continue
                
                # Search in specializations
                for specialization in school.get('specializations', []):
                    if query in specialization.lower():
                        filtered_schools.append(school)
                        break
                
                # Search in tags
                for tag in school.get('tags', []):
                    if query in tag.lower():
                        filtered_schools.append(school)
                        break
            
            return {
                'status': 'success',
                'schools': filtered_schools,
                'query': query,
                'count': len(filtered_schools)
            }
        except Exception as e:
            logger.error(f"Error searching schools: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching schools: {str(e)}")
    
    def get_top_schools(self, limit: int = 10) -> Dict[str, Any]:
        """Get top schools based on rating and reviews"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            # Sort by rating (descending), then by reviews count (descending)
            sorted_schools = sorted(schools, key=lambda x: (x.get('rating', 0), x.get('reviews_count', 0)), reverse=True)
            
            top_schools = sorted_schools[:limit]
            
            return {
                'status': 'success',
                'schools': top_schools,
                'limit': limit,
                'count': len(top_schools)
            }
        except Exception as e:
            logger.error(f"Error getting top schools: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting top schools: {str(e)}")
    
    def get_boards_list(self) -> Dict[str, Any]:
        """Get list of all boards with school counts"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            board_counts = {}
            for school in schools:
                board = school.get('board', 'Unknown')
                board_counts[board] = board_counts.get(board, 0) + 1
            
            # Convert to list and sort by count
            boards_list = [{'board': board, 'count': count} for board, count in board_counts.items()]
            boards_list.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'status': 'success',
                'boards': boards_list,
                'total_boards': len(boards_list)
            }
        except Exception as e:
            logger.error(f"Error getting boards list: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting boards list: {str(e)}")
    
    def get_school_types(self) -> Dict[str, Any]:
        """Get list of all school types with counts"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            type_counts = {}
            for school in schools:
                school_type = school.get('type', 'Unknown')
                type_counts[school_type] = type_counts.get(school_type, 0) + 1
            
            # Convert to list and sort by count
            types_list = [{'type': school_type, 'count': count} for school_type, count in type_counts.items()]
            types_list.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'status': 'success',
                'types': types_list,
                'total_types': len(types_list)
            }
        except Exception as e:
            logger.error(f"Error getting school types: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting school types: {str(e)}")
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all school categories"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"Error reading categories: {str(e)}")
            return []
    
    def filter_schools(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter schools based on multiple criteria"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                schools = json.load(f)
            
            filtered_schools = schools.copy()
            
            # Filter by board
            if 'board' in filters and filters['board']:
                filtered_schools = [school for school in filtered_schools if school.get('board', '').lower() == filters['board'].lower()]
            
            # Filter by type
            if 'type' in filters and filters['type']:
                filtered_schools = [school for school in filtered_schools if school.get('type', '').lower() == filters['type'].lower()]
            
            # Filter by location
            if 'location' in filters and filters['location']:
                location = filters['location'].lower()
                filtered_schools = [school for school in filtered_schools if location in school.get('location', '').lower()]
            
            # Filter by rating minimum
            if 'min_rating' in filters and filters['min_rating']:
                min_rating = float(filters['min_rating'])
                filtered_schools = [school for school in filtered_schools if school.get('rating', 0) >= min_rating]
            
            # Filter by fees maximum
            if 'max_fees' in filters and filters['max_fees']:
                # This is a simplified check - in real implementation, you'd parse the fees range
                max_fees = filters['max_fees'].lower()
                filtered_schools = [school for school in filtered_schools if max_fees in school.get('fees_range', '').lower()]
            
            # Filter by facilities
            if 'facilities' in filters and filters['facilities']:
                required_facilities = filters['facilities']
                filtered_schools = [school for school in filtered_schools 
                                  if all(facility in school.get('facilities', []) for facility in required_facilities)]
            
            return {
                'status': 'success',
                'schools': filtered_schools,
                'filters': filters,
                'count': len(filtered_schools)
            }
        except Exception as e:
            logger.error(f"Error filtering schools: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering schools: {str(e)}")
