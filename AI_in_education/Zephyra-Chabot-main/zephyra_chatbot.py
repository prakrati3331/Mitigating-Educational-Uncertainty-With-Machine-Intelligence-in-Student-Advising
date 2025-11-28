import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import os

class ZephyraChatbot:
    def __init__(self, intents_path='intents.json', words_path='words.pkl', 
                 classes_path='classes.pkl', model_path='chatbot_model.h5'):
        """
        Initialize the Zephyra Chatbot with the trained model and data.
        
        Args:
            intents_path: Path to the intents JSON file
            words_path: Path to the words pickle file
            classes_path: Path to the classes pickle file
            model_path: Path to the trained Keras model
        """
        # Initialize lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Load intents and pre-trained model
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Load files using the correct paths
            with open(os.path.join(self.BASE_DIR, intents_path), 'r', encoding='utf-8') as f:
                self.intents = json.load(f)
                
            with open(os.path.join(self.BASE_DIR, words_path), 'rb') as f:
                self.words = pickle.load(f)
                
            with open(os.path.join(self.BASE_DIR, classes_path), 'rb') as f:
                self.classes = pickle.load(f)
                
            self.model = load_model(os.path.join(self.BASE_DIR, model_path))
            
        except Exception as e:
            raise Exception(f"Error initializing Zephyra Chatbot: {str(e)}")
    
    def clean_up_sentence(self, sentence):
        """Tokenize and lemmatize the input sentence."""
        try:
            if not isinstance(sentence, str):
                return []
                
            # Convert to string and lowercase
            sentence = str(sentence).lower().strip()
            if not sentence:
                return []
                
            # Tokenize and lemmatize
            sentence_words = nltk.word_tokenize(sentence)
            sentence_words = [self.lemmatizer.lemmatize(word) for word in sentence_words]
            return sentence_words
            
        except Exception as e:
            print(f"Error in clean_up_sentence: {e}")
            return []
    
    def bag_of_words(self, sentence):
        """Convert a sentence into a bag of words array."""
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        for w in sentence_words:
            for i, word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)
    
    def predict_class(self, sentence):
        """Predict the intent of a given sentence."""
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]

        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return [{'intent': self.classes[r[0]], 'probability': str(r[1])} for r in results]
    
    def get_response(self, message):
        """Get a response for the given message."""
        predicted_intents = self.predict_class(message)
        
        if not predicted_intents:
            return "I'm not sure how to respond to that. Could you try rephrasing?"

        tag = predicted_intents[0]['intent']
        for intent in self.intents['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])

        return "I'm not sure how to respond to that. Could you try rephrasing?"
