from flask import Blueprint, request, jsonify
from database import get_db

flow_bp = Blueprint('flow', __name__)

@flow_bp.route('/api/flows', methods=['GET', 'POST'])
def flows():
    conn = get_db()
    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name', 'Custom IVR Flow')
        flow_json = data.get('flow_json', '{}')
        
        # Deactivate all others if this is active
        is_active = data.get('is_active', 0)
        if is_active == 1:
            conn.execute("UPDATE ivr_flows SET is_active = 0")
            
        conn.execute(
            "INSERT OR REPLACE INTO ivr_flows (name, flow_json, is_active, updated_at) VALUES (?, ?, ?, datetime('now'))",
            (name, flow_json, is_active)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Flow saved successfully"})
        
    rows = conn.execute("SELECT * FROM ivr_flows ORDER BY updated_at DESC").fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r['id'],
            "name": r['name'],
            "flow_json": r['flow_json'],
            "is_active": r['is_active'],
            "updated_at": r['updated_at']
        })
    return jsonify(result)

@flow_bp.route('/api/flows/active', methods=['GET'])
def active_flow():
    conn = get_db()
    row = conn.execute("SELECT * FROM ivr_flows WHERE is_active = 1").fetchone()
    conn.close()
    if row:
        return jsonify({
            "id": row['id'],
            "name": row['name'],
            "flow_json": row['flow_json']
        })
    return jsonify({"error": "No active flow found"}), 404

@flow_bp.route('/api/flows/<int:flow_id>/activate', methods=['POST'])
def activate_flow(flow_id):
    conn = get_db()
    conn.execute("UPDATE ivr_flows SET is_active = 0")
    conn.execute("UPDATE ivr_flows SET is_active = 1 WHERE id = ?", (flow_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Flow activated"})

@flow_bp.route('/api/flows/<int:flow_id>', methods=['DELETE'])
def delete_flow(flow_id):
    conn = get_db()
    conn.execute("DELETE FROM ivr_flows WHERE id = ?", (flow_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Flow deleted"})
