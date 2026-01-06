// Array of Mathematics questions for Class 10
const mathematicsQuestions = [
    {
        question: "If (x + 3)(x – 2) = 0, then the roots are:",
        options: ["A) –3, 2", "B) 3, –2", "C) 3, 2", "D) –3, –2"],
        answer: "A) –3, 2",
        explanation: "Setting each factor equal to zero: x + 3 = 0 gives x = -3, x - 2 = 0 gives x = 2."
    },
    {
        question: "The sum of roots of the quadratic equation 2x² – 5x + 3 = 0 is:",
        options: ["A) 5/2", "B) –5/2", "C) 3/2", "D) –3/2"],
        answer: "A) 5/2",
        explanation: "For ax² + bx + c = 0, sum of roots = -b/a = -(-5)/2 = 5/2."
    },
    {
        question: "The nth term of an arithmetic progression (AP) is given by an = 7 + (n – 1)×3. Find the 10th term.",
        options: ["A) 34", "B) 37", "C) 31", "D) 40"],
        answer: "A) 34",
        explanation: "a₁₀ = 7 + (10-1)×3 = 7 + 9×3 = 7 + 27 = 34."
    },
    {
        question: "If sin A = 3/5, then cos A = ?",
        options: ["A) 4/5", "B) 5/4", "C) 3/4", "D) 5/3"],
        answer: "A) 4/5",
        explanation: "In a right triangle, cos A = adjacent/hypotenuse. By Pythagoras: cos A = √(1 - sin²A) = √(1 - 9/25) = √(16/25) = 4/5."
    },
    {
        question: "The distance between the points (–3, 4) and (3, –4) is:",
        options: ["A) 5", "B) 7", "C) 8", "D) 10"],
        answer: "D) 10",
        explanation: "Distance = √[(x₂-x₁)² + (y₂-y₁)²] = √[(3-(-3))² + (-4-4)²] = √[(6)² + (-8)²] = √(36 + 64) = √100 = 10."
    },
    {
        question: "The sum of the first 20 natural numbers is:",
        options: ["A) 200", "B) 190", "C) 210", "D) 220"],
        answer: "C) 210",
        explanation: "Sum of first n natural numbers = n(n+1)/2 = 20×21/2 = 420/2 = 210."
    },
    {
        question: "In a right-angled triangle, if one angle is 30°, then the ratio of sides opposite and hypotenuse is:",
        options: ["A) 1:1", "B) 1:2", "C) √3:1", "D) 2:1"],
        answer: "B) 1:2",
        explanation: "In 30-60-90 triangle, sides are in ratio 1 : √3 : 2, where opposite 30° is smallest side, hypotenuse is twice that."
    },
    {
        question: "The mean of the first five odd natural numbers is:",
        options: ["A) 3", "B) 5", "C) 7", "D) 9"],
        answer: "B) 5",
        explanation: "First five odd numbers: 1,3,5,7,9. Mean = (1+3+5+7+9)/5 = 25/5 = 5."
    },
    {
        question: "The surface area of a sphere of radius 7 cm is:",
        options: ["A) 154 cm²", "B) 308 cm²", "C) 616 cm²", "D) 1540 cm²"],
        answer: "C) 616 cm²",
        explanation: "Surface area of sphere = 4πr² = 4×3.14×49 ≈ 615.44 cm², which is approximately 616 cm²."
    },
    {
        question: "If the coordinates of A and B are (2, 3) and (4, 7), then the coordinates of the midpoint M are:",
        options: ["A) (3, 5)", "B) (2, 5)", "C) (3, 4)", "D) (4, 5)"],
        answer: "A) (3, 5)",
        explanation: "Midpoint formula: ((x₁+x₂)/2, (y₁+y₂)/2) = ((2+4)/2, (3+7)/2) = (6/2, 10/2) = (3, 5)."
    }
];

// Array of Science questions (Physics + Chemistry)
const scienceQuestions = [
    {
        question: "What is the SI unit of force?",
        options: ["A) Newton", "B) Joule", "C) Watt", "D) Pascal"],
        answer: "A) Newton",
        explanation: "Force is measured in Newtons (N), where 1 N = 1 kg·m/s²."
    },
    {
        question: "Which gas is evolved when metals react with acids?",
        options: ["A) Oxygen", "B) Hydrogen", "C) Carbon dioxide", "D) Nitrogen"],
        answer: "B) Hydrogen",
        explanation: "Metals react with dilute acids to produce hydrogen gas: Metal + Acid → Salt + H₂."
    },
    {
        question: "The speed of light in vacuum is approximately:",
        options: ["A) 3 × 10⁶ m/s", "B) 3 × 10⁸ m/s", "C) 3 × 10¹⁰ m/s", "D) 3 × 10¹² m/s"],
        answer: "B) 3 × 10⁸ m/s",
        explanation: "Speed of light in vacuum is 299,792,458 m/s, approximately 3 × 10⁸ m/s."
    },
    {
        question: "What is the chemical formula of table salt?",
        options: ["A) NaOH", "B) NaCl", "C) Na₂CO₃", "D) NaHCO₃"],
        answer: "B) NaCl",
        explanation: "Sodium chloride (NaCl) is the chemical name for table salt."
    },
    {
        question: "Which of the following is a renewable source of energy?",
        options: ["A) Coal", "B) Petroleum", "C) Solar energy", "D) Natural gas"],
        answer: "C) Solar energy",
        explanation: "Solar energy is renewable as it comes from the sun and is inexhaustible."
    },
    {
        question: "What is the boiling point of water at standard atmospheric pressure?",
        options: ["A) 0°C", "B) 50°C", "C) 100°C", "D) 150°C"],
        answer: "C) 100°C",
        explanation: "Water boils at 100°C at standard atmospheric pressure (1 atm or 760 mm Hg)."
    },
    {
        question: "Which element has the atomic number 1?",
        options: ["A) Helium", "B) Hydrogen", "C) Lithium", "D) Carbon"],
        answer: "B) Hydrogen",
        explanation: "Hydrogen has atomic number 1, making it the lightest and first element in the periodic table."
    },
    {
        question: "What is the chemical symbol for gold?",
        options: ["A) Go", "B) Gd", "C) Au", "D) Ag"],
        answer: "C) Au",
        explanation: "Gold's chemical symbol is Au, derived from the Latin word 'aurum' meaning gold."
    },
    {
        question: "Which force keeps us grounded on Earth?",
        options: ["A) Magnetic force", "B) Gravitational force", "C) Frictional force", "D) Electrostatic force"],
        answer: "B) Gravitational force",
        explanation: "Gravity is the force that attracts objects with mass toward each other, keeping us on Earth's surface."
    },
    {
        question: "What is the pH value of pure water?",
        options: ["A) 0", "B) 7", "C) 14", "D) 10"],
        answer: "B) 7",
        explanation: "Pure water has a neutral pH of 7, meaning it is neither acidic nor basic."
    }
];

// Array of Biology questions
const biologyQuestions = [
    {
        question: "What is the powerhouse of the cell?",
        options: ["A) Nucleus", "B) Mitochondria", "C) Ribosome", "D) Endoplasmic reticulum"],
        answer: "B) Mitochondria",
        explanation: "Mitochondria are called the powerhouse of the cell as they produce ATP (energy currency of the cell)."
    },
    {
        question: "Which blood group is known as the universal donor?",
        options: ["A) A", "B) B", "C) AB", "D) O"],
        answer: "D) O",
        explanation: "Blood group O is the universal donor as it can donate blood to all other blood groups."
    },
    {
        question: "What is the process by which plants make their food?",
        options: ["A) Respiration", "B) Photosynthesis", "C) Transpiration", "D) Digestion"],
        answer: "B) Photosynthesis",
        explanation: "Photosynthesis is the process where plants use sunlight, CO₂, and water to produce glucose and oxygen."
    },
    {
        question: "Which vitamin is produced by our skin when exposed to sunlight?",
        options: ["A) Vitamin A", "B) Vitamin B", "C) Vitamin C", "D) Vitamin D"],
        answer: "D) Vitamin D",
        explanation: "Vitamin D is synthesized in the skin when exposed to ultraviolet rays from sunlight."
    },
    {
        question: "What is the largest organ in the human body?",
        options: ["A) Heart", "B) Brain", "C) Liver", "D) Skin"],
        answer: "D) Skin",
        explanation: "The skin is the largest organ, covering the entire body and serving as a protective barrier."
    },
    {
        question: "What is the basic unit of life?",
        options: ["A) Tissue", "B) Organ", "C) Cell", "D) System"],
        answer: "C) Cell",
        explanation: "The cell is the basic structural and functional unit of all living organisms."
    },
    {
        question: "Which part of the plant conducts photosynthesis?",
        options: ["A) Root", "B) Stem", "C) Leaf", "D) Flower"],
        answer: "C) Leaf",
        explanation: "Leaves contain chlorophyll and are the primary sites for photosynthesis in plants."
    },
    {
        question: "What is the function of red blood cells?",
        options: ["A) Fight infections", "B) Carry oxygen", "C) Blood clotting", "D) Produce antibodies"],
        answer: "B) Carry oxygen",
        explanation: "Red blood cells contain hemoglobin which binds to oxygen and transports it throughout the body."
    },
    {
        question: "Which gas do plants absorb during photosynthesis?",
        options: ["A) Oxygen", "B) Nitrogen", "C) Carbon dioxide", "D) Hydrogen"],
        answer: "C) Carbon dioxide",
        explanation: "Plants absorb carbon dioxide from the atmosphere and use it in photosynthesis to produce glucose."
    },
    {
        question: "What is the longest bone in the human body?",
        options: ["A) Humerus", "B) Femur", "C) Tibia", "D) Radius"],
        answer: "B) Femur",
        explanation: "The femur (thigh bone) is the longest and strongest bone in the human body."
    }
];

// Array of English questions
const englishQuestions = [
    {
        question: "Which of the following is a synonym for 'happy'?",
        options: ["A) Sad", "B) Angry", "C) Joyful", "D) Tired"],
        answer: "C) Joyful",
        explanation: "Joyful means feeling or expressing great pleasure and happiness."
    },
    {
        question: "What is the past tense of 'run'?",
        options: ["A) Running", "B) Ran", "C) Runs", "D) Run"],
        answer: "B) Ran",
        explanation: "The past tense of the irregular verb 'run' is 'ran'."
    },
    {
        question: "Which sentence uses the correct article?",
        options: ["A) I saw elephant in the zoo", "B) I saw a elephant in the zoo", "C) I saw an elephant in the zoo", "D) I saw the elephant in zoo"],
        answer: "C) I saw an elephant in the zoo",
        explanation: "We use 'an' before words starting with vowel sounds. 'Elephant' starts with a vowel sound."
    },
    {
        question: "What type of word is 'quickly'?",
        options: ["A) Noun", "B) Verb", "C) Adjective", "D) Adverb"],
        answer: "D) Adverb",
        explanation: "Quickly is an adverb as it modifies verbs, adjectives, or other adverbs."
    },
    {
        question: "Choose the correct preposition: She is afraid _____ spiders.",
        options: ["A) at", "B) of", "C) in", "D) on"],
        answer: "B) of",
        explanation: "We use 'afraid of' to express fear of something."
    },
    {
        question: "Which of the following is an antonym of 'brave'?",
        options: ["A) Courageous", "B) Fearless", "C) Cowardly", "D) Bold"],
        answer: "C) Cowardly",
        explanation: "Cowardly means lacking courage, which is the opposite of brave."
    },
    {
        question: "What is the plural form of 'child'?",
        options: ["A) Childs", "B) Childes", "C) Children", "D) Childrens"],
        answer: "C) Children",
        explanation: "The plural of 'child' is 'children', which is an irregular plural form."
    },
    {
        question: "Which sentence is in the present continuous tense?",
        options: ["A) I eat breakfast", "B) I ate breakfast", "C) I am eating breakfast", "D) I will eat breakfast"],
        answer: "C) I am eating breakfast",
        explanation: "Present continuous tense uses 'am/is/are' + verb-ing form."
    },
    {
        question: "What is the correct spelling of the word meaning 'to make something simpler'?",
        options: ["A) Simplify", "B) Simplefy", "C) Simpify", "D) Simplefie"],
        answer: "A) Simplify",
        explanation: "The correct spelling is 'simplify', meaning to make something easier to understand or do."
    },
    {
        question: "Which punctuation mark is used to show possession?",
        options: ["A) Comma (,)", "B) Apostrophe (')", "C) Question mark (?)", "D) Exclamation mark (!)"],
        answer: "B) Apostrophe (')",
        explanation: "An apostrophe is used to show possession, as in 'John's book'."
    }
];

// Array of Social Studies questions
const socialStudiesQuestions = [
    {
        question: "Who was the first President of India?",
        options: ["A) Jawaharlal Nehru", "B) Mahatma Gandhi", "C) Dr. Rajendra Prasad", "D) Sardar Patel"],
        answer: "C) Dr. Rajendra Prasad",
        explanation: "Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962."
    },
    {
        question: "In which year did India gain independence?",
        options: ["A) 1945", "B) 1947", "C) 1950", "D) 1952"],
        answer: "B) 1947",
        explanation: "India gained independence from British rule on August 15, 1947."
    },
    {
        question: "What is the capital of France?",
        options: ["A) London", "B) Berlin", "C) Paris", "D) Rome"],
        answer: "C) Paris",
        explanation: "Paris is the capital and largest city of France."
    },
    {
        question: "The Great Wall of China was built primarily to protect against:",
        options: ["A) Mongols", "B) Japanese", "C) Russians", "D) Koreans"],
        answer: "A) Mongols",
        explanation: "The Great Wall was built to protect Chinese states from invasions by nomadic groups like the Mongols."
    },
    {
        question: "Which river is considered sacred in Hinduism?",
        options: ["A) Indus", "B) Brahmaputra", "C) Ganges", "D) Yamuna"],
        answer: "C) Ganges",
        explanation: "The Ganges River is considered sacred in Hinduism and is worshipped as Goddess Ganga."
    },
    {
        question: "Who was the first Prime Minister of India?",
        options: ["A) Dr. Rajendra Prasad", "B) Sardar Patel", "C) Jawaharlal Nehru", "D) Lal Bahadur Shastri"],
        answer: "C) Jawaharlal Nehru",
        explanation: "Jawaharlal Nehru was the first Prime Minister of independent India, serving from 1947 to 1964."
    },
    {
        question: "Which continent is known as the 'Dark Continent'?",
        options: ["A) Asia", "B) Africa", "C) South America", "D) Australia"],
        answer: "B) Africa",
        explanation: "Africa was called the 'Dark Continent' due to lack of European knowledge about its interior until the 19th century."
    },
    {
        question: "What is the largest desert in the world?",
        options: ["A) Sahara Desert", "B) Arabian Desert", "C) Gobi Desert", "D) Kalahari Desert"],
        answer: "A) Sahara Desert",
        explanation: "The Sahara Desert in North Africa is the largest hot desert in the world, covering about 9.2 million square kilometers."
    },
    {
        question: "Which is the longest river in the world?",
        options: ["A) Amazon River", "B) Nile River", "C) Yangtze River", "D) Mississippi River"],
        answer: "B) Nile River",
        explanation: "The Nile River in Africa is the longest river in the world, flowing for about 6,650 kilometers."
    },
    {
        question: "In which year was the United Nations founded?",
        options: ["A) 1940", "B) 1945", "C) 1950", "D) 1955"],
        answer: "B) 1945",
        explanation: "The United Nations was established on October 24, 1945, after World War II to maintain international peace and security."
    }
];

// Array of Language questions (Hindi/Other)
const languageQuestions = [
    {
        question: "नमस्ते का अंग्रेजी में क्या मतलब होता है?",
        options: ["A) Goodbye", "B) Hello", "C) Thank you", "D) Sorry"],
        answer: "B) Hello",
        explanation: "नमस्ते (Namaste) का अंग्रेजी में मतलब 'Hello' होता है।"
    },
    {
        question: "हिंदी भाषा में 'मैं' का बहुवचन क्या है?",
        options: ["A) हम", "B) आप", "C) वे", "D) यह"],
        answer: "A) हम",
        explanation: "'मैं' का बहुवचन 'हम' होता है।"
    },
    {
        question: "कौन सा शब्द पुल्लिंग है?",
        options: ["A) किताब", "B) मेज", "C) कुर्सी", "D) दीवार"],
        answer: "B) मेज",
        explanation: "मेज (table) पुल्लिंग शब्द है।"
    },
    {
        question: "हिंदी वर्णमाला में कितने स्वर हैं?",
        options: ["A) 10", "B) 11", "C) 12", "D) 13"],
        answer: "D) 13",
        explanation: "हिंदी वर्णमाला में 13 स्वर हैं: अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ, अं, अः।"
    },
    {
        question: "कौन सा त्योहार दीपावली कहलाता है?",
        options: ["A) होली", "B) दशहरा", "C) दीपावली", "D) ईद"],
        answer: "C) दीपावली",
        explanation: "दीपावली भारत का प्रमुख त्योहार है जिसे रोशनी का त्योहार कहा जाता है।"
    },
    {
        question: "हिंदी में 'नमकीन' का मतलब क्या है?",
        options: ["A) मीठा", "B) खट्टा", "C) नमकीन", "D) तीखा"],
        answer: "C) नमकीन",
        explanation: "'नमकीन' शब्द का मतलब नमक वाला या नमक मिला हुआ होता है।"
    },
    {
        question: "'किताब' शब्द किस लिंग का है?",
        options: ["A) पुल्लिंग", "B) स्त्रीलिंग", "C) नपुंसकलिंग", "D) कोई नहीं"],
        answer: "B) स्त्रीलिंग",
        explanation: "'किताब' (book) स्त्रीलिंग शब्द है।"
    },
    {
        question: "हिंदी में सबसे छोटा शब्द कौन सा है?",
        options: ["A) अ", "B) आ", "C) इ", "D) उ"],
        answer: "A) अ",
        explanation: "'अ' हिंदी का सबसे छोटा और पहला स्वर है।"
    },
    {
        question: "कौन सा शब्द 'बहुत' का पर्यायवाची है?",
        options: ["A) कम", "B) अधिक", "C) थोड़ा", "D) कुछ"],
        answer: "B) अधिक",
        explanation: "'बहुत' का पर्यायवाची 'अधिक' है।"
    },
    {
        question: "हिंदी साहित्य के किस काल को 'आधुनिक काल' कहा जाता है?",
        options: ["A) 1850-1900", "B) 1900-1947", "C) 1947-वर्तमान", "D) 1800-1850"],
        answer: "C) 1947-वर्तमान",
        explanation: "हिंदी साहित्य का आधुनिक काल 1947 से वर्तमान समय तक माना जाता है।"
    }
];

// Global state variables
let currentQuizType = '';
let currentQuestion = 0;
let score = 0;
let userAnswers = [];

// Function to start the quiz with specified type
function startQuiz(type) {
    currentQuizType = type;
    document.getElementById('main-content').classList.add('hidden');
    document.getElementById('quiz-container').classList.add('active');
    currentQuestion = 0;
    score = 0;
    userAnswers = []; // Reset user answers
    displayAllQuestions();
}

// Function to go back to main page
function goBack() {
    window.location.href = '../recommendation_hub.html';
}

// Function to display all questions at once
function displayAllQuestions() {
    const quizContainer = document.getElementById('quiz-container');

    // Show loading state first
    quizContainer.innerHTML = `
        <div class="quiz-content">
            <button id="back-btn" onclick="goBack()">Back to Main</button>
            <div class="quiz-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Quiz...</div>
            </div>
        </div>
    `;

    // Simulate loading delay for better UX
    setTimeout(() => {
        let questions;

        // Determine which question array to use based on current quiz type
        if (currentQuizType === 'science') {
            questions = scienceQuestions;
        } else if (currentQuizType === 'biology') {
            questions = biologyQuestions;
        } else if (currentQuizType === 'english') {
            questions = englishQuestions;
        } else if (currentQuizType === 'social-studies') {
            questions = socialStudiesQuestions;
        } else if (currentQuizType === 'language') {
            questions = languageQuestions;
        } else {
            questions = mathematicsQuestions;
        }

        // Initialize userAnswers array if not already done
        if (userAnswers.length === 0) {
            userAnswers = new Array(questions.length).fill(null);
        }

        // Generate HTML for all questions
        let questionsHTML = questions.map((q, index) => `
            <div class="question-card" id="question-${index}">
                <h3 class="question-number">Question ${index + 1}</h3>
                <h4 class="question-text">${q.question}</h4>
                <div class="question-options">
                    ${q.options.map((option, optionIndex) => `
                        <label class="option-label">
                            <input type="radio" name="question-${index}" value="${option}" ${userAnswers[index] === option ? 'checked' : ''} onchange="saveAnswer(${index}, '${option}')">
                            <span class="option-text">${option}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `).join('');

        quizContainer.innerHTML = `
            <div class="quiz-content">
                <button id="back-btn" onclick="goBack()">Back to Main</button>
                <div class="quiz-progress">
                    <span>Answer all questions and click submit to see your results</span>
                </div>
                <div class="all-questions">
                    ${questionsHTML}
                </div>
                <div class="submit-section">
                    <button class="btn btn-primary submit-btn" onclick="submitQuiz()">Submit Quiz</button>
                </div>
            </div>
        `;
    }, 800); // 800ms loading delay for better UX
}

// Function to save user's answer for a specific question
function saveAnswer(questionIndex, selectedAnswer) {
    userAnswers[questionIndex] = selectedAnswer;
}

// Function to submit quiz and calculate score
function submitQuiz() {
    let questions;

    // Determine which question array to use based on current quiz type
    if (currentQuizType === 'science') {
        questions = scienceQuestions;
    } else if (currentQuizType === 'biology') {
        questions = biologyQuestions;
    } else if (currentQuizType === 'english') {
        questions = englishQuestions;
    } else if (currentQuizType === 'social-studies') {
        questions = socialStudiesQuestions;
    } else if (currentQuizType === 'language') {
        questions = languageQuestions;
    } else {
        questions = mathematicsQuestions;
    }

    // Calculate score
    score = 0;
    for (let i = 0; i < questions.length; i++) {
        if (userAnswers[i] === questions[i].answer) {
            score++;
        }
    }

    // Show results
    showResults(questions);
}

// Function to show quiz results
function showResults(questions) {
    const quizContainer = document.getElementById('quiz-container');
    console.log('showResults called with questions:', questions.length);
    console.log('Questions data:', questions);

    // Generate results HTML with detailed feedback
    let resultsHTML = `
        <div class="quiz-content results-content">
            <button id="back-btn" onclick="goBack()">Back to Main</button>
            <div class="results-header">
                <h2>Quiz Complete!</h2>
                <div class="final-score">Your Score: ${score} / ${questions.length}</div>
                <div class="score-percentage">${Math.round((score / questions.length) * 100)}%</div>
            </div>
    `;

    // Add detailed question review - show for all questions
    resultsHTML += `
        <div class="question-review">
            <h3>Question Review:</h3>
            ${questions.map((q, index) => {
                console.log(`Question ${index + 1}:`, q.question, 'Answer:', q.answer, 'User Answer:', userAnswers[index], 'Has explanation:', !!q.explanation);
                return `
            <div class="review-item ${userAnswers[index] === q.answer ? 'correct' : 'incorrect'}">
                <div class="review-question">
                    <strong>Q${index + 1}:</strong> ${q.question}
                </div>
                <div class="review-answer">
                    <strong>Your Answer:</strong> ${userAnswers[index] || 'Not answered'}
                </div>
                <div class="review-correct">
                    <strong>Correct Answer:</strong> ${q.answer}
                </div>
                ${q.explanation ? `
                    <div class="review-explanation">
                        <strong>Explanation:</strong> ${q.explanation}
                    </div>
                ` : `
                    <div class="review-explanation">
                        <strong>Explanation:</strong> <em>Explanation not available for this question.</em>
                    </div>
                `}
            </div>
        `}).join('')}
        </div>
    `;

    resultsHTML += `
            <div class="results-actions">
                <button class="btn btn-primary" onclick="startQuiz('${currentQuizType}')">Retake Quiz</button>
                <button class="btn btn-outline-primary" onclick="goBack()">Back to Categories</button>
            </div>
        </div>
    `;

    console.log('Generated results HTML length:', resultsHTML.length);
    console.log('Setting innerHTML...');
    quizContainer.innerHTML = resultsHTML;
    console.log('Results displayed successfully');
}
