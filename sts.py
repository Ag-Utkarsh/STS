import os
import threading
import queue
import re
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingEvents,
    BeginEvent,
    TurnEvent,
    TerminationEvent,
    StreamingError,
)

# Load environment variables (API keys, etc.)
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")  # Set this in your .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

SAMPLE_RATE = 16000
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
SYSTEM_PROMPT = "You are a helpful assistant. Give short, crisp answers."

openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def get_llm_reply_streaming(conversation, buffer_chars=50):
    buffer = ""
    response_stream = openai_client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=conversation[-10:],
        temperature=0.6,
        max_tokens=280,
        stream=True
    )
    for chunk in response_stream:
        content_piece = chunk.choices[0].delta.content
        if content_piece:
            buffer += content_piece
            if len(buffer) >= buffer_chars or buffer.endswith(('.', '!', '?')):
                yield buffer
                buffer = ""
    if buffer.strip():
        yield buffer

def speak_streaming(text):
    try:
        audio_stream = elevenlabs_client.text_to_speech.stream(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128"
        )
        print("Streaming TTS playback started...")
        stream(audio_stream)
        print("TTS playback complete.")
    except Exception as e:
        print("TTS streaming error:", e)

def main():
    print("Initializing Real-Time VoiceBot...")
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    stop_event = threading.Event()

    def on_transcript(transcript):
        # Called when a transcript is received from AssemblyAI
        conversation.append({"role": "user", "content": transcript})
        print(f"YOU SAID: {transcript}")
        print("THINKING...")

        def run_tts_stream():
            for phrase in get_llm_reply_streaming(conversation):
                print(f"\nBOT: {phrase}\n")
                conversation.append({"role": "assistant", "content": phrase})
                speak_streaming(phrase)

        threading.Thread(target=run_tts_stream, daemon=True).start()

    client = StreamingClient(
        StreamingClientOptions(api_key=ASSEMBLYAI_API_KEY)
    )

    def on_begin(self, event: BeginEvent):
        print(f"Session started: {event.id}")

    def on_turn(self, event: TurnEvent):
    # Only act on the final, formatted transcript
        if event.end_of_turn and getattr(event, 'turn_is_formatted', False) and event.transcript.strip():
            print(f"Final transcript: {event.transcript}")
            on_transcript(event.transcript)
    # You may optionally print partial/unformatted here for debugging, but do not use them


    def on_terminated(self, event: TerminationEvent):
        print(f"Session terminated: {event.audio_duration_seconds} seconds of audio processed")
        stop_event.set()

    def on_error(self, error: StreamingError):
        print(f"Error occurred: {error}")
        stop_event.set()

    # Register event handlers
    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    def stream_thread():
        client.connect(StreamingParameters(sample_rate=SAMPLE_RATE, format_turns=True))
        try:
            client.stream(aai.extras.MicrophoneStream(sample_rate=SAMPLE_RATE))
        finally:
            client.disconnect(terminate=True)

    stt_thread = threading.Thread(target=stream_thread)
    stt_thread.start()

    try:
        input("Press Enter to stop...\n")
    except KeyboardInterrupt:
        print("Manual Interrupt.")
    finally:
        stop_event.set()
        stt_thread.join()
        print("VoiceBot shut down.")

if __name__ == "__main__":
    main()
