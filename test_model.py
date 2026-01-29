import sys
sys.path.append('.')
try:
    from ml_model.model_loader import HeartSoundModel
    print("✅ HeartSoundModel imports work")
    
    # Try to load model
    model = HeartSoundModel()
    print("✅ Model loaded successfully!")
    print(f"   Model info: {model.model_info.get('model_name', 'Heart Sound CNN')}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
