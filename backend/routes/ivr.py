import json
import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import get_db
from models.nlp_engine import extract_entities, analyze_sentiment
from models.classifier import IntentClassifier

ivr_bp = Blueprint('ivr', __name__)

# In-memory session tracking for live simulator calls
active_sessions = {}
classifier = IntentClassifier()
CLASSIFIER_TRAINED = False

def get_classifier():
    global CLASSIFIER_TRAINED
    if not CLASSIFIER_TRAINED:
        conn = get_db()
        rows = conn.execute("""
            SELECT i.name, r.response_text 
            FROM intents i 
            LEFT JOIN responses r ON i.name = r.intent_name
        """).fetchall()
        conn.close()
        patterns = [(r['name'], r['response_text'] or r['name']) for r in rows]
        # Include some default variants
        patterns.append(("Greeting", "hello there"))
        patterns.append(("Greeting", "hi support"))
        patterns.append(("Exit", "bye goodbye stop end exit"))
        patterns.append(("Balance Inquiry", "how many points check balance points details"))
        patterns.append(("Card Block", "lost card block card credit card lost"))
        patterns.append(("Customer Support", "talk to human talk to agent support"))
        classifier.train(patterns)
        CLASSIFIER_TRAINED = True
    return classifier

@ivr_bp.route('/api/ivr/start', methods=['POST'])
def start_call():
    data = request.json or {}
    caller_number = data.get('caller_number', 'SIMULATED_USER')
    call_id = f"CALL_{random.randint(100000, 999999)}"
    
    # Check if a custom flow is active
    conn = get_db()
    active_flow = conn.execute("SELECT * FROM ivr_flows WHERE is_active = 1").fetchone()
    conn.close()
    
    flow_json = None
    initial_prompt = "Welcome to the Modernized IVR Platform. How can I help you today?"
    current_node = "root"
    
    if active_flow:
        try:
            flow_data = json.loads(active_flow['flow_json'])
            # Extract root node or standard entry
            nodes = flow_data.get('nodes', [])
            root_node = next((n for n in nodes if n.get('type') == 'start'), None)
            if root_node:
                initial_prompt = root_node.get('prompt', "Flow Started. How can I help you?")
                current_node = root_node.get('id')
                flow_json = active_flow['flow_json']
        except Exception:
            pass

    active_sessions[call_id] = {
        "call_id": call_id,
        "caller_number": caller_number,
        "start_time": datetime.now().isoformat(),
        "transcript": [],
        "entities": [],
        "intents": [],
        "sentiments": [],
        "flow_json": flow_json,
        "current_node": current_node,
        "status": "connected"
    }

    return jsonify({
        "call_id": call_id,
        "prompt": initial_prompt,
        "status": "connected"
    })

@ivr_bp.route('/api/ivr/dtmf', methods=['POST'])
def handle_input():
    data = request.json or {}
    call_id = data.get('call_id')
    user_input = data.get('digit', '').strip()  # can be DTMF digit or text statement
    
    if not call_id or call_id not in active_sessions:
        return jsonify({"error": "Active call session not found"}), 404
        
    session = active_sessions[call_id]
    session["transcript"].append(f"User: {user_input}")
    
    # 1. NLP Sentiment & Entity analysis
    sentiment_label, sentiment_score = analyze_sentiment(user_input)
    entities = extract_entities(user_input)
    intent_detected, confidence = get_classifier().predict(user_input)
    
    session["sentiments"].append(sentiment_score)
    session["intents"].append(intent_detected)
    
    # Save entities if found
    for key, val in entities.items():
        if val:
            session["entities"].extend(val)

    # 2. Flow Traversal or Default QA Logic
    conn = get_db()
    
    # Custom flow evaluation
    if session["flow_json"]:
        try:
            flow_data = json.loads(session["flow_json"])
            nodes = flow_data.get('nodes', [])
            connections = flow_data.get('connections', [])
            
            curr_node = next((n for n in nodes if n.get('id') == session["current_node"]), None)
            next_node = None
            
            # Simple option or match routing
            if curr_node:
                # Find outbound connections
                outbound = [c for c in connections if c.get('from') == session["current_node"]]
                
                # Check for standard matches
                for conn_line in outbound:
                    condition = conn_line.get('condition', '')
                    if condition.lower() == user_input.lower() or condition.lower() == intent_detected.lower():
                        next_node = next((n for n in nodes if n.get('id') == conn_line.get('to')), None)
                        break
                
                # Fallback outbound if no match
                if not next_node and outbound:
                    next_node = next((n for n in nodes if n.get('id') == outbound[0].get('to')), None)
            
            if next_node:
                session["current_node"] = next_node.get('id')
                prompt = next_node.get('prompt', "Please continue...")
                node_type = next_node.get('type')
                
                if node_type == 'end':
                    return end_call(call_id, prompt, intent_detected, sentiment_label, sentiment_score)
                elif node_type == 'transfer':
                    return end_call(call_id, f"Transferring call: {prompt}", "Transfer Call", sentiment_label, sentiment_score)
                
                return jsonify({
                    "prompt": prompt,
                    "intent": intent_detected,
                    "entities": entities,
                    "sentiment": sentiment_label
                })
        except Exception:
            pass

    # Default fallback NLP Response lookup
    resp_row = conn.execute("SELECT response_text FROM responses WHERE intent_name = ?", (intent_detected,)).fetchone()
    conn.close()
    
    response_prompt = resp_row['response_text'] if resp_row else "I'm sorry, I couldn't process your request. Connecting to an agent."
    
    # End conditions
    if intent_detected in ["Exit", "Customer Support", "Transfer Call"] or "bye" in user_input.lower():
        return end_call(call_id, response_prompt, intent_detected, sentiment_label, sentiment_score)
        
    return jsonify({
        "prompt": response_prompt,
        "intent": intent_detected,
        "entities": entities,
        "sentiment": sentiment_label
    })

def end_call(call_id, message, intent, sentiment, sentiment_score):
    session = active_sessions.pop(call_id)
    start_dt = datetime.fromisoformat(session["start_time"])
    end_dt = datetime.now()
    duration = (end_dt - start_dt).seconds
    
    transcript_str = "\n".join(session["transcript"])
    entities_str = ",".join(session["entities"])
    
    # Save into SQLite
    conn = get_db()
    conn.execute("""
        INSERT INTO conversations 
        (call_id, caller_number, start_time, end_time, duration, transcript, sentiment, sentiment_score, intent_detected, entities)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (call_id, session["caller_number"], session["start_time"], end_dt.isoformat(), duration, 
          transcript_str, sentiment, sentiment_score, intent, entities_str))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "ended",
        "message": message,
        "duration": f"{duration} sec",
        "intent": intent,
        "sentiment": sentiment
    })
