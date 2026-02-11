import sounddevice as sd

print("=== Available Audio Devices ===\n")
devices = sd.query_devices()

for i, device in enumerate(devices):
    print(f"Device {i}: {device['name']}")
    print(f"  Max Input Channels: {device['max_input_channels']}")
    print(f"  Max Output Channels: {device['max_output_channels']}")
    print(f"  Default Sample Rate: {device['default_samplerate']}")
    print()

print("\n=== Look for these devices ===")
print("CABLE Input (VB-Audio Virtual Cable) - for OUTPUT/playback")
print("CABLE Output (VB-Audio Virtual Cable) - for INPUT/recording")
