import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimelineBackend:
    """Backend class for managing timeline tracker data and operations"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the timeline backend with data directory"""
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        else:
            self.data_dir = data_dir
        
        self.events_file = os.path.join(self.data_dir, "timeline_events.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        
        # Initialize data files
        self._initialize_data_files()
        logger.info(f"TimelineBackend initialized with data directory: {self.data_dir}")
    
    def _initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize events data
        if not os.path.exists(self.events_file):
            # Create empty events file - data will be managed separately
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            logger.info(f"Created empty events file: {self.events_file}")
        
        # Initialize categories data
        if not os.path.exists(self.categories_file):
            # Create empty categories file - data will be managed separately
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            logger.info(f"Created empty categories file: {self.categories_file}")
    
    def get_all_events(self) -> Dict[str, Any]:
        """Get all timeline events with categories and counts"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Update category counts
            categories = self.get_categories()
            category_counts = {}
            for event in events:
                category = event.get('category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Update categories with counts
            for category in categories:
                category['count'] = category_counts.get(category['id'], 0)
            
            return {
                'status': 'success',
                'events': events,
                'categories': categories,
                'total_events': len(events)
            }
        except Exception as e:
            logger.error(f"Error reading events data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading events data: {str(e)}")
    
    def get_events_by_category(self, category: str) -> Dict[str, Any]:
        """Get events filtered by category"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            filtered_events = [event for event in events if event.get('category', '').lower() == category.lower()]
            
            return {
                'status': 'success',
                'events': filtered_events,
                'category': category,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events by category: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events by category: {str(e)}")
    
    def get_events_by_stream(self, stream: str) -> Dict[str, Any]:
        """Get events filtered by stream"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            filtered_events = [event for event in events if stream.lower() in event.get('stream', '').lower()]
            
            return {
                'status': 'success',
                'events': filtered_events,
                'stream': stream,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events by stream: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events by stream: {str(e)}")
    
    def get_events_by_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get events filtered by date range"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            filtered_events = []
            for event in events:
                event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d')
                if start_dt <= event_date <= end_dt:
                    filtered_events.append(event)
            
            return {
                'status': 'success',
                'events': filtered_events,
                'date_range': f"{start_date} to {end_date}",
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events by date range: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events by date range: {str(e)}")
    
    def get_upcoming_events(self, days: int = 30) -> Dict[str, Any]:
        """Get upcoming events within specified days"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            today = datetime.now()
            future_date = today + timedelta(days=days)
            
            upcoming_events = []
            for event in events:
                event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d')
                if today <= event_date <= future_date:
                    upcoming_events.append(event)
            
            # Sort by date
            upcoming_events.sort(key=lambda x: x.get('date', ''))
            
            return {
                'status': 'success',
                'events': upcoming_events,
                'days': days,
                'count': len(upcoming_events)
            }
        except Exception as e:
            logger.error(f"Error getting upcoming events: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting upcoming events: {str(e)}")
    
    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific event"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            event = next((event for event in events if event.get('id') == event_id), None)
            
            if not event:
                raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
            
            return {
                'status': 'success',
                'event': event
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting event details: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting event details: {str(e)}")
    
    def search_events(self, query: str) -> Dict[str, Any]:
        """Search events by title, description, tags, or stream"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            query = query.lower()
            filtered_events = []
            
            for event in events:
                # Search in title
                if query in event.get('title', '').lower():
                    filtered_events.append(event)
                    continue
                
                # Search in description
                if query in event.get('description', '').lower():
                    filtered_events.append(event)
                    continue
                
                # Search in stream
                if query in event.get('stream', '').lower():
                    filtered_events.append(event)
                    continue
                
                # Search in tags
                for tag in event.get('tags', []):
                    if query in tag.lower():
                        filtered_events.append(event)
                        break
            
            return {
                'status': 'success',
                'events': filtered_events,
                'query': query,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error searching events: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching events: {str(e)}")
    
    def get_events_by_importance(self, importance: str) -> Dict[str, Any]:
        """Get events filtered by importance level"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            filtered_events = [event for event in events if event.get('importance', '').lower() == importance.lower()]
            
            return {
                'status': 'success',
                'events': filtered_events,
                'importance': importance,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events by importance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events by importance: {str(e)}")
    
    def get_events_by_status(self, status: str) -> Dict[str, Any]:
        """Get events filtered by status"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            filtered_events = [event for event in events if event.get('status', '').lower() == status.lower()]
            
            return {
                'status': 'success',
                'events': filtered_events,
                'status': status,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events by status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events by status: {str(e)}")
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all event categories"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"Error reading categories: {str(e)}")
            return []
    
    def get_streams_list(self) -> Dict[str, Any]:
        """Get list of all streams with event counts"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            stream_counts = {}
            for event in events:
                stream = event.get('stream', 'Unknown')
                stream_counts[stream] = stream_counts.get(stream, 0) + 1
            
            # Convert to list and sort by count
            streams_list = [{'stream': stream, 'count': count} for stream, count in stream_counts.items()]
            streams_list.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'status': 'success',
                'streams': streams_list,
                'total_streams': len(streams_list)
            }
        except Exception as e:
            logger.error(f"Error getting streams list: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting streams list: {str(e)}")
    
    def filter_events(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter events based on multiple criteria"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            filtered_events = events.copy()
            
            # Filter by category
            if 'category' in filters and filters['category']:
                filtered_events = [event for event in filtered_events if event.get('category', '').lower() == filters['category'].lower()]
            
            # Filter by stream
            if 'stream' in filters and filters['stream']:
                stream = filters['stream'].lower()
                filtered_events = [event for event in filtered_events if stream in event.get('stream', '').lower()]
            
            # Filter by importance
            if 'importance' in filters and filters['importance']:
                filtered_events = [event for event in filtered_events if event.get('importance', '').lower() == filters['importance'].lower()]
            
            # Filter by status
            if 'status' in filters and filters['status']:
                filtered_events = [event for event in filtered_events if event.get('status', '').lower() == filters['status'].lower()]
            
            # Filter by date range
            if 'start_date' in filters and filters['start_date']:
                start_dt = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                if 'end_date' in filters and filters['end_date']:
                    end_dt = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                    filtered_events = [event for event in filtered_events 
                                     if start_dt <= datetime.strptime(event.get('date', ''), '%Y-%m-%d') <= end_dt]
            
            return {
                'status': 'success',
                'events': filtered_events,
                'filters': filters,
                'count': len(filtered_events)
            }
        except Exception as e:
            logger.error(f"Error filtering events: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error filtering events: {str(e)}")
    
    def get_monthly_events(self, year: int, month: int) -> Dict[str, Any]:
        """Get events for a specific month and year"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            monthly_events = []
            for event in events:
                event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d')
                if event_date.year == year and event_date.month == month:
                    monthly_events.append(event)
            
            # Sort by date
            monthly_events.sort(key=lambda x: x.get('date', ''))
            
            return {
                'status': 'success',
                'events': monthly_events,
                'year': year,
                'month': month,
                'count': len(monthly_events)
            }
        except Exception as e:
            logger.error(f"Error getting monthly events: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting monthly events: {str(e)}")
