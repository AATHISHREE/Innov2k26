import tensorflow as tf
print(f"✅ TensorFlow {tf.__version__} installed successfully!")
print(f"   GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")
print(f"   Backend: {tf.keras.backend.backend()}")
