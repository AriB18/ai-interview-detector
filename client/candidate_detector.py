"""
Candidate Detection Client
Runs on candidate's computer and reports to recruiter's server
"""

import sys
import os
import requests
import time
import threading
import json

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(application_path, 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


from process_monitor import ProcessMonitor
# from audio_analyzer import AudioAnalyzer  # Disabled - PyAudio dependency
try:
    from audio_analyzer import AudioAnalyzer
except:
    from audio_analyzer_stub import AudioAnalyzer
from behavioral_monitor import BehaviorMonitor
from ml_classifier import AIDetectionClassifier

class CandidateDetectorClient:
    def __init__(self, server_url, session_id, token):
        self.server_url = server_url
        self.session_id = session_id
        self.token = token
        
        # Initialize detection components
        self.process_monitor = ProcessMonitor()
        self.audio_analyzer = AudioAnalyzer()  # Will use stub if pyaudio unavailable
        self.behavioral_monitor = BehaviorMonitor()
        self.classifier = AIDetectionClassifier()
        
        self.is_monitoring = False
        self.detection_scores = []
        self.alerts = []
        
    def start_monitoring(self):
        """Start all monitoring and reporting"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🔍 CANDIDATE DETECTION CLIENT                           ║
║   Interview Monitoring Active                             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

✅ Connected to interview server
📊 Monitoring your system for AI tools
🔒 Data is encrypted and sent to recruiter

⚠️  DO NOT close this window during the interview!
        """)
        
        self.is_monitoring = True
        
        # Start behavioral monitoring
        self.behavioral_monitor.start_monitoring()
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._monitor_processes, daemon=True),
            threading.Thread(target=self._monitor_audio, daemon=True),
            threading.Thread(target=self._report_to_server, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        print("✅ All monitors active")
        print("📡 Sending data to recruiter every 5 seconds...\n")
        
        try:
            while self.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        print("\n🛑 Stopping monitoring...")
        self.is_monitoring = False
        self.behavioral_monitor.stop_monitoring()
        print("✅ Monitoring stopped. You may close this window.")
    
    def _monitor_processes(self):
        """Monitor running processes"""
        suspicious_keywords = [
            'chatgpt', 'claude', 'copilot', 'cluely', 'yoodli',
            'gemini', 'bard', 'perplexity', 'interviewcoder'
        ]
        
        while self.is_monitoring:
            try:
                processes = self.process_monitor.get_running_processes()
                suspicious = self.process_monitor.detect_suspicious_processes(
                    processes, suspicious_keywords
                )
                
                if suspicious:
                    alert = {
                        'timestamp': time.time(),
                        'type': 'PROCESS_DETECTION',
                        'severity': 'HIGH',
                        'details': f"Detected: {', '.join(set(suspicious[:3]))}"
                    }
                    self.alerts.append(alert)
                    print(f"⚠️  {alert['details']}")
                
                time.sleep(5)
            except Exception as e:
                print(f"Process monitor error: {e}")
    
    def _monitor_audio(self):
        """Monitor audio patterns"""
        while self.is_monitoring:
            try:
                if self.audio_analyzer is None:
                    time.sleep(2)
                    continue
                audio_features = self.audio_analyzer.analyze_realtime_audio()
                
                if audio_features:
                    pause_score = audio_features.get('pause_pattern_score', 0)
                    if pause_score > 0.7:
                        alert = {
                            'timestamp': time.time(),
                            'type': 'AUDIO_ANOMALY',
                            'severity': 'MEDIUM',
                            'details': f"Suspicious speech pattern"
                        }
                        self.alerts.append(alert)
                
                time.sleep(2)
            except Exception as e:
                print(f"Audio monitor error: {e}")
    
    def _report_to_server(self):
        """Send detection data to recruiter's server"""
        while self.is_monitoring:
            try:
                # Collect current detection metrics
                features = {
                    'process_score': self.process_monitor.get_suspicion_score(),
                    'audio_score': self.audio_analyzer.get_suspicion_score() if self.audio_analyzer else 0.0,
                    'behavior_score': self.behavioral_monitor.get_suspicion_score(),
                    'timestamp': time.time()
                }
                
                # Get ML prediction
                detection_score = self.classifier.predict(features)
                self.detection_scores.append(detection_score)
                
                # Get suspicious processes
                suspicious_keywords = ['chatgpt', 'claude', 'copilot', 'cluely']
                processes = self.process_monitor.get_running_processes()
                suspicious_procs = []
                for proc in processes:
                    for keyword in suspicious_keywords:
                        if keyword in proc['name']:
                            suspicious_procs.append(proc['name'])
                            break
                
                # Prepare report
                report = {
                    'session_id': self.session_id,
                    'token': self.token,
                    'detection_score': detection_score,
                    'process_score': features['process_score'],
                    'audio_score': features['audio_score'],
                    'behavior_score': features['behavior_score'],
                    'alerts': self.alerts[-10:],  # Last 10 alerts
                    'suspicious_processes': list(set(suspicious_procs)),
                    'timestamp': time.time()
                }
                
                # Send to server
                response = requests.post(
                    f"{self.server_url}/api/report",
                    json=report,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"📡 Report sent | Score: {detection_score:.2%} | " + 
                          f"Process: {features['process_score']:.2f} | " +
                          f"Audio: {features['audio_score']:.2f} | " +
                          f"Behavior: {features['behavior_score']:.2f}")
                else:
                    print(f"❌ Failed to send report: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
            except Exception as e:
                print(f"❌ Error sending report: {e}")
            
            time.sleep(5)  # Report every 5 seconds

def main():
    """Main entry point for candidate client"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🎯 AI INTERVIEW DETECTION - CANDIDATE CLIENT            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Get connection details
    if len(sys.argv) >= 4:
        server_url = sys.argv[1]
        session_id = sys.argv[2]
        token = sys.argv[3]
    else:
        print("Enter your interview session details:")
        server_url = input("Server URL (e.g., http://recruiter-ip:5000): ").strip()
        session_id = input("Session ID: ").strip()
        token = input("Token: ").strip()
    
    if not all([server_url, session_id, token]):
        print("❌ Error: All fields are required!")
        return
    
    print(f"\n🔗 Connecting to: {server_url}")
    print(f"📋 Session ID: {session_id}")
    
    # Create and start client
    client = CandidateDetectorClient(server_url, session_id, token)
    
    try:
        client.start_monitoring()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

