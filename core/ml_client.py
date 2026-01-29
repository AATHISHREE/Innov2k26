# core/ml_client.py
import os
import requests
import json
import numpy as np
import logging
import sys

# Add ml_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_model'))

try:
    from ml_model.model_loader import HeartSoundModel
    HAS_LOCAL_MODEL = True
except ImportError as e:
    print(f"⚠️ Could not import HeartSoundModel: {e}")
    HAS_LOCAL_MODEL = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLClient:
    def __init__(self):
        self.use_real_ml = os.getenv('USE_REAL_ML', 'false').lower() == 'true'
        self.ml_api_url = os.getenv('ML_API_URL', '')
        self.ml_api_key = os.getenv('ML_API_KEY', '')
        
        # Initialize local model if not using external API
        self.local_model = None
        if not self.use_real_ml and HAS_LOCAL_MODEL:
            try:
                self.local_model = HeartSoundModel()
                logger.info("✅ Local ML model initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load local ML model: {e}")
                self.local_model = None
        
        logger.info(f"ML Client initialized - Use Real ML: {self.use_real_ml}, Local Model: {self.local_model is not None}")
    
    def analyze_heart_sound(self, audio_path, patient_context=None):
        """
        Analyze heart sound using either:
        1. External ML API (if USE_REAL_ML=true)
        2. Local ML model (default)
        3. Mock analysis (fallback)
        """
        logger.info(f"Analyzing heart sound: {audio_path}")
        
        # Option 1: External ML API
        if self.use_real_ml and self.ml_api_url:
            logger.info("Using external ML API")
            return self._call_external_ml_api(audio_path, patient_context)
        
        # Option 2: Local ML Model
        if self.local_model:
            logger.info("Using local ML model")
            result = self.local_model.predict_from_audio(audio_path)
            if result:
                return self._format_local_ml_result(result, patient_context)
            else:
                logger.warning("Local ML prediction failed, falling back to mock")
        
        # Option 3: Mock Analysis (fallback)
        logger.info("Using mock analysis")
        return self._mock_analysis(patient_context)
    
    def _call_external_ml_api(self, audio_path, patient_context):
        """Call external ML API"""
        try:
            with open(audio_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'patient_context': json.dumps(patient_context)} if patient_context else {}
                headers = {'Authorization': f'Bearer {self.ml_api_key}'} if self.ml_api_key else {}
                
                response = requests.post(
                    self.ml_api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"ML API error: {response.status_code}")
                    return self._mock_analysis(patient_context)
                    
        except Exception as e:
            logger.error(f"ML API call failed: {str(e)}")
            return self._mock_analysis(patient_context)
    
    def _format_local_ml_result(self, ml_result, patient_context):
        """Format local ML result to match API response format"""
        prediction = ml_result['prediction']
        confidence = ml_result['confidence']
        
        # Map prediction to risk level
        risk_mapping = {
            'normal': 'low',
            'Normal': 'low',
            'abnormal': 'high',
            'Abnormal': 'high',
            'murmur': 'medium',
            'Murmur': 'medium'
        }
        
        risk_level = risk_mapping.get(prediction.lower(), 'medium')
        
        # Generate recommendation based on risk
        recommendations = {
            'high': 'Urgent consultation with cardiologist recommended. Avoid strenuous activity and seek immediate medical attention if symptoms worsen.',
            'medium': 'Schedule a follow-up with healthcare provider. Monitor for symptoms like chest pain, shortness of breath, or fatigue.',
            'low': 'Regular check-up advised. Maintain healthy lifestyle with balanced diet and regular exercise.'
        }
        
        # Add patient context if available
        analysis_note = ""
        if patient_context:
            age = patient_context.get('age', 0)
            if age > 50 and risk_level != 'low':
                analysis_note = "Patient is over 50, increased cardiovascular risk factors."
        
        result = {
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'risk_level': risk_level,
            'recommendation': recommendations.get(risk_level, ''),
            'analysis_note': analysis_note,
            'probabilities': ml_result.get('probabilities', []),
            'class_names': ml_result.get('class_names', ['normal', 'abnormal']),
            'ml_source': 'local_cnn_model',
            'model_info': self.local_model.get_model_info() if self.local_model else {}
        }
        
        logger.info(f"ML Analysis Result: {prediction} ({risk_level} risk, {confidence:.2%} confidence)")
        return result
    
    def _mock_analysis(self, patient_context):
        """Mock analysis (fallback)"""
        import random
        import time
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Mock predictions
        predictions = ['normal', 'abnormal', 'murmur']
        prediction = random.choice(predictions)
        confidence = round(random.uniform(0.6, 0.95), 3)
        
        risk_mapping = {
            'normal': 'low',
            'abnormal': 'high',
            'murmur': 'medium'
        }
        
        risk_level = risk_mapping.get(prediction, 'medium')
        
        recommendations = {
            'high': 'Urgent consultation with cardiologist recommended.',
            'medium': 'Follow-up with healthcare provider advised.',
            'low': 'Regular check-up advised.'
        }
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'risk_level': risk_level,
            'recommendation': recommendations.get(risk_level, ''),
            'ml_source': 'mock',
            'note': 'Using mock analysis - ML model not available'
        }
    
    def get_status(self):
        """Get ML client status"""
        return {
            'use_real_ml': self.use_real_ml,
            'has_local_model': self.local_model is not None,
            'model_loaded': self.local_model is not None,
            'external_api_configured': bool(self.ml_api_url)
        }