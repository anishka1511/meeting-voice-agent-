# Meeting Voice Agent - VB-Cable Integration

An AI-powered voice agent that listens to online meetings (Zoom, Google Meet, Teams) and can respond in real-time using speech-to-text, LLM processing, and text-to-speech capabilities.

## 🎯 Overview

This branch implements VB-Cable virtual audio routing to enable the agent to:
- **Listen** to meeting audio via VB-Cable Output
- **Transcribe** speech using Deepgram WebSocket API
- **Process** conversations using Groq LLM (optimized for speed)
- **Respond** back into the meeting via VB-Cable Input using Google TTS

## 📋 Prerequisites

### Required Software
1. **VB-Audio Virtual Cable** - [Download here](https://vb-audio.com/Cable/)
   - Install and restart your computer after installation
   
2. **Python 3.8+**

### API Keys Required
You'll need API keys for:
- **Deepgram** (for real-time speech-to-text)
- **Groq** (for fast LLM responses)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file in the project root:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Find Your Audio Device Indices

Run the device finder to locate your VB-Cable devices:

```bash
python find_audio_devices.py
```

Look for:
- **CABLE Output (VB-Audio Virtual Cable)** - for listening/recording
- **CABLE Input (VB-Audio Virtual Cable)** - for speaking/playback

### 4. Update Device Indices

Edit `meeting_agent.py` and update the device indices at the top:

```python
CABLE_OUTPUT_INDEX = 17  # Your CABLE Output index
CABLE_INPUT_INDEX = 16   # Your CABLE Input index
```

### 5. Configure Your Meeting Platform

In Zoom/Google Meet/Teams settings:
- **Speaker** → Set to **CABLE Input (VB-Audio Virtual Cable)**
- **Microphone** → Set to **CABLE Output (VB-Audio Virtual Cable)**

### 6. Enable Windows Audio Routing (Important!)

For you to hear the meeting audio through your headphones:

1. Right-click the **speaker icon** in Windows taskbar
2. Select **Sounds** → **Recording** tab
3. Find **CABLE Output** device
4. Right-click → **Properties**
5. Go to **Listen** tab
6. Check ✅ **"Listen to this device"**
7. Select your **headphones/speakers** from the dropdown
8. Click **Apply** and **OK**

### 7. Test Audio Routing (Optional)

```bash
python test_audio_routing.py
```

You should hear a beep through your headphones if routing is configured correctly.

### 8. Run the Meeting Agent

```bash
python meeting_agent.py
```

## 🎙️ How It Works

```
Meeting Audio → VB-Cable Output → Agent Listens → Deepgram STT
                                                       ↓
                                                   Groq LLM
                                                       ↓
Agent Speaks ← VB-Cable Input ← Google TTS ← LLM Response
      ↓
Meeting Participants Hear
```

### Audio Flow Details

1. **Listening Path**:
   - Meeting platform audio → CABLE Input (speaker)
   - Agent captures from CABLE Output (microphone)
   - Windows "Listen to this device" routes to your headphones

2. **Speaking Path**:
   - Agent generates TTS audio
   - Plays to CABLE Input device
   - Meeting platform captures from its microphone (CABLE Output)
   - Participants hear the agent's voice

## 📁 Project Files

- **`meeting_agent.py`** - Main agent with VB-Cable integration
- **`find_audio_devices.py`** - Utility to list audio devices
- **`test_audio_routing.py`** - Test VB-Cable routing setup
- **`stt_deepgram.py`** - Standalone Deepgram STT demo
- **`stt_llm_integration.py`** - Basic STT+LLM integration example
- **`requirements.txt`** - Python dependencies

## ⚙️ Configuration

### Audio Settings (in `meeting_agent.py`)

```python
SAMPLE_RATE = 48000        # VB-Cable sample rate
INPUT_CHANNELS = 1         # Mono for input
OUTPUT_CHANNELS = 2        # Stereo for output
CHUNK_DURATION = 0.05      # 50ms chunks for low latency
```

### Deepgram Settings

Optimized for speed with:
- Model: `nova-2` (fastest, most accurate)
- Interim results: Enabled
- Endpointing: 100ms (quick response)
- Smart formatting: Enabled

### Silence Detection

```python
silence_threshold = 0.01   # Volume threshold
silence_duration = 1.5     # Seconds of silence before processing
```

## 🔧 Troubleshooting

### No audio being captured
- Verify device indices with `find_audio_devices.py`
- Check meeting platform audio settings
- Ensure VB-Cable is properly installed

### Can't hear meeting audio
- Enable "Listen to this device" on CABLE Output
- Select correct playback device (your headphones)
- Check Windows sound mixer levels

### Agent not responding
- Verify API keys in `.env` file
- Check internet connection
- Review console for error messages
- Ensure audio volume is above silence threshold

### Echo or feedback
- Don't set meeting speaker to your actual speakers
- Keep CABLE Input as the meeting speaker
- Use headphones to monitor

## 🛠️ Development

### Testing Components

Test Deepgram STT:
```bash
python stt_deepgram.py
```

Test LLM integration:
```bash
python stt_llm_integration.py
```

### Dependencies

Core libraries:
- `sounddevice` - Audio I/O
- `websockets` - Deepgram WebSocket connection
- `groq` - Fast LLM inference
- `gtts` - Google Text-to-Speech
- `numpy` - Audio processing
- `python-dotenv` - Environment management

## 📝 Notes

- The agent processes speech in real-time with minimal latency
- Silence detection prevents partial transcriptions
- Short utterances (<5 chars) are ignored to reduce noise
- Groq is used for fast LLM responses (optimized for real-time)
- Audio routing requires VB-Cable for virtual audio paths

## 🔒 Security

- Keep your `.env` file private (already in `.gitignore`)
- Never commit API keys to version control
- Obtain meeting participant consent before recording/transcription

## 📄 License

[Add your license here]

## 🤝 Contributing

This is a feature branch. Main development happens on `main` branch.

---

**Current Branch**: `feature/vb-cable-integration`  
**Status**: In Development  
**Last Updated**: February 2026
