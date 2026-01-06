import os
import json
import uuid
import requests
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# 1. LOAD CONFIGURATION
# -----------------------------------------------------------
load_dotenv()

# API Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_API_BASE")
DASHBOARD_API_URL = os.getenv("DASHBOARD_API_URL", "http://localhost:8000")


# -----------------------------------------------------------
# 2. DASHBOARD API CLIENT
# -----------------------------------------------------------
class DashboardAPIClient:
    """Client to interact with the FastAPI Dashboard API"""
    BASE_URL = "http://localhost:8000/api"  # Point to /api for FastAPI
    
    @classmethod
    def _make_request(cls, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Helper method to make HTTP requests with error handling"""
        url = f"{cls.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out")
            raise
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"Request to {url} failed with status {e.response.status_code}"
                try:
                    error_detail = e.response.json().get('detail', 'No details')
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {e.response.text}"
                logger.error(error_msg)
            else:
                logger.error(f"Request to {url} failed: {str(e)}")
            raise
    
    @classmethod
    def get_user_data(cls, user_id: str) -> Dict[str, Any]:
        """Fetch user dashboard data"""
        try:
            response = cls._make_request('GET', f"dashboard/user/{user_id}")
            data = response.json()
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return {}
    
    @classmethod
    def get_quiz_scores(cls, user_id: str) -> Dict[str, Any]:
        """Fetch quiz scores for a user - get from user data instead of separate endpoint"""
        try:
            # First get user data which contains quiz scores
            user_data = cls.get_user_data(user_id)
            
            if not user_data:
                print(f"🔍 DEBUG: No user data found for quiz scores")
                return {}
            
            print(f"🔍 DEBUG: User data keys for quiz: {list(user_data.keys())}")
            
            # Check for quiz scores in different possible locations
            quiz_scores = {}
            
            # Check if scores are directly in user data
            if 'scores' in user_data and user_data['scores']:
                quiz_scores = user_data['scores']
                print(f"🔍 DEBUG: Found scores in user_data: {quiz_scores}")
            
            # Check if scores are in tracking_scores.quiz_breakdown
            elif 'tracking_scores' in user_data and user_data['tracking_scores']:
                tracking_scores = user_data['tracking_scores']
                if 'quiz_breakdown' in tracking_scores and tracking_scores['quiz_breakdown']:
                    # Extract actual quiz scores from quiz_breakdown
                    quiz_breakdown = tracking_scores['quiz_breakdown']
                    quiz_scores = {}
                    for quiz_name, score_data in quiz_breakdown.items():
                        if score_data and isinstance(score_data, dict) and score_data.get('latest_score', 0) > 0:
                            quiz_scores[quiz_name] = {
                                'score': score_data.get('latest_score', 0),
                                'total': score_data.get('best_score', 100),  # Assuming 100 is max
                                'percentage': score_data.get('average_score', 0),
                                'date': tracking_scores.get('dates', [''])[0] if tracking_scores.get('dates') else '',
                                'category': score_data.get('category', 'Unknown')
                            }
                    print(f"🔍 DEBUG: Extracted quiz scores from tracking_scores: {quiz_scores}")
                
                # Also check for recent quiz history
                if 'history' in tracking_scores and 'dates' in tracking_scores and 'types' in tracking_scores:
                    history = tracking_scores['history']
                    dates = tracking_scores['dates']
                    types = tracking_scores['types']
                    
                    if history and dates and types:
                        for i, (score, date, quiz_type) in enumerate(zip(history, dates, types)):
                            if score > 0:  # Only include non-zero scores
                                quiz_name = quiz_type.replace('Quiz: ', '').lower().replace(' ', '_')
                                quiz_scores[quiz_name] = {
                                    'score': score,
                                    'total': 100,  # Assuming 100 is max
                                    'percentage': score,
                                    'date': date,
                                    'category': 'Recent Quiz'
                                }
                        print(f"🔍 DEBUG: Added quiz history: {quiz_scores}")
            
            # Check if scores are in activities
            elif 'activities' in user_data:
                activities = user_data['activities']
                quiz_activities = [
                    act for act in activities 
                    if isinstance(act, dict) and 
                       (act.get('type') == 'quiz' or act.get('title', '').lower().find('quiz') != -1)
                ]
                if quiz_activities:
                    # Get the latest quiz activity
                    latest_quiz = max(quiz_activities, key=lambda x: x.get('timestamp', ''))
                    if 'data' in latest_quiz:
                        quiz_scores = latest_quiz['data']
                        print(f"🔍 DEBUG: Found quiz in activities: {quiz_scores}")
            
            print(f"🔍 DEBUG: Final quiz scores: {quiz_scores}")
            return quiz_scores if isinstance(quiz_scores, dict) else {}
            
        except Exception as e:
            logger.error(f"Error getting quiz scores: {e}")
            return {}
    
    @classmethod
    def get_recent_activities(cls, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent user activities"""
        try:
            response = cls._make_request(
                'GET', 
                f"dashboard/activities/{user_id}",
                params={"limit": limit}
            )
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'activities' in data:
                    return data['activities']
                if 'data' in data:
                    return data['data']
                if 'results' in data:
                    return data['results']
                return []
            return data if isinstance(data, list) else []
                
        except Exception as e:
            logger.error(f"Error getting activities: {e}")
            return []
    
    @classmethod
    def get_stream_recommendation(cls, user_id: str) -> Dict[str, Any]:
        """Get stream recommendation for user - extract from user data"""
        try:
            # First get user data which contains stream info
            user_data = cls.get_user_data(user_id)
            
            if not user_data:
                print(f"🔍 DEBUG: No user data found for stream recommendation")
                return {"error": "User data not found"}
            
            print(f"🔍 DEBUG: User data keys for stream: {list(user_data.keys())}")
            
            # Check if stream data is directly available
            if 'stream' in user_data and user_data['stream']:
                stream = user_data['stream']
                print(f"🔍 DEBUG: Found stream: {stream}")
                
                # Look for stream-specific recommendations
                stream_key = f"{stream.lower()}_recommendations"
                if stream_key in user_data:
                    stream_recs = user_data[stream_key]
                    if isinstance(stream_recs, dict) and 'recommendations' in stream_recs:
                        return {
                            "recommended_stream": stream,
                            "recommendations": stream_recs['recommendations'],
                            "careers": stream_recs.get('careers', []),
                            "best_course": stream_recs.get('best_course', '')
                        }
                
                # Check course recommendations for this stream
                if 'course_recommendations' in user_data:
                    course_recs = user_data['course_recommendations']
                    if isinstance(course_recs, dict):
                        current_stream = course_recs.get('current_stream', '').lower()
                        if current_stream == stream.lower() and 'all_stream_recommendations' in course_recs:
                            all_recs = course_recs['all_stream_recommendations']
                            if stream.lower() in all_recs:
                                return {
                                    "recommended_stream": stream,
                                    "recommendations": [rec.get('course', rec) for rec in all_recs[stream.lower()]],
                                    "careers": [rec.get('careers', '') for rec in all_recs[stream.lower()]],
                                    "total_courses": len(all_recs[stream.lower()])
                                }
                
                return {"recommended_stream": stream}
            
            # Check career_data for stream
            if 'career_data' in user_data and user_data['career_data']:
                career_data = user_data['career_data']
                if isinstance(career_data, dict) and career_data.get('stream'):
                    stream = career_data['stream']
                    print(f"🔍 DEBUG: Found stream in career_data: {stream}")
                    
                    # Check for PCB recommendations in career_data
                    if stream.lower() == 'pcb' and 'assessment' in career_data:
                        assessment = career_data['assessment']
                        if isinstance(assessment, dict) and 'pcb_recommendations' in assessment:
                            pcb_recs = assessment['pcb_recommendations']
                            return {
                                "recommended_stream": stream,
                                "recommendations": pcb_recs.get('recommendations', []),
                                "careers": pcb_recs.get('careers', []),
                                "best_course": pcb_recs.get('best_course', '')
                            }
                    
                    return {"recommended_stream": stream}
            
            print(f"🔍 DEBUG: No stream recommendation found")
            return {"message": "No stream recommendation found. Please complete the Stream Assessment."}
            
        except Exception as e:
            logger.error(f"Error getting stream recommendation: {e}")
            return {"error": "Could not retrieve stream recommendation"}
    
    @classmethod
    def get_dropout_risk_assessment(cls, user_id: str) -> Dict[str, Any]:
        """Fetch dropout risk assessment for a user"""
        try:
            # First get user data which contains dropout assessment
            user_data = cls.get_user_data(user_id)
            
            if not user_data:
                print(f"🔍 DEBUG: No user data found for dropout assessment")
                return {}
            
            print(f"🔍 DEBUG: User data keys for dropout: {list(user_data.keys())}")
            
            # Check if dropout assessment is directly available
            if 'dropout_assessment' in user_data and user_data['dropout_assessment']:
                dropout_assessment = user_data['dropout_assessment']
                print(f"🔍 DEBUG: Found dropout_assessment: {dropout_assessment}")
                
                # Only return if it's based on real data
                if dropout_assessment.get('based_on_real_data', False):
                    return dropout_assessment
                else:
                    print(f"🔍 DEBUG: Dropout assessment not based on real data, ignoring")
                    return {}
            
            # Check if we need to generate it from engagement metrics (only if real activities exist)
            elif 'engagement_metrics' in user_data and user_data['engagement_metrics']:
                engagement = user_data['engagement_metrics']
                if isinstance(engagement, dict) and engagement.get('has_real_activities', False):
                    # Generate dropout assessment from engagement metrics
                    risk_score = max(0, 100 - engagement.get('engagement_score', 0))
                    
                    dropout_assessment = {
                        'risk_level': 'Low' if risk_score < 30 else 'Medium' if risk_score < 60 else 'High',
                        'risk_score': risk_score,
                        'factors': {
                            'engagement_score': engagement.get('engagement_score', 0),
                            'streak_days': engagement.get('streak_days', 0),
                            'total_activities': engagement.get('total_activities', 0)
                        },
                        'recommendations': [],
                        'assessment_date': user_data.get('last_updated', ''),
                        'based_on_real_data': True
                    }
                    print(f"🔍 DEBUG: Generated dropout assessment: {dropout_assessment}")
                    return dropout_assessment
                else:
                    print(f"🔍 DEBUG: No real activities found, skipping dropout assessment")
            
            print(f"🔍 DEBUG: No dropout assessment data found")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting dropout risk assessment: {e}")
            return {}


# -----------------------------------------------------------
# 3. USER SESSION MANAGEMENT
# -----------------------------------------------------------
def get_or_create_user_id() -> str:
    """Get or create a persistent user ID"""
    user_id_file = "user_id.txt"
    
    # Try to load existing user ID
    if os.path.exists(user_id_file):
        try:
            with open(user_id_file, "r") as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Could not read user ID file: {e}")
    
    # Create new user ID
    new_id = str(uuid.uuid4())
    try:
        with open(user_id_file, "w") as f:
            f.write(new_id)
    except Exception as e:
        logger.error(f"Could not save user ID: {e}")
        
    return new_id


# -----------------------------------------------------------
# 4. LOAD DASHBOARD CONTENT
# -----------------------------------------------------------
def load_dashboard_html(file_path: str) -> str:
    """Load HTML content from dashboard file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading dashboard HTML: {e}")
        return ""


def load_dashboard_js(file_path: str) -> str:
    """Extract JavaScript from dashboard HTML with proper error handling and logging
    
    Args:
        file_path: Path to the HTML file containing dashboard JavaScript
        
    Returns:
        str: Extracted JavaScript code as a string, or empty string on error
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Dashboard file not found: {file_path}")
            return ""

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            logger.error(f"Error reading dashboard file {file_path}: {str(e)}")
            return ""

        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"Error parsing HTML in {file_path}: {str(e)}")
            return ""

        js_components = []
        script_tags = soup.find_all("script")
        
        if not script_tags:
            logger.warning(f"No script tags found in {file_path}")
            return ""

        for script in script_tags:
            try:
                # Handle inline scripts
                if script.string and script.string.strip():
                    js_components.append(script.string.strip())
                
                # Handle external scripts
                if script.get("src"):
                    src = script.get("src", "").strip()
                    if src:
                        js_components.append(f"// External script: {src}")
                
            except Exception as e:
                logger.warning(f"Error processing script tag: {str(e)}")
                continue

        if not js_components:
            logger.warning("No JavaScript content found in script tags")
            return ""

        # Join with double newlines for better readability
        return "\n\n".join(js_components)

    except Exception as e:
        logger.error(f"Unexpected error in load_dashboard_js: {str(e)}", exc_info=True)
        return ""


def build_dashboard_kb(file_path: str) -> str:
    """Build knowledge base from dashboard files"""
    try:
        html_data = load_dashboard_html(file_path)
        js_data = load_dashboard_js(file_path)

        combined = f"""
### DASHBOARD HTML CONTENT ###
{html_data}

### DASHBOARD JAVASCRIPT CONTENT ###
{js_data}
"""
        splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
        chunks = splitter.split_text(combined)
        return "\n\n".join(chunks)[:50000]
    except Exception as e:
        logger.error(f"Error building dashboard KB: {e}")
        return ""


# -----------------------------------------------------------
# 5. INITIALIZE LLM MODEL
# -----------------------------------------------------------
llm = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    temperature=0.3
)


# -----------------------------------------------------------
# 6. CHATBOT PROMPT TEMPLATE
# -----------------------------------------------------------
qa_template = """
You are a helpful AI assistant for the AI Education Dashboard. You have access to the user's data and can provide personalized responses.

User Context:
- User ID: {user_id}
- Recent Activities: {recent_activities}
- Quiz Scores: {quiz_scores}

Dashboard Structure:
{context}

Rules:
1. Be conversational and helpful
2. Use the user's data to provide personalized responses
3. If the user asks about their data, provide specific information
4. If data is not available, say: "I couldn't find that information. Would you like me to help you find it?"
5. For quiz scores, provide details about their performance
6. For activity history, list recent actions with timestamps
7. Always be concise and to the point
8. If the user asks about features, explain how they work

USER QUESTION: {question}

Reply conversationally, using the available data.
"""

prompt_template = PromptTemplate(
    template=qa_template,
    input_variables=["user_id", "recent_activities", "quiz_scores", "context", "question"]
)


# -----------------------------------------------------------
# 7. CHATBOT RESPONSE GENERATION
# -----------------------------------------------------------
def ask_dashboard(user_id: str, context: str, question: str) -> str:
    """Generate a response to a user question with their data"""
    try:
        print("\n📡 Fetching user data...")
        
        # Get all available data
        print("\n🔍 Retrieving user profile data...")
        user_data = DashboardAPIClient.get_user_data(user_id)
        print("✅ User Data:", json.dumps(user_data, indent=2) if user_data else "No user data found")
        
        print("\n📊 Retrieving quiz scores...")
        quiz_scores = DashboardAPIClient.get_quiz_scores(user_id)
        print("✅ Quiz Scores:", json.dumps(quiz_scores, indent=2) if quiz_scores else "No quiz scores found")
        
        print("\n🔄 Retrieving recent activities...")
        recent_activities = DashboardAPIClient.get_recent_activities(user_id, limit=5)
        print("✅ Recent Activities:", json.dumps(recent_activities, indent=2) if recent_activities else "No recent activities found")
        
        print("\n🎓 Retrieving stream recommendations...")
        stream_info = DashboardAPIClient.get_stream_recommendation(user_id)
        print("✅ Stream Recommendation:", json.dumps(stream_info, indent=2) if stream_info else "No stream recommendation available")
        
        print("\n⚠️ Retrieving dropout risk assessment...")
        dropout_assessment = DashboardAPIClient.get_dropout_risk_assessment(user_id)
        print("✅ Dropout Assessment:", json.dumps(dropout_assessment, indent=2) if dropout_assessment else "No dropout assessment found")
        
        # Format data for the prompt
        prompt_data = {
            "user_id": user_id,
            "user_profile": json.dumps(user_data, indent=2) if user_data else "No user profile data available.",
            "recent_activities": json.dumps(recent_activities, indent=2) if recent_activities else "No recent activities found.",
            "quiz_scores": json.dumps(quiz_scores, indent=2) if quiz_scores else "No quiz scores found.",
            "stream_recommendation": json.dumps(stream_info, indent=2) if stream_info else "No stream recommendation available.",
            "dropout_assessment": json.dumps(dropout_assessment, indent=2) if dropout_assessment else "No dropout assessment found.",
            "context": context,
            "question": question
        }
        
        # Update the prompt template to include all data
        enhanced_qa_template = """
        You are a helpful AI assistant for the AI Education Dashboard. You have access to the user's data and can personalized responses.
        
        User ID: {user_id}
        
        User Profile Data:
        {user_profile}
        
        Recent Activities:
        {recent_activities}
        
        Quiz Scores:
        {quiz_scores}
        
        Stream Recommendation:
        {stream_recommendation}
        
        Dropout Risk Assessment:
        {dropout_assessment}
        
        Context: {context}
        Question: {question}
        """
        
        print("\n🤖 Generating response with the following data:")
        print(json.dumps({
            "user_id": user_id,
            "has_user_data": bool(user_data),
            "has_quiz_scores": bool(quiz_scores),
            "activity_count": len(recent_activities) if isinstance(recent_activities, list) else 0,
            "has_stream_recommendation": bool(stream_info and 'recommended_stream' in stream_info),
            "has_dropout_assessment": bool(dropout_assessment)
        }, indent=2))
        
        # Generate response
        final_prompt = enhanced_qa_template.format(**prompt_data)
        result = llm.invoke(final_prompt)
        
        # Handle different response formats
        response = ""
        if hasattr(result, 'content'):
            response = result.content.strip()
        elif isinstance(result, str):
            response = result.strip()
        else:
            response = str(result).strip()
            
        print("\n📝 Generated Response:", response)
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        error_msg = f"I'm having trouble accessing your data. Error: {str(e)}. Please make sure the main server is running and try again."
        print(f"\n❌ Error: {error_msg}")
        return error_msg


# -----------------------------------------------------------
# 8. MAIN CHATBOT INTERFACE
# -----------------------------------------------------------
if __name__ == "__main__":
    # Initialize
    print("🚀 AI Education Dashboard Chatbot")
    print("-------------------------------")
    print("Loading dashboard knowledge...")
    
    # Get or create user ID
    user_id = get_or_create_user_id()
    print(f"\n👤 User ID: {user_id}")
    
    # Load dashboard context
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "dashboard",
        "templates",
        "dashboard.html"
    )
    
    if not os.path.exists(dashboard_path):
        print("❌ Error: Could not find dashboard template. Please check the path.")
        exit(1)
    
    print("� Loading dashboard content...")
    context = build_dashboard_kb(dashboard_path)
    
    print("\n�📊 Dashboard Chatbot Ready!")
    print("Ask me anything about your dashboard or type 'exit' to quit.\n")
    print("Try asking:")
    print("- What are my recent activities?")
    print("- How did I do on my last quiz?")
    print("- What courses do you recommend for me?\n")

    # Main chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Goodbye! Feel free to come back if you have more questions! 👋")
                break
                
            # Get and display response
            print("\n🤖 ", end="", flush=True)
            response = ask_dashboard(user_id, context, user_input)
            print(response + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print("\n⚠️  Sorry, I encountered an error. Please try again.")
