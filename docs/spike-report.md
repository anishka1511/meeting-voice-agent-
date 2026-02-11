# Meeting Voice Agent (MVA) — Research Spike

This research spike explores the feasibility of building a Meeting Voice Agent (MVA) that can join online meetings via audio, participate in real-time voice conversations with humans, and persist post-call artifacts such as transcripts and audio recordings.

The goal of this spike is not production readiness, but to validate:
- real-time conversational feasibility,
- viable meeting entry methods,
- system architecture,
- and cost implications.

## Scope

- Real-time audio input and output
- Streaming speech-to-text (STT)
- LLM-based response generation
- Streaming text-to-speech (TTS)
- Turn-taking and interruption handling
- Transcript and audio capture

## Non-Goals (for this spike)

- Full WebRTC bot participation
- Video handling
- UI / frontend
- Perfect diarization
- Production-grade scaling

## Development Environment

- OS: Windows 10
- Language: Python 3.11
- Environment: Python virtual environment (venv)

Key libraries:
- sounddevice (audio I/O)
- numpy (audio buffers)
- streaming STT provider
- TTS provider
- LLM API

## Audio I/O Validation

The first validation step was to confirm reliable microphone input and speaker output on the development environment.

A local audio loopback test was implemented:
- Record microphone input for a fixed duration
- Immediately play the recorded audio back

Result:
- Microphone access confirmed
- Speaker output confirmed
- Audio latency acceptable for conversational use

This validates that the system can support real-time audio pipelines.

## Real-Time Speech-to-Text (STT)

This phase evaluates the feasibility of low-latency, streaming speech recognition for a real-time conversational voice agent.

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
- the response latency is acceptable for conversational use.

This phase does not yet include speech synthesis or interruption handling.

### LLM Provider Selection

Multiple LLM providers were evaluated based on the following criteria:

**Evaluation Criteria:**
- **Latency**: Response time directly impacts conversational naturalness
- **Cost**: Free tier availability for development and testing
- **Request limits**: Sufficient quota for iterative prototyping
- **Quality**: Coherent, context-aware responses

**Provider Comparison:**

| Provider | Free Tier | Latency | Rate Limits | Notes |
|----------|-----------|---------|-------------|-------|
| **Groq** | ✅ Generous | ⚡ Extremely fast (~100-500ms TTFT) | ~30 req/min, ~14.4k req/day | Llama 3, Mixtral models |
| **Google Gemini** | ✅ Available | ⚡ Fast | Generous free tier | Gemini 1.5 Flash |
| **OpenAI** | ❌ Paid only | Fast | Pay-per-token | Requires $5+ credit |
| **Anthropic Claude** | ❌ Paid only | Fast | Pay-per-token | Similar pricing to OpenAI |

**Decision: Groq (Llama 3)**

Groq was selected as the LLM provider for this research spike for the following reasons:

1. **Latency-optimized infrastructure**: Groq's custom LPU (Language Processing Unit) architecture delivers industry-leading inference speeds with Time-to-First-Token (TTFT) typically under 500ms, critical for real-time voice interaction.

2. **Zero-cost prototyping**: The free tier provides ~14,400 requests/day and ~30 requests/minute, which is effectively unlimited for single-developer research and well beyond the throughput requirements of a conversational voice agent prototype.

3. **Conversational suitability**: Groq hosts Meta's Llama 3 models, which are proven for dialogue applications and produce coherent, concise responses suitable for voice interaction.

4. **No financial barrier**: Unlike OpenAI and Anthropic, Groq does not require upfront payment or credit card registration, enabling immediate iteration without budget approval.

**Capacity Analysis:**

For a typical voice conversation:
- **~20 turns** (back-and-forth exchanges)
- **~500-1000 tokens per turn** (transcript + context + response)
- **Total: ~10,000-20,000 tokens per conversation**

With Groq's free tier limits:
- **Hundreds of full conversations per day** are feasible
- **30 requests/minute** exceeds real-time conversational demand (humans speak slower than 30 turns/min)

This makes Groq ideal for validating conversational feasibility without cost or quota concerns.

**Alternative Considered:**

Google Gemini 1.5 Flash was a close second choice, offering a free tier with competitive latency. However, Groq's extreme speed advantage and purpose-built inference infrastructure made it the optimal choice for a latency-sensitive voice application.

## Text-to-Speech (TTS) Integration

Following successful STT and LLM integration, the next critical component was adding text-to-speech to enable the agent to respond vocally, completing the full conversational loop.

### TTS Provider Evaluation

Multiple TTS providers were evaluated based on the following criteria:

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
- Not viable for cost-free prototyping

**Verdict:** Abandoned due to free tier restrictions.

---

**Attempt 2: Edge TTS (Microsoft)**

Edge TTS was selected as the second option, offering unlimited free usage with high-quality Microsoft Azure Neural voices (e.g., "en-US-AriaNeural").

**Initial implementation:**
- Used WebSocket streaming API
- Good voice quality
- Fast generation

**Issues encountered:**
- WebSocket connection timeouts after 3-5 requests:
  ```
  Connection timeout to host wss://speech.platform.bing.com/...
  ```
- Rate limiting on Microsoft's free service
- Unreliable for sustained conversational testing
- Required retry logic that added complexity

**Verdict:** Abandoned due to connection stability issues.

---

**Attempt 3: gTTS (Google Text-to-Speech) ✅ Final Choice**

gTTS was selected as the final TTS provider after stability issues with ElevenLabs and Edge TTS.

**Decision rationale:**

1. **Reliability**: Simple REST API with no WebSocket timeouts
2. **Unlimited free usage**: No rate limits or abuse detection
3. **Sufficient quality**: Voice quality is acceptable for prototyping (not premium, but clear and understandable)
4. **Simplicity**: Easy integration with minimal code
5. **Proven stability**: Handles multiple consecutive requests without connection issues

**Implementation approach:**
- Generate MP3 audio using gTTS
- Convert to WAV format using pydub
- Play audio using sounddevice in non-blocking mode
- Agent continues listening while speaking (enables natural conversation flow)

### TTS Integration Architecture

```
LLM Response (text)
   ↓
gTTS Generation (REST API)
   ↓
MP3 Audio Data
   ↓
pydub Conversion (MP3 → WAV)
   ↓
NumPy Audio Array
   ↓
sounddevice Playback (non-blocking)
   ↓
Audio Output (speakers)
```

### Trade-offs and Limitations

**Voice Quality:**
- gTTS voice quality is good but not premium (compared to ElevenLabs or OpenAI TTS)
- Acceptable for research spike and feasibility validation
- Production system may require upgrading to paid TTS service

**Latency:**
- gTTS generation is moderately fast (~1-2 seconds for short responses)
- Slower than streaming TTS options but acceptable for conversational use
- Non-blocking playback ensures agent remains responsive

**Reliability vs. Quality Trade-off:**
- Prioritized reliability and zero-cost over premium voice quality
- This decision aligns with spike objectives: validate feasibility, not production polish

### Lessons Learned

1. **Free tier limitations are real**: Premium providers (ElevenLabs) aggressively enforce usage limits
2. **WebSocket stability matters**: Edge TTS's timeout issues made it unsuitable for sustained testing
3. **Simplicity wins for prototyping**: gTTS's REST API proved more reliable than WebSocket-based solutions
4. **Non-blocking audio is critical**: Playing TTS audio without blocking the event loop prevents WebSocket timeouts and maintains conversational flow

### Final TTS Configuration

- **Provider**: gTTS (Google Text-to-Speech)
- **Language**: English (US)
- **Output format**: MP3 (converted to WAV for playback)
- **Playback mode**: Non-blocking (agent listens while speaking)
- **Cost**: $0 (unlimited free usage)

This configuration successfully enables full voice conversation: microphone → STT → LLM → TTS → speakers.