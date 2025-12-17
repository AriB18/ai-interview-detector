#!/usr/bin/env python3
"""
AI Interview Detector - Main Entry Point
Run this file to start the detection system with web dashboard
"""

import sys
import os
import threading
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import from src
from src.main_detector import AIInterviewDetector
from src.ml_classifier import AIDetectionClassifier
from src.web_dashboard import run_dashboard, set_detector

def setup_directories():
    """Create necessary directories"""
    directories = ['logs', 'models', 'config', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created")

def initialize_ml_model():
    """Initialize ML model with synthetic training data"""
    print("🤖 Initializing ML model...")
    classifier = AIDetectionClassifier()
    
    if not classifier.is_trained:
        print("📚 No pre-trained model found. Generating training data...")
        classifier.initialize_model()
    
    return classifier

def main():
    parser = argparse.ArgumentParser(description='AI Interview Detector')
    parser.add_argument('--no-dashboard', action='store_true', 
                       help='Run without web dashboard')
    parser.add_argument('--train-model', action='store_true',
                       help='Train a new ML model')
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🔍 AI INTERVIEW DETECTOR v1.0                      ║
║        Multi-Modal AI Cheating Detection System          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Setup
    setup_directories()
    
    # Initialize ML model
    if args.train_model:
        classifier = AIDetectionClassifier()
        classifier.initialize_model()
        print("✅ Model training complete!")
        return
    
    # Create detector instance
    detector = AIInterviewDetector()
    
    if not args.no_dashboard:
        # Set detector for dashboard
        set_detector(detector)
        
        # Start dashboard in separate thread
        dashboard_thread = threading.Thread(
            target=run_dashboard,
            daemon=True
        )
        dashboard_thread.start()
        
        print("\n🌐 Web Dashboard: http://127.0.0.1:5000")
        print("📊 Open the dashboard in your browser to view real-time detection\n")
    
    # Start detection
    try:
        detector.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        detector.stop_monitoring()

if __name__ == "__main__":
    main()