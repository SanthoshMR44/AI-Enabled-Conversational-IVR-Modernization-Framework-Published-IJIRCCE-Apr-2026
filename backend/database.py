import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ivr_platform.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Intents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)
    
    # 3. Custom Responses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        intent_name TEXT NOT NULL,
        response_text TEXT NOT NULL,
        FOREIGN KEY(intent_name) REFERENCES intents(name) ON DELETE CASCADE
    )
    """)
    
    # 4. Flows Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ivr_flows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        flow_json TEXT NOT NULL,
        is_active INTEGER DEFAULT 0,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 5. Conversations Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_id TEXT UNIQUE NOT NULL,
        caller_number TEXT,
        start_time TEXT,
        end_time TEXT,
        duration INTEGER,
        transcript TEXT,
        sentiment TEXT,
        sentiment_score REAL,
        intent_detected TEXT,
        entities TEXT,
        resolution_status TEXT DEFAULT 'Resolved',
        flow_id INTEGER,
        FOREIGN KEY(flow_id) REFERENCES ivr_flows(id)
    )
    """)
    
    # 6. Knowledge Base Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        content TEXT NOT NULL,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Insert admin and basic user if not exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                       ("admin", "admin123", "admin", "admin@ivr.local"))
        cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                       ("agent", "agent123", "agent", "agent@ivr.local"))
        
    # Prepopulate default intents and responses
    cursor.execute("SELECT COUNT(*) FROM intents")
    if cursor.fetchone()[0] == 0:
        default_intents = [
            ("Greeting", "Welcome greeting"),
            ("Complaint", "Filing complaints"),
            ("Balance Inquiry", "Checking accounts/loyalty points balance"),
            ("Payment", "Bill payments & recharges"),
            ("Account Opening", "Requests for new account opening"),
            ("Loan", "Mortgage, gold and personal loans"),
            ("Insurance", "Travel, health and life insurance"),
            ("Card Block", "Urgent loss/blocking of cards"),
            ("Customer Support", "Agent assistance request"),
            ("Transfer Call", "Route calls to department"),
            ("Exit", "End the call"),
            ("Unknown Intent", "Fallback handling")
        ]
        cursor.executemany("INSERT INTO intents (name, description) VALUES (?, ?)", default_intents)
        
        default_responses = [
            ("Greeting", "Welcome to the IVR Modernization Platform. How can I help you today?"),
            ("Complaint", "I have registered your complaint. A support ticket has been created."),
            ("Balance Inquiry", "Your current balance is 14,200 points."),
            ("Payment", "To pay your bill, press 1 or type your card details."),
            ("Account Opening", "Please hold while we route you to new accounts department."),
            ("Loan", "We offer competitive interest rates from 6.5%. Transferring to loan officer."),
            ("Insurance", "Keep your family secure. Press 1 for health, press 2 for vehicle insurance."),
            ("Card Block", "Your card has been blocked successfully to prevent unauthorized transactions."),
            ("Customer Support", "Connecting to a live agent. Please stand by."),
            ("Transfer Call", "Transferring your call to the specialist desk."),
            ("Exit", "Thank you for calling. Have a great day!"),
            ("Unknown Intent", "I didn't quite catch that. Could you please repeat?")
        ]
        cursor.executemany("INSERT INTO responses (intent_name, response_text) VALUES (?, ?)", default_responses)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
