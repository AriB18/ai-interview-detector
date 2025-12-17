import threading
import time
import json
from datetime import datetime
from collections import deque
import numpy as np

from process_monitor import ProcessMonitor
from audio_analyzer import AudioAnalyzer
from behavioral_monitor import BehaviorMonitor
from ml_classifier import AIDetectionClassifier

class AIInterviewDetector:
    def __init__(self):
        self.process_monitor = ProcessMonitor()
        self.audio_analyzer = AudioAnalyzer()
        self.behavioral_monitor = BehaviorMonitor()
        self.classifier = AIDetectionClassifier()
        
        self.detection_scores = deque(maxlen=100)
        self.alerts = []
        self.is_monitoring = False
        
    def start_monitoring(self):
        """Start all monitoring threads"""
        print("🚀 Starting AI Interview Detector...")
        self.is_monitoring = True
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._monitor_processes, daemon=True),
            threading.Thread(target=self._monitor_audio, daemon=True),
            threading.Thread(target=self._monitor_behavior, daemon=True),
            threading.Thread(target=self._analyze_patterns, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        print("✅ All monitors active. Press Ctrl+C to stop.")
        
        try:
            while self.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        print("\n🛑 Stopping monitors...")
        self.is_monitoring = False
        self.generate_report()
    
    def _monitor_processes(self):
        """Monitor running processes for suspicious AI tools"""
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
                        'timestamp': datetime.now().isoformat(),
                        'type': 'PROCESS_DETECTION',
                        'severity': 'HIGH',
                        'details': f"Suspicious processes detected: {suspicious}"
                    }
                    self.alerts.append(alert)
                    print(f"⚠️  ALERT: {alert['details']}")
                
                time.sleep(5)
            except Exception as e:
                print(f"Process monitor error: {e}")
    
    def _monitor_audio(self):
        """Monitor audio patterns for AI-generated speech indicators"""
        while self.is_monitoring:
            try:
                audio_features = self.audio_analyzer.analyze_realtime_audio()
                
                if audio_features:
                    # Check for suspicious patterns
                    pause_score = audio_features.get('pause_pattern_score', 0)
                    fluency_score = audio_features.get('fluency_score', 0)
                    
                    # High pause score + high fluency = potential AI assistance
                    if pause_score > 0.7 and fluency_score > 0.8:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'AUDIO_ANOMALY',
                            'severity': 'MEDIUM',
                            'details': f"Suspicious speech pattern detected (pause: {pause_score:.2f}, fluency: {fluency_score:.2f})"
                        }
                        self.alerts.append(alert)
                        print(f"⚠️  ALERT: {alert['details']}")
                
                time.sleep(2)
            except Exception as e:
                print(f"Audio monitor error: {e}")
    
    def _monitor_behavior(self):
        """Monitor keyboard, mouse, and clipboard activity"""
        while self.is_monitoring:
            try:
                behavior_data = self.behavioral_monitor.get_activity_summary()
                
                # Check clipboard for AI-generated text patterns
                clipboard_score = behavior_data.get('clipboard_ai_score', 0)
                if clipboard_score > 0.7:
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'CLIPBOARD_DETECTION',
                        'severity': 'HIGH',
                        'details': f"AI-generated text detected in clipboard (confidence: {clipboard_score:.2f})"
                    }
                    self.alerts.append(alert)
                    print(f"⚠️  ALERT: {alert['details']}")
                
                # Check for rapid perfect typing (copy-paste indicator)
                if behavior_data.get('rapid_typing_detected', False):
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'TYPING_ANOMALY',
                        'severity': 'MEDIUM',
                        'details': "Unnaturally fast typing detected"
                    }
                    self.alerts.append(alert)
                    print(f"⚠️  ALERT: {alert['details']}")
                
                time.sleep(3)
            except Exception as e:
                print(f"Behavior monitor error: {e}")
    
    def _analyze_patterns(self):
        """Use ML to analyze combined patterns"""
        while self.is_monitoring:
            try:
                # Collect features from all monitors
                features = {
                    'process_score': self.process_monitor.get_suspicion_score(),
                    'audio_score': self.audio_analyzer.get_suspicion_score(),
                    'behavior_score': self.behavioral_monitor.get_suspicion_score(),
                    'timestamp': time.time()
                }
                
                # Get ML prediction
                ai_probability = self.classifier.predict(features)
                self.detection_scores.append(ai_probability)
                
                # Calculate rolling average
                if len(self.detection_scores) > 10:
                    avg_score = np.mean(list(self.detection_scores)[-10:])
                    
                    if avg_score > 0.75:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'AI_DETECTION',
                            'severity': 'CRITICAL',
                            'details': f"High probability of AI assistance (confidence: {avg_score:.2%})"
                        }
                        self.alerts.append(alert)
                        print(f"🚨 CRITICAL ALERT: {alert['details']}")
                
                time.sleep(5)
            except Exception as e:
                print(f"Pattern analyzer error: {e}")
    
    def generate_report(self):
        """Generate final detection report"""
        report = {
            'session_duration': 'N/A',
            'total_alerts': len(self.alerts),
            'alerts_by_severity': {
                'CRITICAL': len([a for a in self.alerts if a['severity'] == 'CRITICAL']),
                'HIGH': len([a for a in self.alerts if a['severity'] == 'HIGH']),
                'MEDIUM': len([a for a in self.alerts if a['severity'] == 'MEDIUM'])
            },
            'average_detection_score': np.mean(list(self.detection_scores)) if self.detection_scores else 0,
            'alerts': self.alerts
        }
        
        # Save report
        filename = f"detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"logs/{filename}", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Detection Report:")
        print(f"   Total Alerts: {report['total_alerts']}")
        print(f"   Critical: {report['alerts_by_severity']['CRITICAL']}")
        print(f"   High: {report['alerts_by_severity']['HIGH']}")
        print(f"   Medium: {report['alerts_by_severity']['MEDIUM']}")
        print(f"   Average Detection Score: {report['average_detection_score']:.2%}")
        print(f"   Report saved to: logs/{filename}")

if __name__ == "__main__":
    detector = AIInterviewDetector()
    detector.start_monitoring()