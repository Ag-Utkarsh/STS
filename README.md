# Voice_Bot: Real-Time Speech-to-Speech (STS) Assistant

This project is a **real-time Speech-to-Speech (STS) VoiceBot** that listens to your voice, transcribes it using Google Speech-to-Text, generates a response with OpenAI GPT, and speaks the reply using ElevenLabs TTS.

---

## Pipeline Overview

1. **Microphone Input:**  
   Audio is captured in real time from your microphone using PyAudio.

2. **Streaming Speech-to-Text (STT):**  
   The audio stream is sent to Google Cloud Speech-to-Text, which transcribes your speech as you talk.

3. **Conversational AI (LLM):**  
   The transcribed text is sent to OpenAI's GPT models (via API), which generate a short, crisp response.

4. **Streaming Text-to-Speech (TTS):**  
   The response is sent to ElevenLabs, which streams back high-quality speech audio.

5. **Audio Playback:**  
   The bot's reply is played back to you immediately.

All steps are pipelined and multithreaded for low-latency, natural-feeling interaction.

---

## Why Use Cloud APIs Instead of Open-Source Models?

My laptop is low-end and cannot run GPU-based open-source models efficiently.  
By using Google, OpenAI, and ElevenLabs APIs, I achieve **very low latency** (2–4 seconds per interaction, and sometimes 1–2 seconds for short answers or after the system is warmed up).  
This makes the experience much more responsive than running local models on limited hardware.

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
- 'mpv' player
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

## Current Limitations

- **No mid-interruption handling:**  
  The model cannot handle user interruptions while the bot is speaking. If you start talking while the bot is responding, it will not stop and listen.
- **Silence triggers:**  
  As soon as there is a small silence in your speech, the model assumes you are done and starts processing.
- **No UI yet:**  
  Currently, the bot is terminal-based. A UI is planned for future versions.

---

## Notes

- **Latency:** The current pipeline achieves 2–4 seconds response time (1–2 seconds for short answers or after warm-up).
- **Feedback Loop:** Use headphones to avoid the bot picking up its own voice.
- **Development:** This is a work-in-progress. Expect breaking changes and improvements.

---

## Troubleshooting

- **No audio output:** Ensure `ffplay` is installed and in your `PATH`.
- **No response from bot:** Check your API keys, credentials, and microphone.
- **Bot repeats itself:** Use headphones and check your input device settings.
- **Google STT errors:** Make sure your Google credentials are valid and billing is enabled.

---