import pyaudio
import numpy as np
import librosa
import threading
import queue
from collections import deque
import time

class AudioAnalyzer:
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        # Analysis metrics
        self.pause_timings = deque(maxlen=50)
        self.speech_segments = deque(maxlen=100)
        self.suspicion_score = 0.0
        
        # PyAudio setup
        self.p = pyaudio.PyAudio()
        
    def start_recording(self):
        """Start audio recording in background thread"""
        self.is_recording = True
        thread = threading.Thread(target=self._record_audio, daemon=True)
        thread.start()
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
    
    def _record_audio(self):
        """Record audio from microphone"""
        try:
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_queue.put(data)
            
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Audio recording error: {e}")
    
    def analyze_realtime_audio(self):
        """Analyze audio for AI-generated speech patterns"""
        if not self.is_recording:
            self.start_recording()
        
        try:
            # Collect audio chunks
            audio_chunks = []
            timeout = time.time() + 2  # 2 second window
            
            while time.time() < timeout and not self.audio_queue.empty():
                audio_chunks.append(self.audio_queue.get())
            
            if not audio_chunks:
                return None
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(audio_chunks), dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Extract features
            features = self._extract_audio_features(audio_float)
            
            return features
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return None
    
    def _extract_audio_features(self, audio):
        """Extract audio features for AI detection"""
        features = {}
        
        # 1. Detect pauses
        energy = librosa.feature.rms(y=audio)[0]
        pause_threshold = np.mean(energy) * 0.3
        is_speech = energy > pause_threshold
        
        # Calculate pause patterns
        pauses = self._detect_pauses(is_speech)
        features['pause_count'] = len(pauses)
        features['avg_pause_duration'] = np.mean([p[1] - p[0] for p in pauses]) if pauses else 0
        
        # 2. Analyze speech fluency
        features['fluency_score'] = self._calculate_fluency(is_speech)
        
        # 3. Pitch variation (AI speech often has less variation)
        if len(audio) > 2048:
            pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
            pitch_values = pitches[pitches > 0]
            features['pitch_variation'] = np.std(pitch_values) if len(pitch_values) > 0 else 0
        else:
            features['pitch_variation'] = 0
        
        # 4. Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        features['spectral_centroid_mean'] = np.mean(spectral_centroids)
        
        # 5. Calculate pause pattern score (suspicious if long pauses followed by fluent speech)
        features['pause_pattern_score'] = self._calculate_pause_pattern_score(pauses, features['fluency_score'])
        
        # Update suspicion score
        self._update_suspicion_score(features)
        
        return features
    
    def _detect_pauses(self, is_speech):
        """Detect pause segments in audio"""
        pauses = []
        in_pause = False
        pause_start = 0
        
        for i, speaking in enumerate(is_speech):
            if not speaking and not in_pause:
                pause_start = i
                in_pause = True
            elif speaking and in_pause:
                pauses.append((pause_start, i))
                in_pause = False
        
        return pauses
    
    def _calculate_fluency(self, is_speech):
        """Calculate speech fluency score"""
        if len(is_speech) == 0:
            return 0.0
        
        # Fluency is ratio of speech to total time
        speech_ratio = np.sum(is_speech) / len(is_speech)
        
        # High fluency with minimal hesitation
        transitions = np.sum(np.diff(is_speech.astype(int)) != 0)
        transition_penalty = min(1.0, transitions / 10)
        
        fluency = speech_ratio * (1 - transition_penalty * 0.3)
        return fluency
    
    def _calculate_pause_pattern_score(self, pauses, fluency_score):
        """Calculate score based on suspicious pause patterns"""
        # AI tools often cause: long thinking pause -> perfect fluent answer
        if not pauses or fluency_score < 0.5:
            return 0.0
        
        # Check for pauses longer than 2 seconds
        long_pauses = [p for p in pauses if (p[1] - p[0]) > 32]  # ~2 sec at 16kHz
        
        if long_pauses and fluency_score > 0.8:
            return 0.8  # Suspicious pattern
        
        return 0.3 if long_pauses else 0.0
    
    def _update_suspicion_score(self, features):
        """Update overall audio suspicion score"""
        score = 0.0
        
        # High pause pattern score
        if features['pause_pattern_score'] > 0.7:
            score += 0.4
        
        # Perfect fluency is suspicious
        if features['fluency_score'] > 0.9:
            score += 0.3
        
        # Low pitch variation (robotic)
        if features['pitch_variation'] < 50:
            score += 0.2
        
        # Very long pauses followed by speech
        if features['avg_pause_duration'] > 3.0 and features['fluency_score'] > 0.7:
            score += 0.3
        
        self.suspicion_score = min(1.0, score)
    
    def get_suspicion_score(self):
        """Get current audio suspicion score"""
        return self.suspicion_score
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.stop_recording()
        self.p.terminate()
