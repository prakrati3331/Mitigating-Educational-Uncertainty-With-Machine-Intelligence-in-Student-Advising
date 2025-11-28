from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS  # Add CORS support
import pandas as pd
import numpy as np
import pickle
import os
import json
import time
from datetime import datetime
import json
from mistralai import Mistral
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

# Initialize the client
client = Mistral(api_key=MISTRAL_API_KEY)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)  # This allows cross-origin requests from the frontend
# Configure secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24).hex()

# Load models and encoders
def load_models():
    with open("stream_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("stream_scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("stream_label_encoder.pkl", "rb") as f:
        le = pickle.load(f)
    return model, scaler, le

model, scaler, le = load_models()

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from request
        data = request.get_json()
        
        # Prepare input data in the correct order
        input_data = [
            data['math'],
            data['science'],
            data['biology'],
            data['english'],
            data['social'],
            data['language'],
            data['logical'],
            data['analytical'],
            data['numerical'],
            data['creativity'],
            data['communication'],
            data['artistic'],
            data['practical']
        ]
        
        # Convert to DataFrame with correct column names
        columns = [
            'Math', 'Science', 'Biology', 'English', 'SocialStudies', 'Language',
            'LogicalReasoning', 'AnalyticalSkills', 'NumericalAbility',
            'Creativity', 'CommunicationSkills', 'ArtisticSkills', 'PracticalSkills'
        ]
        
        input_df = pd.DataFrame([input_data], columns=columns)
        
        # Scale the input
        scaled_input = scaler.transform(input_df)
        
        # Make prediction
        probabilities = model.predict_proba(scaled_input)[0]
        stream_names = le.classes_
        
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
            'scores': data  # Include original scores for AI analysis
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

def categorize_score(score):
    """Categorize a single score."""
    if score >= 80:
        return 'high'
    elif score >= 60:
        return 'moderate'
    else:
        return 'low'

def format_score_analysis(scores, categorized_scores):
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

def generate_insights_prompt(stream, scores, question=None, conversation_history=None):
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
        categorized_scores = {subject: categorize_score(score) for subject, score in scores.items()}
        prompt = f"""As a career advisor, provide personalized guidance based on the student's academic performance in the {stream} stream.
        
        Performance Analysis:
        {format_score_analysis(scores, categorized_scores)}
        
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

@app.route('/get_insights', methods=['POST'])
def get_insights():
    try:
        data = request.get_json()
        stream = data.get('stream')
        scores = data.get('scores', {})
        question = data.get('question')
        conversation_history = data.get('conversation_history')

        # Debug logging to see what data we're receiving
        print(f"DEBUG: Received data - Stream: '{stream}', Scores: {scores}")
        print(f"DEBUG: Stream type: {type(stream)}, Stream value: {repr(stream)}")

        # Validate that we have the required data
        if not stream:
            return jsonify({
                'status': 'error',
                'message': 'Stream recommendation is required for career guidance.'
            }), 400

        # Generate performance analysis
        categorized_scores = {subject: categorize_score(score) for subject, score in scores.items()}
        performance_analysis = format_score_analysis(scores, categorized_scores)

        print(f"DEBUG: Performance analysis generated: {performance_analysis[:100]}...")

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
                prompt = CAREER_GUIDANCE_PROMPT.format(
                    stream=stream,
                    scores=str(scores),
                    performance_analysis=performance_analysis
                )
                print(f"DEBUG: Template formatted successfully")
                print(f"DEBUG: First 200 chars of prompt: {prompt[:200]}...")
            except Exception as template_error:
                print(f"DEBUG: Template formatting error: {template_error}")
                # Fallback to manual prompt construction
                prompt = f"""
                You are an expert career counselor. Based on the student's assessment in the {stream} stream, provide comprehensive, personalized career guidance.

                STUDENT PROFILE:
                - Recommended Stream: {stream}
                - Assessment Scores: {str(scores)}
                - Performance Analysis: {performance_analysis}

                Please provide a detailed career guidance response...
                """

        # Call Mistral API
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": "You are an expert career counselor. Provide accurate, professional, and encouraging career guidance."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return jsonify({
            'status': 'success',
            'insights': response.choices[0].message.content
        })

    except Exception as e:
        app.logger.error(f"Error in get_insights: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Sorry, I encountered an error while processing your request.'
        }), 500

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

@app.route('/api/mistral-chat', methods=['POST'])
def mistral_chat():
    try:
        app.logger.info("Received request to /api/mistral-chat")
        data = request.get_json()
        
        if not data or 'message' not in data:
            app.logger.error("Message is required")
            return jsonify({'error': 'Message is required'}), 400
            
        # Support both 'userId' and 'user_id' for backward compatibility
        user_id = data.get('userId') or data.get('user_id') or f'anonymous_{int(time.time())}'
        user_message = data['message']
        
        app.logger.info(f"Processing message from user {user_id}: {user_message}")
        
        # Get or initialize conversation
        conversation = get_user_conversation(user_id)
        
        # Add user message to conversation
        conversation['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get user data from session
        recommended_stream = session.get('recommended_stream')
        if not recommended_stream and 'result' in session:
            recommended_stream = session['result'].get('recommended_stream')
        recommended_stream = recommended_stream or 'a suitable academic'  # Fallback if still None
        
        academic_scores = session.get('academic_scores', {})
        
        # Format conversation history
        conversation_history = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" 
            for msg in conversation['messages'][-5:]  # Last 5 messages
        )
        
        # Generate performance analysis
        categorized_scores = {subject: categorize_score(score) for subject, score in academic_scores.items()}
        performance_analysis = format_score_analysis(academic_scores, categorized_scores)
        
        # Create chat prompt following CAREER_GUIDANCE_PROMPT structure
        CHAT_PROMPT_TEMPLATE = """You are an expert career counselor. Based on the student's assessment in the {recommended_stream} stream, provide personalized career guidance.

STUDENT PROFILE:
- Recommended Stream: {recommended_stream}
- Performance Analysis: {performance_analysis}

CONVERSATION HISTORY:
{conversation_history}

USER'S QUESTION: {user_message}

Please provide a concise response (2-3 sentences) that directly addresses the user's question, references their stream and performance when relevant, and suggests specific actions or next steps. End with a clarifying question if appropriate."""
        
        # Format the prompt with user context
        prompt = CHAT_PROMPT_TEMPLATE.format(
            recommended_stream=recommended_stream,
            performance_analysis=performance_analysis,
            conversation_history=conversation_history,
            user_message=user_message
        )
        
        # Prepare messages for Mistral
        messages = [
            {"role": "system", "content": "You are an expert career counselor. The user has been recommended the {recommended_stream} stream based on their assessment. Provide accurate, professional, and encouraging career guidance. Keep responses concise (2-3 sentences).".format(recommended_stream=recommended_stream)},
            {"role": "user", "content": prompt}
        ]
        
        app.logger.info("Sending request to Mistral API with user context")
        
        # Generate AI response using the correct API method
        try:
            response = client.chat.complete(
                model="mistral-tiny",
                messages=messages,
                temperature=0.7
            )
            
            # Extract the AI's response from the response structure
            if hasattr(response, 'choices') and len(response.choices) > 0:
                ai_response = response.choices[0].message.content
            else:
                ai_response = "I apologize, but I'm having trouble generating a response. Could you please rephrase your question?"
                
        except Exception as e:
            app.logger.error(f"Error in Mistral API call: {str(e)}")
            ai_response = "I'm sorry, I encountered an error while processing your request. Please try again later."
        
        # Add AI response to conversation
        conversation['messages'].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': ai_response,
            'conversation_id': user_id
        })
        
    except Exception as e:
        app.logger.error(f"Error in mistral_chat: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request',
            'details': str(e)
        })

# Add this at the end of flask_app.py, after all your route definitions

@app.route('/api/set-recommended-stream', methods=['POST'])
def set_recommended_stream():
    try:
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
        stream = data.get('stream')
        if not stream:
            return jsonify({'status': 'error', 'message': 'Stream is required'}), 400
            
        # Store in session
        session['recommended_stream'] = stream
        session['academic_scores'] = data.get('scores', {})
        session.modified = True  # Ensure session is saved
        
        app.logger.info(f"Stored in session - Stream: {stream}, Scores: {data.get('scores', {})}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        app.logger.error(f"Error in set_recommended_stream: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    
    # Set the port
    port = int(os.environ.get('PORT', 5006))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)