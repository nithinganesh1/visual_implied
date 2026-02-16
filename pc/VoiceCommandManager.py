import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer


class VoiceCommandManager:

    def __init__(self, model_path="vosk-model-small-en-us-0.15"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))

    def listen(self):
        print("Listening for command...")

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    command = result.get("text", "")
                    if command:
                        return command
