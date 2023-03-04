# Use https://github.com/Uberi/speech_recognition
# python3 -m pip install git+https://github.com/openai/whisper.git soundfile

# brew install portaudio
# pip install pyaudio
# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

try:
    print("Whisper thinks you said " + r.recognize_whisper(audio, language="english"))
except sr.UnknownValueError:
    print("Whisper could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Whisper")