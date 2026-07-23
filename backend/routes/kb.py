import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import get_db
from models.kb_engine import KBEngine, extract_text_from_file

kb_bp = Blueprint('kb', __name__)
kb_engine = KBEngine()
INDEX_BUILT = False

def get_kb_engine():
    global INDEX_BUILT
    if not INDEX_BUILT:
        conn = get_db()
        rows = conn.execute("SELECT filename, content FROM knowledge_base").fetchall()
        conn.close()
        for r in rows:
            kb_engine.add_document(r['filename'], r['content'])
        kb_engine.rebuild_index()
        INDEX_BUILT = True
    return kb_engine

@kb_bp.route('/api/kb', methods=['GET', 'POST'])
def manage_kb():
    global INDEX_BUILT
    conn = get_db()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
            
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        try:
            content = extract_text_from_file(filepath)
            if len(content.strip()) < 5:
                return jsonify({"error": "Document appears empty or unreadable"}), 400
                
            conn.execute("INSERT INTO knowledge_base (filename, content) VALUES (?, ?)", (filename, content))
            conn.commit()
            
            # Update index
            engine = get_kb_engine()
            engine.add_document(filename, content)
            engine.rebuild_index()
            INDEX_BUILT = True
            
        except Exception as e:
            return jsonify({"error": f"Failed to extract document text: {str(e)}"}), 500
        finally:
            conn.close()
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass
        return jsonify({"status": "success", "message": "Document uploaded and indexed successfully"})
        
    rows = conn.execute("SELECT id, filename, uploaded_at FROM knowledge_base ORDER BY uploaded_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@kb_bp.route('/api/kb/<int:doc_id>', methods=['DELETE'])
def delete_doc(doc_id):
    global INDEX_BUILT
    conn = get_db()
    conn.execute("DELETE FROM knowledge_base WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    # Reload engine
    kb_engine.documents = []
    INDEX_BUILT = False
    get_kb_engine()
    
    return jsonify({"status": "success", "message": "Document deleted"})

@kb_bp.route('/api/kb/search', methods=['POST'])
def search_kb():
    data = request.json or {}
    query = data.get('query')
    if not query:
        return jsonify([])
    engine = get_kb_engine()
    results = engine.search(query, top_n=3)
    return jsonify(results)
