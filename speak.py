import pyttsx3
from gtts import gTTS
import os
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
import pyaudio
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

class Voice():
    @staticmethod
    def speak_pyttsx(words, rate, volume, voice):
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice].id)
        engine.say(words)
        engine.runAndWait()
    @staticmethod
    def speak_google(words):
        tts = gTTS(words)
        tts.save("voice-google.mp3")
        print(words)
        os.system("mplayer voice-google.mp3")
    @staticmethod
    def speak_ibm(*words):
        authenticator = IAMAuthenticator('RMIQ1HwIDakLulaTrMsWbfJeu87gT4l5_7xUVHnsTCv_')
        service = TextToSpeechV1(authenticator=authenticator)
        service.set_service_url('https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/0dc8fc0f-71b4-4636-b389-a92cd2fd182e')

        class Play(object):

            def __init__(self):
                self.format = pyaudio.paInt16
                self.channels = 1
                self.rate = 22050
                self.chunk = 1024
                self.pyaudio = None
                self.stream = None

            def start_streaming(self):
                self.pyaudio = pyaudio.PyAudio()
                self.stream = self._open_stream()
                self._start_stream()

            def _open_stream(self):
                stream = self.pyaudio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    output=True,
                    frames_per_buffer=self.chunk,
                    start=False
                )
                return stream

            def _start_stream(self):
                self.stream.start_stream()

            def write_stream(self, audio_stream):
                self.stream.write(audio_stream)

            def complete_playing(self):
                self.stream.stop_stream()
                self.stream.close()
                self.pyaudio.terminate()

        class MySynthesizeCallback(SynthesizeCallback):
            def __init__(self):
                SynthesizeCallback.__init__(self)
                self.play = Play()

            def on_connected(self):
                print('Opening stream to play')
                self.play.start_streaming()

            def on_error(self, error):
                print('Error received: {}'.format(error))

            def on_timing_information(self, timing_information):
                print(timing_information)

            def on_audio_stream(self, audio_stream):
                self.play.write_stream(audio_stream)

            def on_close(self):
                print('Completed synthesizing')
                self.play.complete_playing()

        test_callback = MySynthesizeCallback()
        if len(words) == 1:
            SSML_text = "<speak>"+ words[0]  +"</speak>"
        if len(words) == 2:
            SSML_text = """
            <speak version="1.0">
              <paragraph>
                <sentence>"""+ words[0] +"""</sentence>
                <s>"""+ words[1] +"""</s>
              </paragraph>
            </speak>"""

        service.synthesize_using_websocket(SSML_text,
                                           test_callback,
                                           accept='audio/wav',
                                           voice="en-US_HenryV3Voice"
                                           )
    @staticmethod
    def speak_mimic(*words):
        if len(words) == 1:
            os.system('cd ~/mimic1/ && ./mimic -t "'+ words[0] +'" ')
        if len(words) == 2:
            os.system('cd ~/mimic1/ && ./mimic -t "'+ words[0] +', '+ words[1] +'"')