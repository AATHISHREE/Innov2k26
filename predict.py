"""
predict.py - ML Prediction Endpoint (can run independently)
"""

import numpy as np
import tensorflow as tf
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from preprocess.audio_features import extract_mel_spectrogram
    MODEL_LOADED = True
except ImportError:
    print("⚠️ Warning: preprocess module not found. Using fallback.")
    MODEL_LOADED = False

def predict_heart_risk(audio_path):
    """
    Predict heart risk using CNN model
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Dict with prediction results
    """
    if not MODEL_LOADED:
        return {
            "error": "ML model dependencies not found",
            "normal": 50.0,
            "abnormal": 50.0
        }
    
    try:
        # Check if model exists
        model_path = os.path.join('ml_model', 'heart_sound_cnn.h5')
        if not os.path.exists(model_path):
            return {
                "error": "Model file not found. Train the model first.",
                "normal": 50.0,
                "abnormal": 50.0
            }
        
        # Load model
        model = tf.keras.models.load_model(model_path)
        
        # Extract features
        spec = extract_mel_spectrogram(audio_path)
        spec = spec[np.newaxis, ..., np.newaxis]
        
        # Predict
        prediction = model.predict(spec, verbose=0)[0]
        
        return {
            "normal": float(prediction[0] * 100),
            "abnormal": float(prediction[1] * 100),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "normal": 50.0,
            "abnormal": 50.0,
            "success": False
        }

if __name__ == "__main__":
    # Test with sample audio
    test_audio = "test.wav"  # Change this to your test file
    
    if os.path.exists(test_audio):
        print(f"🔍 Testing prediction on: {test_audio}")
        result = predict_heart_risk(test_audio)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Prediction Results:")
            print(f"   Normal acoustic pattern: {result['normal']:.2f}%")
            print(f"   Abnormal acoustic pattern: {result['abnormal']:.2f}%")
            
            # Determine risk
            if result['abnormal'] > 70:
                risk = "HIGH"
            elif result['abnormal'] > 40:
                risk = "MEDIUM"
            elif result['abnormal'] > 15:
                risk = "LOW"
            else:
                risk = "SAFE"
            
            print(f"   Risk Level: {risk}")
    else:
        print(f"⚠️ Test file not found: {test_audio}")
        print("📋 Usage: python predict.py")
        print("Make sure you have a test.wav file in the current directory")