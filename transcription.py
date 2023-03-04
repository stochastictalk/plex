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

with open("audio_file.wav", "wb") as file:
    file.write(audio.get_wav_data())

try:
    print("Whisper thinks you said " + r.recognize_whisper(audio, language="english"))
except sr.UnknownValueError:
    print("Whisper could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Whisper")

import os
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(model="text-davinci-003", prompt="Say this is a test", temperature=0, max_tokens=7)