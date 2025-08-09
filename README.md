# Voice_Bot: Real-Time Speech-to-Speech (STS) Assistant

This project is a **real-time Speech-to-Speech (STS) VoiceBot** that listens to your voice, transcribes it using Google Speech-to-Text, generates a response with OpenAI GPT, and speaks the reply using ElevenLabs TTS.

---

## Features

- **Real-time microphone input** using PyAudio
- **Streaming speech-to-text** with Google Cloud Speech-to-Text
- **Conversational AI** using OpenAI's GPT models
- **Streaming text-to-speech** with ElevenLabs
- **Multithreaded pipeline** for low-latency interaction
- **Environment variable support** for API keys
- **Works on Windows** (tested), should work on Mac/Linux with minor changes

---

## Requirements

- Python 3.8+
- Google Cloud service account credentials for STT
- [OpenAI API key](https://platform.openai.com/)
- [ElevenLabs API key](https://elevenlabs.io/)
- `ffmpeg` (with `ffplay`) installed and available in your `PATH`
- Microphone

### Python Dependencies

Install with pip:
```
pip install sounddevice numpy python-dotenv openai elevenlabs google-cloud-speech pyaudio
```

---

## Setup

1. **Clone this repository** and enter the folder.

2. **Create a `.env` file** in the project root with your API keys:
    ```
    OPENAI_API_KEY=your_openai_key
    ELEVENLABS_API_KEY=your_elevenlabs_key
    ```

3. **Place your Google Cloud credentials** file (e.g., `googleCredentials.json`) in the project root.

4. **Ensure `ffplay` is available** (part of ffmpeg) and added to your `PATH`.

5. **Run the bot:**
    ```bash
    python sts.py
    ```

---

## Usage

- Speak into your microphone.
- The bot will transcribe, generate a reply, and speak back.
- Type or press Enter in the terminal to stop the bot.

---

## Notes

- **Latency:** The current pipeline has a 3–4 second response time due to API and processing delays.
- **Feedback Loop:** Use headphones to avoid the bot picking up its own voice.
- **Development:** This is a work-in-progress. Expect breaking changes and improvements.

---

## Troubleshooting

- **No audio output:** Ensure `ffplay` is installed and in your `PATH`.
- **No response from bot:** Check your API keys, credentials, and microphone.
- **Bot repeats itself:** Use headphones and check your input device settings.
- **Google STT errors:** Make sure your Google credentials are valid and billing is enabled.

---