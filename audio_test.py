import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000
DURATION = 5  # seconds

print("🎤 Speak now...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32"
)

sd.wait()

print("🔊 Playing back...")
sd.play(audio, SAMPLE_RATE)
sd.wait()

print("✅ Done")