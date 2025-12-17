from pynput import keyboard, mouse
try:
    import pyperclip
except Exception:
    pyperclip = None
import time
import re
from collections import deque
import threading

class BehaviorMonitor:
    def __init__(self):
        self.keystroke_times = deque(maxlen=1000)
        self.mouse_events = deque(maxlen=500)
        self.clipboard_history = deque(maxlen=50)
        self.suspicion_score = 0.0
        
        self.is_monitoring = False
        self.last_clipboard = ""
        
        # Pattern detectors
        self.ai_patterns = [
            r'\b(as an ai|i apologize|i cannot|i\'m sorry, but)\b',
            r'\b(certainly|however|furthermore|additionally)\b.*\b(certainly|however|furthermore)\b',
            r'^\d+\.\s+[A-Z].*\n\d+\.\s+[A-Z]',  # Numbered lists
            r'\*\*[^*]+\*\*',  # Markdown bold
        ]
    
    def start_monitoring(self):
        """Start monitoring keyboard, mouse, and clipboard"""
        self.is_monitoring = True
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press
        )
        self.keyboard_listener.start()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move
        )
        self.mouse_listener.start()
        
        # Start clipboard monitor
        thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        self.is_monitoring = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
    
    def _on_key_press(self, key):
        """Capture keyboard events"""
        try:
            current_time = time.time()
            self.keystroke_times.append(current_time)
        except Exception as e:
            pass
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Capture mouse clicks"""
        if pressed:
            self.mouse_events.append({
                'type': 'click',
                'x': x,
                'y': y,
                'time': time.time()
            })
    
    def _on_mouse_move(self, x, y):
        """Capture mouse movement (sampled)"""
        # Sample mouse movements (not every pixel)
        if len(self.mouse_events) == 0 or time.time() - self.mouse_events[-1]['time'] > 0.5:
            self.mouse_events.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': time.time()
            })
    
    def _monitor_clipboard(self):
        """Monitor clipboard for AI-generated text"""
        while self.is_monitoring:
            try:
                if pyperclip is None:
                    # Clipboard support not available in this build
                    time.sleep(1)
                    continue

                current_clipboard = pyperclip.paste()
                
                if current_clipboard != self.last_clipboard and current_clipboard.strip():
                    # Analyze clipboard content
                    ai_score = self._analyze_text_for_ai(current_clipboard)
                    
                    self.clipboard_history.append({
                        'text': current_clipboard[:200],  # Store first 200 chars
                        'ai_score': ai_score,
                        'time': time.time()
                    })
                    
                    self.last_clipboard = current_clipboard
                    
                    # Update suspicion score
                    if ai_score > 0.7:
                        self.suspicion_score = min(1.0, self.suspicion_score + 0.3)
                
                time.sleep(1)
            except Exception as e:
                pass
    
    def _analyze_text_for_ai(self, text):
        """Analyze text for AI-generated content patterns"""
        if not text or len(text) < 20:
            return 0.0
        
        score = 0.0
        text_lower = text.lower()
        
        # Check for AI patterns
        pattern_matches = 0
        for pattern in self.ai_patterns:
            if re.search(pattern, text_lower):
                pattern_matches += 1
        
        if pattern_matches > 0:
            score += min(0.5, pattern_matches * 0.2)
        
        # Check for perfect grammar and formal structure
        sentences = text.split('.')
        if len(sentences) > 3:
            # Very consistent sentence length is suspicious
            lengths = [len(s.strip()) for s in sentences if s.strip()]
            if len(lengths) > 0:
                avg_length = sum(lengths) / len(lengths)
                std_length = (sum((x - avg_length) ** 2 for x in lengths) / len(lengths)) ** 0.5
                
                # AI tends to have consistent sentence lengths
                if std_length < 20 and avg_length > 50:
                    score += 0.3
        
        # Check for markdown formatting
        if '**' in text or '##' in text or '```' in text:
            score += 0.2
        
        # Very formal language patterns
        formal_words = ['furthermore', 'additionally', 'consequently', 'nevertheless', 'therefore']
        formal_count = sum(1 for word in formal_words if word in text_lower)
        if formal_count > 2:
            score += 0.2
        
        return min(1.0, score)
    
    def get_activity_summary(self):
        """Get summary of behavioral activity"""
        summary = {}
        
        # Analyze typing patterns
        if len(self.keystroke_times) > 10:
            typing_intervals = []
            times = list(self.keystroke_times)
            for i in range(1, len(times)):
                interval = times[i] - times[i-1]
                if interval < 1.0:  # Within 1 second
                    typing_intervals.append(interval)
            
            if typing_intervals:
                avg_interval = sum(typing_intervals) / len(typing_intervals)
                std_interval = (sum((x - avg_interval) ** 2 for x in typing_intervals) / len(typing_intervals)) ** 0.5
                
                # Very consistent typing = potential copy-paste
                summary['avg_typing_interval'] = avg_interval
                summary['typing_consistency'] = std_interval
                summary['rapid_typing_detected'] = avg_interval < 0.05  # < 50ms between keystrokes
        
        # Check clipboard
        if self.clipboard_history:
            recent_clipboard = list(self.clipboard_history)[-5:]
            summary['clipboard_ai_score'] = max([c['ai_score'] for c in recent_clipboard])
        else:
            summary['clipboard_ai_score'] = 0.0
        
        # Mouse activity
        summary['mouse_activity_level'] = len(self.mouse_events) / max(1, time.time() - self.mouse_events[0]['time']) if self.mouse_events else 0
        
        return summary
    
    def get_suspicion_score(self):
        """Get current behavioral suspicion score"""
        # Consider typing patterns
        summary = self.get_activity_summary()
        
        score = self.suspicion_score
        
        # Rapid typing is suspicious
        if summary.get('rapid_typing_detected', False):
            score = min(1.0, score + 0.2)
        
        # Low mouse activity during typing (suggests copy-paste)
        if summary.get('mouse_activity_level', 1.0) < 0.1 and len(self.keystroke_times) > 50:
            score = min(1.0, score + 0.1)
        
        return score
