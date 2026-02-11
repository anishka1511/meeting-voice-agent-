# Meeting Voice Agent (MVA)

A real-time conversational AI agent capable of participating in online meetings through voice interaction. The agent listens to meeting audio, processes speech using advanced AI models, and responds naturally using text-to-speech synthesis.

## Overview

This project implements a voice-based conversational agent that can:
- Listen to real-time audio input from meetings or microphone
- Transcribe speech using streaming speech-to-text services
- Generate contextual responses using large language models
- Respond verbally using text-to-speech synthesis
- Participate in online meetings (Zoom, Google Meet, etc.) via virtual audio routing

## Features

- **Real-time Speech-to-Text**: Streaming transcription with partial and final results using Deepgram
- **Fast LLM Response**: Low-latency conversational responses using Groq's Llama 3.1
- **Natural Speech Synthesis**: Text-to-speech output using Google TTS
- **Meeting Integration**: Virtual audio cable support for joining Zoom/Google Meet
- **Non-blocking Architecture**: Asynchronous processing for real-time conversation flow
- **Zero-cost Prototyping**: Free-tier services for development and testing

## Technology Stack

### Core
- **Python**: 3.11.5
- **OS**: Windows 10/11

### Key Libraries
- **sounddevice**: Audio I/O interface
- **websockets**: WebSocket communication for streaming STT
- **numpy**: Audio buffer manipulation
- **pydub**: Audio format conversion

### AI Services
- **Deepgram Nova-2**: Streaming speech-to-text
- **Groq (Llama 3.1 8B)**: Large language model for response generation
- **gTTS**: Google Text-to-Speech synthesis

## Project Structure

```
meeting-voice-agent/
├── stt_llm_integration.py    # Main voice agent implementation (STT + LLM + TTS)
├── stt_deepgram.py            # Standalone Deepgram STT test
├── audio_test.py              # Audio I/O validation
├── test_env.py                # Environment and dependency testing
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not tracked in git)
├── docs/
│   └── spike-report.md        # Detailed research and implementation documentation
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Windows 10/11 (for VB-Cable support)
- Active internet connection for API services

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-voice-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   PowerShell:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Command Prompt:
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   Git Bash:
   ```bash
   source venv/Scripts/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure API keys**
   
   Create a `.env` file in the project root:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Getting API Keys

### Deepgram (Speech-to-Text)
1. Sign up at [https://deepgram.com](https://deepgram.com)
2. Create a new API key in the console
3. Free tier includes $200 credit

### Groq (Language Model)
1. Sign up at [https://groq.com](https://groq.com)
2. Generate an API key
3. Free tier: 14,400 requests/day, 30 requests/minute

## Usage

### Basic Voice Agent (Microphone)

Run the main voice agent that listens to your microphone and responds:

```bash
python stt_llm_integration.py
```

**What it does:**
- Captures audio from your microphone
- Transcribes speech in real-time
- Generates AI responses using Groq
- Speaks responses using Google TTS

**Example interaction:**
```
[USER] What is the weather?
[AGENT] Thinking...
[AGENT] I don't have real-time weather data, but I can help with general information.
[AGENT] Speaking...
```

### Test STT Only

Test speech-to-text transcription without LLM or TTS:

```bash
python stt_deepgram.py
```

### Test Audio I/O

Verify microphone and speaker functionality:

```bash
python audio_test.py
```

### Meeting Integration (Advanced)

To integrate with Zoom/Google Meet, see the [VB-Cable Integration Guide](docs/spike-report.md#virtual-audio-routing-for-meeting-integration) in the spike report.

## Configuration

### Audio Settings

Default configuration in `stt_llm_integration.py`:

```python
SAMPLE_RATE = 16000  # 16kHz for telephony quality
CHANNELS = 1         # Mono audio
CHUNK_DURATION = 0.05  # 50ms chunks for low latency
```

### LLM Settings

Modify the system prompt in `stt_llm_integration.py`:

```python
{
    "role": "system",
    "content": "You are a helpful meeting assistant. Be concise and conversational."
}
```

Adjust response length:
```python
max_tokens=100  # Increase for longer responses
temperature=0.7  # 0.0 = deterministic, 1.0 = creative
```

## How It Works

### Architecture Flow

```
Microphone Audio
   ↓
Local Audio Chunking (50ms)
   ↓
WebSocket Stream → Deepgram STT
   ↓
Partial / Final Transcripts
   ↓
Groq LLM (Llama 3.1)
   ↓
Text Response
   ↓
gTTS Speech Synthesis
   ↓
Speaker Output
```

### Key Components

1. **Audio Capture**: `sounddevice` captures microphone input in small chunks
2. **Streaming STT**: Audio chunks stream to Deepgram via WebSocket
3. **Transcript Processing**: Partial transcripts displayed, final transcripts trigger LLM
4. **LLM Response**: Groq generates contextual responses in ~100-500ms
5. **Speech Synthesis**: gTTS converts text to natural speech
6. **Non-blocking Playback**: Agent continues listening while speaking

## Performance Characteristics

- **STT Latency**: ~1 second for partial transcripts
- **LLM Latency**: ~100-500ms (Groq's LPU advantage)
- **TTS Latency**: ~1-2 seconds for short responses
- **Total Response Time**: ~2-4 seconds (human-acceptable for conversation)

## Limitations

### Current Implementation
- Microphone-only (no automatic meeting integration)
- Single-speaker focus (no diarization)
- English language only
- No conversation history tracking
- Basic error handling

### Free Tier Constraints
- Deepgram: Limited by credit ($200 initial)
- Groq: 14,400 requests/day (sufficient for hundreds of conversations)
- gTTS: Unlimited but moderate voice quality

## Troubleshooting

### No audio input detected
- Check microphone permissions in Windows settings
- Verify correct microphone selected in `sounddevice.default.device`
- Run `python audio_test.py` to validate audio I/O

### WebSocket connection errors
- Verify DEEPGRAM_API_KEY is correct in `.env`
- Check internet connection
- Ensure firewall allows WebSocket connections

### API key errors
- Confirm `.env` file exists in project root
- Verify API keys are valid (no quotes around values)
- Check API key has not expired

### Dependencies not found
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.11+)

## Development Notes

This is a research spike focused on feasibility validation, not production deployment. The implementation prioritizes:
- Rapid prototyping
- Low latency for real-time conversation
- Zero-cost development using free tiers
- Simple architecture for easy iteration

For production considerations, see [docs/spike-report.md](docs/spike-report.md).

## Documentation

Comprehensive research documentation available in:
- [docs/spike-report.md](docs/spike-report.md) - Detailed technical report covering architecture decisions, provider evaluations, implementation challenges, and lessons learned

## Future Enhancements

Potential next steps (outside current scope):
- Multi-speaker diarization
- Conversation memory and context retention
- Wake word activation ("Hey assistant")
- Support for multiple languages
- Automated meeting platform integration
- WebRTC-based meeting participation
- Improved TTS voice quality (upgrade to paid service)

## License

This project is for educational and research purposes.

## Contributing

This is a research spike project. For questions or feedback, please open an issue.

## Acknowledgments

- **Deepgram**: For providing accessible streaming STT API
- **Groq**: For ultra-low latency LLM inference
- **Google**: For free and reliable TTS service
- **VB-Audio**: For virtual audio cable software
