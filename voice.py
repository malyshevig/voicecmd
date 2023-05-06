import json, queue, logging

from vosk import Model, KaldiRecognizer
import pyaudio

logging.basicConfig(level = logging.DEBUG, format='%(process)d-%(levelname)s-%(message)s')


class SpeechRecognizer:
    def __init__(self):
        self.model = Model(lang="ru")
        self.rec = KaldiRecognizer(self.model, 48000)
        self.p = pyaudio.PyAudio()
        self.q = queue.Queue()

    def __iter__(self):
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            frames_per_buffer=8000
        )
        self.stream.start_stream()

        return self

    def __next__(self):
        dt = self.stream.read(4000, exception_on_overflow=True)
        if len(dt) == 0 and self.q.empty():
            raise StopIteration

        res = self.rec.AcceptWaveform(dt)
        txt = ""

        if res:
            s = json.loads(self.rec.Result())
            txt: str = s["text"]
        else:
            pass

        for w in txt.split (" "):
            if len(w) > 0:
                self.q.put(w)

        if self.q.empty():
            return None
        else:
            return self.q.get()

    def close(self):
        self.stream.close()


def main ():
    sr = SpeechRecognizer()
    try:

        it = iter(sr)

        while True:
            w = next(it)
            if w:
                print (f"{w}")
            if w == "стоп":
                break
    finally:
        sr.close()


if __name__ == "__main__":
    main()