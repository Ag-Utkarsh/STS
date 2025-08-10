import os
import threading
import queue
import re
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import pyaudio
from google.cloud import speech

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"googleCredentials.json"

SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = int(SAMPLE_RATE * 400 / 1000)
ELEVENLABS_VOICE_ID = "nbOs83cg1fbwnhG6tlRB"
SYSTEM_PROMPT = "You are a helpful assistant. Give short, crisp answers."

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

class MicrophoneStream:
    def __init__(self, rate=SAMPLE_RATE, chunk=FRAMES_PER_BUFFER):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            yield chunk

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

    def on_transcript(sentence):
        conversation.append({"role": "user", "content": sentence})
        print("THINKING...")
        # Stream LLM response in buffered chunks
        def run_tts_stream():
            for phrase in get_llm_reply_streaming(conversation):
                print(f"\nBOT: {phrase}\n")
                conversation.append({"role": "assistant", "content": phrase})
                speak_streaming(phrase)
        threading.Thread(target=run_tts_stream, daemon=True).start()

    def google_stt_stream():
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=False
        )
        with MicrophoneStream(SAMPLE_RATE, FRAMES_PER_BUFFER) as stream_mic:
            audio_generator = stream_mic.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if result.is_final and transcript.strip():
                    print(f"YOU SAID: {transcript}")
                    on_transcript(transcript)
                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    print("Exiting..")
                    stop_event.set()
                    break

    stt_thread = threading.Thread(target=google_stt_stream)
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
