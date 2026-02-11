# Meeting Voice Agent (MVA) — Research Spike

This research spike explores the feasibility of building a Meeting Voice Agent (MVA) that can join online meetings via audio, participate in real-time voice conversations, and persist post-call artifacts such as transcripts and audio recordings.

The goal is to validate real-time conversational feasibility, viable meeting entry methods, system architecture, and cost implications.

## Scope

- Real-time audio input and output
- Streaming speech-to-text (STT)
- LLM-based response generation
- Streaming text-to-speech (TTS)
- Turn-taking and interruption handling
- Transcript and audio capture

## Non-Goals

- Full WebRTC bot participation
- Video handling
- UI / frontend
- Perfect diarization
- Production-grade scaling

## Development Environment

- OS: Windows 10
- Language: Python 3.11
- Environment: Python virtual environment (venv)

Key libraries: sounddevice, numpy, websockets, groq, gtts, pydub

## Audio I/O Validation

A local audio loopback test was implemented to confirm reliable microphone input and speaker output:
- Record microphone input for a fixed duration
- Immediately play the recorded audio back

Results confirmed microphone access, speaker output, and acceptable audio latency for conversational use. This validates the system can support real-time audio pipelines.

## Speech-to-Text Implementation

### STT Provider Selection

Multiple speech-to-text approaches were evaluated, including local ASR models (e.g., Whisper) and managed cloud-based services. The evaluation criteria focused on:

- native support for real-time (streaming) transcription
- low end-to-end latency
- availability of partial (interim) transcripts
- suitability for conversational turn-taking and interruption handling

Based on these criteria, **:contentReference[oaicite:0]{index=0}** was selected as the speech-to-text provider for this research spike.

### Rationale for Choosing Deepgram

Deepgram was chosen for the following reasons:

- Native WebSocket-based streaming STT, eliminating the need for simulated streaming
- Low transcription latency suitable for conversational agents
- Support for partial and final transcript events
- Reduced engineering complexity compared to batch-based ASR approaches

This allowed the spike to focus on conversational feasibility rather than ASR infrastructure.

### Architectural Placement

Speech-to-text and text-to-speech responsibilities are intentionally separated across providers to allow independent optimization of latency and quality.


This separation reflects common industry practice in real-time voice systems.

### Implementation Approach

- Microphone audio is captured in small, fixed-size chunks
- Audio chunks are streamed to Deepgram over a persistent connection
- Partial transcripts are emitted in near real time
- Silence detection is used to infer conversational turn boundaries

This streaming approach enables natural conversational flow and supports interruption handling.

### Expected Outcomes

- Live transcription visible while the user is speaking
- Latency low enough to support conversational interaction
- Clear separation between audio ingestion, transcription, and reasoning layers

These results validate the feasibility of using managed streaming STT for a meeting voice agent.

### Limitations (Spike Scope)

- Accuracy depends on microphone quality and background noise
- Speaker diarization is not enabled in this phase
- The implementation prioritizes latency over transcript post-processing

These limitations are acceptable within the scope of a feasibility-focused research spike.


Environment-specific secrets were managed via a `.env` file excluded from version control to follow security best practices.


## Streaming Speech-to-Text Implementation (Deepgram)

After validating local audio input/output, the next phase focused on implementing real-time, low-latency speech-to-text transcription using a managed streaming STT provider.

### Implementation Overview

A persistent WebSocket connection is established with the Deepgram streaming API. Microphone audio is captured locally in small, fixed-size chunks and streamed continuously to the STT service. Partial and final transcription events are received asynchronously while the user is speaking.

This approach avoids batch transcription and enables conversational turn-taking.

### Audio Configuration

- Sample rate: 16 kHz
- Channels: Mono
- Encoding: Linear PCM (16-bit)

This configuration aligns with common telephony and real-time voice system requirements.

### Runtime Behavior

- Partial transcripts are emitted while the user is speaking
- Final transcripts are produced once speech ends
- Silence detection is used to infer conversational boundaries

### Observations

- Live transcription latency was low enough to support interactive conversation
- Partial transcripts enabled immediate feedback during speech
- The system reliably transitioned from speaking to silence without manual triggers

This confirms the feasibility of using managed streaming STT for a meeting voice agent.

### Limitations

- Transcription accuracy varies with microphone quality and ambient noise
- Speaker diarization was not enabled in this phase
- The implementation prioritizes low latency over transcript post-processing

These tradeoffs are acceptable within the scope of a feasibility-focused research spike.

## Streaming Speech-to-Text (STT) — Deepgram WebSocket Implementation

After encountering compatibility challenges with higher-level SDK abstractions, real-time speech-to-text was implemented using Deepgram’s native realtime WebSocket API.

This approach provided a stable, SDK-independent integration path while preserving full support for low-latency streaming transcription.

### Implementation Overview

A persistent WebSocket connection is established with the Deepgram realtime transcription endpoint. Microphone audio is captured locally in small, fixed-size chunks and streamed continuously over the WebSocket connection. Transcription results are received asynchronously as JSON messages.

The system distinguishes between:
- **Partial transcripts** (interim results while the user is speaking)
- **Final transcripts** (emitted after speech endpoint detection)

### Audio Configuration

- Sample rate: **16 kHz**
- Channels: **Mono**
- Encoding: **Linear PCM (16-bit)**
- Chunk size: **~50 ms per audio frame**

This configuration aligns with common telephony and real-time voice system requirements and is compatible with meeting audio pipelines.

### Runtime Behavior

- Audio is streamed continuously during microphone capture
- Partial transcripts are emitted during speech
- Final transcripts are emitted once a silence boundary is detected
- Transcription output is processed in near real time

### Observed Latency Characteristics

- Partial transcription results exhibit an approximate **~1 second delay**
- Final transcripts are emitted shortly after speech completion
- Partial and final transcripts are often similar for short utterances

This behavior is consistent with real-time ASR systems that prioritize transcription stability over extremely aggressive interim updates.

### Findings

- Streaming transcription was successfully achieved
- Latency was acceptable for conversational interaction
- The system reliably distinguished speech and silence boundaries
- The WebSocket-based approach proved more stable than SDK abstractions during rapid prototyping

### Limitations

- Partial transcript latency may affect very fast turn-taking scenarios
- Speaker diarization was not enabled
- No post-processing (punctuation correction, summarization) was applied at this stage

These limitations are acceptable within the scope of a feasibility-focused research spike.

### Rationale for WebSocket-Based Integration

The final implementation uses Deepgram’s realtime WebSocket API directly rather than higher-level SDK abstractions. This decision was made to:
- avoid SDK version incompatibilities,
- reduce integration risk during the spike,
- retain explicit control over audio streaming and transcript handling.

This approach remains fully aligned with supported Deepgram APIs and reflects common practice in time-boxed research and proof-of-concept systems.

### Latency Considerations

Observed interim transcription latency (~1 second) is attributed to endpointing heuristics, network buffering, and stability-focused decoding strategies employed by streaming ASR systems. This tradeoff improves transcript accuracy and reduces jitter in conversational output. For a production system, latency can be further tuned by adjusting endpointing parameters or audio chunk sizes.

### STT Data Flow

Microphone Audio
   ↓
Local Audio Chunking (~50 ms)
   ↓
Realtime WebSocket Stream
   ↓
Deepgram ASR Engine
   ↓
Partial / Final Transcripts

## Large Language Model (LLM) Integration

Following successful real-time speech-to-text transcription, the next phase focused on integrating a Large Language Model (LLM) to generate conversational responses based on transcribed user input.

### Objective

The goal of this phase was to validate that:
- finalized speech transcripts can be passed to an LLM,
- the LLM can generate coherent, context-aware responses,
- the response latency iIntegration

The LLM component generates conversational responses based on transcribed speech. Key requirements were low latency, zero cost for prototyping, and sufficient quality for dialogue.

### Provider Evaluation

| Provider | Free Tier | Latency | Rate Limits | Notes |
|----------|-----------|---------|-------------|-------|
| Groq | Generous | Very fast (~100-500ms) | 30 req/min, 14.4k req/day | Llama 3, Mixtral models |
| Google Gemini | Available | Fast | Generous | Gemini 1.5 Flash |
| OpenAI | Paid only | Fast | Pay-per-token | Requires credit |
| Anthropic | Paid only | Fast | Pay-per-token | Similar to OpenAI |

### Decision: Groq (Llama 3.1)

Groq was selected for:
1. Latency-optimized infrastructure with Time-to-First-Token under 500ms
2. Zero-cost prototyping (14,400 requests/day free tier)
3. Proven conversational performance with Llama 3 models
4. No financial barrier or credit card requirement

**Capacity analysis:** A typical 20-turn conversation uses 10,000-20,000 tokens. Groq's free tier supports hundreds of full conversations daily, far exceeding prototype requirements
**Evaluation Criteria:**
- **Voice quality**: Natural-sounding, human-like voices
- **Latency**: Fast generation for real-time conversation
- **Cost**: Free tier availability for prototyping
- **Reliability**: Stable connections without frequent timeouts
- **Integration complexity**: Ease of implementation in Python

**Provider Comparison:**

| Provider | Free Tier | Voice Quality | Latency | Reliability | Notes |
|----------|-----------|---------------|---------|-------------|-------|
| **ElevenLabs** | ❌ Limited (10k chars/month) | ⭐⭐⭐⭐⭐ Excellent | Fast | ⚠️ Issues | Abuse detection blocked free tier |
| **Edge TTS** | ✅ Unlimited | ⭐⭐⭐⭐ Very Good | Fast | ❌ Unstable | WebSocket timeouts after multiple requests |
| **gTTS (Google)** | ✅ Unlimited | ⭐⭐⭐ Good | Moderate | ✅ Stable | Simple REST API, very reliable |
| **OpenAI TTS** | ❌ Paid (~$15/1M chars) | ⭐⭐⭐⭐ Very Good | Fast | ✅ Stable | Not suitable for free prototyping |

### TTS Implementation Journey

**Attempt 1: ElevenLabs**

ElevenLabs was initially selected for its industry-leading voice quality and natural-sounding speech synthesis. However, during testing, the free tier was blocked due to "unusual activity detection":

```
status_code: 401
message: 'Unusual activity detected. Free Tier usage disabled.'
```

**Issues encountered:**
- Free tier flagged due to VPN/proxy usage or multiple test requests
- Required paid subscription to continue
- Not viable for cIntegration

Three TTS providers were evaluated for voice quality, latency, cost, and reliability.

### Provider Comparison

| Provider | Free Tier | Voice Quality | Latency | Reliability | Notes |
|----------|-----------|---------------|---------|-------------|-------|
| ElevenLabs | Limited (10k chars/month) | Excellent | Fast | Issues | Free tier blocked |
| Edge TTS | Unlimited | Very Good | Fast | Unstable | WebSocket timeouts |
| gTTS (Google) | Unlimited | Good | Moderate | Stable | REST API, reliable |
| OpenAI TTS | Paid (~$15/1M chars) | Very Good | Fast | Stable | Not free |

### Implementation Journey

**ElevenLabs:** Initially selected for voice quality but free tier was blocked due to abuse detection after testing.

**Edge TTS:** Attempted next for unlimited free usage with Azure Neural voices, but encountered persistent WebSocket timeout issues after 3-5 requests.

**gTTS (Final Choice):** Selected for reliability despite moderate voice quality. Simple REST API with no connection issues, unlimited free usage, and proven stability for consecutive requests.

### Implementation

```
LLM Response → gTTS Generation → MP3 Audio → pydub Conversion → 
NumPy Array → sounddevice Playback → Audio Output
```

**Configuration:**
- Provider: gTTS (Google Text-to-Speech)
- Language: English (US)
- Format: MP3 converted to WAV
- Playback: Non-blocking (agent continues listening)

### Trade-offs

- Voice quality acceptable but not premium
- Generation latency 1-2 seconds for short responses
- Prioritized reliability and zero cost over premium quality
- Non-blocking playback maintains conversational flow

## Conclusion

This research spike successfully validates the feasibility of building a real-time conversational voice agent using managed services and zero-cost tooling.

### Key Achievements

- Real-time speech-to-text with acceptable latency (approximately 1 second for partial transcripts)
- Fast LLM response generation (100-500ms using Groq)
- Reliable text-to-speech synthesis (gTTS)
- Complete audio pipeline: listen → transcribe → reason → respond → speak
- Non-blocking architecture enabling natural conversation flow

### Technical Stack

- STT: Deepgram Nova-2 (WebSocket streaming)
- LLM: Groq Llama 3.1 8B Instant
- TTS: Google Text-to-Speech (gTTS)
- Audio: sounddevice, numpy, pydub, websockets

### Performance Summary

- Transcription latency: approximately 1 second
- LLM inference: 100-500ms
- TTS generation: 1-2 seconds
- Total response time: 2-4 seconds (acceptable for conversation)

### Cost Analysis

All components utilize free tiers:
- Deepgram: $200 initial credit
- Groq: 14,400 requests/day, 30 requests/minute
- gTTS: Unlimited
- Total development cost: $0

### Limitations

- Moderate TTS voice quality (acceptable for prototyping only)
- No speaker diarization
- Single language support (English)
- No conversation history tracking
- No meeting platform integration

### Future Enhancements

Potential next steps outside current scope:
- Virtual audio cable integration for meeting participation
- Wake word activation ("Hey assistant")
- Multi-speaker diarization
- Conversation memory and context retention
- Improved TTS quality (upgrade to paid service)
- Cross-platform support (macOS, Linux)
- Multi-language support

This spike confirms that a functional conversational voice agent can be built rapidly and cost-effectively using current managed AI services. The total implementation time was approximately 2-3 days with zero infrastructure or API costs during development.

This completes the full conversational pipeline