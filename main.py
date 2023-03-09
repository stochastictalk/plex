from enum import Enum
import logging

from dotenv import dotenv_values
import openai
import pyttsx3
import re
import sounddevice as sd
import speech_recognition as sr
import torch



terminate_regex = re.compile(r"flex[^a-zA-Z0-9]+terminate", re.IGNORECASE)


class SpeechInput:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def record(self) -> sr.AudioData:
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
        return audio
    
    def transcribe(self, audio: sr.AudioData) -> str:
        try:
            return self.recognizer.recognize_whisper(audio, language="english")
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Whisper")


class SpeechOutputOld:

    def __init__(self):
        self.engine = pyttsx3.init()

    def play(self, statement: str):
        self.engine.say(statement)
        self.engine.runAndWait()

class SpeechOutput:

    def __init__(self):
        self.sample_rate = 48000
        self.speaker = "en_0"
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="en",
            speaker="v3_en"
        )

    def play(self, statement: str):
        audio = self.model.apply_tts(
            text=statement,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
        )

        sd.play(audio.numpy(), self.sample_rate, blocking=True)


class ConversationRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

class TerminateConversation(Exception):
    pass


class Conversation:

    def __init__(self):
        config = dotenv_values(".env")
        openai.api_key = config["OPENAI_API_KEY"]
        self.history = [
            {"role": "system", "content": "You are a helpful, wise-cracking assistant named FLEX."},
        ]
        
        self.speech_input = SpeechInput()
        self.speech_output = SpeechOutput()
        logging.info("Created speech input device.")

    def insert_statement(self, role: ConversationRole, speak: bool = False) -> None:
        if role == ConversationRole.USER:
            logging.info("Inserting user statement.")
            audio_clip = self.speech_input.record()
            logging.info("User recorded speech input.")
            statement = self.speech_input.transcribe(audio_clip) # @TODO handle transcription failure.
            logging.info(f"User speech audio transcribed to: '{statement}'.")

        elif role == ConversationRole.ASSISTANT:
            logging.info("Inserting assistant statement.")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.history
            ) # @TODO Handle API request failure.
            statement = response["choices"][0]["message"]["content"]
            logging.info(f"Assistant stated: '{statement}'.")
        
        else:
            raise ValueError("`role` should be a valid ConversationRole value.")

        if speak:
            self.speech_output.play(statement)
        
        self.history.append(
            {"role": role.value, "content": statement}            
        )
        
        if terminate_regex.search(statement) is not None:
            raise TerminateConversation()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    greeting = "FLEX online. Beepity-boopity. It's good to see you Jerome."
    goodbye = "Conversation terminated. FLEX going into standby."
    logging.info(greeting)
    conversation = Conversation()
    conversation.speech_output.play(greeting)
    try:
        while True:
            conversation.insert_statement(role=ConversationRole.USER)
            conversation.insert_statement(role=ConversationRole.ASSISTANT, speak=True)
    except TerminateConversation:
        conversation.speech_output.play(goodbye)
        logging.info(goodbye)