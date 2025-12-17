# AI Interview Detector Configuration

# Detection Thresholds
DETECTION_THRESHOLDS = {
    'process': 0.6,      # Threshold for process detection alerts
    'audio': 0.7,        # Threshold for audio pattern alerts
    'behavior': 0.65,    # Threshold for behavioral alerts
    'overall': 0.75      # Threshold for overall AI detection
}

# Suspicious Process Keywords
SUSPICIOUS_KEYWORDS = [
    'chatgpt', 'claude', 'copilot', 'cluely', 'yoodli',
    'gemini', 'bard', 'perplexity', 'interviewcoder',
    'openai', 'anthropic', 'gpt', 'ai-assistant'
]

# Audio Analysis Settings
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'chunk_size': 1024,
    'pause_threshold_seconds': 2.0,
    'fluency_threshold': 0.8
}

# Behavioral Monitoring
BEHAVIOR_CONFIG = {
    'keystroke_buffer_size': 1000,
    'mouse_event_buffer_size': 500,
    'clipboard_history_size': 50,
    'rapid_typing_threshold_ms': 50  # milliseconds between keystrokes
}

# ML Model Settings
ML_CONFIG = {
    'model_path': 'models/ai_detector_model.pkl',
    'scaler_path': 'models/scaler.pkl',
    'feature_weights': {
        'process': 0.4,
        'audio': 0.35,
        'behavior': 0.25
    }
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'host': '127.0.0.1',
    'port': 5000,
    'update_interval_seconds': 2
}

# Logging Settings
LOGGING_CONFIG = {
    'log_dir': 'logs',
    'save_reports': True,
    'verbose': True
}

