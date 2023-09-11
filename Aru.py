import vosk
import sounddevice as sd
import queue
import json
import commands
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import os
import azure.cognitiveservices.speech as speechsdk
from work import Aru

aru = Aru()
q = queue.Queue()
model = vosk.Model('vosk-model-kz-0.15')
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                       region=os.environ.get('SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_voice_name = 'kk-KZ-AigulNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def recognize(data, vectorizer, clf):
    name_aru = commands.voice_start.intersection(data.split())
    if not name_aru:
        return
    data.replace(list(name_aru)[0], '')
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]

    answer = str(answer)
    func_name = answer.split()[0]

    speech_synthesizer.speak_text_async(answer.replace(func_name, '')).get()
    func = 'aru.' + func_name + '()'
    exec(func)


def main():
    vectorizer = CountVectorizer()

    vectors = vectorizer.fit_transform(list(commands.data_set.keys()))

    clf = LogisticRegression()
    clf.fit(vectors, list(commands.data_set.values()))

    del commands.data_set

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0], dtype='int16', channels=1,
                           callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf)


if __name__ == '__main__':
    main()
