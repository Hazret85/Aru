import vosk
import sounddevice as sd
import queue

q = queue.Queue()
model = vosk.Model('vosk-model-kz-0.15')
device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])


def callback(indata, frames, time, status):
    q.put(bytes(indata))


with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0], dtype='int16', channels=1,
                       callback=callback):
    rec = vosk.KaldiRecognizer(model, samplerate)

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            print(rec.Result())
