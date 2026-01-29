import librosa
import numpy as np

def extract_mel_spectrogram(
    file_path,
    duration=2.0,
    sr=22050,
    n_mels=128
):
    # Load audio
    audio, sr = librosa.load(file_path, sr=sr, duration=duration)

    # Ensure fixed length
    target_length = int(sr * duration)
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)))
    else:
        audio = audio[:target_length]

    # Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=n_mels,
        fmax=800
    )

    # Convert to log scale
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)

    return mel_db
