import os
import sqlite3
from flask import Blueprint, request, jsonify, send_file
from database import DB_PATH

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/users', methods=['GET', 'POST'])
def manage_users():
    from database import get_db
    conn = get_db()
    if request.method == 'POST':
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({"error": "Missing fields"}), 400
            
        try:
            conn.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                         (username, password, role, email))
            conn.commit()
        except Exception:
            return jsonify({"error": "User already exists"}), 409
        finally:
            conn.close()
        return jsonify({"status": "success", "message": "User created"})
        
    users = conn.execute("SELECT id, username, role, email, created_at FROM users").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    from database import get_db
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "User deleted"})

@admin_bp.route('/api/admin/backup', methods=['POST'])
def backup_db():
    backup_file = DB_PATH + ".bak"
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_file)
        return jsonify({"status": "success", "message": "Database backup completed successfully."})
    except Exception as e:
        return jsonify({"error": f"Backup failed: {str(e)}"}), 500

@admin_bp.route('/api/admin/restore', methods=['POST'])
def restore_db():
    backup_file = DB_PATH + ".bak"
    if not os.path.exists(backup_file):
        return jsonify({"error": "No backup file found"}), 400
    try:
        import shutil
        shutil.copy2(backup_file, DB_PATH)
        return jsonify({"status": "success", "message": "Database successfully restored from backup."})
    except Exception as e:
        return jsonify({"error": f"Restore failed: {str(e)}"}), 500
