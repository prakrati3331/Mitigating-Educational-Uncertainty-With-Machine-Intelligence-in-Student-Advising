"""
Institution Directory Backend - FastAPI backend class for educational institutions management
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import os
from fastapi import HTTPException

# Setup logging
logger = logging.getLogger(__name__)

class InstitutionBackend:
    """Backend class for educational institutions directory management"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'data')
        self.institutions_file = os.path.join(self.data_dir, 'institutions.json')
        self.categories_file = os.path.join(self.data_dir, 'categories.json')
        
        # Initialize data files
        self._initialize_data_files()
        logger.info(f"InstitutionBackend initialized with data directory: {self.data_dir}")
    
    def _initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize institutions data
        if not os.path.exists(self.institutions_file):
            # Create empty institutions file - data will be managed separately
            with open(self.institutions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            logger.info(f"Created empty institutions file: {self.institutions_file}")
        
        # Initialize categories data
        if not os.path.exists(self.categories_file):
            # Create empty categories file - data will be managed separately
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            logger.info(f"Created empty categories file: {self.categories_file}")
    
        
    def get_all_institutions(self) -> Dict[str, Any]:
        """Get all institutions with categories"""
        try:
            with open(self.institutions_file, 'r', encoding='utf-8') as f:
                institutions = json.load(f)
            
            # Update category counts
            categories = self.get_categories()
            category_counts = {}
            for institution in institutions:
                for category in categories:
                    if category['name'].lower() == institution.get('category', '').lower():
                        category_counts[category['id']] = category_counts.get(category['id'], 0) + 1
            
            for category in categories:
                category['count'] = category_counts.get(category['id'], 0)
            
            logger.info(f"Retrieved {len(institutions)} institutions")
            return {
                'status': 'success',
                'institutions': institutions,
                'categories': categories,
                'total_count': len(institutions)
            }
        except Exception as e:
            logger.error(f"Error getting institutions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_institutions_by_category(self, category: str) -> Dict[str, Any]:
        """Get institutions filtered by category"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            filtered_institutions = [inst for inst in result['institutions'] 
                                   if inst.get('category', '').lower() == category.lower()]
            
            logger.info(f"Retrieved {len(filtered_institutions)} institutions for category: {category}")
            return {
                'status': 'success',
                'institutions': filtered_institutions,
                'category': category,
                'count': len(filtered_institutions)
            }
        except Exception as e:
            logger.error(f"Error getting institutions by category: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_institutions_by_state(self, state: str) -> Dict[str, Any]:
        """Get institutions filtered by state"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            filtered_institutions = [inst for inst in result['institutions'] 
                                   if inst.get('state', '').lower() == state.lower()]
            
            logger.info(f"Retrieved {len(filtered_institutions)} institutions for state: {state}")
            return {
                'status': 'success',
                'institutions': filtered_institutions,
                'state': state,
                'count': len(filtered_institutions)
            }
        except Exception as e:
            logger.error(f"Error getting institutions by state: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_institution_details(self, institution_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific institution"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            institution = next((inst for inst in result['institutions'] 
                               if inst.get('id') == institution_id), None)
            
            if not institution:
                logger.warning(f"Institution not found: {institution_id}")
                raise HTTPException(status_code=404, detail="Institution not found")
            
            logger.info(f"Retrieved details for institution: {institution_id}")
            return {
                'status': 'success',
                'institution': institution
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting institution details: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def search_institutions(self, query: str) -> Dict[str, Any]:
        """Search institutions by name, city, description, or tags"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            query_lower = query.lower()
            filtered_institutions = []
            
            for institution in result['institutions']:
                # Search in name, city, description, and tags
                if (query_lower in institution.get('name', '').lower() or
                    query_lower in institution.get('city', '').lower() or
                    query_lower in institution.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in institution.get('tags', []))):
                    filtered_institutions.append(institution)
            
            logger.info(f"Search for '{query}' returned {len(filtered_institutions)} results")
            return {
                'status': 'success',
                'institutions': filtered_institutions,
                'query': query,
                'count': len(filtered_institutions)
            }
        except Exception as e:
            logger.error(f"Error searching institutions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all institution categories"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_top_institutions(self, limit: int = 10) -> Dict[str, Any]:
        """Get top institutions based on ranking and rating"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            # Sort by ranking and rating
            sorted_institutions = sorted(result['institutions'], 
                                       key=lambda x: (x.get('ranking', 999), x.get('rating', 0)), 
                                       reverse=True)
            
            logger.info(f"Retrieved {min(limit, len(sorted_institutions))} top institutions")
            return {
                'status': 'success',
                'institutions': sorted_institutions[:limit],
                'count': len(sorted_institutions[:limit])
            }
        except Exception as e:
            logger.error(f"Error getting top institutions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_states_list(self) -> Dict[str, Any]:
        """Get list of all states with institution counts"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            states = {}
            for institution in result['institutions']:
                state = institution.get('state', 'Unknown')
                if state not in states:
                    states[state] = 0
                states[state] += 1
            
            # Convert to list and sort by count
            states_list = [{'state': state, 'count': count} for state, count in states.items()]
            states_list.sort(key=lambda x: x['count'], reverse=True)
            
            logger.info(f"Retrieved {len(states_list)} states")
            return {
                'status': 'success',
                'states': states_list,
                'total_states': len(states_list)
            }
        except Exception as e:
            logger.error(f"Error getting states list: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def filter_institutions(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter institutions based on multiple criteria"""
        try:
            result = self.get_all_institutions()
            if result['status'] != 'success':
                return result
            
            filtered_institutions = result['institutions']
            
            # Apply filters
            if 'category' in filters and filters['category']:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('category', '').lower() == filters['category'].lower()]
            
            if 'state' in filters and filters['state']:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('state', '').lower() == filters['state'].lower()]
            
            if 'city' in filters and filters['city']:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('city', '').lower() == filters['city'].lower()]
            
            if 'type' in filters and filters['type']:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('type', '').lower() == filters['type'].lower()]
            
            if 'hostel_facility' in filters:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('hostel_facility', False) == filters['hostel_facility']]
            
            if 'min_rating' in filters:
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if inst.get('rating', 0) >= filters['min_rating']]
            
            if 'max_fees' in filters:
                # Extract numeric value from fees range (simplified)
                filtered_institutions = [inst for inst in filtered_institutions 
                                       if self._extract_fees(inst.get('fees_range', '')) <= filters['max_fees']]
            
            logger.info(f"Filter returned {len(filtered_institutions)} institutions")
            return {
                'status': 'success',
                'institutions': filtered_institutions,
                'filters': filters,
                'count': len(filtered_institutions)
            }
        except Exception as e:
            logger.error(f"Error filtering institutions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _extract_fees(self, fees_range: str) -> int:
        """Extract numeric fees value from fees range string"""
        try:
            # Simple extraction - looks for numbers in the string
            import re
            numbers = re.findall(r'\d+', fees_range.replace(',', ''))
            if numbers:
                return int(numbers[0])
            return 999999  # Default high value
        except:
            return 999999
    
    def save_college_selection(self, user_id: str, selected_colleges: List[str]) -> Dict[str, Any]:
        """Save user's college selection preferences"""
        try:
            selections_file = os.path.join(self.data_dir, 'college_selections.json')
            
            # Load existing selections
            selections = {}
            if os.path.exists(selections_file):
                with open(selections_file, 'r', encoding='utf-8') as f:
                    selections = json.load(f)
            
            # Update user selections
            selections[user_id] = {
                'selected_colleges': selected_colleges,
                'updated_at': datetime.now().isoformat(),
                'count': len(selected_colleges)
            }
            
            # Save updated selections
            with open(selections_file, 'w', encoding='utf-8') as f:
                json.dump(selections, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved college selection for user {user_id}: {len(selected_colleges)} colleges")
            return {
                'status': 'success',
                'message': 'College selection saved successfully',
                'count': len(selected_colleges)
            }
        except Exception as e:
            logger.error(f"Error saving college selection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_college_selection(self, user_id: str) -> Dict[str, Any]:
        """Get user's college selection preferences"""
        try:
            selections_file = os.path.join(self.data_dir, 'college_selections.json')
            
            if not os.path.exists(selections_file):
                return {
                    'status': 'success',
                    'selected_colleges': [],
                    'count': 0
                }
            
            with open(selections_file, 'r', encoding='utf-8') as f:
                selections = json.load(f)
            
            user_selection = selections.get(user_id, {})
            selected_colleges = user_selection.get('selected_colleges', [])
            
            # Get full institution details for selected colleges
            result = self.get_all_institutions()
            if result['status'] == 'success':
                selected_institutions = [inst for inst in result['institutions'] 
                                       if inst.get('id') in selected_colleges]
            else:
                selected_institutions = []
            
            logger.info(f"Retrieved college selection for user {user_id}: {len(selected_colleges)} colleges")
            return {
                'status': 'success',
                'selected_colleges': selected_colleges,
                'selected_institutions': selected_institutions,
                'count': len(selected_colleges),
                'updated_at': user_selection.get('updated_at')
            }
        except Exception as e:
            logger.error(f"Error getting college selection: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
