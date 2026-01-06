from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import random
from datetime import datetime

# Configure Flask app to use the correct template folder
app = Flask(__name__,
            template_folder='templates',  # Explicitly set template folder
            static_folder='templates')  # Serve static files from templates folder
CORS(app)

# Quiz data - moved from JavaScript to Python for better management
QUIZ_DATA = {
    'creativity': [
        {
            'question': "Alternate Uses: You're given a plain brick. Which use is the most original and useful?",
            'options': ["A) Doorstop", "B) Garden marker with painted labels", "C) Modular bookend system (stack & interlock)", "D) Paperweight"],
            'answer': "C) Modular bookend system (stack & interlock)",
            'explanation': "This option transforms the brick into a new, reusable product with modular functionality, combining originality and practicality."
        },
        {
            'question': "Story starter: Finish this opening line in the most surprising way: 'Every clock in town stopped at 3:07 — except…'",
            'options': ["A) …the church clock, which chimed merrily.", "B) …my grandmother's watch, which continued to tick backwards.", "C) …a tiny wristwatch in the pocket of a person who hadn't been born yet.", "D) …the streetlamp, which started telling stories."],
            'answer': "C) …a tiny wristwatch in the pocket of a person who hadn't been born yet.",
            'explanation': "This creates a striking, paradoxical image that sparks curiosity and imagination, making it highly surprising and creative."
        },
        {
            'question': "Product pivot: A reusable water bottle isn't selling. Which pivot is most creative and likely to open a new market?",
            'options': ["A) Add trendy colors", "B) Market to athletes with sponsor logos", "C) Convert it into a plant propagation kit (cap = seedling dome)", "D) Drop price by 20%"],
            'answer': "C) Convert it into a plant propagation kit (cap = seedling dome)",
            'explanation': "This reframes the product into a completely new category (from drinkware to gardening), showing high creativity and potential market expansion."
        }
    ],
    'logical': [
        {
            'question': "Pattern completion: What is the next number in the sequence? 2, 6, 12, 20, 30, ?",
            'options': ["A) 36", "B) 40", "C) 42", "D) 48"],
            'answer': "C) 42",
            'explanation': "This sequence is formed by adding 4, 6, 8, 10, ... to the previous term. The next difference should be 12, so the next number in the sequence is 30 + 12 = 42."
        },
        {
            'question': "Syllogism: All speakers are listeners. Some listeners are writers. Which is true?",
            'options': ["A) Some speakers are writers.", "B) No speakers are writers.", "C) All writers are speakers.", "D) Cannot be determined."],
            'answer': "D) Cannot be determined.",
            'explanation': "From the given statements, we can conclude that some listeners are writers, but we cannot determine if any speakers are writers."
        },
        {
            'question': "Analogies: Book is to Reading as Fork is to:",
            'options': ["A) Drawing", "B) Stirring", "C) Eating", "D) Writing"],
            'answer': "C) Eating",
            'explanation': "The relationship between 'Book' and 'Reading' is that a book is used for reading. Similarly, a fork is used for eating."
        }
    ],
    'analytical': [
        {
            'question': "Percent change: A shirt costs $100. Its price increases by 20% and then later decreases by 20%. What is the final price?",
            'options': ["A) $96", "B) $100", "C) $104", "D) $120"],
            'answer': "A) $96",
            'explanation': "First, price increases by 20%: 100 + 20% of 100 = 100 + 20 = 120. Then decreases by 20%: 120 - 20% of 120 = 120 - 24 = 96."
        },
        {
            'question': "Missing value from average: The average of five numbers is 14. Four of them are 10, 12, 14 and 16. What is the fifth number?",
            'options': ["A) 14", "B) 16", "C) 18", "D) 20"],
            'answer': "C) 18",
            'explanation': "Sum of five numbers = 5 × 14 = 70. Sum of four known numbers = 10 + 12 + 14 + 16 = 52. Fifth number = 70 - 52 = 18."
        },
        {
            'question': "Ratio chaining: If A : B = 3 : 5 and B : C = 2 : 7, what is A : C?",
            'options': ["A) 3 : 35", "B) 6 : 35", "C) 3 : 7", "D) 6 : 7"],
            'answer': "B) 6 : 35",
            'explanation': "A:B = 3:5, B:C = 2:7. To chain, equalize B: multiply A:B by 2 → 6:10, B:C by 5 → 10:35. So A:C = 6:35."
        }
    ],
    'communication': [
        {
            'question': "Active Listening: When someone shares a problem with you, the best first response is to:",
            'options': ["A) Give quick advice", "B) Interrupt to share a similar story", "C) Listen carefully and paraphrase their concern", "D) Change the topic"],
            'answer': "C) Listen carefully and paraphrase their concern",
            'explanation': "Active listening involves fully focusing on the speaker and confirming understanding by paraphrasing. This shows empathy and avoids jumping to conclusions."
        },
        {
            'question': "Body Language: Which gesture generally signals openness during a conversation?",
            'options': ["A) Crossed arms", "B) Avoiding eye contact", "C) Leaning slightly forward", "D) Looking at your phone"],
            'answer': "C) Leaning slightly forward",
            'explanation': "Leaning forward signals engagement and interest, whereas crossed arms or avoiding eye contact can signal defensiveness or disinterest."
        },
        {
            'question': "Email Etiquette: What is the most effective subject line for a professional email requesting feedback?",
            'options': ["A) 'Need Help ASAP'", "B) 'Feedback Request: Draft Report (Due Friday)'", "C) 'Hey, quick question'", "D) 'Re: FYI'"],
            'answer': "B) 'Feedback Request: Draft Report (Due Friday)'",
            'explanation': "A clear, professional subject line indicates the purpose, urgency, and context, helping the recipient prioritize and respond appropriately."
        }
    ],
    'numerical': [
        {
            'question': "Percentage: A laptop costs ₹50,000 and is sold at a 10% discount. What is the selling price?",
            'options': ["A) ₹45,000", "B) ₹47,000", "C) ₹48,000", "D) ₹49,000"],
            'answer': "A) ₹45,000",
            'explanation': "Selling price = Cost price - Discount = 50,000 - (10% of 50,000) = 50,000 - 5,000 = ₹45,000."
        },
        {
            'question': "Simple Interest: Find the simple interest on ₹12,000 at 5% per annum for 3 years.",
            'options': ["A) ₹1,800", "B) ₹2,000", "C) ₹1,600", "D) ₹2,200"],
            'answer': "A) ₹1,800",
            'explanation': "SI = P × R × T / 100 = 12,000 × 5 × 3 / 100 = ₹1,800."
        },
        {
            'question': "Ratio & Proportion: If 3 pencils cost ₹15, how much will 8 pencils cost?",
            'options': ["A) ₹35", "B) ₹38", "C) ₹40", "D) ₹45"],
            'answer': "C) ₹40",
            'explanation': "Cost of 1 pencil = 15 / 3 = ₹5. Cost of 8 pencils = 8 × 5 = ₹40."
        }
    ],
    'artistic': [
        {
            'question': "Color Theory: Which color combination creates the strongest visual contrast?",
            'options': ["A) Blue and green", "B) Red and orange", "C) Blue and yellow", "D) Purple and violet"],
            'answer': "C) Blue and yellow",
            'explanation': "Blue and yellow are complementary colors, located opposite each other on the color wheel, creating maximum contrast and visual impact."
        },
        {
            'question': "Perspective: In one-point perspective drawing, all parallel lines converge at:",
            'options': ["A) A single vanishing point", "B) Two vanishing points", "C) The horizon line", "D) The viewer's eye"],
            'answer': "A) A single vanishing point",
            'explanation': "One-point perspective uses a single vanishing point on the horizon line to create depth and realistic spatial representation."
        },
        {
            'question': "Shading: Which pencil technique gives the smoothest transition between light and dark?",
            'options': ["A) Hatching", "B) Cross-hatching", "C) Blending", "D) Stippling"],
            'answer': "C) Blending",
            'explanation': "Blending smooths out pencil marks to create gradual tonal transitions, unlike hatching or stippling which produce visible texture lines or dots."
        }
    ],
    'practical': [
        {
            'question': "Basic Electrical Safety: You notice a frayed wire on a lamp. What's the safest first step?",
            'options': ["A) Plug it in to see if it works", "B) Touch it to test current", "C) Unplug it and repair or replace", "D) Cover with tape and continue"],
            'answer': "C) Unplug it and repair or replace",
            'explanation': "Exposed or frayed wires are a serious shock hazard. Always unplug before attempting any repair or replacement to ensure safety."
        },
        {
            'question': "Time Management: You have 3 tasks due today: one urgent, two important. Which do you do first?",
            'options': ["A) Start with an easy task", "B) Complete urgent task first", "C) Ignore deadlines and multitask", "D) Take a break first"],
            'answer': "B) Complete urgent task first",
            'explanation': "Tasks that are urgent and time-sensitive should be prioritized to prevent negative consequences, while important but non-urgent tasks can follow."
        },
        {
            'question': "Home Maintenance: You find a small leak under the sink. What's the best initial action?",
            'options': ["A) Tighten the pipe connections", "B) Pour sealant immediately", "C) Ignore it; it will stop", "D) Remove all pipes"],
            'answer': "A) Tighten the pipe connections",
            'explanation': "Small leaks are often caused by loose connections. Tightening them is the safest first step before considering more extensive repairs."
        }
    ],
    'mathematics': [
        {
            'question': "Algebra: Solve for x: 2x + 5 = 15",
            'options': ["A) x = 3", "B) x = 5", "C) x = 7", "D) x = 10"],
            'answer': "B) x = 5",
            'explanation': "2x + 5 = 15, subtract 5 from both sides: 2x = 10, divide by 2: x = 5."
        },
        {
            'question': "Geometry: What is the area of a circle with radius 7 cm?",
            'options': ["A) 154 cm²", "B) 44 cm²", "C) 22 cm²", "D) 154π cm²"],
            'answer': "A) 154 cm²",
            'explanation': "Area = πr² = π × 7² = π × 49 ≈ 3.14 × 49 = 154 cm²."
        },
        {
            'question': "Trigonometry: What is sin(30°)?",
            'options': ["A) 0", "B) 1/2", "C) √3/2", "D) 1"],
            'answer': "B) 1/2",
            'explanation': "sin(30°) = opposite/hypotenuse = 1/2 in a 30-60-90 triangle."
        }
    ],
    'science': [
        {
            'question': "Physics: What is the acceleration due to gravity on Earth?",
            'options': ["A) 5.8 m/s²", "B) 9.8 m/s²", "C) 12.8 m/s²", "D) 15.8 m/s²"],
            'answer': "B) 9.8 m/s²",
            'explanation': "The standard acceleration due to gravity on Earth's surface is approximately 9.8 m/s²."
        },
        {
            'question': "Chemistry: What is the chemical formula for water?",
            'options': ["A) CO₂", "B) H₂O", "C) O₂", "D) NaCl"],
            'answer': "B) H₂O",
            'explanation': "Water consists of two hydrogen atoms and one oxygen atom, so its formula is H₂O."
        },
        {
            'question': "Biology: What is the powerhouse of the cell?",
            'options': ["A) Nucleus", "B) Mitochondria", "C) Ribosome", "D) Endoplasmic reticulum"],
            'answer': "B) Mitochondria",
            'explanation': "Mitochondria are responsible for cellular respiration and energy production, earning them the nickname 'powerhouse of the cell'."
        }
    ],
    'biology': [
        {
            'question': "Cell Structure: What is the function of the cell membrane?",
            'options': ["A) Protein synthesis", "B) Energy production", "C) Selective permeability", "D) Genetic material storage"],
            'answer': "C) Selective permeability",
            'explanation': "The cell membrane controls what enters and exits the cell, providing selective permeability."
        },
        {
            'question': "Photosynthesis: Where does photosynthesis primarily occur in plants?",
            'options': ["A) Roots", "B) Stems", "C) Leaves", "D) Flowers"],
            'answer': "C) Leaves",
            'explanation': "Photosynthesis mainly occurs in the leaves where chloroplasts are concentrated and can capture sunlight."
        },
        {
            'question': "Ecology: What is the term for organisms that can make their own food?",
            'options': ["A) Heterotrophs", "B) Autotrophs", "C) Decomposers", "D) Carnivores"],
            'answer': "B) Autotrophs",
            'explanation': "Autotrophs (like plants) can synthesize their own food from inorganic substances using light or chemical energy."
        }
    ],
    'english': [
        {
            'question': "Grammar: Which sentence is grammatically correct?",
            'options': ["A) She don't like apples", "B) She doesn't like apples", "C) She don't likes apples", "D) She doesn't likes apples"],
            'answer': "B) She doesn't like apples",
            'explanation': "The correct form is 'doesn't' for third person singular in present simple tense."
        },
        {
            'question': "Vocabulary: What does 'ubiquitous' mean?",
            'options': ["A) Rare", "B) Present everywhere", "C) Temporary", "D) Expensive"],
            'answer': "B) Present everywhere",
            'explanation': "'Ubiquitous' means existing or being everywhere at the same time."
        },
        {
            'question': "Literature: Who wrote 'Romeo and Juliet'?",
            'options': ["A) Charles Dickens", "B) Jane Austen", "C) William Shakespeare", "D) Mark Twain"],
            'answer': "C) William Shakespeare",
            'explanation': "William Shakespeare wrote the tragic play 'Romeo and Juliet' in the late 16th century."
        }
    ],
    'social_studies': [
        {
            'question': "History: In which year did World War II end?",
            'options': ["A) 1943", "B) 1944", "C) 1945", "D) 1946"],
            'answer': "C) 1945",
            'explanation': "World War II ended in 1945 with the surrender of Japan following the atomic bombings of Hiroshima and Nagasaki."
        },
        {
            'question': "Geography: What is the largest continent by land area?",
            'options': ["A) Africa", "B) Asia", "C) North America", "D) Europe"],
            'answer': "B) Asia",
            'explanation': "Asia is the largest continent, covering about 30% of Earth's land area."
        },
        {
            'question': "Civics: What is the supreme law of the United States?",
            'options': ["A) The Declaration of Independence", "B) The Constitution", "C) The Bill of Rights", "D) The Federalist Papers"],
            'answer': "B) The Constitution",
            'explanation': "The United States Constitution is the supreme law of the land, establishing the framework of government."
        }
    ],
    'language': [
        {
            'question': "Linguistics: What is a synonym?",
            'options': ["A) A word with opposite meaning", "B) A word with similar meaning", "C) A made-up word", "D) A word from another language"],
            'answer': "B) A word with similar meaning",
            'explanation': "A synonym is a word or phrase that means exactly or nearly the same as another word or phrase."
        },
        {
            'question': "Etymology: What does the prefix 'anti-' mean?",
            'options': ["A) Before", "B) After", "C) Against", "D) With"],
            'answer': "C) Against",
            'explanation': "The prefix 'anti-' means against, opposed to, or preventing."
        },
        {
            'question': "Grammar: What is the past tense of 'run'?",
            'options': ["A) Runned", "B) Running", "C) Ran", "D) Run"],
            'answer': "C) Ran",
            'explanation': "'Ran' is the correct past tense form of the irregular verb 'run'."
        }
    ]
}

# Quiz results storage
quiz_results = {}

# Quiz progress storage (for partial progress)
quiz_progress = {}

@app.route('/api/quiz/progress/save', methods=['POST'])
def save_quiz_progress():
    """Save partial quiz progress with score tracking"""
    try:
        data = request.get_json()
        quiz_type = data.get('quiz_type')
        answers = data.get('answers', [])
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        timestamp = data.get('timestamp', datetime.now().isoformat())

        if not quiz_type:
            return jsonify({'error': 'Quiz type is required'}), 400

        # Calculate progress metrics
        questions_answered = len([a for a in answers if a is not None])
        progress_percentage = (questions_answered / total_questions * 100) if total_questions > 0 else 0

        # Store progress with comprehensive data
        progress_id = f"{quiz_type}_progress"
        quiz_progress[progress_id] = {
            'quiz_type': quiz_type,
            'answers': answers,
            'score': score,
            'total_questions': total_questions,
            'questions_answered': questions_answered,
            'progress_percentage': round(progress_percentage, 1),
            'timestamp': timestamp,
            'last_updated': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'message': 'Progress saved successfully',
            'quiz_type': quiz_type,
            'questions_answered': questions_answered,
            'total_questions': total_questions,
            'progress_percentage': round(progress_percentage, 1),
            'score': score
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/progress/<quiz_type>')
def load_quiz_progress(quiz_type):
    """Load saved quiz progress"""
    try:
        progress_id = f"{quiz_type}_progress"

        if progress_id in quiz_progress:
            return jsonify(quiz_progress[progress_id])
        else:
            return jsonify({
                'quiz_type': quiz_type,
                'answers': [],
                'message': 'No saved progress found'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/progress/clear/<quiz_type>', methods=['DELETE'])
def clear_quiz_progress(quiz_type):
    """Clear saved quiz progress"""
    try:
        progress_id = f"{quiz_type}_progress"

        if progress_id in quiz_progress:
            del quiz_progress[progress_id]
            return jsonify({'success': True, 'message': 'Progress cleared'})
        else:
            return jsonify({'success': True, 'message': 'No progress to clear'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve the main quiz index page"""
    return render_template('quizzes_index.html')

@app.route('/tracker')
def score_tracker():
    """Serve the score tracking page"""
    return render_template('score_tracker.html')

@app.route('/score_tracker.html')
def score_tracker_html():
    """Serve the score tracking page (HTML version)"""
    return render_template('score_tracker.html')

# Add routes with .html extension to match HTML links
@app.route('/aptitude_quizzes.html')
def aptitude_quizzes_html():
    """Serve the aptitude quizzes page (HTML version)"""
    return render_template('aptitude_quizzes.html')

@app.route('/subject_quizzes.html')
def subject_quizzes_html():
    """Serve the subject quizzes page (HTML version)"""
    return render_template('subject_quizzes.html')

@app.route('/subject_quiz.js')
def serve_subject_quiz_js():
    """Serve the subject quiz JavaScript file"""
    try:
        with open('templates/subject_quiz.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return 'File not found', 404

@app.route('/quiz.js')
def serve_quiz_js():
    """Serve the aptitude quiz JavaScript file"""
    try:
        with open('templates/quiz.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return 'File not found', 404

@app.route('/api/quiz/<quiz_type>')
def get_quiz(quiz_type):
    """Get quiz questions for a specific type"""
    if quiz_type not in QUIZ_DATA:
        return jsonify({'error': f'Quiz type "{quiz_type}" not found'}), 404

    questions = QUIZ_DATA[quiz_type]
    # Shuffle questions for variety
    shuffled_questions = random.sample(questions, min(len(questions), 10))

    return jsonify({
        'quiz_type': quiz_type,
        'questions': shuffled_questions,
        'total_questions': len(shuffled_questions)
    })

@app.route('/api/quiz/<quiz_type>/submit', methods=['POST'])
def submit_quiz(quiz_type):
    """Submit quiz answers and calculate score"""
    try:
        data = request.get_json()
        user_answers = data.get('answers', {})
        quiz_type = data.get('quiz_type', quiz_type)
        completed_locally = data.get('completed_locally', False)
        client_score = data.get('client_score')  # Client's calculated score
        client_total = data.get('client_total')  # Client's total questions

        if quiz_type not in QUIZ_DATA:
            return jsonify({'error': f'Quiz type "{quiz_type}" not found'}), 404

        questions = QUIZ_DATA[quiz_type]

        # Use client's score if provided and completed locally, otherwise calculate server score
        if completed_locally and client_score is not None and client_total is not None:
            score = client_score
            total_questions = client_total
            percentage = (score / total_questions) * 100 if total_questions > 0 else 0

            # Create results based on client's data (simplified)
            results = []
            for i, (question_key, user_answer) in enumerate(user_answers.items()):
                if i < len(questions):
                    question = questions[i]
                    # We don't know if this was correct since we used client's calculation
                    results.append({
                        'question': question['question'],
                        'user_answer': user_answer,
                        'correct_answer': question['answer'],
                        'is_correct': True,  # Assume correct since client calculated it
                        'explanation': question['explanation']
                    })
        else:
            # Original server-side calculation
            score = 0
            total_questions = len(user_answers)
            results = []

            for i, (question_key, user_answer) in enumerate(user_answers.items()):
                if i < len(questions):
                    question = questions[i]
                    correct_answer = question['answer']
                    is_correct = user_answer == correct_answer

                    if is_correct:
                        score += 10

                    results.append({
                        'question': question['question'],
                        'user_answer': user_answer,
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                        'explanation': question['explanation']
                    })

            percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        # Store result
        result_id = f"{quiz_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        user_id = data.get('user_id', f'quiz_user_{datetime.now().strftime("%Y%m%d")}')
        
        quiz_results[result_id] = {
            'quiz_type': quiz_type,
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'completed_locally': completed_locally,
            'user_id': user_id  # Store user_id for better tracking
        }

        # Log activity to dashboard service
        try:
            # Import dashboard service to log activity
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from dashboard.dashboard_service import DashboardService
            
            # Get user ID from request or create a default one
            user_id = data.get('user_id', f'quiz_user_{datetime.now().strftime("%Y%m%d")}')
            
            # Import the main user_data_store from main.py to ensure consistency
            try:
                # Import the global user_data_store from main.py
                import importlib.util
                spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py"))
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                user_data_store = main_module.user_data_store
            except:
                # Fallback to creating our own if import fails
                user_data_store = {}
            
            # Initialize dashboard service with the shared user_data_store
            dashboard_service = DashboardService(user_data_store)
            
            # Submit quiz results using the dashboard service method
            quiz_submission_data = {
                'user_id': user_id,
                'quiz_type': quiz_type,
                'score': percentage,
                'total_questions': total_questions,
                'timestamp': datetime.now().isoformat()
            }
            
            # Use the dashboard service's submit_quiz_for_user method
            dashboard_result = dashboard_service.submit_quiz_for_user(quiz_submission_data)
            if 'error' in dashboard_result:
                print(f"Dashboard service error: {dashboard_result['error']}")
            else:
                print(f"Successfully submitted quiz to dashboard: {dashboard_result}")
            
        except Exception as e:
            print(f"Error logging quiz activity to dashboard: {e}")
            # Don't fail the quiz submission if dashboard logging fails

        return jsonify({
            'result_id': result_id,
            'quiz_type': quiz_type,
            'score': score,
            'total_questions': total_questions,
            'percentage': round(percentage, 1),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/results/<result_id>')
def get_quiz_result(result_id):
    """Get a specific quiz result"""
    if result_id in quiz_results:
        return jsonify(quiz_results[result_id])
    return jsonify({'error': 'Result not found'}), 404

@app.route('/api/quiz/results')
def get_all_results():
    """Get all quiz results"""
    return jsonify({
        'results': list(quiz_results.values()),
        'total_results': len(quiz_results)
    })

@app.route('/api/quiz/score-analytics')
def get_score_analytics():
    """Get comprehensive score analytics across all quiz types"""
    try:
        # Calculate analytics for completed quizzes
        all_results = list(quiz_results.values())
        progress_data = list(quiz_progress.values())

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

        return jsonify(analytics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/user-progress/<quiz_type>')
def get_user_progress(quiz_type):
    """Get detailed progress for a specific quiz type"""
    try:
        progress_id = f"{quiz_type}_progress"

        if progress_id in quiz_progress:
            progress = quiz_progress[progress_id]

            # Get completed results for this quiz type
            completed_results = [r for r in quiz_results.values() if r['quiz_type'] == quiz_type]

            return jsonify({
                'current_progress': progress,
                'completed_attempts': len(completed_results),
                'best_score': max([r['score'] for r in completed_results], default=0),
                'average_score': round(sum([r['score'] for r in completed_results]) / len(completed_results), 2) if completed_results else 0,
                'improvement_suggestions': generate_improvement_suggestions(quiz_type, progress, completed_results)
            })
        else:
            return jsonify({
                'current_progress': None,
                'completed_attempts': 0,
                'best_score': 0,
                'average_score': 0,
                'improvement_suggestions': []
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_improvement_suggestions(quiz_type, progress, completed_results):
    """Generate personalized improvement suggestions"""
    suggestions = []

    if not progress or progress['questions_answered'] == 0:
        suggestions.append("Start the quiz to begin tracking your progress!")
        return suggestions

    # Analyze weak areas based on progress
    if progress['progress_percentage'] < 50:
        suggestions.append("Focus on completing more questions to build confidence.")
    elif progress['progress_percentage'] < 80:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
