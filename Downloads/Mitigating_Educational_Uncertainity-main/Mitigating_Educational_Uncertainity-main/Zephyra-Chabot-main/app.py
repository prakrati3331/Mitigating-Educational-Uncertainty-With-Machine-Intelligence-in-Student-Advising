from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import nltk
from zephyra_chatbot import ZephyraChatbot

# Download required NLTK data
print("Downloading required NLTK data...")
for package in ['punkt', 'wordnet', 'omw-1.4', 'stopwords']:
    try:
        nltk.download(package, quiet=True)
        print(f"Downloaded NLTK package: {package}")
    except Exception as e:
        print(f"Error downloading {package}: {e}")

# Initialize Flask app
app = Flask(__name__)

# Initialize the chatbot
try:
    chatbot = ZephyraChatbot()
    print("Zephyra Chatbot initialized successfully!")
except Exception as e:
    print(f"Error initializing Zephyra Chatbot: {e}")
    exit(1)

# Root route that redirects to the chat page
@app.route('/')
def home():
    return redirect(url_for('chat'))

# Main chat route
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form.get('msg')  # Get the user message from the form
        bot_response = chatbot.get_response(user_input)
        return jsonify({'response': bot_response})
    
    # On GET request, render page with a default bot greeting
    return render_template('index.html', bot_response="Hello! I'm Zephyra. How can I assist you today?")

if __name__ == '__main__':
    app.run(debug=True)
