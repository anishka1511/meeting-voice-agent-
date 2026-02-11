import sounddevice as sd
import numpy as np
import queue
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== CONFIGURE THESE AFTER RUNNING find_audio_devices.py ==========
CABLE_OUTPUT_INDEX = 17  # CABLE Output (VB-Audio Virtual Cable) - for listening (48kHz stereo)
CABLE_INPUT_INDEX = 16   # CABLE Input (VB-Audio Virtual Cable) - for speaking (48kHz stereo)
# =========================================================================

client = OpenAI()  # Make sure OPENAI_API_KEY is set in environment

# Audio parameters
SAMPLE_RATE = 48000  # Match VB-Cable sample rate
CHANNELS = 2         # Stereo for VB-Cable
BLOCKSIZE = 24000    # 0.5 seconds of audio at 48kHz

audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    """Callback for audio input stream"""
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(indata.copy())

def speech_to_text(audio_data):
    """Convert audio to text using Whisper"""
    try:
        # Convert stereo to mono by averaging channels
        if audio_data.ndim == 2:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data
        
        # Convert numpy array to bytes
        audio_bytes = (audio_mono * 32767).astype(np.int16).tobytes()
        
        # Save to temporary file (Whisper API requires file)
        with open("temp_audio.wav", "wb") as f:
            import wave
            with wave.open(f, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono for Whisper
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(SAMPLE_RATE)
                wav_file.writeframes(audio_bytes)
        
        with open("temp_audio.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

def get_llm_response(text):
    """Get response from GPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant. Keep responses concise and professional."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        return ""

def text_to_speech(text):
    """Convert text to speech using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save and play
        response.stream_to_file("temp_speech.mp3")
        
        # Play through VB-Cable Input
        import soundfile as sf
        audio_data, sr = sf.read("temp_speech.mp3")
        
        # Play to VB-Cable Input (this goes into Zoom mic)
        sd.play(audio_data, samplerate=sr, device=CABLE_INPUT_INDEX)
        sd.wait()
        
    except Exception as e:
        print(f"TTS Error: {e}")

def main():
    if CABLE_OUTPUT_INDEX is None or CABLE_INPUT_INDEX is None:
        print("❌ Please run find_audio_devices.py first and update device indices!")
        return
    
    print("🎙️ Meeting Voice Agent Starting...")
    print(f"📥 Listening on device {CABLE_OUTPUT_INDEX}")
    print(f"📤 Speaking on device {CABLE_INPUT_INDEX}")
    print("\n⚙️ Make sure to configure Zoom/Meet:")
    print("   Speaker → CABLE Input")
    print("   Microphone → CABLE Output")
    print("\nPress Ctrl+C to stop\n")
    
    audio_buffer = []
    silence_threshold = 0.01
    silence_duration = 1.5  # seconds
    silence_blocks = int(silence_duration * SAMPLE_RATE / BLOCKSIZE)
    
    try:
        with sd.InputStream(
            device=CABLE_OUTPUT_INDEX,
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
            callback=audio_callback
        ):
            print("✅ Agent is now listening to the meeting...\n")
            
            silence_count = 0
            
            while True:
                try:
                    data = audio_queue.get(timeout=1)
                    
                    # Check if audio is speech or silence
                    volume = np.abs(data).mean()
                    
                    if volume > silence_threshold:
                        audio_buffer.append(data)
                        silence_count = 0
                    else:
                        silence_count += 1
                    
                    # Process when speech ends (silence detected)
                    if silence_count >= silence_blocks and len(audio_buffer) > 0:
                        print("🎧 Processing speech...")
                        
                        # Combine audio chunks
                        full_audio = np.concatenate(audio_buffer)
                        
                        # STT
                        text = speech_to_text(full_audio)
                        if text and len(text) > 5:  # Ignore very short utterances
                            print(f"💬 Heard: {text}")
                            
                            # LLM
                            response = get_llm_response(text)
                            if response:
                                print(f"🤖 Responding: {response}")
                                
                                # TTS
                                text_to_speech(response)
                        
                        # Reset buffer
                        audio_buffer = []
                        silence_count = 0
                
                except queue.Empty:
                    continue
    
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped")

if __name__ == "__main__":
    main()
