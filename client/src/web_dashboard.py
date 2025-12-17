from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import json
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global detector instance (to be set from main)
detector = None

def set_detector(detector_instance):
    global detector
    detector = detector_instance

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current detection status"""
    if detector is None:
        return jsonify({'error': 'Detector not initialized'}), 500
    
    return jsonify({
        'is_monitoring': detector.is_monitoring,
        'total_alerts': len(detector.alerts),
        'recent_alerts': list(detector.alerts)[-10:] if detector.alerts else [],
        'detection_scores': list(detector.detection_scores)[-50:] if detector.detection_scores else []
    })

@app.route('/api/scores')
def get_scores():
    """Get current suspicion scores"""
    if detector is None:
        return jsonify({'error': 'Detector not initialized'}), 500
    
    return jsonify({
        'process_score': detector.process_monitor.get_suspicion_score(),
        'audio_score': detector.audio_analyzer.get_suspicion_score(),
        'behavior_score': detector.behavioral_monitor.get_suspicion_score(),
        'overall_score': detector.detection_scores[-1] if detector.detection_scores else 0.0
    })

def background_updates():
    """Send real-time updates to clients"""
    while True:
        if detector and detector.is_monitoring:
            socketio.emit('update', {
                'process_score': detector.process_monitor.get_suspicion_score(),
                'audio_score': detector.audio_analyzer.get_suspicion_score(),
                'behavior_score': detector.behavioral_monitor.get_suspicion_score(),
                'overall_score': detector.detection_scores[-1] if detector.detection_scores else 0.0,
                'alert_count': len(detector.alerts)
            })
        time.sleep(2)

def run_dashboard(host='127.0.0.1', port=5000):
    """Run the web dashboard"""
    # Start background update thread
    thread = threading.Thread(target=background_updates, daemon=True)
    thread.start()
    
    print(f"🌐 Dashboard running at http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
