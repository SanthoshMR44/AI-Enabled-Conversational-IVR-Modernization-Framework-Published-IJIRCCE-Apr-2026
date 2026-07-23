import re
import spacy
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Load NLTK Vader
try:
    sia = SentimentIntensityAnalyzer()
except Exception:
    sia = None

# Entity extraction using Regex + spaCy
def extract_entities(text: str) -> dict:
    entities = {
        "names": [],
        "phones": [],
        "dates": [],
        "emails": [],
        "amounts": [],
        "locations": [],
        "account_numbers": [],
        "reference_numbers": []
    }
    
    # Regex rules
    email_matches = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone_matches = re.findall(r'\b\d{10}\b|\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', text)
    acct_matches = re.findall(r'\b\d{9,18}\b', text)
    ref_matches = re.findall(r'\b(?:TKT|REF|PNR)\d{4,8}\b|\b[A-Z]{3}\d{3,6}\b', text)
    
    entities["emails"] = list(set(email_matches))
    entities["phones"] = list(set(phone_matches))
    entities["account_numbers"] = list(set(acct_matches) - set(phone_matches))
    entities["reference_numbers"] = list(set(ref_matches))
    
    # spaCy NER
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.text not in entities["names"]:
                entities["names"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"] and ent.text not in entities["locations"]:
                entities["locations"].append(ent.text)
            elif ent.label_ == "DATE" and ent.text not in entities["dates"]:
                entities["dates"].append(ent.text)
            elif ent.label_ in ["MONEY", "CARDINAL"] and ent.text not in entities["amounts"]:
                if any(char.isdigit() for char in ent.text):
                    entities["amounts"].append(ent.text)
                    
    return entities

# Offline Sentiment Analysis using TextBlob & NLTK Vader
def analyze_sentiment(text: str) -> tuple:
    """
    Returns (label, score)
    label: Positive, Neutral, Negative
    score: float (-1.0 to 1.0)
    """
    blob_score = TextBlob(text).sentiment.polarity
    vader_score = 0.0
    if sia:
        vader_score = sia.polarity_scores(text)['compound']
    
    # Average score
    score = (blob_score + vader_score) / 2.0
    
    if score > 0.05:
        label = "Positive"
    elif score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return label, round(score, 2)
