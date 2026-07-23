from flask import Blueprint, request, jsonify
from database import get_db

intent_bp = Blueprint('intent', __name__)

@intent_bp.route('/api/intents', methods=['GET', 'POST'])
def manage_intents():
    conn = get_db()
    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name')
        description = data.get('description', '')
        response_text = data.get('response_text', '')
        
        if not name:
            return jsonify({"error": "Intent name is required"}), 400
            
        try:
            conn.execute("INSERT INTO intents (name, description) VALUES (?, ?)", (name, description))
            if response_text:
                conn.execute("INSERT INTO responses (intent_name, response_text) VALUES (?, ?)", (name, response_text))
            conn.commit()
        except Exception as e:
            return jsonify({"error": f"Intent already exists or database error: {str(e)}"}), 409
        finally:
            conn.close()
        return jsonify({"status": "success", "message": "Intent created successfully"})
        
    intents = conn.execute("""
        SELECT i.id, i.name, i.description, r.response_text 
        FROM intents i 
        LEFT JOIN responses r ON i.name = r.intent_name
    """).fetchall()
    conn.close()
    
    return jsonify([dict(ix) for ix in intents])

@intent_bp.route('/api/intents/<int:intent_id>', methods=['PUT', 'DELETE'])
def update_delete_intent(intent_id):
    conn = get_db()
    intent = conn.execute("SELECT * FROM intents WHERE id = ?", (intent_id,)).fetchone()
    if not intent:
        conn.close()
        return jsonify({"error": "Intent not found"}), 404
        
    if request.method == 'DELETE':
        conn.execute("DELETE FROM responses WHERE intent_name = ?", (intent['name'],))
        conn.execute("DELETE FROM intents WHERE id = ?", (intent_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Intent deleted"})
        
    # PUT update
    data = request.json or {}
    description = data.get('description', intent['description'])
    response_text = data.get('response_text')
    
    conn.execute("UPDATE intents SET description = ? WHERE id = ?", (description, intent_id))
    if response_text:
        conn.execute("INSERT OR REPLACE INTO responses (intent_name, response_text) VALUES (?, ?)", 
                     (intent['name'], response_text))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Intent updated"})
