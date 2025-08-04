from dotenv import load_dotenv
import os
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone

load_dotenv()

deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

def speechRecognition():
    try:
        dg_connection = deepgram.listen.live.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"USER:\n {sentence}")

        def on_error(self, error):
            print(f"ERROR: Problem with transcription.\n {error}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
        )

        dg_connection.start(options)

        microphone = Microphone(dg_connection.send)
        microphone.start()

        # Wait until finished
        input("Press Enter to stop recording...\n\n")

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"ERROR: Exception with transcription.\n {e}")
        return

if __name__ == "__main__":
    speechRecognition()