import os
import json
import asyncio
import sounddevice as sd
import websockets
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.05  # 50 ms
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Deepgram WebSocket URL
DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-2"
    "&language=en-US"
    "&encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&interim_results=true"
    "&endpointing=300"
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
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

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
            print(f"[AGENT] {llm_response}\n")

async def main():
    """Main function to run STT + LLM pipeline."""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    async with websockets.connect(DEEPGRAM_URL, additional_headers=headers) as ws:
        print("🎤 Voice Agent Ready - Speak now (Ctrl+C to stop)")
        print("=" * 60)

        send_task = asyncio.create_task(send_audio(ws))
        recv_task = asyncio.create_task(receive_transcripts(ws))

        await asyncio.gather(send_task, recv_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Voice agent stopped.")
