# Voice_Bot: In-Development Speech-to-Speech (STS) Model

This project is an **in-development real-time Speech-to-Speech (STS) VoiceBot** that listens to your voice, transcribes it using **Google Cloud Speech-to-Text**, generates a response using an LLM (OpenAI), and speaks the reply using ElevenLabs TTS.

---

## Features

- **Real-time microphone input**
- **Streaming speech-to-text** with Google Cloud Speech-to-Text
- **Conversational AI** using OpenAI's GPT models
- **Streaming text-to-speech** with ElevenLabs
- **Multithreaded pipeline** for low-latency interaction
- **Environment variable support** for API keys

---

## Requirements

- Python 3.8+
- [Google Cloud Speech-to-Text credentials](https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries)
- [OpenAI API key](https://platform.openai.com/)
- [ElevenLabs API key](https://elevenlabs.io/)
- Linux, Mac, or Windows (tested on Windows)
- `ffmpeg` (with `ffplay`) and/or `mpv` installed and available in your `PATH`

### Python Dependencies

Typical requirements:
- `sounddevice`
- `numpy`
- `python-dotenv`
- `google-cloud-speech`
- `openai`
- `elevenlabs`
- `pyaudio`

---

## Setup

1. **Clone this repository** and enter the folder.

2. **Create a `.env` file** in the project root with your API keys:

    ```
    OPENAI_API_KEY=your_openai_key
    ELEVENLABS_API_KEY=your_elevenlabs_key
    ```

3. **Set up Google Cloud credentials:**
    - Download your service account JSON from Google Cloud Console.
    - Place it in the project root (e.g., `googleCredentials.json`).
    - The script sets `GOOGLE_APPLICATION_CREDENTIALS` to this file automatically.

4. **Ensure `ffplay` or `mpv` is available:**
    - Download [ffmpeg](https://ffmpeg.org/) and/or [mpv](https://mpv.io/).
    - Add the folder containing `ffplay.exe` or `mpv.exe` to your `PATH`, or edit the script to append the path at runtime.
  ```

---

## Usage

- Speak into your microphone.
- The bot will transcribe, generate a reply, and speak back.
- Press Enter to stop the bot.

---

## Notes

- **Latency:** The pipeline is multithreaded for responsiveness, but actual latency is currently **4–5 seconds** per turn (mainly due to API and network speed).
- **No timeout:** As soon as silence is detected in your speech, the bot immediately starts the next phase (transcription → LLM → TTS), so you don't have to wait for a fixed timeout.
- **No barge-in:** The bot does **not** capture or process user speech while it is speaking its response. You must wait for the bot to finish before speaking again.
- **Feedback Loop:** Use headphones to avoid the bot picking up its own voice.
- **Development:** This is a work-in-progress. Expect breaking changes and improvements.

---

## Troubleshooting

- **Google credentials error:** Make sure your service account JSON is present and the path is set correctly.
- **No audio output:** Ensure `ffplay` or `mpv` is installed and in your `PATH`.
- **Bot repeats itself:** Use headphones and check your input device settings.

---