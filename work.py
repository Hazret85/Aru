import os
import azure.cognitiveservices.speech as speechsdk
import datetime
import requests
from bs4 import BeautifulSoup
import random
from yeelight import Bulb


class Aru:
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                           region=os.environ.get('SPEECH_REGION'))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name = 'kk-KZ-AigulNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    bulb = Bulb('192.168.100.12')

    def weather(self):
        req = requests.get('https://kaz.tengrinews.kz/weather/semey/day/')
        soup = BeautifulSoup(req.text, 'lxml')

        temp = soup.find(class_='temp').text.replace('\n', '')
        value = soup.findAll(class_='testimony-item')
        sky = ''
        for el in value:
            sky = el.text
        if temp.startswith('-'):
            weath = 'далада {} градус, нөлден төмен, {}!'.format(temp, sky)
        else:
            weath = 'далада {} градус, {}!'.format(temp, sky)
        self.speech_synthesizer.speak_text_async(weath).get()

    def say_ertegi(self):
        def list_html():
            ertegiler = []
            for page in range(2, 10):
                req = requests.get('https://www.zharar.com/kz/ertegi/page/{}/'.format(page))
                soup = BeautifulSoup(req.content, 'lxml')
                for el in soup.findAll(class_='block story shortstory'):
                    ertegi = str(el.find(class_='title')).split('=')[2]
                    href = (ertegi.split('"')[1])
                    ertegiler.append(href)
            return ertegiler

        try:
            ertegi = random.choice(list_html())

            req = requests.get(ertegi)
            soup = BeautifulSoup(req.text, 'lxml')
            texts = soup.find(class_='quote').text
            title = soup.find('h1').text
            self.speech_synthesizer.speak_text_async(title).get()
            self.speech_synthesizer.speak_text_async(texts).get()
        except Exception:
            self.say_ertegi()

    def today(self):
        d = datetime.datetime.today().strftime("%d-%m-%Y-%H-%M").split('-')
        w = datetime.date.today()
        week = datetime.datetime.weekday(w)
        weeks = ['Дүйсенбі', 'сейсенбі', 'сәрсенбі', 'бейсенбі', 'Жұма', 'сенбі', 'жексенбі']
        today = 'Бүгін {}-сі, {}-ші ай, {}-ші жыл,{}!'.format(d[0], d[1], d[2], weeks[week])
        self.speech_synthesizer.speak_text_async(today).get()

    def times(self):
        d = datetime.datetime.today().strftime("%d-%m-%Y-%H-%M").split('-')
        uaqyt = 'Қазір сағат {},{}!'.format(d[3], d[4])
        self.speech_synthesizer.speak_text_async(uaqyt).get()

    def siko(self):
        text = 'кеменемене бектебе, кеменеме бек. Жлоламана фомана, фомана сет. ауана беееже , бееже.'
        self.speech_synthesizer.speak_text_async(text).get()

    def news(self):

        req = requests.get('https://kaz.tengrinews.kz/')
        soup = BeautifulSoup(req.content, 'lxml')

        titles = []
        url = []

        for block in soup.findAll(class_='tn-tape-title'):
            href = 'https://kaz.tengrinews.kz' + block.attrs.get('href')
            title = block.text
            titles.append(title)
            url.append(href)
            if len(url) == 5:
                break
        self.speech_synthesizer.speak_text_async('Басты жаңалықтар !!!').get()
        for title in titles:
            self.speech_synthesizer.speak_text_async(title).get()

    def kurs(self):
        today = datetime.date.today()
        req = requests.get(
            'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/report?rates%5B%5D=5&rates%5B%5D=6&rates%5B%5D=8&rates%5B%5D=16&beginDate={}&endDate={}'.format(
                today, today))

        soup = BeautifulSoup(req.text, 'lxml')
        lst = []
        for value in soup.findAll(class_='text-center'):
            try:
                kurs = float(value.text)
                if kurs != 1:
                    lst.append(kurs)
            except Exception:
                continue
        text = "Доллар курсы - {} тенге,Евро курсы - {} тенге,Юань курсы - {} тенге,Рубль курсы - {} тенге".format(
            lst[0], lst[1], lst[2], lst[3])
        self.speech_synthesizer.speak_text_async(text).get()

    def svet_on(self):
        self.bulb.turn_on()

    def svet_off(self):
        self.bulb.turn_off()
