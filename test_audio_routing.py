import sounddevice as sd
import numpy as np

CABLE_OUTPUT_INDEX = 8   # CABLE Output (VB-Audio Virtual Cable)
CABLE_INPUT_INDEX = 16   # CABLE Input (VB-Audio Virtual Cable) - 48kHz stereo

print("Testing VB-Cable routing...")
print("You should hear a beep through your headphones if 'Listen' is enabled")

# Generate test tone (stereo - 2 channels) at 48kHz
duration = 2  # seconds
frequency = 440  # Hz (A note)
sample_rate = 48000  # Match device sample rate
t = np.linspace(0, duration, int(sample_rate * duration))
test_tone_mono = 0.3 * np.sin(2 * np.pi * frequency * t)

# Convert to stereo (duplicate mono to both channels)
test_tone = np.column_stack((test_tone_mono, test_tone_mono))

# Play through VB-Cable Input (goes to Zoom mic)
sd.play(test_tone, samplerate=sample_rate, device=CABLE_INPUT_INDEX)
sd.wait()

print("✅ Test complete")
