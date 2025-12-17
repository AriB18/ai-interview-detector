import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AIDetectionClassifier:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Try to load pre-trained model
        self._load_model()
        
        # If no model exists, use rule-based system
        if not self.is_trained:
            print("⚠️  No trained model found. Using rule-based detection.")
    
    def _load_model(self):
        """Load pre-trained model if available"""
        model_path = 'models/ai_detector_model.pkl'
        scaler_path = 'models/scaler.pkl'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                print("✅ Loaded pre-trained AI detection model")
            except Exception as e:
                print(f"Failed to load model: {e}")
    
    def predict(self, features):
        """Predict probability of AI assistance"""
        # Extract feature values
        feature_vector = self._extract_feature_vector(features)
        
        if self.is_trained and self.model is not None:
            # Use ML model
            feature_scaled = self.scaler.transform([feature_vector])
            probability = self.model.predict_proba(feature_scaled)[0][1]
        else:
            # Use rule-based system
            probability = self._rule_based_prediction(features)
        
        return probability
    
    def _extract_feature_vector(self, features):
        """Convert feature dict to vector"""
        return [
            features.get('process_score', 0.0),
            features.get('audio_score', 0.0),
            features.get('behavior_score', 0.0),
        ]
    
    def _rule_based_prediction(self, features):
        """Rule-based AI detection when no trained model available"""
        process_score = features.get('process_score', 0.0)
        audio_score = features.get('audio_score', 0.0)
        behavior_score = features.get('behavior_score', 0.0)
        
        # Weighted combination
        weights = {
            'process': 0.4,   # Process detection is most reliable
            'audio': 0.35,    # Audio patterns are strong indicator
            'behavior': 0.25  # Behavioral patterns support
        }
        
        combined_score = (
            process_score * weights['process'] +
            audio_score * weights['audio'] +
            behavior_score * weights['behavior']
        )
        
        # Apply threshold logic
        # If ANY score is very high (>0.9), increase overall probability
        max_score = max(process_score, audio_score, behavior_score)
        if max_score > 0.9:
            combined_score = max(combined_score, 0.85)
        
        # If multiple scores are moderate-high, boost probability
        high_scores = sum([1 for s in [process_score, audio_score, behavior_score] if s > 0.6])
        if high_scores >= 2:
            combined_score = min(1.0, combined_score + 0.15)
        
        return combined_score
    
    def train(self, X_train, y_train):
        """Train the ML model with labeled data"""
        print("🔧 Training AI detection model...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train ensemble model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X_scaled, y_train)
        self.is_trained = True
        
        # Save model
        os.makedirs('models', exist_ok=True)
        with open('models/ai_detector_model.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open('models/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print("✅ Model trained and saved")
    
    def generate_training_data(self):
        """Generate synthetic training data for model"""
        print("📊 Generating synthetic training data...")
        
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features for AI-assisted cases (label=1)
        n_ai = n_samples // 2
        ai_process = np.random.beta(8, 2, n_ai)  # High process scores
        ai_audio = np.random.beta(7, 3, n_ai)    # High audio scores
        ai_behavior = np.random.beta(6, 4, n_ai) # Moderate-high behavior
        
        X_ai = np.column_stack([ai_process, ai_audio, ai_behavior])
        y_ai = np.ones(n_ai)
        
        # Generate features for genuine cases (label=0)
        n_genuine = n_samples - n_ai
        genuine_process = np.random.beta(2, 8, n_genuine)  # Low process scores
        genuine_audio = np.random.beta(3, 7, n_genuine)    # Low audio scores
        genuine_behavior = np.random.beta(4, 6, n_genuine) # Moderate behavior
        
        X_genuine = np.column_stack([genuine_process, genuine_audio, genuine_behavior])
        y_genuine = np.zeros(n_genuine)
        
        # Combine data
        X = np.vstack([X_ai, X_genuine])
        y = np.concatenate([y_ai, y_genuine])
        
        # Shuffle
        indices = np.random.permutation(n_samples)
        X = X[indices]
        y = y[indices]
        
        print(f"✅ Generated {n_samples} training samples")
        return X, y
    
    def initialize_model(self):
        """Initialize model with synthetic data"""
        X, y = self.generate_training_data()
        self.train(X, y)
