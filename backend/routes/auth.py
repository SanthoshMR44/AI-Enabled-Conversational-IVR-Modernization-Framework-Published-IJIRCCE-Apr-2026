from flask import Blueprint, request, jsonify, session
from database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            "status": "success",
            "user": {
                "username": user['username'],
                "role": user['role'],
                "email": user['email']
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, 'user', ?)",
                     (username, password, email))
        conn.commit()
    except Exception:
        return jsonify({"error": "Username already exists"}), 409
    finally:
        conn.close()
        
    return jsonify({"status": "success", "message": "User registered successfully"})

@auth_bp.route('/api/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})

@auth_bp.route('/api/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = get_db()
    if request.method == 'POST':
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')
        if password:
            conn.execute("UPDATE users SET email = ?, password = ? WHERE username = ?", (email, password, session['username']))
        else:
            conn.execute("UPDATE users SET email = ? WHERE username = ?", (email, session['username']))
        conn.commit()
        
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    conn.close()
    
    return jsonify({
        "username": user['username'],
        "role": user['role'],
        "email": user['email']
    })
