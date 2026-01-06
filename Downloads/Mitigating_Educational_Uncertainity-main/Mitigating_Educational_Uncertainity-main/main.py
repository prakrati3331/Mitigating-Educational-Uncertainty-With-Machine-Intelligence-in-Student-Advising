from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Career_Mapping.career_service import CareerService
import pandas as pd
import numpy as np
import pickle
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pydantic import BaseModel
from mistralai import Mistral
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

if TYPE_CHECKING:
    # Forward references for type hints
    pass

# Load environment variables
load_dotenv()

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

client = Mistral(api_key=MISTRAL_API_KEY)

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Arts_dataset'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Commerce_dataset'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Vocational_dataset'))

from flask_app import ArtsCourseRecommender
from Commerce_dataset.flask_app import CommerceCourseRecommender
from pcb_dataset.flask_app import PCBCourseRecommender
from pcm_dataset.flask_app import PCMCourseRecommender
from Vocational_dataset.flask_app import VocationalCourseRecommender
from Interest_and_quizzes.quiz_service import QuizService
from Dropout_risk_factor.imp.dropout_risk_service import DropoutRiskService
from dashboard.dashboard_service import DashboardService
from ebooks.ebooks_backend import EbooksBackend
from institution_directory.institution_backend import InstitutionBackend
from school_directory.school_backend import SchoolBackend
from timeline_tracker.timeline_backend import TimelineBackend

# Initialize services
dropout_risk_service = DropoutRiskService()
ebooks_backend = EbooksBackend()
institution_backend = InstitutionBackend()
school_backend = SchoolBackend()
timeline_backend = TimelineBackend()

# Initialize the arts recommender instance
arts_recommender = ArtsCourseRecommender()

# Initialize the quiz service
quiz_service = QuizService()

# Setup templates for Interest and Quizzes section
interest_quizzes_templates = Jinja2Templates(directory=r"d:\AI_in_education\Interest_and_quizzes\templates")

# Setup templates for Career Mapping section
career_templates = Jinja2Templates(directory=os.path.join("Career_Mapping", "templates"))

# Initialize the commerce recommender instance
commerce_recommender = CommerceCourseRecommender()

# Initialize the PCB recommender instance
pcb_recommender = PCBCourseRecommender()

# Initialize the PCM recommender instance
pcm_recommender = PCMCourseRecommender()

# Initialize the vocational recommender instance
vocational_recommender = VocationalCourseRecommender()

# Initialize FastAPI app
app = FastAPI(title="Stream Recommendation System", version="1.0.0")

# Mount static files (use non-conflicting prefixes)
app.mount("/Dataset/Arts_dataset/static", StaticFiles(directory="Arts_dataset/static"), name="arts_static")
app.mount("/static/commerce", StaticFiles(directory="Commerce_dataset"), name="commerce_static")
app.mount("/static/pcb", StaticFiles(directory="pcb_dataset"), name="pcb_static")
app.mount("/static/pcm", StaticFiles(directory="pcm_dataset"), name="pcm_static")
app.mount("/static/vocational", StaticFiles(directory="Vocational_dataset"), name="vocational_static")
# Mount static files for quiz pages
app.mount("/Interest_and_quizzes", StaticFiles(directory="Interest_and_quizzes"), name="quiz_static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory="training/templates")  # Default directory

# Create a custom template loader for additional directories
from jinja2 import FileSystemLoader, ChoiceLoader
import os

# Get the list of template directories
template_dirs = [
    os.path.join(os.path.dirname(__file__), "training/templates"),
    os.path.join(os.path.dirname(__file__), "pcm_dataset/templates"),
    os.path.join(os.path.dirname(__file__), "pcb_dataset/templates"),
    os.path.join(os.path.dirname(__file__), "Vocational_dataset/templates"),
    os.path.join(os.path.dirname(__file__), "Commerce_dataset/templates")
]

# Create a choice loader with all template directories
loaders = [FileSystemLoader(directory) for directory in template_dirs]
templates.env.loader = ChoiceLoader(loaders)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Stream Recommendation Class
class StreamRecommender:
    """Class to handle all stream recommendation functionality"""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.career_guidance_prompt = None
        self._load_models()
        self._init_prompts()

    def _load_models(self):
        """Load the ML models and encoders"""
        try:
            with open("training/stream_model.pkl", "rb") as f:
                self.model = pickle.load(f)
            with open("training/stream_scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            with open("training/stream_label_encoder.pkl", "rb") as f:
                self.label_encoder = pickle.load(f)
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise RuntimeError(f"Failed to load models: {str(e)}")

    def _init_prompts(self):
        """Initialize prompt templates"""
        self.career_guidance_prompt = PromptTemplate(
            input_variables=["stream", "scores", "performance_analysis"],
            template="""
You are an expert career counselor. Based on the student's assessment in the {stream} stream, provide personalized career guidance.

STUDENT PROFILE:
- Recommended Stream: {stream}
- Assessment Scores: {scores}
- Performance Analysis: {performance_analysis}

Please provide a concise career guidance response including:

1. CAREER SUITABILITY:
   - How well their skills align with {stream} careers
   - Key strengths for this stream

2. RECOMMENDED CAREERS:
   - 3-4 career options in the {stream} field
   - Brief explanation for each choice

3. SKILL DEVELOPMENT:
   - Key skills to focus on
   - Recommended next steps

Keep the response clear and actionable.
Focus on the {stream} stream recommendation.
"""
        )

    def predict_stream(self, data: "PredictionRequest"):
        """Predict the most suitable stream for a student"""
        try:
            # Prepare input data in the correct order
            input_data = [
                data.math, data.science, data.biology, data.english,
                data.social, data.language, data.logical, data.analytical,
                data.numerical, data.creativity, data.communication,
                data.artistic, data.practical
            ]

            # Convert to DataFrame with correct column names
            columns = [
                'Math', 'Science', 'Biology', 'English', 'SocialStudies', 'Language',
                'LogicalReasoning', 'AnalyticalSkills', 'NumericalAbility',
                'Creativity', 'CommunicationSkills', 'ArtisticSkills', 'PracticalSkills'
            ]

            input_df = pd.DataFrame([input_data], columns=columns)

            # Scale the input
            scaled_input = self.scaler.transform(input_df)

            # Make prediction
            probabilities = self.model.predict_proba(scaled_input)[0]
            stream_names = self.label_encoder.classes_

            # Get top 3 streams
            top_indices = np.argsort(probabilities)[::-1][:3]
            top_streams = [stream_names[i] for i in top_indices]
            top_probs = [float(probabilities[i] * 100) for i in top_indices]

            # Prepare response
            result = {
                'status': 'success',
                'predictions': [
                    {'stream': stream, 'probability': prob}
                    for stream, prob in zip(top_streams, top_probs)
                ],
                'best_stream': top_streams[0],
                'scores': data.dict()  # Include original scores for AI analysis
            }

            return result

        except Exception as e:
            logger.error(f"Error in predict_stream: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    def categorize_score(self, score):
        """Categorize a single score."""
        if score >= 80:
            return 'high'
        elif score >= 60:
            return 'moderate'
        else:
            return 'low'

    def format_score_analysis(self, scores, categorized_scores):
        """Format the score analysis section of the prompt."""
        analysis = []

        # Group subjects by category
        high = [subj for subj, cat in categorized_scores.items() if cat == 'high']
        moderate = [subj for subj, cat in categorized_scores.items() if cat == 'moderate']
        low = [subj for subj, cat in categorized_scores.items() if cat == 'low']

        # Build analysis sections
        if high:
            analysis.append("⭐ Strongest Areas (80-100%):")
            for subj in high:
                analysis.append(f"   - {subj}: {scores[subj]}%")

        if moderate:
            analysis.append("\n📊 Areas with Good Potential (60-80%):")
            for subj in moderate:
                analysis.append(f"   - {subj}: {scores[subj]}%")

        if low:
            analysis.append("\n📝 Areas Needing Improvement (Below 60%):")
            for subj in low:
                analysis.append(f"   - {subj}: {scores[subj]}%")

        return "\n".join(analysis)

    def generate_insights_prompt(self, stream, scores, question=None, conversation_history=None):
        """Generate a prompt for the AI based on the context and conversation history."""
        if question:
            # For follow-up questions
            prompt = f"""
            You are a helpful career advisor. The user is interested in the {stream} career stream.

            Previous conversation:
            {conversation_history if conversation_history else 'No previous conversation'}

            User's question: {question}

            Please provide a helpful and detailed response to the user's question.
            Keep it professional, accurate, and encouraging.
            """
        else:
            # Initial insights
            categorized_scores = {subject: self.categorize_score(score) for subject, score in scores.items()}
            prompt = f"""As a career advisor, provide personalized guidance based on the student's academic performance in the {stream} stream.

            Performance Analysis:
            {self.format_score_analysis(scores, categorized_scores)}

            Please provide a detailed career guidance report including:

            1. Career Suitability Analysis:
               - How their performance in key subjects aligns with {stream} careers
               - Strengths to leverage based on high-scoring subjects
               - Areas for improvement and how they might impact career choices

            2. Career Pathway Recommendations:
               - 3-5 specific career options that match their profile
               - For each, explain why it's a good fit based on their scores
               - Required qualifications and skills for each path

            3. Development Plan:
               - Key skills to focus on improving
               - Recommended courses or certifications
               - Extracurricular activities that could strengthen their profile

            4. Next Steps:
               - Immediate actions they can take
               - Resources for exploring careers further
               - How to build on their strengths and address weaknesses

            Format your response with clear sections and bullet points for better readability.
            Keep the tone professional, friendly, and encouraging.
            """
        return prompt.strip()

    def get_insights(self, request: "InsightsRequest"):
        """Generate career insights for a student"""
        try:
            stream = request.stream
            scores = request.scores
            question = request.question
            conversation_history = request.conversation_history

            logger.info(f"Received data - Stream: '{stream}', Scores: {scores}")

            # Validate that we have the required data
            if not stream:
                raise HTTPException(
                    status_code=400,
                    detail='Stream recommendation is required for career guidance.'
                )

            # Generate performance analysis
            categorized_scores = {subject: self.categorize_score(score) for subject, score in scores.items()}
            performance_analysis = self.format_score_analysis(scores, categorized_scores)

            logger.info(f"Performance analysis generated: {performance_analysis[:100]}...")

            if question:
                # For follow-up questions
                prompt = f"""
                You are a helpful career advisor. The user is interested in the {stream} career stream.

                Previous conversation:
                {conversation_history if conversation_history else 'No previous conversation'}

                User's question: {question}

                Please provide a helpful and detailed response to the user's question.
                Keep it professional, accurate, and encouraging.
                """
            else:
                # Use the comprehensive prompt template for initial guidance
                try:
                    prompt = self.career_guidance_prompt.format(
                        stream=stream,
                        scores=str(scores),
                        performance_analysis=performance_analysis
                    )
                    logger.info("Template formatted successfully")
                except Exception as template_error:
                    logger.error(f"Template formatting error: {template_error}")
                    # Fallback to manual prompt construction
                    prompt = f"""
                    You are an expert career counselor. Based on the student's assessment in the {stream} stream, provide comprehensive, personalized career guidance.

                    STUDENT PROFILE:
                    - Recommended Stream: {stream}
                    - Assessment Scores: {str(scores)}
                    - Performance Analysis: {performance_analysis}

                    Please provide a detailed career guidance response...
                    """

            return prompt

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_insights: {str(e)}")
            raise HTTPException(status_code=500, detail='Sorry, I encountered an error while processing your request.')

# Pydantic models
class PredictionRequest(BaseModel):
    math: float
    science: float
    biology: float
    english: float
    social: float
    language: float
    logical: float
    analytical: float
    numerical: float
    creativity: float
    communication: float
    artistic: float
    practical: float

class StreamData(BaseModel):
    stream: str
    scores: Dict[str, float]
    predictions: Optional[List[Dict[str, Any]]] = None
    user_id: Optional[str] = None

class InsightsRequest(BaseModel):
    stream: str
    scores: Dict[str, float]
    question: Optional[str] = None
    conversation_history: Optional[str] = None

class MistralChatRequest(BaseModel):
    message: str
    userId: Optional[str] = None
    user_id: Optional[str] = None

# Initialize the stream recommender
stream_recommender = StreamRecommender()

# Initialize the career service
career_service = CareerService()

# Create comprehensive prompt template for career guidance
CAREER_GUIDANCE_PROMPT = PromptTemplate(
    input_variables=["stream", "scores", "performance_analysis"],
    template="""
You are an expert career counselor. Based on the student's assessment in the {stream} stream, provide personalized career guidance.

STUDENT PROFILE:
- Recommended Stream: {stream}
- Assessment Scores: {scores}
- Performance Analysis: {performance_analysis}

Please provide a concise career guidance response including:

1. CAREER SUITABILITY:
   - How well their skills align with {stream} careers
   - Key strengths for this stream

2. RECOMMENDED CAREERS:
   - 3-4 career options in the {stream} field
   - Brief explanation for each choice

3. SKILL DEVELOPMENT:
   - Key skills to focus on
   - Recommended next steps

Keep the response clear and actionable.
Focus on the {stream} stream recommendation.
"""
)

# In-memory storage for conversation history (in production, use a database)
conversation_history = {}

def get_user_conversation(user_id, max_history=10):
    """Get or initialize conversation history for a user"""
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'messages': [],
            'user_data': None,
            'recommended_stream': None,
            'last_activity': datetime.now().isoformat()
        }
    return conversation_history[user_id]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with open("recommendation_hub.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/predict")
async def predict(data: "PredictionRequest"):
    """Predict the most suitable academic stream for a student"""
    result = stream_recommender.predict_stream(data)
    return JSONResponse(result)

@app.post("/get_insights")
async def get_insights(request: "InsightsRequest"):
    """Generate personalized career guidance and insights"""
    try:
        # Use the class method to generate insights prompt
        prompt = stream_recommender.get_insights(request)

        # Call Mistral API
        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor. Provide accurate, professional, and encouraging career guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return JSONResponse({
                'status': 'success',
                'insights': response.choices[0].message.content
            })

        except Exception as api_error:
            logger.error(f"Mistral API error: {str(api_error)}")

            # Check if it's an authentication error
            if "401" in str(api_error) or "Unauthorized" in str(api_error):
                return JSONResponse({
                    'status': 'error',
                    'message': 'Invalid or expired Mistral API key. Please check your MISTRAL_API_KEY in the .env file.'
                }, status_code=500)
            else:
                return JSONResponse({
                    'status': 'error',
                    'message': 'Error communicating with AI service. Please try again later.'
                }, status_code=500)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_insights: {str(e)}")
        raise HTTPException(status_code=500, detail='Sorry, I encountered an error while processing your request.')

@app.post("/api/mistral-chat")
async def mistral_chat(request: Request):
    """Handle Mistral AI chat requests"""
    try:
        logger.info("Received request to /api/mistral-chat")
        data = await request.json()

        if not data or 'message' not in data:
            logger.error("Message is required")
            raise HTTPException(status_code=400, detail='Message is required')

        # Support both 'userId' and 'user_id' for backward compatibility
        user_id = data.get('userId') or data.get('user_id') or f'anonymous_{int(time.time())}'
        user_message = data['message']

        logger.info(f"Processing message from user {user_id}: {user_message}")
        logger.info(f"Current user data store keys: {list(user_data_store.keys())}")
        
        # Get user data from the in-memory store
        user_data = user_data_store.get(user_id, {})
        recommended_stream = user_data.get('stream', 'a suitable academic stream')
        academic_scores = user_data.get('scores', {})
        
        logger.info(f"Retrieved user data - Stream: {recommended_stream}, Scores: {academic_scores}")

        # Get or initialize conversation
        conversation = get_user_conversation(user_id)

        # Add user message to conversation
        conversation['messages'].append({
            'role': 'user',
            'content': str(user_message),  # Ensure content is a string
            'timestamp': datetime.now().isoformat()
        })

        # Get user data from the in-memory store
        user_data = user_data_store.get(user_id, {})
        recommended_stream = user_data.get('stream', 'a suitable academic stream')
        academic_scores = user_data.get('scores', {})
        
        logger.info(f"Retrieved user data - Stream: {recommended_stream}, Scores: {academic_scores}")

        # Format conversation history
        logger.info("Formatting conversation history...")
        try:
            conversation_history_text = "\n".join(
                f"{str(msg.get('role', '')).capitalize()}: {str(msg.get('content', ''))}"
                for msg in conversation['messages'][-5:]  # Last 5 messages
            )
            logger.info(f"Conversation history formatted: {conversation_history_text[:100]}...")
        except Exception as e:
            logger.error(f"Error formatting conversation history: {e}")
            conversation_history_text = ""

        # Generate performance analysis
        logger.info("Generating performance analysis...")
        try:
            categorized_scores = {subject: stream_recommender.categorize_score(score) for subject, score in academic_scores.items()}
            performance_analysis = stream_recommender.format_score_analysis(academic_scores, categorized_scores)
            logger.info(f"Performance analysis generated: {performance_analysis[:100]}...")
        except Exception as e:
            logger.error(f"Error generating performance analysis: {e}")
            performance_analysis = ""

        # Create chat prompt following CAREER_GUIDANCE_PROMPT structure
        logger.info("Creating chat prompt...")
        CHAT_PROMPT_TEMPLATE = """You are an expert career counselor. Based on the student's assessment in the {recommended_stream} stream, provide personalized career guidance.

STUDENT PROFILE:
- Recommended Stream: {recommended_stream}
- Performance Analysis: {performance_analysis}

CONVERSATION HISTORY:
{conversation_history}

USER'S QUESTION: {user_message}

Please provide a concise response (2-3 sentences) that directly addresses the user's question, references their stream and performance when relevant, and suggests specific actions or next steps. End with a clarifying question if appropriate.

If the user asks about their recommended stream or scores, be sure to mention that they've been recommended the {recommended_stream} stream based on their assessment. If they ask about specific subjects or scores, you can mention their performance in those areas if the information is available in the performance analysis."""

        # Format the prompt with user context
        logger.info("Formatting prompt...")
        try:
            prompt = CHAT_PROMPT_TEMPLATE.format(
                recommended_stream=recommended_stream,
                performance_analysis=performance_analysis,
                conversation_history=conversation_history_text,
                user_message=user_message
            )
            logger.info(f"Prompt formatted: {prompt[:100]}...")
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            prompt = f"User question: {user_message}"

        # Prepare messages for Mistral
        logger.info("Preparing messages for Mistral...")
        try:
            system_content = "You are an expert career counselor. The user has been recommended the {recommended_stream} stream based on their assessment. Provide accurate, professional, and encouraging career guidance. Keep responses concise (2-3 sentences).".format(recommended_stream=recommended_stream)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
            logger.info("Messages prepared successfully")
        except Exception as e:
            logger.error(f"Error preparing messages: {e}")
            messages = [
                {"role": "system", "content": "You are an expert career counselor."},
                {"role": "user", "content": f"User question: {user_message}"}
            ]

        logger.info("Sending request to Mistral API with user context")

        # Generate AI response using the correct API method
        try:
            response = client.chat.complete(
                model="mistral-tiny",
                messages=messages,
                temperature=0.7
            )

            # Extract the AI's response from the response structure
            if hasattr(response, 'choices') and len(response.choices) > 0:
                ai_response = str(response.choices[0].message.content)
            else:
                ai_response = "I apologize, but I'm having trouble generating a response. Could you please rephrase your question?"

        except Exception as api_error:
            logger.error(f"Mistral API error in chat: {str(api_error)}")

            # Check if it's an authentication error
            if "401" in str(api_error) or "Unauthorized" in str(api_error):
                ai_response = "I'm experiencing authentication issues with the AI service. Please check the MISTRAL_API_KEY configuration."
            else:
                ai_response = "I'm sorry, I encountered an error while processing your request. Please try again later."

        # Add AI response to conversation
        conversation['messages'].append({
            'role': 'assistant',
            'content': str(ai_response),  # Ensure content is a string
            'timestamp': datetime.now().isoformat()
        })

        # Track chat activity
        try:
            activity_data = {
                'user_id': user_id,
                'type': 'ai_chat',
                'title': 'AI Career Counseling Session',
                'description': f'Asked: "{user_message[:50]}{"..." if len(user_message) > 50 else ""}"',
                'icon': 'fas fa-robot',
                'data': {
                    'question': user_message[:100],
                    'stream': recommended_stream,
                    'page': 'ai-chat',
                    'timestamp': datetime.now().isoformat()
                },
                'page': 'ai-chat',
                'action': 'chat'
            }
            dashboard_service.track_activity(activity_data)
            logger.info(f"Tracked AI chat activity for user {user_id}")
        except Exception as activity_error:
            logger.error(f"Error tracking AI chat activity: {activity_error}")

        return JSONResponse({
            'response': ai_response,
            'conversation_id': user_id
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mistral_chat: {str(e)}")
        raise HTTPException(status_code=500, detail='An error occurred while processing your request')

# In-memory storage for user data (in production, use a database)
user_data_store = {}

# Initialize the dashboard service
dashboard_service = DashboardService(user_data_store)

@app.post('/api/set-course-recommendations')
async def set_course_recommendations(request: Request):
    """Store course recommendations for a user"""
    try:
        data = await request.json()
        stream = data.get('stream')
        recommendations = data.get('recommendations')
        user_id = data.get('user_id', f'anonymous_{int(datetime.now().timestamp())}')
        
        print(f"🔥 DEBUG: Received course recommendation data:")
        print(f"  - User ID: {user_id}")
        print(f"  - Stream: {stream}")
        print(f"  - Recommendations: {recommendations}")
        
        if not stream or not recommendations:
            raise HTTPException(status_code=400, detail='Stream and recommendations are required')
        
        # Store course recommendations in user data
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        
        recommendation_key = f"{stream}_recommendations"
        user_data_store[user_id][recommendation_key] = recommendations
        
        print(f"🔥 DEBUG: Stored course data with key: {recommendation_key}")
        print(f"🔥 DEBUG: User data store now contains: {list(user_data_store[user_id].keys())}")
        
        # DO NOT store the stream here - this is course data, not stream data
        # Stream data should only be set by the stream assessment endpoint
        
        # Track activity
        activity = {
            'type': 'course_recommendation',
            'title': f'Got {stream.upper()} Course Recommendations',
            'description': f'Received {len(recommendations.get("recommendations", []))} course recommendations',
            'timestamp': datetime.now().isoformat(),
            'icon': 'fas fa-graduation-cap',
            'data': {
                'stream': stream,
                'recommendations': recommendations
            }
        }
        
        if 'activities' not in user_data_store[user_id]:
            user_data_store[user_id]['activities'] = []
        user_data_store[user_id]['activities'].append(activity)
        
        logger.info(f"Stored {stream} course recommendations for user {user_id}")
        
        return JSONResponse({
            'status': 'success',
            'message': f'{stream.upper()} course recommendations stored successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error storing course recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/set-recommended-stream')
async def set_recommended_stream(data: StreamData):
    """Set the recommended stream for a user"""
    try:
        stream = data.stream
        scores = data.scores
        predictions = data.predictions  # Add predictions
        user_id = data.user_id or f'anonymous_{int(time.time())}'

        if not stream:
            raise HTTPException(status_code=400, detail='Stream is required')

        # Store the data in the in-memory store
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
            
        user_data_store[user_id].update({
            'stream': stream,
            'scores': scores,
            'predictions': predictions,  # Store predictions
            'last_updated': datetime.now().isoformat()
        })
        
        logger.info(f"Stored stream data for user {user_id} - Stream: {stream}, Scores: {scores}, Predictions: {predictions}")

        return JSONResponse({
            'status': 'success',
            'message': 'Stream and scores stored successfully',
            'user_id': user_id
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set_recommended_stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

@app.get("/arts")
async def arts_page():
    """Serve the arts course recommendation page"""
    with open("Arts_dataset/static/arts_course_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/recommend")
async def recommend_arts_legacy(request: Request):
    """Legacy endpoint for arts course recommendations (same as /arts/recommend)"""
    try:
        data = await request.json()
        user_profile_dict = data.get('user_profile', {})

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in arts_recommender.feature_columns]

        if len(user_profile) != len(arts_recommender.feature_columns):
            return JSONResponse({
                'error': f'Expected {len(arts_recommender.feature_columns)} features, got {len(user_profile)}',
                'features': arts_recommender.feature_columns
            }, status_code=400)

        recommendations = arts_recommender.recommend_courses(user_profile)
        return JSONResponse(recommendations)

    except Exception as e:
        logger.error(f"Error in recommend_arts_legacy: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/arts/recommend")
async def recommend_arts(request: Request):
    """API endpoint for getting arts course recommendations"""
    try:
        data = await request.json()
        user_profile_dict = data.get('user_profile', {})

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in arts_recommender.feature_columns]

        if len(user_profile) != len(arts_recommender.feature_columns):
            return JSONResponse({
                'error': f'Expected {len(arts_recommender.feature_columns)} features, got {len(user_profile)}',
                'features': arts_recommender.feature_columns
            }, status_code=400)

        recommendations = arts_recommender.recommend_courses(user_profile)
        return JSONResponse(recommendations)

    except Exception as e:
        logger.error(f"Error in recommend_arts: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/api/recommend")
async def recommend_commerce_courses_legacy(request: Request):
    """Legacy endpoint for commerce course recommendations (same as /api/commerce/recommend)"""
    try:
        data = await request.json()
        user_profile_dict = data.get('user_profile', {})

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in commerce_recommender.feature_columns]

        if len(user_profile) != len(commerce_recommender.feature_columns):
            return JSONResponse({
                'error': f'Expected {len(commerce_recommender.feature_columns)} features, got {len(user_profile)}',
                'features': commerce_recommender.feature_columns
            }, status_code=400)

        recommendations = commerce_recommender.recommend_courses(user_profile)
        return JSONResponse(recommendations)

    except Exception as e:
        logger.error(f"Error in recommend_commerce_courses_legacy: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/api/commerce/recommend")
async def recommend_commerce_courses(request: Request):
    """API endpoint for getting commerce course recommendations"""
    try:
        data = await request.json()
        user_profile_dict = data.get('user_profile', {})

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in commerce_recommender.feature_columns]

        if len(user_profile) != len(commerce_recommender.feature_columns):
            return JSONResponse({
                'error': f'Expected {len(commerce_recommender.feature_columns)} features, got {len(user_profile)}',
                'features': commerce_recommender.feature_columns
            }, status_code=400)

        recommendations = commerce_recommender.recommend_courses(user_profile)
        return JSONResponse(recommendations)

    except Exception as e:
        logger.error(f"Error in recommend_commerce_courses: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)


@app.post("/get_recommendations")
async def get_pcm_recommendations(request: Request):
    """Handle PCM recommendation requests"""
    try:
        data = await request.json()
        user_profile_dict = data

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in pcm_recommender.feature_columns]

        if len(user_profile) != len(pcm_recommender.feature_columns):
            return JSONResponse({
                'status': 'error',
                'message': f'Expected {len(pcm_recommender.feature_columns)} features, got {len(user_profile)}'
            }, status_code=400)

        # Get predictions and recommendations
        best_course = pcm_recommender.predict_course(user_profile)
        recommendations = pcm_recommender.recommend_courses(user_profile, top_n=5)

        # Get careers for the best course
        careers = pcm_recommender.df[pcm_recommender.df["Suggested_Course"] == best_course]["Career Options"].unique().tolist()

        return JSONResponse({
            'status': 'success',
            'best_course': best_course,
            'recommendations': recommendations,
            'careers': careers
        })
    except Exception as e:
        logger.error(f"Error in get_pcm_recommendations: {str(e)}")
        return JSONResponse({
            'status': 'error',
            'message': str(e)
        }, status_code=500)

@app.post("/vocational/recommend")
async def recommend_vocational_courses(request: Request):
    """API endpoint for getting Vocational course recommendations"""
    try:
        data = await request.json()
        user_profile_dict = data.get('user_profile', {})

        # Convert dictionary to list in the correct feature order
        user_profile = [user_profile_dict.get(feature, 50) for feature in vocational_recommender.feature_columns]

        if len(user_profile) != len(vocational_recommender.feature_columns):
            return JSONResponse({
                'error': f'Expected {len(vocational_recommender.feature_columns)} features, got {len(user_profile)}',
                'features': vocational_recommender.feature_columns
            }, status_code=400)

        recommendations = vocational_recommender.recommend_courses(user_profile)
        return JSONResponse(recommendations)

    except Exception as e:
        logger.error(f"Error in recommend_vocational_courses: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/Dataset/pcb_dataset/templates/pcb_recommendation.html", response_class=HTMLResponse)
async def pcb_recommendation_legacy():
    """Legacy redirect for old PCB template URL"""
    with open("pcb_dataset/templates/pcb_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

# Dashboard Endpoints

@app.get("/ebooks", response_class=HTMLResponse)
async def ebooks():
    with open("ebooks/templates/ebooks.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/home", response_class=HTMLResponse)
async def home_page():
    with open("home.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/institution_directory_fixed", response_class=HTMLResponse)
async def institution_directory_fixed():
    try:
        with open("institution_directory/templates/institution_directory.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Institution Directory Not Found</h1><p>The institution directory page could not be found.</p>", status_code=404)

@app.get("/recommendation_hub", response_class=HTMLResponse)
async def recommendation_hub():
    try:
        with open("recommendation_hub.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Recommendation Hub Not Found</h1><p>The recommendation hub page could not be found.</p>", status_code=404)

@app.get("/school_directory", response_class=HTMLResponse)
async def school_directory():
    try:
        with open("school_directory/templates/school_directory.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>School Directory Not Found</h1><p>The school directory page could not be found.</p>", status_code=404)

@app.get("/stream_selection", response_class=HTMLResponse)
async def stream_selection():
    with open("stream_selection.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/recommendation_hub.html", response_class=HTMLResponse)
async def recommendation_hub_html():
    with open("recommendation_hub.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/institution_directory.html", response_class=HTMLResponse)
async def institution_directory_html():
    with open("institution_directory/templates/institution_directory.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/school_directory.html", response_class=HTMLResponse)
async def school_directory_html():
    with open("school_directory/templates/school_directory.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/ebooks.html", response_class=HTMLResponse)
async def ebooks_html():
    with open("ebooks/templates/ebooks.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_html():
    """Serve the dashboard page"""
    try:
        with open("dashboard/templates/dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Dashboard Not Found</h1><p>The dashboard page could not be found.</p>", status_code=404)

@app.get("/dashboard/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page with trailing slash"""
    try:
        with open("dashboard/templates/dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Dashboard Not Found</h1><p>The dashboard page could not be found.</p>", status_code=404)

@app.get("/stream_selection.html", response_class=HTMLResponse)
async def stream_selection_html():
    with open("stream_selection.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/training/", response_class=HTMLResponse)
async def training_page():
    with open("d:/AI_in_education/training/templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/arts/courses/", response_class=HTMLResponse)
async def arts_courses_page():
    with open("d:/AI_in_education/Arts_dataset/static/arts_course_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/commerce/courses/", response_class=HTMLResponse)
async def commerce_courses_page():
    with open("d:/AI_in_education/Commerce_dataset/templates/commerce_course_recommendation_.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/pcm/courses/", response_class=HTMLResponse)
async def pcm_courses_page():
    with open("d:/AI_in_education/PCM_dataset/templates/pcm_course_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/pcb/courses/", response_class=HTMLResponse)
async def pcb_courses_page():
    with open("d:/AI_in_education/PCB_dataset/templates/pcb_course_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/vocational/courses/", response_class=HTMLResponse)
async def vocational_courses_page():
    with open("d:/AI_in_education/Vocational_dataset/templates/vocational_course_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/training/templates/index.html", response_class=HTMLResponse)
async def index_html():
    with open("d:/AI_in_education/training/templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/career_path_visualization.html", response_class=HTMLResponse)
async def career_path_visualization():
    with open("career_path_visualization.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)


# Career Mapping Pages

@app.get("/career_mapping", response_class=HTMLResponse)
async def career_mapping_page(request: Request, user_id: Optional[str] = None):
    """Serve the career path assessment page with optional user_id parameter"""
    return career_templates.TemplateResponse(
        "career_path_assessment.html",
        {"request": request}
    )

@app.get("/career/assessment", response_class=HTMLResponse)
async def career_assessment_page(request: Request):
    """Serve the career path assessment page"""
    return career_templates.TemplateResponse(
        "career_path_assessment.html",
        {"request": request}
    )


@app.get("/career/guidance", response_class=HTMLResponse)
async def career_guidance_page(request: Request, user_id: Optional[str] = None):
    """Serve the career guidance page populated with the latest assessment"""
    assessment_data = None
    error_message = None

    try:
        assessment_data = career_service.get_latest_assessment(user_id=user_id)
    except Exception as e:
        logger.error(f"Error retrieving assessment data for guidance page: {e}")
        error_message = "Error loading assessment data"

    context = {
        "request": request,
        "assessment_data": json.dumps(assessment_data) if assessment_data else 'null',
        "error": error_message
    }

    return career_templates.TemplateResponse("career_guidance.html", context)


# Career Mapping APIs

@app.post("/api/career-assessment")
async def submit_career_assessment(request: Request):
    """Handle career assessment form submissions"""
    try:
        data = await request.json()
        # Extract user_id and IP address
        user_id = data.get('user_id')
        ip_address = request.client.host if request.client else '127.0.0.1'
        
        # Process the assessment data with proper parameters
        result = career_service.process_assessment(data, ip_address, user_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing career assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing assessment")

@app.get("/guidance", response_class=HTMLResponse)
async def redirect_guidance():
    """Redirect /guidance to /career/guidance"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/career/guidance")

@app.post("/api/career/assess", response_class=JSONResponse)
async def process_career_assessment(request: Request):
    """Process career assessment submissions"""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    ip_address = request.client.host if request.client else None
    user_id = data.get('user_id')

    try:
        result = career_service.process_assessment(data, ip_address=ip_address, user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing career assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to process assessment")


@app.get("/api/career/assessment/latest", response_class=JSONResponse)
async def get_latest_career_assessment(user_id: Optional[str] = None):
    """Fetch the latest saved career assessment"""
    try:
        assessment = career_service.get_latest_assessment(user_id=user_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found")
        return JSONResponse(content={"status": "success", "data": assessment})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest career assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment")


@app.get("/api/career-data/{stream}", response_class=JSONResponse)
async def get_career_data(stream: str):
    """Return career data for a specific stream"""
    try:
        result = career_service.get_career_data(stream)
        status = result.get('status')
        if status == 'error':
            raise HTTPException(status_code=404, detail=result.get('message', 'Stream not found'))
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching career data for stream {stream}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch career data")

@app.get("/pcb")
async def pcb_page(request: Request):
    """Serve the PCB course recommendation page"""
    # Import the categories from the PCB module
    from pcb_dataset.flask_app import SUBJECT_CATEGORIES
    return templates.TemplateResponse("pcb_recommendation.html", {"request": request, "categories": SUBJECT_CATEGORIES})

@app.get("/pcm")
async def pcm_page(request: Request):
    """Serve the PCM course recommendation page"""
    try:
        from pcm_dataset.flask_app import SUBJECT_CATEGORIES
        return templates.TemplateResponse("pcm_recommendation.html", {
            "request": request,
            "categories": SUBJECT_CATEGORIES
        })
    except Exception as e:
        logger.error(f"Error loading PCM page: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load PCM page: {str(e)}"}
        )

@app.get("/vocational")
async def vocational_page(request: Request):
    """Serve the Vocational course recommendation page"""
    try:
        from Vocational_dataset.flask_app import SUBJECT_CATEGORIES
        return templates.TemplateResponse(
            "vocational_recommendation.html",  # Now in the search path
            {
                "request": request, 
                "categories": SUBJECT_CATEGORIES
            }
        )
    except Exception as e:
        logger.error(f"Error loading Vocational page: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load Vocational page: {str(e)}"}
        )

@app.get("/Dataset/Vocational_dataset/templates/vocational_recommendation.html", response_class=HTMLResponse)
async def vocational_recommendation_legacy():
    """Legacy redirect for old Vocational template URL"""
    with open("Vocational_dataset/templates/vocational_recommendation.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/api/features")
async def get_features():
    """Return feature information for all recommenders"""
    try:
        return JSONResponse({
            'status': 'success',
            'features': {
                'arts': arts_recommender.feature_columns,
                'commerce': commerce_recommender.feature_columns,
                'pcb': pcb_recommender.feature_columns,
                'pcm': pcm_recommender.feature_columns,
                'vocational': vocational_recommender.feature_columns
            },
            'subjects': {
                'arts': [subj for cat in arts_recommender.SUBJECT_CATEGORIES.values() for subj in cat['subjects']] if hasattr(arts_recommender, 'SUBJECT_CATEGORIES') else [],
                'commerce': [subj for cat in commerce_recommender.SUBJECT_CATEGORIES.values() for subj in cat['subjects']] if hasattr(commerce_recommender, 'SUBJECT_CATEGORIES') else [],
                'pcb': [subj for cat in pcb_recommender.SUBJECT_CATEGORIES.values() for subj in cat['subjects']] if hasattr(pcb_recommender, 'SUBJECT_CATEGORIES') else [],
                'pcm': [subj for cat in pcm_recommender.SUBJECT_CATEGORIES.values() for subj in cat['subjects']] if hasattr(pcm_recommender, 'SUBJECT_CATEGORIES') else [],
                'vocational': [subj for cat in vocational_recommender.SUBJECT_CATEGORIES.values() for subj in cat['subjects']] if hasattr(vocational_recommender, 'SUBJECT_CATEGORIES') else []
            }
        })
    except Exception as e:
        logger.error(f"Error in get_features: {str(e)}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/commerce_recommendation.html", response_class=HTMLResponse)
async def commerce_recommendation_html(request: Request):
    """Serve the commerce recommendation template from training/templates"""
    try:
        from Commerce_dataset.flask_app import SUBJECT_CATEGORIES as COMMERCE_SUBJECT_CATEGORIES
        context = {
            "request": request,
            "categories": COMMERCE_SUBJECT_CATEGORIES
        }
        return templates.TemplateResponse("commerce_recommendation.html", context)
    except Exception as e:
        logger.error(f"Error loading Commerce page: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/favicon.ico")
async def favicon():
    # Return a simple 204 No Content response for favicon requests
    # This prevents 404 errors in browser logs
    from fastapi.responses import Response
    return Response(status_code=204)

# Interest and Quizzes HTML Endpoints

@app.get("/interest-quizzes", response_class=HTMLResponse)
async def interest_quizzes_home(request: Request):
    """Serve the main interest and quizzes page"""
    return interest_quizzes_templates.TemplateResponse(
        "quizzes_index.html",
        {"request": request, "title": "Interest & Quizzes | AI in Education"}
    )

@app.get("/interest-quizzes/aptitude", response_class=HTMLResponse)
async def aptitude_quizzes(request: Request):
    """Serve the aptitude quizzes page"""
    return interest_quizzes_templates.TemplateResponse(
        "aptitude_quizzes.html",
        {"request": request, "title": "Aptitude Quizzes | AI in Education"}
    )

@app.get("/interest-quizzes/subject_quizzes.html", response_class=HTMLResponse)
@app.get("/interest-quizzes/subject", response_class=HTMLResponse)
async def subject_quizzes(request: Request):
    """Serve the subject quizzes page"""
    return interest_quizzes_templates.TemplateResponse(
        "subject_quizzes.html",
        {"request": request, "title": "Subject Quizzes | AI in Education"}
    )

@app.get("/interest-quizzes/scores", response_class=HTMLResponse)
async def score_tracker(request: Request):
    """Serve the score tracker page"""
    return interest_quizzes_templates.TemplateResponse(
        "score_tracker.html",
        {"request": request, "title": "Score Tracker | AI in Education"}
    )

# Dropout Risk Assessment Page
@app.get("/dropout-risk", response_class=HTMLResponse)
async def dropout_risk_page():
    """Serve the dropout risk assessment page"""
    # Path to the HTML file
    html_file_path = os.path.join(
        os.path.dirname(__file__), 
        "Dropout_risk_factor", 
        "imp", 
        "templates", 
        "index.html"
    )
    
    # Check if the file exists
    if not os.path.exists(html_file_path):
        raise HTTPException(
            status_code=404, 
            detail="Dropout risk assessment page not found"
        )
    
    # Read and return the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Quiz Results and Analytics Endpoints

@app.get("/api/quiz/results", response_class=JSONResponse)
async def get_quiz_results():
    """Get all quiz results"""
    try:
        return JSONResponse(content={"results": list(dashboard_service.quiz_service.quiz_results.values()), "total_results": len(dashboard_service.quiz_service.quiz_results)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quiz/score-analytics", response_class=JSONResponse)
async def get_score_analytics():
    """Get quiz score analytics"""
    try:
        # Calculate basic analytics using dashboard service
        analytics = {
            "total_quizzes_taken": len(dashboard_service.quiz_service.quiz_results),
            "average_scores": {},
            "quizzes_by_type": {},
            "recent_quizzes": list(dashboard_service.quiz_service.quiz_results.values())[-5:],  # Last 5 quizzes
        }
        
        # Calculate average scores by quiz type
        scores_by_type = {}
        for result in dashboard_service.quiz_service.quiz_results.values():
            quiz_type = result.get('quiz_type')
            if quiz_type not in scores_by_type:
                scores_by_type[quiz_type] = []
            scores_by_type[quiz_type].append(result.get('score', 0))
        
        # Calculate averages
        for quiz_type, scores in scores_by_type.items():
            analytics['average_scores'][quiz_type] = sum(scores) / len(scores)
            analytics['quizzes_by_type'][quiz_type] = len(scores)
        
        return JSONResponse(content=analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dropout Risk Assessment Page
@app.get("/dropout-risk", response_class=HTMLResponse)
async def dropout_risk_page(request: Request):
    """Serve the dropout risk assessment page"""
    # Check if the template exists
    template_path = os.path.join("Dropout_risk_factor", "imp", "templates", "index.html")
    if not os.path.exists(os.path.join(os.path.dirname(__file__), template_path)):
        raise HTTPException(status_code=500, detail="Template not found")
    
    # Create a custom template loader for the dropout risk templates
    dropout_template_dir = os.path.join(os.path.dirname(__file__), "Dropout_risk_factor", "imp", "templates")
    loader = ChoiceLoader([
        FileSystemLoader(dropout_template_dir),
        app.state.jinja_loader  # Keep the default loader as fallback
    ])
    
    # Create a new templates environment for this request
    templates = Jinja2Templates(directory=dropout_template_dir)
    templates.env.loader = loader
    
    # Add static URL helper
    templates.env.globals['url_for'] = request.url_for
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Dropout Risk Assessment Endpoints

class DropoutAssessmentRequest(BaseModel):
    """Request model for dropout risk assessment"""
    user_id: str = "anonymous"
    grades: float
    attendance: float
    assignments: float
    exams: float
    participation: float
    absences: float
    tardiness: float
    behavioral_issues: float
    financial_stress: float
    work_hours: float
    family_support: float
    health_status: float
    course_load: float
    major_fit: float
    faculty_interaction: float
    campus_involvement: float
    peer_network: float
    mentorship: float
    bullying: float
    commute_time: float
    family_responsibilities: float
    work_life_balance: float
    motivation: float
    self_efficacy: float
    stress_level: float
    previous_dropout: float
    grade_retention: float
    school_changes: float
    lms_activity: float
    online_engagement: float
    warning_signs: float
    early_alerts: float

@app.post("/api/dropout-risk/assess", response_class=JSONResponse)
async def assess_dropout_risk(assessment: DropoutAssessmentRequest):
    """Assess student dropout risk"""
    try:
        # Convert the Pydantic model to a dictionary
        assessment_data = assessment.dict()
        
        # Map field names to match the service's expected format
        mapped_data = {
            'grades': assessment_data['grades'],
            'attendance': assessment_data['attendance'],
            'assignments': assessment_data['assignments'],
            'exams': assessment_data['exams'],
            'participation': assessment_data['participation'],
            'absences': assessment_data['absences'],
            'tardiness': assessment_data['tardiness'],
            'behavioralIssues': assessment_data['behavioral_issues'],
            'financialStress': assessment_data['financial_stress'],
            'workHours': assessment_data['work_hours'],
            'familySupport': assessment_data['family_support'],
            'healthStatus': assessment_data['health_status'],
            'courseLoad': assessment_data['course_load'],
            'majorFit': assessment_data['major_fit'],
            'facultyInteraction': assessment_data['faculty_interaction'],
            'campusInvolvement': assessment_data['campus_involvement'],
            'peerNetwork': assessment_data['peer_network'],
            'mentorship': assessment_data['mentorship'],
            'bullying': assessment_data['bullying'],
            'commuteTime': assessment_data['commute_time'],
            'familyResponsibilities': assessment_data['family_responsibilities'],
            'workLifeBalance': assessment_data['work_life_balance'],
            'motivation': assessment_data['motivation'],
            'selfEfficacy': assessment_data['self_efficacy'],
            'stressLevel': assessment_data['stress_level'],
            'previousDropout': assessment_data['previous_dropout'],
            'gradeRetention': assessment_data['grade_retention'],
            'schoolChanges': assessment_data['school_changes'],
            'lmsActivity': assessment_data['lms_activity'],
            'onlineEngagement': assessment_data['online_engagement'],
            'warningSigns': assessment_data['warning_signs'],
            'earlyAlerts': assessment_data['early_alerts']
        }
        
        # Get risk assessment
        result = dropout_risk_service.assess_risk(mapped_data)
        
        # Get progress data
        progress = dropout_risk_service.get_category_progress(mapped_data)
        
        # Get trends with error handling
        trends = {}
        try:
            trends_data = dropout_risk_service.generate_trends("current_student", mapped_data)
            if trends_data and isinstance(trends_data, dict):
                trends = {
                    "dates": trends_data.get("dates", []),
                    "grades": trends_data.get("grades", []),
                    "attendance": trends_data.get("attendance", []),
                    "assignments": trends_data.get("assignments", []),
                    "participation": trends_data.get("participation", [])
                }
        except Exception as e:
            print(f"Error generating trends: {str(e)}")
            # Provide default empty trends data
            trends = {
                "dates": [],
                "grades": [],
                "attendance": [],
                "assignments": [],
                "participation": []
            }
        
        # Store assessment data in dashboard service - CRITICAL for LLM to work
        try:
            # Get user_id from assessment data, or use the LLM's persistent user ID
            user_id = assessment_data.get('user_id')
            if not user_id:
                # Try to get the LLM's user ID
                try:
                    llm_user_id_path = os.path.join(os.path.dirname(__file__), 'LLM', 'user_id.txt')
                    if os.path.exists(llm_user_id_path):
                        with open(llm_user_id_path, 'r', encoding='utf-8') as f:
                            user_id = f.read().strip()
                            logger.info(f"Read user_id from file: {user_id}")
                    else:
                        logger.warning(f"LLM user_id file not found at {llm_user_id_path}")
                        user_id = 'anonymous'
                except Exception as e:
                    logger.error(f"Error reading LLM user_id: {e}")
                    user_id = 'anonymous'
            
            logger.info(f"Received dropout assessment for user_id: {user_id}")
            logger.info(f"Assessment data keys: {list(assessment_data.keys())}")
            
            # Initialize user data if not exists
            if user_id not in dashboard_service.user_data:
                dashboard_service.user_data[user_id] = {
                    'activities': [],
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
                logger.info(f"Initialized user data for {user_id}")
            
            # Create the assessment object
            assessment_data_to_store = {
                'risk_score': result["risk_score"],
                'risk_level': result["risk_level"],
                'factors': result["factors"],
                'based_on_real_data': True,
                'assessment_date': datetime.now().isoformat()
            }
            
            # Store the assessment results
            dashboard_service.user_data[user_id]['dropout_assessment'] = assessment_data_to_store
            logger.info(f"Stored dropout assessment: {assessment_data_to_store}")
            
            # Store the original form data
            dashboard_service.user_data[user_id]['form_data'] = assessment_data
            
            # Track this activity
            dashboard_service._track_activity(user_id, {
                'type': 'dropout_assessment',
                'title': 'Dropout Risk Assessment Completed',
                'description': f'Risk level: {result["risk_level"]}',
                'icon': 'fas fa-exclamation-triangle',
                'duration': 5
            })
            
            logger.info(f"Successfully stored dropout assessment for user {user_id}")
            logger.info(f"User data keys after storage: {list(dashboard_service.user_data[user_id].keys())}")
            
            # Verify storage worked
            stored_assessment = dashboard_service.user_data[user_id].get('dropout_assessment')
            if stored_assessment:
                logger.info(f"Verification: Assessment stored successfully with risk_score {stored_assessment.get('risk_score')}")
            else:
                logger.error("Verification: Assessment storage failed!")
                raise Exception("Assessment storage verification failed")
            
        except Exception as e:
            logger.error(f"CRITICAL: Error storing dropout assessment in dashboard service: {str(e)}")
            logger.error(f"This means the LLM will NOT be able to see the assessment data!")
            # Still return the result but add a warning
            return {
                "success": True,
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "factors": result["factors"],
                "progress": progress,
                "trends": trends,
                "warning": "Assessment data storage failed - LLM may not see this result"
            }
        
        return {
            "success": True,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "factors": result["factors"],
            "progress": progress,
            "trends": trends
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/dropout-risk/progress", response_class=JSONResponse)
async def get_dropout_progress():
    """Get progress data for the current student"""
    try:
        # In a real application, you would fetch the student's progress data here
        # For now, we'll return sample progress data
        return {
            "success": True,
            "progress": {
                "academic": {
                    "score": 75,
                    "label": "Academic Performance",
                    "trend": "up"
                },
                "behavioral": {
                    "score": 60,
                    "label": "Behavioral Indicators",
                    "trend": "stable"
                },
                "personal": {
                    "score": 45,
                    "label": "Personal Factors",
                    "trend": "down"
                },
                "institutional": {
                    "score": 70,
                    "label": "Institutional Factors",
                    "trend": "up"
                },
                "social": {
                    "score": 65,
                    "label": "Social Factors",
                    "trend": "stable"
                }
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/dropout-risk/trends/{student_id}", response_class=JSONResponse)
async def get_dropout_trends(student_id: str):
    """Get trend data for a student"""
    try:
        # In a real application, you would fetch the student's historical data here
        # For now, we'll return sample data with proper error handling
        import random
        from datetime import datetime, timedelta
        
        try:
            # Generate sample trend data for the last 6 months
            dates = [(datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
            
            # Ensure we have valid numeric data
            def generate_sample_data():
                return [max(0, min(100, random.uniform(50, 100))) for _ in range(7)]
            
            trend_data = {
                "dates": dates,
                "grades": generate_sample_data(),
                "attendance": generate_sample_data(),
                "assignments": generate_sample_data(),
                "participation": generate_sample_data()
            }
            
            # Validate the data structure
            required_keys = ["dates", "grades", "attendance", "assignments", "participation"]
            if not all(key in trend_data for key in required_keys):
                raise ValueError("Missing required trend data keys")
                
            if not all(isinstance(trend_data[key], list) for key in required_keys):
                raise ValueError("Trend data values must be lists")
                
            return trend_data
            
        except Exception as gen_error:
            print(f"Error generating sample trends: {str(gen_error)}")
            # Return empty but valid data structure
            return {
                "dates": [],
                "grades": [],
                "attendance": [],
                "assignments": [],
                "participation": []
            }
        
        trends = dropout_risk_service.generate_trends(student_id, sample_data)
        return {
            "success": True,
            "trends": trends
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Mount static files for the Dropout Risk section (if directory exists)
dropout_static_dir = os.path.join(os.path.dirname(__file__), "Dropout_risk_factor", "imp", "static")
dropout_templates_dir = os.path.join(os.path.dirname(__file__), "Dropout_risk_factor", "imp", "templates")

# Create the directories if they don't exist
os.makedirs(dropout_static_dir, exist_ok=True)
os.makedirs(dropout_templates_dir, exist_ok=True)

# Mount static files for Dropout Risk
app.mount(
    "/dropout-risk/static",
    StaticFiles(directory=dropout_static_dir, html=True),
    name="dropout_static"
)

# Mount templates for Dropout Risk
dropout_templates = Jinja2Templates(directory=dropout_templates_dir)

# Mount static files for the Interest and Quizzes section
app.mount(
    "/interest-quizzes/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "Interest_and_quizzes", "static"), html=True),
    name="interest_quizzes_static"
)

# Dashboard API Endpoints

@app.post("/api/dashboard/activity")
async def track_user_activity(request: Request):
    """Track any user activity for dashboard"""
    try:
        activity_data = await request.json()
        result = dashboard_service.track_activity(activity_data)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error tracking activity: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/activity")
async def get_user_activity(user_id: str):
    """Get user's activity data including stream assessments"""
    try:
        result = dashboard_service.get_user_activities(user_id, limit=50)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/user/{user_id}")
async def get_user_dashboard(user_id: str):
    """Get comprehensive dashboard for user"""
    try:
        result = dashboard_service.get_user_dashboard_data(user_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/activities/{user_id}")
async def get_user_activities(user_id: str, limit: int = 20):
    """Get user's recent activities"""
    try:
        result = dashboard_service.get_user_activities(user_id, limit)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting user activities: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get detailed user statistics"""
    try:
        result = dashboard_service.get_detailed_stats(user_id)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/dashboard/quiz")
async def submit_quiz_result(request: Request):
    """Submit quiz result and track in dashboard"""
    try:
        quiz_data = await request.json()
        result = dashboard_service.submit_quiz_for_user(quiz_data)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/dashboard/career-assessment")
async def submit_career_assessment(request: Request):
    """Submit career assessment and track in dashboard"""
    try:
        assessment_data = await request.json()
        result = dashboard_service.assess_career_for_user(assessment_data)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error submitting career assessment: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/dashboard/dropout-risk/sync")
async def sync_dropout_risk(request: Request):
    """Sync dropout risk assessment from external source"""
    try:
        sync_data = await request.json()
        user_id = sync_data.get('user_id')
        dropout_assessment = sync_data.get('dropout_assessment')
        
        if not user_id or not dropout_assessment:
            return JSONResponse(content={'error': 'Missing user_id or dropout_assessment'}, status_code=400)
        
        # Store in user data
        if user_id not in dashboard_service.user_data:
            dashboard_service.user_data[user_id] = {}
        
        # Mark as based on real data since it came from an actual assessment
        dropout_assessment['based_on_real_data'] = True
        dropout_assessment['sync_date'] = datetime.now().isoformat()
        
        dashboard_service.user_data[user_id]['dropout_assessment'] = dropout_assessment
        
        logger.info(f"Synced dropout assessment for user {user_id}")
        return JSONResponse(content={'success': True, 'message': 'Dropout assessment synced successfully'})
        
    except Exception as e:
        logger.error(f"Error syncing dropout risk: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/api/dashboard/dropout-risk")
async def assess_dropout_risk(request: Request):
    """Assess dropout risk and track in dashboard"""
    try:
        risk_data = await request.json()
        result = dashboard_service.assess_dropout_risk_for_user(risk_data)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error assessing dropout risk: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/dashboard/stream-prediction")
async def predict_stream(request: Request):
    """Predict stream and track in dashboard"""
    try:
        prediction_data = await request.json()
        result = dashboard_service.predict_stream_for_user(prediction_data)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error predicting stream: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/dashboard/course-recommendation")
async def get_course_recommendations(request: Request):
    """Get course recommendations and track in dashboard"""
    try:
        recommendation_data = await request.json()
        result = dashboard_service.recommend_courses_for_user(
            recommendation_data.get('stream', ''),
            recommendation_data
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting course recommendations: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get overall dashboard overview for all users"""
    try:
        result = dashboard_service.get_overview_stats()
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/dashboard/{user_id}")
async def get_dashboard_data(user_id: str):
    """Get dashboard data for a specific user"""
    try:
        data = dashboard_service.get_user_dashboard_data(user_id)
        if 'error' in data:
            return JSONResponse(content=data, status_code=500)
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error in get_dashboard_data: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/api/dashboard/overview/{user_id}")
async def get_dashboard_overview(user_id: str):
    """Get dashboard overview (summary stats)"""
    try:
        data = dashboard_service.get_user_dashboard_data(user_id)
        if 'error' in data:
            return JSONResponse(content=data, status_code=500)
        
        overview = {
            'stats': data.get('stats', {}),
            'best_stream': data.get('stream_recommendation', {}).get('best_stream'),
            'total_recommendations': len(data.get('course_recommendations', {})),
            'recent_activities': data.get('recent_activities', [])[:3]
        }
        
        return JSONResponse(content=overview)
    except Exception as e:
        logger.error(f"Error in get_dashboard_overview: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Stream Recommendation Endpoints
@app.post("/api/stream/predict")
async def predict_stream_dashboard(request: Request):
    """Predict stream for user"""
    try:
        data = await request.json()
        result = dashboard_service.predict_stream_for_user(data)
        if 'error' in result:
            return JSONResponse(content=result, status_code=500)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in predict_stream_dashboard: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Course Recommendation Endpoints
@app.post("/api/courses/recommend/{stream}")
async def recommend_courses_dashboard(stream: str, request: Request):
    """Get course recommendations for a stream"""
    try:
        data = await request.json()
        result = dashboard_service.recommend_courses_for_user(stream, data)
        if 'error' in result:
            return JSONResponse(content=result, status_code=500)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in recommend_courses_dashboard: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Career Assessment Endpoints
@app.post("/api/career/assess")
async def assess_career_dashboard(request: Request):
    """Process career assessment"""
    try:
        data = await request.json()
        result = dashboard_service.assess_career_for_user(data)
        if 'error' in result:
            return JSONResponse(content=result, status_code=500)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in assess_career_dashboard: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Quiz Endpoints
@app.post("/api/quiz/submit")
async def submit_quiz_dashboard(request: Request):
    """Submit quiz results"""
    try:
        data = await request.json()
        result = dashboard_service.submit_quiz_for_user(data)
        if 'error' in result:
            return JSONResponse(content=result, status_code=500)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in submit_quiz_dashboard: {str(e)}")
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Dropout Risk Assessment Endpoints

# E-books Endpoints
@app.get("/api/ebooks")
async def get_all_ebooks():
    """Get all e-books with categories"""
    try:
        result = ebooks_backend.get_all_ebooks()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting all e-books: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/category/{category}")
async def get_ebooks_by_category(category: str):
    """Get e-books filtered by category"""
    try:
        result = ebooks_backend.get_ebooks_by_category(category)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting e-books by category: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/stream/{stream}")
async def get_ebooks_by_stream(stream: str):
    """Get e-books filtered by academic stream"""
    try:
        result = ebooks_backend.get_ebooks_by_stream(stream)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting e-books by stream: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/{ebook_id}")
async def get_ebook_details(ebook_id: str):
    """Get detailed information about a specific e-book"""
    try:
        result = ebooks_backend.get_ebook_details(ebook_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting e-book details: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/search/{query}")
async def search_ebooks(query: str):
    """Search e-books by title, author, description, or tags"""
    try:
        result = ebooks_backend.search_ebooks(query)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching e-books: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/popular")
async def get_popular_ebooks(limit: int = 10):
    """Get most popular e-books based on downloads and ratings"""
    try:
        result = ebooks_backend.get_popular_ebooks(limit)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting popular e-books: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/recent")
async def get_recent_ebooks(limit: int = 10):
    """Get most recently added e-books"""
    try:
        result = ebooks_backend.get_recent_ebooks(limit)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting recent e-books: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/ebooks/progress/{user_id}")
async def update_user_progress(user_id: str, request: Request):
    """Update user reading progress for an e-book"""
    try:
        data = await request.json()
        result = ebooks_backend.update_user_progress(user_id, data.get('ebook_id'), data.get('progress_data', {}))
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating user progress: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/ebooks/progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get user's reading progress for all e-books"""
    try:
        result = ebooks_backend.get_user_progress(user_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

# Institution Directory Endpoints
@app.get("/institution_directory/", response_class=HTMLResponse)
async def institution_directory_page():
    """Serve the institution directory page"""
    try:
        with open("institution_directory/templates/institution_directory.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Institution Directory Not Found</h1><p>The institution directory page could not be found.</p>", status_code=404)

@app.get("/api/institutions")
async def get_all_institutions():
    """Get all institutions with categories"""
    try:
        result = institution_backend.get_all_institutions()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting all institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/category/{category}")
async def get_institutions_by_category(category: str):
    """Get institutions filtered by category"""
    try:
        result = institution_backend.get_institutions_by_category(category)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institutions by category: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/state/{state}")
async def get_institutions_by_state(state: str):
    """Get institutions filtered by state"""
    try:
        result = institution_backend.get_institutions_by_state(state)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institutions by state: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/{institution_id}")
async def get_institution_details(institution_id: str):
    """Get detailed information about a specific institution"""
    try:
        result = institution_backend.get_institution_details(institution_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institution details: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/search/{query}")
async def search_institutions(query: str):
    """Search institutions by name, city, description, or tags"""
    try:
        result = institution_backend.search_institutions(query)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/top")
async def get_top_institutions(limit: int = 10):
    """Get top institutions based on ranking and rating"""
    try:
        result = institution_backend.get_top_institutions(limit)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting top institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/states")
async def get_states_list():
    """Get list of all states with institution counts"""
    try:
        result = institution_backend.get_states_list()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting states list: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/institutions/filter")
async def filter_institutions(request: Request):
    """Filter institutions based on multiple criteria"""
    try:
        data = await request.json()
        result = institution_backend.filter_institutions(data)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error filtering institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

# Mount static files for Institution Directory section
app.mount(
    "/institution_directory/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "institution_directory", "static"), html=True),
    name="institution_directory_static"
)

# Mount static files for School Directory section
app.mount(
    "/school_directory/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "school_directory", "static"), html=True),
    name="school_directory_static"
)

# Mount static files for Timeline Tracker section
app.mount(
    "/timeline_tracker/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "timeline_tracker", "static"), html=True),
    name="timeline_tracker_static"
)

# Timeline Tracker Endpoints
@app.get("/timeline_tracker/", response_class=HTMLResponse)
async def timeline_tracker_page():
    """Serve the timeline tracker page"""
    try:
        with open("timeline_tracker/templates/timeline_tracker.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Timeline Tracker Not Found</h1><p>The timeline tracker page could not be found.</p>", status_code=404)

@app.get("/api/timeline/events")
async def get_all_timeline_events():
    """Get all timeline events with categories and counts"""
    try:
        result = timeline_backend.get_all_events()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting all timeline events: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/category/{category}")
async def get_events_by_category(category: str):
    """Get events filtered by category"""
    try:
        result = timeline_backend.get_events_by_category(category)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting events by category: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/stream/{stream}")
async def get_events_by_stream(stream: str):
    """Get events filtered by stream"""
    try:
        result = timeline_backend.get_events_by_stream(stream)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting events by stream: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/date-range")
async def get_events_by_date_range(start_date: str, end_date: str):
    """Get events filtered by date range"""
    try:
        result = timeline_backend.get_events_by_date_range(start_date, end_date)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting events by date range: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/upcoming")
async def get_upcoming_events(days: int = 30):
    """Get upcoming events within specified days"""
    try:
        result = timeline_backend.get_upcoming_events(days)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting upcoming events: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/{event_id}")
async def get_event_details(event_id: str):
    """Get detailed information about a specific event"""
    try:
        result = timeline_backend.get_event_details(event_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting event details: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/search/{query}")
async def search_timeline_events(query: str):
    """Search events by title, description, tags, or stream"""
    try:
        result = timeline_backend.search_events(query)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching timeline events: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/importance/{importance}")
async def get_events_by_importance(importance: str):
    """Get events filtered by importance level"""
    try:
        result = timeline_backend.get_events_by_importance(importance)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting events by importance: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/status/{status}")
async def get_events_by_status(status: str):
    """Get events filtered by status"""
    try:
        result = timeline_backend.get_events_by_status(status)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting events by status: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/streams")
async def get_streams_list():
    """Get list of all streams with event counts"""
    try:
        result = timeline_backend.get_streams_list()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting streams list: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/timeline/events/filter")
async def filter_timeline_events(request: Request):
    """Filter events based on multiple criteria"""
    try:
        data = await request.json()
        result = timeline_backend.filter_events(data)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error filtering timeline events: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/timeline/events/monthly")
async def get_monthly_events(year: int, month: int):
    """Get events for a specific month and year"""
    try:
        result = timeline_backend.get_monthly_events(year, month)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting monthly events: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

# School Directory Endpoints
@app.get("/school_directory/", response_class=HTMLResponse)
async def school_directory_page():
    """Serve the school directory page"""
    try:
        with open("school_directory/templates/school_directory.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    except FileNotFoundError:
        return HTMLResponse("<h1>School Directory Not Found</h1><p>The school directory page could not be found.</p>", status_code=404)

@app.get("/api/schools")
async def get_all_schools():
    """Get all schools with categories and counts"""
    try:
        result = school_backend.get_all_schools()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting all schools: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/board/{board}")
async def get_schools_by_board(board: str):
    """Get schools filtered by board"""
    try:
        result = school_backend.get_schools_by_board(board)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting schools by board: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/type/{school_type}")
async def get_schools_by_type(school_type: str):
    """Get schools filtered by type"""
    try:
        result = school_backend.get_schools_by_type(school_type)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting schools by type: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/location/{location}")
async def get_schools_by_location(location: str):
    """Get schools filtered by location"""
    try:
        result = school_backend.get_schools_by_location(location)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting schools by location: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/{school_id}")
async def get_school_details(school_id: str):
    """Get detailed information about a specific school"""
    try:
        result = school_backend.get_school_details(school_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting school details: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/search/{query}")
async def search_schools(query: str):
    """Search schools by name, location, specialization, or tags"""
    try:
        result = school_backend.search_schools(query)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching schools: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/top")
async def get_top_schools(limit: int = 10):
    """Get top schools based on rating and reviews"""
    try:
        result = school_backend.get_top_schools(limit)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting top schools: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/boards")
async def get_boards_list():
    """Get list of all boards with school counts"""
    try:
        result = school_backend.get_boards_list()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting boards list: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/schools/types")
async def get_school_types():
    """Get list of all school types with counts"""
    try:
        result = school_backend.get_school_types()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting school types: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/schools/filter")
async def filter_schools(request: Request):
    """Filter schools based on multiple criteria"""
    try:
        data = await request.json()
        result = school_backend.filter_schools(data)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error filtering schools: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

# Institution Directory Endpoints
@app.get("/institution_directory/")
async def institution_directory_page():
    """Serve the institution directory page"""
    try:
        return FileResponse("institution_directory/templates/institution_directory.html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Institution directory page not found")

@app.get("/api/institutions")
async def get_institutions():
    """Get all institutions"""
    try:
        result = institution_backend.get_all_institutions()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/category/{category}")
async def get_institutions_by_category(category: str):
    """Get institutions by category"""
    try:
        result = institution_backend.get_institutions_by_category(category)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institutions by category: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/state/{state}")
async def get_institutions_by_state(state: str):
    """Get institutions by state"""
    try:
        result = institution_backend.get_institutions_by_state(state)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institutions by state: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/{institution_id}")
async def get_institution_details(institution_id: str):
    """Get institution details"""
    try:
        result = institution_backend.get_institution_details(institution_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting institution details: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/search/{query}")
async def search_institutions(query: str):
    """Search institutions"""
    try:
        result = institution_backend.search_institutions(query)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/institutions/top")
async def get_top_institutions(limit: int = 10):
    """Get top institutions"""
    try:
        result = institution_backend.get_top_institutions(limit)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting top institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/states")
async def get_states_list():
    """Get list of states"""
    try:
        result = institution_backend.get_states_list()
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting states list: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/institutions/filter")
async def filter_institutions(request: Request):
    """Filter institutions"""
    try:
        data = await request.json()
        result = institution_backend.filter_institutions(data)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error filtering institutions: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.post("/api/college-selection/save")
async def save_college_selection(request: Request):
    """Save college selection"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        selected_colleges = data.get("selected_colleges", [])
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        result = institution_backend.save_college_selection(user_id, selected_colleges)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving college selection: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

@app.get("/api/college-selection/{user_id}")
async def get_college_selection(user_id: str):
    """Get college selection"""
    try:
        result = institution_backend.get_college_selection(user_id)
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting college selection: {str(e)}")
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=500)

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5006))
    uvicorn.run(app, host='0.0.0.0', port=port, reload=True)