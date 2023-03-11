"""
Idea with this class is that it is an uninterrupted log of spoken audio.

Initially assume a single speaker.

Thinking that this can be used with asyncio...
"""

import logging
from multiprocessing import Manager, Process, log_to_stderr
from multiprocessing.managers import ValueProxy
from time import sleep

import speech_recognition as sr


class SpeechInput:

    def __init__(self, conversation_proxy: ValueProxy, logger: logging.Logger = None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(0)
        self.conversation_proxy = conversation_proxy
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        if logger is not None:
            self.logger = logger

    def start(self) -> sr.AudioData:
        self.logger.info("Listening in background")
        stop = self.recognizer.listen_in_background(self.microphone, self.transcribe, phrase_time_limit=20)
            
    
    def transcribe(self, recognizer: sr.Recognizer, audio: sr.AudioData):
        self.logger.info("Transcribing audio")
        try:
            transcription = recognizer.recognize_whisper(audio, language="english")
            if transcription.strip() != "":
                self.conversation_proxy.value = self.conversation_proxy.value + [
                    {"role": "user", "content": transcription}    
                ]
        except sr.UnknownValueError:
            self.logger.info("Whisper could not understand audio")
        except sr.RequestError as e:
            self.logger.info("Could not request results from Whisper")


def run_assistant(logger: logging.Logger, conversation_proxy: ValueProxy):
    logger.info("Assistant stream: Launched.")
    while True:
        sleep(1)
        #conversation_proxy.value = conversation_proxy.value + [
        #    {"role": "assistant", "content": "."}
        #] 
    
    # @TODO: each time a new user statement appears in the conversation, get a response from the chatbot.


def run_user(logger: logging.Logger, conversation_proxy: ValueProxy):
    logger.info("User stream: Launched.")
    speech_input = SpeechInput(conversation_proxy, logger)
    stop_input = speech_input.start()
    while True:
        sleep(1)
        logger.info(conversation_proxy.value)
    #conversation_proxy.value = conversation_proxy.value + [transcription]
    #logger.info(conversation_proxy.value)
    
    # Receive all input audio.
    # Segment into statements to pass to ChatGPT.

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = log_to_stderr()
    logger.setLevel(logging.INFO)

    manager = Manager()
    conversation = manager.Value("conversation", [])

    user_process = Process(target=run_user, args=(logger, conversation))
    assistant_process = Process(target=run_assistant, args=(logger, conversation))
    processes = [user_process, assistant_process]

    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
