"""
Detection Server - Recruiter Side
Receives detection data from all candidates in real-time
"""

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import secrets
import os

# Create Flask app
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = secrets.token_hex(16)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

# Store active candidate sessions
active_sessions = {}
session_tokens = {}  # candidate_id -> token mapping

@app.route('/')
def index():
    """Recruiter dashboard"""
    return render_template('recruiter_dashboard.html')

@app.route('/api/create-session', methods=['POST'])
def create_session():
    """Create a new interview session"""
    data = request.json
    candidate_name = data.get('candidate_name', 'Unknown')
    
    # Generate unique session
    session_id = secrets.token_urlsafe(8)
    session_token = secrets.token_hex(32)
    
    session_tokens[session_id] = {
        'token': session_token,
        'candidate_name': candidate_name,
        'created_at': datetime.now().isoformat(),
        'status': 'waiting'
    }
    
    return jsonify({
        'session_id': session_id,
        'token': session_token,
        'candidate_name': candidate_name,
        'download_url': f'/download/client/{session_id}'
    })

@app.route('/api/report', methods=['POST'])
def receive_detection_report():
    """Receive detection data from candidate"""
    data = request.json
    session_id = data.get('session_id')
    token = data.get('token')
    
    # Verify token
    if session_id not in session_tokens:
        return jsonify({'error': 'Invalid session'}), 401
    
    if session_tokens[session_id]['token'] != token:
        return jsonify({'error': 'Invalid token'}), 401
    
    # Update session status
    session_tokens[session_id]['status'] = 'active'
    
    # Store detection data
    active_sessions[session_id] = {
        'candidate_name': session_tokens[session_id]['candidate_name'],
        'last_update': datetime.now().isoformat(),
        'detection_score': data.get('detection_score', 0),
        'alerts': data.get('alerts', []),
        'process_score': data.get('process_score', 0),
        'audio_score': data.get('audio_score', 0),
        'behavior_score': data.get('behavior_score', 0),
        'suspicious_processes': data.get('suspicious_processes', []),
        'status': 'active'
    }
    
    # Broadcast to recruiter dashboard
    socketio.emit('candidate_update', {
        'session_id': session_id,
        'data': active_sessions[session_id]
    })
    
    # Send alert if high risk
    if data.get('detection_score', 0) > 0.75:
        socketio.emit('high_risk_alert', {
            'session_id': session_id,
            'candidate_name': session_tokens[session_id]['candidate_name'],
            'score': data.get('detection_score', 0)
        })
    
    return jsonify({'status': 'success'})

@app.route('/api/sessions')
def get_all_sessions():
    """Get all active candidate sessions"""
    # Clean up old sessions (inactive for > 5 minutes)
    current_time = datetime.now()
    for session_id, data in list(active_sessions.items()):
        last_update = datetime.fromisoformat(data['last_update'])
        if current_time - last_update > timedelta(minutes=5):
            data['status'] = 'disconnected'
    
    return jsonify({
        'active_sessions': active_sessions,
        'total_sessions': len(active_sessions)
    })

@app.route('/api/session/<session_id>')
def get_session_details(session_id):
    """Get detailed info for a specific session"""
    if session_id in active_sessions:
        return jsonify(active_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/session/<session_id>/history')
def get_session_history(session_id):
    """Get detection history for a session"""
    # TODO: Store history in database
    return jsonify({'history': []})

@app.route('/api/end-session/<session_id>', methods=['POST'])
def end_session(session_id):
    """End an interview session"""
    if session_id in active_sessions:
        active_sessions[session_id]['status'] = 'ended'
        
        # Generate final report
        report = {
            'session_id': session_id,
            'candidate_name': active_sessions[session_id]['candidate_name'],
            'final_score': active_sessions[session_id]['detection_score'],
            'total_alerts': len(active_sessions[session_id]['alerts']),
            'ended_at': datetime.now().isoformat()
        }
        
        socketio.emit('session_ended', report)
        
        return jsonify(report)
    
    return jsonify({'error': 'Session not found'}), 404

@socketio.on('connect')
def handle_connect():
    """Handle recruiter dashboard connection"""
    print('✅ Recruiter dashboard connected')
    emit('connected', {'status': 'Connected to detection server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle recruiter dashboard disconnection"""
    print('❌ Recruiter dashboard disconnected')

def run_server(host='0.0.0.0', port=5000):
    """Run the detection server"""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🎯 AI INTERVIEW DETECTION SERVER                        ║
║   Recruiter Dashboard Running                             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

🌐 Recruiter Dashboard: http://localhost:{port}
📡 Server listening for candidate connections...

Next Steps:
1. Open the dashboard in your browser
2. Create a new interview session
3. Send the client link to your candidate
4. Monitor their AI usage in real-time!
    """)
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_server()

