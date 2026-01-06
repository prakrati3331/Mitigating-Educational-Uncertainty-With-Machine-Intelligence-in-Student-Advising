# AI Education Dashboard

A unified dashboard backend that aggregates all user information from the AI Education system.

## Features

- **Stream Recommendations**: Displays recommended academic streams based on user assessments
- **Course Recommendations**: Shows personalized course recommendations based on stream
- **Career Guidance**: Integrates career assessment results and path recommendations
- **Quiz Results**: Displays quiz scores and analytics
- **Dropout Risk Assessment**: Shows risk assessment results and progress tracking
- **User Statistics**: Overall profile completion and achievement tracking
- **Real-time Updates**: Auto-refreshes dashboard data every 30 seconds

## Architecture

The dashboard backend integrates with all existing services:

- **Stream Recommendation Service**: Main stream prediction logic
- **Course Recommenders**: Arts, Commerce, PCM, PCB, Vocational course recommendation engines
- **Career Service**: Career assessment and guidance
- **Quiz Service**: Quiz results and analytics
- **Dropout Risk Service**: Risk assessment and monitoring

## Installation

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the dashboard directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DASHBOARD_PORT=5007
MAIN_API_URL=http://localhost:5006
LOG_LEVEL=INFO
```

## Running the Dashboard

Start the dashboard server:

```bash
python app.py
```

The dashboard will be available at: `http://localhost:5007`

## API Endpoints

### Dashboard Data
- `GET /api/dashboard/<user_id>` - Get complete dashboard data for user
- `GET /api/dashboard/overview/<user_id>` - Get dashboard overview (summary stats)

### Stream Recommendations
- `POST /api/stream/predict` - Predict stream for user

### Course Recommendations
- `POST /api/courses/recommend/<stream>` - Get course recommendations for stream

### Career Assessment
- `POST /api/career/assess` - Process career assessment

### Quiz Results
- `POST /api/quiz/submit` - Submit quiz results

### Dropout Risk Assessment
- `POST /api/dropout-risk/assess` - Assess dropout risk

## Data Structure

### Dashboard Response
```json
{
  "user_id": "string",
  "stats": {
    "profile_completion": 85,
    "skills_mastered": "7/10",
    "active_courses": 5,
    "achievements": 3
  },
  "stream_recommendation": {
    "best_stream": "PCM",
    "predictions": [...]
  },
  "course_recommendations": {
    "pcm": {
      "recommendations": [...]
    }
  },
  "career_guidance": {
    "assessment": {...},
    "career_paths": [...]
  },
  "quiz_results": {
    "total_quizzes": 7,
    "average_score": 78.5,
    "recent_quizzes": [...]
  },
  "dropout_risk": {
    "risk_score": 25,
    "risk_level": "Low"
  },
  "recent_activities": [...],
  "last_updated": "2023-03-15T10:30:00"
}
```

## Integration with Main System

The dashboard integrates with the main FastAPI application by:

1. **Importing Services**: Direct imports from existing service modules
2. **Data Aggregation**: Collects data from all services into unified format
3. **User Management**: Maintains user session data in memory (production should use database)
4. **Real-time Updates**: Provides API endpoints for frontend updates

## Frontend Integration

The dashboard HTML template includes:

- **Responsive Design**: Bootstrap-based responsive layout
- **Real-time Updates**: JavaScript auto-refresh functionality
- **Interactive Charts**: ApexCharts for data visualization
- **User Actions**: Buttons to trigger assessments and quizzes
- **Activity Feed**: Recent user activities and notifications

## Development Notes

### User Management
Currently uses in-memory storage for user data. In production, implement:
- Database persistence (MongoDB/PostgreSQL)
- User authentication (JWT)
- Session management

### Error Handling
- Comprehensive error logging
- User-friendly error messages
- Graceful degradation when services are unavailable

### Performance
- Data caching for frequent requests
- Lazy loading of dashboard components
- Optimized API responses

## Security Considerations

1. **Input Validation**: All user inputs are validated
2. **CORS Configuration**: Properly configured for production
3. **Session Security**: Secure cookie settings
4. **API Rate Limiting**: Implement rate limiting for production

## Future Enhancements

1. **Real-time WebSocket**: Live updates without polling
2. **Advanced Analytics**: More sophisticated user analytics
3. **Customizable Dashboard**: User-configurable widgets
4. **Export Functionality**: Export dashboard data and reports
5. **Mobile App**: Dedicated mobile application

## Troubleshooting

### Common Issues

1. **Service Import Errors**: Ensure all service modules are in Python path
2. **Port Conflicts**: Change DASHBOARD_PORT if port 5007 is in use
3. **CORS Issues**: Configure CORS origins properly for production
4. **Memory Issues**: Monitor user data storage in production

### Logging

Check the logs for debugging:
```bash
tail -f dashboard.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the AI Education system. See the main project license for details.
