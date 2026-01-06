from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import pickle
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING
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

# Initialize the arts recommender instance
arts_recommender = ArtsCourseRecommender()

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

        # Get or initialize conversation
        conversation = get_user_conversation(user_id)

        # Add user message to conversation
        conversation['messages'].append({
            'role': 'user',
            'content': str(user_message),  # Ensure content is a string
            'timestamp': datetime.now().isoformat()
        })

        # Get user data from session (simplified for FastAPI)
        recommended_stream = 'a suitable academic'  # Default fallback
        academic_scores = {}

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

Please provide a concise response (2-3 sentences) that directly addresses the user's question, references their stream and performance when relevant, and suggests specific actions or next steps. End with a clarifying question if appropriate."""

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

        return JSONResponse({
            'response': ai_response,
            'conversation_id': user_id
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mistral_chat: {str(e)}")
        raise HTTPException(status_code=500, detail='An error occurred while processing your request')

@app.post('/api/set-recommended-stream')
async def set_recommended_stream(data: "StreamData"):
    """Set the recommended stream for a user"""
    try:
        stream = data.stream
        scores = data.scores

        if not stream:
            raise HTTPException(status_code=400, detail='Stream is required')

        # In FastAPI, we'll use a simple in-memory store instead of sessions
        # Store in global conversation history (simplified approach)
        logger.info(f"Stored stream data - Stream: {stream}, Scores: {scores}")

        return JSONResponse({'status': 'success'})

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

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/ebooks", response_class=HTMLResponse)
async def ebooks():
    with open("ebooks.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/home", response_class=HTMLResponse)
async def home_page():
    with open("home.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/institution_directory_fixed", response_class=HTMLResponse)
async def institution_directory_fixed():
    with open("institution_directory_fixed.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/recommendation_hub", response_class=HTMLResponse)
async def recommendation_hub():
    with open("recommendation_hub.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/school_directory", response_class=HTMLResponse)
async def school_directory():
    with open("school_directory.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

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
    with open("institution_directory_fixed.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/school_directory.html", response_class=HTMLResponse)
async def school_directory_html():
    with open("school_directory.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/ebooks.html", response_class=HTMLResponse)
async def ebooks_html():
    with open("ebooks.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_html():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/stream_selection.html", response_class=HTMLResponse)
async def stream_selection_html():
    with open("stream_selection.html", "r", encoding="utf-8") as f:
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

@app.get("/timeline_tracker.html", response_class=HTMLResponse)
async def timeline_tracker():
    with open("timeline_tracker.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/favicon.ico")
async def favicon():
    # Return a simple 204 No Content response for favicon requests
    # This prevents 404 errors in browser logs
    from fastapi.responses import Response
    return Response(status_code=204)

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5006))
    uvicorn.run(app, host='0.0.0.0', port=port, reload=True)