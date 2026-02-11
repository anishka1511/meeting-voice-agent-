import os
import json
import asyncio
import sounddevice as sd
import websockets
import numpy as np
from groq import Groq
from gtts import gTTS
import io
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.05  # 50 ms
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Deepgram WebSocket URL - OPTIMIZED FOR SPEED
DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-2"
    "&language=en-US"
    "&encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&interim_results=true"
    "&endpointing=100"
    "&smart_format=true"
)

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def mic_stream():
    """Stream audio from microphone."""
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=CHUNK_SIZE,
    ) as stream:
        while True:
            data, _ = stream.read(CHUNK_SIZE)
            yield data.tobytes()

async def send_audio(ws):
    """Send microphone audio chunks to Deepgram."""
    for chunk in mic_stream():
        await ws.send(chunk)

def get_llm_response(transcript):
    """Get response from Groq LLM."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful meeting assistant. Be concise and conversational. Keep responses under 2 sentences."
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def text_to_speech(text):
    """Convert text to speech using gTTS and play it."""
    try:
        # Generate speech using Google TTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to in-memory buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Convert MP3 to WAV for playback
        audio = AudioSegment.from_mp3(audio_buffer)
        samples = np.array(audio.get_array_of_samples())
        
        # Convert to int16 if needed
        if audio.sample_width == 2:
            samples = samples.astype(np.int16)
        
        # Reshape for stereo if needed
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
        
        # Play audio WITHOUT blocking
        sd.play(samples, samplerate=audio.frame_rate)
        
    except Exception as e:
        print(f"TTS Error: {str(e)}")

async def receive_transcripts(ws):
    """Receive transcripts from Deepgram and send final ones to LLM."""
    async for message in ws:
        data = json.loads(message)

        if "channel" not in data:
            continue

        alternatives = data["channel"].get("alternatives", [])
        if not alternatives:
            continue

        transcript = alternatives[0].get("transcript", "")
        if not transcript:
            continue

        # Show partial transcripts for feedback
        if not data.get("is_final"):
            print(f"[USER] {transcript}", end="\r")
        else:
            # Final transcript - send to LLM
            print(f"\n[USER] {transcript}")
            
            # Get LLM response
            print("[AGENT] Thinking...")
            llm_response = await asyncio.to_thread(get_llm_response, transcript)
            print(f"[AGENT] {llm_response}")
            
            # Convert to speech and play (non-blocking)
            print("[AGENT] Speaking...")
            await asyncio.to_thread(text_to_speech, llm_response)
            print()

async def main():
    """Main function to run STT + LLM + TTS pipeline."""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    async with websockets.connect(DEEPGRAM_URL, additional_headers=headers) as ws:
        print("🎤 Speak now (Ctrl+C to stop)")

        send_task = asyncio.create_task(send_audio(ws))
        recv_task = asyncio.create_task(receive_transcripts(ws))

        await asyncio.gather(send_task, recv_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Voice agent stopped.")