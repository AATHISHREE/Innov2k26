import os
import numpy as np

from preprocess.audio_features import extract_mel_spectrogram
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from preprocess.audio_features import extract_mel_spectrogram

# --------------------
# Load Dataset
# --------------------
X = []
y = []

DATA_DIR = "data"
CLASSES = ["normal", "abnormal"]

for label, class_name in enumerate(CLASSES):
    folder = os.path.join(DATA_DIR, class_name)
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            path = os.path.join(folder, file)
            spec = extract_mel_spectrogram(path)
            X.append(spec)
            y.append(label)

X = np.array(X)
X = X[..., np.newaxis]   # (samples, 128, time, 1)
y = to_categorical(y, num_classes=2)

print("Dataset shape:", X.shape)

# --------------------
# CNN Model
# --------------------
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=X.shape[1:]),
    MaxPooling2D((2,2)),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),

    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D((2,2)),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.4),

    Dense(2, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# --------------------
# Train
# --------------------
model.fit(X, y, epochs=10, batch_size=2)

# --------------------
# Save Model
# --------------------
os.makedirs("model", exist_ok=True)
model.save("model/heart_sound_cnn.h5")

print("✅ MODEL TRAINED & SAVED")
