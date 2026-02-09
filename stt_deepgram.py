import os
import json
import asyncio
import sounddevice as sd
import websockets
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.05  # 50 ms
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

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

def mic_stream():
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
    for chunk in mic_stream():
        await ws.send(chunk)

async def receive_transcripts(ws):
    async for message in ws:
        data = json.loads(message)

        if "channel" not in data:
            continue

        alternatives = data["channel"].get("alternatives", [])
        if not alternatives:
            continue

        transcript = alternatives[0].get("transcript", "")
        if transcript:
            if data.get("is_final"):
                print(f"\n[FINAL] {transcript}")
            else:
                print(f"[PARTIAL] {transcript}", end="\r")

async def main():
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
        print("\nStopped.")