# Voice_Bot: In-Development Speech-to-Speech (STS) Model

This project is an **in-development real-time Speech-to-Speech (STS) VoiceBot** that listens to your voice, transcribes it, generates a response using an LLM (OpenAI), and speaks the reply using ElevenLabs TTS. It uses Deepgram for streaming speech-to-text.

---

## Features

- **Real-time microphone input**
- **Streaming speech-to-text** with Deepgram
- **Conversational AI** using OpenAI's GPT models
- **Streaming text-to-speech** with ElevenLabs
- **Multithreaded pipeline** for low-latency interaction
- **Environment variable support** for API keys

---

## Requirements

- Python 3.8+
- [Deepgram API key](https://console.deepgram.com/)
- [OpenAI API key](https://platform.openai.com/)
- [ElevenLabs API key](https://elevenlabs.io/)
- Linux (tested), should work on Mac/Windows with minor changes
- `ffmpeg` (with `ffplay`) installed and available in your `PATH`

### Python Dependencies

Typical requirements:
- `sounddevice`
- `numpy`
- `python-dotenv`
- `deepgram-sdk`
- `openai`
- `elevenlabs`

---

## Setup

1. **Clone this repository** and enter the folder.

2. **Create a `.env` file** in the project root with your API keys:

    ```
    OPENAI_API_KEY=your_openai_key
    ELEVENLABS_API_KEY=your_elevenlabs_key
    DEEPGRAM_API_KEY=your_deepgram_key
    ```

3. **Ensure `ffplay` is available** (part of ffmpeg)

4. **Run the bot:**

    ```bash
    python3 sts.py
    ```

---

## Usage

- Speak into your microphone.
- The bot will transcribe, generate a reply, and speak back.
- Press Enter to stop the bot.

---

## Notes

- **Feedback Loop:** Use headphones to avoid the bot picking up its own voice.
- **Latency:** The pipeline is multithreaded for responsiveness, but actual latency depends on network and API speed.
- **Development:** This is a work-in-progress. Expect breaking changes and improvements.

---

## Troubleshooting

- **Deepgram 401 errors:** Check your API key and `.env` file.
- **No audio output:** Ensure `ffplay` is installed and in your `PATH`.
- **Bot repeats itself:** Use headphones and check your input device settings.