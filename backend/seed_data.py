import sqlite3
import random
from datetime import datetime, timedelta
from database import get_db, DB_PATH

def seed_analytics():
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if we already have conversation logs
    cursor.execute("SELECT COUNT(*) FROM conversations")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
        
    print("Seeding default conversations history...")
    
    sample_conversations = [
        ("Greeting", "hello", "Positive", 0.6, "None"),
        ("Balance Inquiry", "what is my balance please", "Neutral", 0.0, "14200"),
        ("Complaint", "my bag tag lost tag number 43821", "Negative", -0.4, "43821"),
        ("Card Block", "i lost my credit card block it", "Negative", -0.7, "None"),
        ("Loan", "what gold loan offers do you have", "Positive", 0.2, "None"),
        ("Payment", "pay my premium of 5000", "Neutral", 0.0, "5000"),
        ("Insurance", "i want travel insurance", "Positive", 0.3, "None"),
        ("Customer Support", "transfer to agent support", "Neutral", 0.0, "None")
    ]
    
    for i in range(25):
        intent, text, sentiment, score, entities = random.choice(sample_conversations)
        call_id = f"CALL_{random.randint(100000, 999999)}"
        caller = f"+1555019{random.randint(10,99)}"
        duration = random.randint(10, 90)
        
        # Simulated timestamp within last 7 days
        start = datetime.now() - timedelta(days=random.randint(0,7), minutes=random.randint(10,120))
        end = start + timedelta(seconds=duration)
        
        cursor.execute("""
            INSERT INTO conversations 
            (call_id, caller_number, start_time, end_time, duration, transcript, sentiment, sentiment_score, intent_detected, entities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (call_id, caller, start.isoformat(), end.isoformat(), duration, 
              f"User: {text}\nBot: Handled", sentiment, score, intent, entities))
              
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_analytics()
    print("Database seeded with sample statistics.")
