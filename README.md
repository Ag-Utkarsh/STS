# Real-Time Speech-to-Speech (STS)
***

## Overview

This project delivers a **real-time speech-to-speech (STS) conversation model** using [Pipecat](https://docs.pipecat.ai/)—a powerful Python framework for AI pipelines—integrated with leading speech recognition, large language model (LLM), and text-to-speech (TTS) services. This solution supports fast, natural back-and-forth spoken dialogues with context awareness, VAD-based audio control, and streaming responses.

*While I previously built a similar model by independently linking STT, LLM, and TTS modules. You can find the older architecture in the commit history for understanding.*

***

## Features

- **Real-time speech-to-speech interaction**: Users converse naturally, and the bot speaks responses instantly.
- **Low-latency streaming**: Average response latency is ~2.5s, the first response takes time; the goal is to achieve ~1s latency for first outputs.
- **Interruption handling**: Users can interrupt with new input, and the pipeline adapts its response.
- **Dynamic context**: Maintains conversation flow using context aggregation.
- **Modular Pipecat pipeline**: Simplifies complex integrations and provides observability.
- **Pluggable components**:
  - Deepgram for ASR (STT)
  - Google Gemini LLM
  - ElevenLabs for TTS
  - Silero for VAD
- **WebRTC-based audio transport** using SmallWebRTCTransport
- **Voice user interface**: (UI to be improved—see current limitations)

***

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Ag-Utkarsh/STS.git
cd STS
```

### 2. Install Dependencies

> **Note:** It’s recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file with your API keys:

```dotenv
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GEMINI_API_KEY=your_gemini_key
```

### 4. Run the Bot

```bash
python sts.py
```

### 5. Connect and test

Open http://localhost:7860/client in your browser and click Connect(top right corner, and give the microphone permission) to start talking to your bot.

***

## Pipeline Structure

The speech-to-speech model is built using Pipecat’s pipeline abstraction, combining the following components:

```python
Pipeline(
    transport.input(),          # Raw audio in from user
    rtvi,                      # Real-time voice interaction processing
    stt,                       # Speech-to-text (Deepgram)
    context_aggregator.user(), # Aggregate LLM context (user side)
    llm,                       # LLM (Google Gemini)
    tts,                       # Text-to-speech (ElevenLabs)
    transport.output(),        # Audio back to user
    context_aggregator.assistant() # Aggregated assistant utterances
)
```

***

## Current Limitations & Roadmap

- **Custom UI Needed**: While audio interaction works, a polished **voice UI kit** or frontend is still pending. Refer to community kits for inspiration.
- **First sentence control**: At present, customizing the bot’s first utterance is limited; Pipecat’s system prompt currently manages this.
- **Latency**: Average response latency is 2.5s at current configuration. Target: sub-1s response time for optimal interactivity.
- **First Message**: Don't have control over the first message.

***

## Contribution & Feedback

If you have ideas for improving the UI, reducing latency, or adding new integrations, contributions are welcome!.

***

## References

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Pipecat Quickstart](https://github.com/pipecat-ai/pipecat-quickstart/tree/main)
- Deepgram, ElevenLabs, Google Gemini API guides

***

**Give it a try—your voice assistant is now just a conversation away!**