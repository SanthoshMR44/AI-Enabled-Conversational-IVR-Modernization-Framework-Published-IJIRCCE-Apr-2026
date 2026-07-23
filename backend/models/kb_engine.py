import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
from docx import Document
from .classifier import preprocess_text

class KBEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
        self.documents = []  # List of dicts: {"filename": ..., "content": ...}
        self.trained = False
        self.X = None
        
    def add_document(self, filename: str, content: str):
        # Paragraph or line segmentation
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 10]
        if not paragraphs:
            paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 10]
            
        for i, para in enumerate(paragraphs):
            self.documents.append({
                "filename": filename,
                "content": para,
                "index": i
            })
            
    def rebuild_index(self):
        if not self.documents:
            self.trained = False
            return
        contents = [doc["content"] for doc in self.documents]
        self.X = self.vectorizer.fit_transform(contents)
        self.trained = True
        
    def search(self, query: str, top_n: int = 3) -> list:
        if not self.trained or not query:
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.X)[0]
        
        # Sort indices
        sorted_indices = similarities.argsort()[::-1]
        results = []
        
        for idx in sorted_indices[:top_n]:
            score = similarities[idx]
            if score > 0.05:  # Relevance threshold
                results.append({
                    "filename": self.documents[idx]["filename"],
                    "content": self.documents[idx]["content"],
                    "score": round(float(score), 2)
                })
        return results

def extract_text_from_file(filepath: str) -> str:
    _, ext = os.path.splitext(filepath.lower())
    text = ""
    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif ext == ".pdf":
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif ext in [".docx", ".doc"]:
        doc = Document(filepath)
        for p in doc.paragraphs:
            text += p.text + "\n"
    return text
