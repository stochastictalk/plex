"""
Idea with this class is that it is an uninterrupted log of spoken audio.

Initially assume a single speaker.

Thinking that this can be used with asyncio...
"""

from multiprocessing import Manager, Process
from multiprocessing.managers import ValueProxy
from time import sleep

import speech_recognition as sr


class SpeechInput:

    def __init__(self, conversation_proxy: ValueProxy):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(0)
        self.conversation_proxy = conversation_proxy
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def start(self) -> sr.AudioData:
        print("Listening")
        stop = self.recognizer.listen_in_background(self.microphone, self.transcribe, phrase_time_limit=5)
            
    
    def transcribe(self, recognizer: sr.Recognizer, audio: sr.AudioData):
        print("Transcribing")
        try:
            transcription = recognizer.recognize_whisper(audio, language="english")
            self.conversation_proxy.value = self.conversation_proxy.value + [
                {"role": "user", "content": transcription}    
            ]
            print(self.conversation_proxy.value)
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Whisper")


def run_assistant(conversation_proxy: ValueProxy):
    while True:
        sleep(1)
        conversation_proxy.value = conversation_proxy.value + [
            {"role": "assistant", "content": "hey"}
        ] 
    
    # @TODO: each time a new user statement appears in the conversation, get a response from the chatbot.


def run_user(conversation_proxy: ValueProxy):
    print("User stream: Launched.")
    speech_input = SpeechInput(conversation_proxy)
    stop_input = speech_input.start()
    while True:
        sleep(1)
    #conversation_proxy.value = conversation_proxy.value + [transcription]
    #print(conversation_proxy.value)
    
    # Receive all input audio.
    # Segment into statements to pass to ChatGPT.

if __name__ == '__main__':
    manager = Manager()
    conversation = manager.Value("conversation", [])

    user_process = Process(target=run_user, args=(conversation,))
    assistant_process = Process(target=run_assistant, args=(conversation,))
    processes = [user_process, assistant_process]

    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
