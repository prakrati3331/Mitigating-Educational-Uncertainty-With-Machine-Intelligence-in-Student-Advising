"""
Quiz and Interest data for career assessment
"""

# Interest categories and questions
INTEREST_QUESTIONS = [
    {
        'id': 'scientific',
        'text': 'How much do you enjoy conducting experiments or analyzing data?',
        'category': 'scientific'
    },
    {
        'id': 'artistic',
        'text': 'How much do you enjoy creative activities like drawing, writing, or music?',
        'category': 'artistic'
    },
    {
        'id': 'social',
        'text': 'How much do you enjoy helping or teaching others?',
        'category': 'social'
    },
    {
        'id': 'enterprising',
        'text': 'How much do you enjoy leading or influencing others?',
        'category': 'enterprising'
    },
    {
        'id': 'conventional',
        'text': 'How much do you enjoy working with numbers and following set procedures?',
        'category': 'conventional'
    },
    {
        'id': 'realistic',
        'text': 'How much do you enjoy working with tools, machines, or outdoor activities?',
        'category': 'realistic'
    }
]

# Career assessment quizzes
QUIZZES = {
    'personality': {
        'title': 'Personality Assessment',
        'description': 'Discover your work personality type',
        'questions': [
            'I enjoy working with my hands and practical tasks.',
            'I like to analyze problems and find solutions.',
            'I enjoy creative activities like art, music, or writing.',
            'I like helping and working with people.',
            'I enjoy leading and making decisions.',
            'I prefer structured and organized work environments.'
        ],
        'categories': ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
    },
    'skills': {
        'title': 'Skills Assessment',
        'description': 'Rate your skills in different areas',
        'questions': [
            'Mechanical skills (using tools, fixing things)',
            'Analytical and mathematical skills',
            'Creative and artistic abilities',
            'Communication and interpersonal skills',
            'Leadership and management skills',
            'Organizational and administrative skills'
        ],
        'categories': ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
    }
}

# Career interest areas
CAREER_INTERESTS = {
    'realistic': {
        'title': 'Realistic',
        'description': 'Practical, hands-on, tool-oriented',
        'careers': ['Mechanic', 'Engineer', 'Farmer', 'Electrician', 'Carpenter']
    },
    'investigative': {
        'title': 'Investigative',
        'description': 'Analytical, intellectual, scientific',
        'careers': ['Scientist', 'Mathematician', 'Researcher', 'Doctor', 'Analyst']
    },
    'artistic': {
        'title': 'Artistic',
        'description': 'Creative, original, independent',
        'careers': ['Artist', 'Writer', 'Musician', 'Designer', 'Actor']
    },
    'social': {
        'title': 'Social',
        'description': 'Helping, teaching, healing',
        'careers': ['Teacher', 'Counselor', 'Nurse', 'Social Worker', 'Psychologist']
    },
    'enterprising': {
        'title': 'Enterprising',
        'description': 'Leading, persuading, managing',
        'careers': ['Entrepreneur', 'Lawyer', 'Manager', 'Salesperson', 'Politician']
    },
    'conventional': {
        'title': 'Conventional',
        'description': 'Organized, clerical, systematic',
        'careers': ['Accountant', 'Banker', 'Secretary', 'Data Entry Clerk', 'Librarian']
    }
}

def get_quiz(quiz_type):
    """Get quiz by type"""
    return QUIZZES.get(quiz_type)

def get_interest_questions():
    """Get all interest assessment questions"""
    return INTEREST_QUESTIONS

def get_career_interest(interest_type):
    """Get career interest details by type"""
    return CAREER_INTERESTS.get(interest_type, {})

def get_all_career_interests():
    """Get all career interest categories"""
    return CAREER_INTERESTS
