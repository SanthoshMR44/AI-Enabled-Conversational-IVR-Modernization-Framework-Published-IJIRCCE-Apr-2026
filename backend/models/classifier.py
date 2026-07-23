import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download stopwords offline safely
try:
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    STOPWORDS = set()

stemmer = PorterStemmer()

def preprocess_text(text: str) -> str:
    # Tokenize, lowercase, remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    tokens = text.split()
    # Filter stopwords & stem
    tokens = [stemmer.stem(t) for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
        self.intents = []
        self.patterns = []
        self.trained = False
        
    def train(self, intent_patterns: list):
        """
        intent_patterns: List of tuples (intent_name, pattern_text)
        """
        if not intent_patterns:
            return
        self.intents = [item[0] for item in intent_patterns]
        self.patterns = [item[1] for item in intent_patterns]
        
        self.X = self.vectorizer.fit_transform(self.patterns)
        self.trained = True
        
    def predict(self, text: str, threshold: float = 0.2) -> tuple:
        """
        Predicts intent. Returns (intent_name, confidence_score)
        """
        if not self.trained or not text:
            return "Unknown Intent", 0.0
            
        text_vec = self.vectorizer.transform([text])
        similarities = cosine_similarity(text_vec, self.X)[0]
        max_idx = np.argmax(similarities)
        score = similarities[max_idx]
        
        if score >= threshold:
            return self.intents[max_idx], round(float(score), 2)
        else:
            return "Unknown Intent", round(float(score), 2)
