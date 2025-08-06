import os
import threading
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import queue
import re
from google.cloud import speech
import pyaudio
import webrtcvad  # New: Import VAD for speech/silence detection
import time


# Load environment variables
load_dotenv()
os.environ["PATH"] += os.pathsep + r"C:\Users\Chotu chapri\Downloads\mpv-x86_64-20250730-git-a6f3236"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"googleCredentials.json"  # Update path as needed


# Audio input config
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 30   # Smaller chunks for VAD (10, 20, 30ms allowed)
FRAMES_PER_BUFFER = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)


# VAD config
VAD_MODE = 1  # 0=aggressive, 3=relaxed; tune as needed
SILENCE_TIMEOUT_S = 1.2  # 1.5 seconds of silence to end utterance

# Voice & system prompt
ELEVENLABS_VOICE_ID = "nbOs83cg1fbwnhG6tlRB"
SYSTEM_PROMPT = "You are a helpful voice assistant."


# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))



############################
# Google STT Microphone Stream With VAD Enhancement
############################


class MicrophoneStream:
    def __init__(self, rate=SAMPLE_RATE, chunk=FRAMES_PER_BUFFER):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self.vad = webrtcvad.Vad(VAD_MODE)


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
        # VAD variables
        silence_seconds = 0
        frame_duration_s = CHUNK_DURATION_MS / 1000.0


        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            is_speech = self.vad.is_speech(chunk, self._rate)


            if is_speech:
                silence_seconds = 0
            else:
                silence_seconds += frame_duration_s


            yield chunk


            # If we have hit 2 seconds silence, treat as end of utterance (signal with None)
            if silence_seconds >= SILENCE_TIMEOUT_S:
                yield None
                silence_seconds = 0  # Reset for next utterance



#########################
# LLM + Streaming TTS
#########################


def get_llm_reply(conversation, result_dict):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=conversation[-10:],
            temperature=0.6,
            max_tokens=260,
        )
        result_dict["reply"] = response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM ERROR:", e)
        result_dict["reply"] = ""



# New: Listen for user speech to interrupt TTS with a separate VAD stream
def listen_for_user_interrupt_during_tts(stop_event):
    vad = webrtcvad.Vad(VAD_MODE)
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )
    try:
        while not stop_event.is_set():
            data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
            if vad.is_speech(data, SAMPLE_RATE):
                print("INTERRUPT: User started speaking during TTS.")
                stop_event.set()  # Signal TTS playback to stop
                break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


def speak_streaming(text):
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=listen_for_user_interrupt_during_tts, args=(stop_event,))
   
    try:
        audio_stream = elevenlabs_client.text_to_speech.stream(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        print("STREAMING TTS AUDIO...")
        listener_thread.start()


        # Pass whole generator to stream() - let ElevenLabs handle playback
        stream(audio_stream)  # This plays entire stream automatically
       
        print("TTS PLAYBACK COMPLETED.")
   
    except Exception as e:
        print("TTS STREAMING ERROR:", e)
    finally:
        stop_event.set()
        listener_thread.join()




############################
# Main VoiceBot Logic
############################


def main():
    print("INITIALIZING VOICEBOT.")


    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    stop_event = threading.Event()


    # Timing state (shared between threads)
    phase_times = {
        "stt_start": None,
        "stt_end": None,
        "llm_start": None,
        "llm_end": None,
        "tts_start": None,
        "tts_end": None,
    }


    def print_metrics():
        stt_time = (phase_times["stt_end"] - phase_times["stt_start"]) if phase_times["stt_start"] and phase_times["stt_end"] else None
        llm_time = (phase_times["llm_end"] - phase_times["llm_start"]) if phase_times["llm_start"] and phase_times["llm_end"] else None
        tts_time = (phase_times["tts_end"] - phase_times["tts_start"]) if phase_times["tts_start"] and phase_times["tts_end"] else None
        print("\n--- Phase Timings ---")
        if stt_time is not None:
            print(f"STT Transcription: {stt_time:.2f} s")
        if llm_time is not None:
            print(f"LLM Response:      {llm_time:.2f} s")
        if tts_time is not None:
            print(f"TTS Generation:    {tts_time:.2f} s")
        print("---------------------\n")


    def on_transcript(sentence):
        phase_times["stt_end"] = time.time()
        print(f"THINKING... (STT took {phase_times['stt_end'] - phase_times['stt_start']:.2f} s)")
        conversation.append({"role": "user", "content": sentence})


        # Threaded LLM inference
        llm_result = {}
        def llm_with_timing():
            phase_times["llm_start"] = time.time()
            get_llm_reply(conversation, llm_result)
            phase_times["llm_end"] = time.time()
        llm_thread = threading.Thread(target=llm_with_timing)
        llm_thread.start()


        def run_tts_after_llm():
            llm_thread.join()
            reply = llm_result.get("reply", "")
            if not reply:
                print("NO REPLY FROM LLM.")
                return


            print(f"\n🤖 BOT: {reply}\n")
            conversation.append({"role": "assistant", "content": reply})


            def tts_with_timing():
                phase_times["tts_start"] = time.time()
                speak_streaming(reply)
                phase_times["tts_end"] = time.time()
                print_metrics()
                # Reset for next turn
                for k in phase_times:
                    phase_times[k] = None


            # Now stream TTS audio in a thread, with interruption detection
            tts_thread = threading.Thread(target=tts_with_timing, daemon=True)
            tts_thread.start()


        threading.Thread(target=run_tts_after_llm, daemon=True).start()


    def google_stt_stream():
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=False
        )


        with MicrophoneStream(SAMPLE_RATE, FRAMES_PER_BUFFER) as stream:
            audio_generator = stream.generator()
            buffer = b''


            for content in audio_generator:
                if content is None:
                    if buffer:
                        phase_times["stt_start"] = time.time()  # Start STT timing here
                        requests = [speech.StreamingRecognizeRequest(audio_content=buffer)]
                        responses = client.streaming_recognize(streaming_config, iter(requests))
                        for response in responses:
                            if not response.results:
                                continue
                            result = response.results[0]
                            if not result.alternatives:
                                continue
                            transcript = result.alternatives[0].transcript
                            if transcript.strip():
                                print(f"YOU SAID: {transcript}")
                                on_transcript(transcript)
                            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                                print("EXITING")
                                stop_event.set()
                                return
                        buffer = b''
                    continue


                buffer += content


    stt_thread = threading.Thread(target=google_stt_stream)
    stt_thread.start()


    try:
        input("PRESS ENTER TO STOP...\n")
    except KeyboardInterrupt:
        print("MANUAL INTERRUPT.")
    finally:
        stop_event.set()
        stt_thread.join()
        print("VOICEBOT SHUT DOWN.")


if __name__ == "__main__":
    main()