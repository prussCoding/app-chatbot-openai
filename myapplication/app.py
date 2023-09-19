#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import openai
import logging
import argparse
import pyttsx3
import threading
import speech_recognition as sr

from typing import List
from attrs import define
from datetime import datetime
from dotenv import dotenv_values
from speech_recognition.exceptions import UnknownValueError

# Setting Parameters agrs for program to run
parser  = argparse.ArgumentParser( prog='Speech-to-Text and OpenAI Chat Interface',description='Process speech to text to be send to OpenAI chat for a response')
parser.add_argument('-d', '--duration', dest='duration', type=int, help='set the lenght of time to listen to user voice input', required=True)
parser.add_argument('-c', '--conversation', dest='conversation', type=str, help='set the conversation.', required=True)

# Setting Params from Parser Arguments
params = parser.parse_args()

# Setting secrets for .env file
secrets = dotenv_values("../.env")

# Configure logging
current_date = datetime.now().strftime("%Y-%m-%d")

# Global Variables 
conversation = {}
text: str = None
conversation_dir: str = 'conversations'
duration: int = params.duration
filename_json: str = f'{conversation_dir}/{params.conversation}.json'
mymodule = 'myapplication'
engine = pyttsx3.init()


# Setting Properties for Pyttsx3
engine.setProperty('rate', secrets['PYTTSX_RATE'])
engine.setProperty('volume',secrets['PYTTSX_VOLUME'])


# Basic Configuration for Logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] -> %(message)s',
    level=logging.INFO,
    force=True,
    handlers=[
        logging.FileHandler(f'logs/{mymodule}-{str(current_date)}.log'),
        logging.StreamHandler()
    ]
)

# Initialize the speech recognizer
init_rec = sr.Recognizer()


@define
class Prompt:
    role: str
    content: str
    
    
    def render(self) -> None:
        """
        Render the Prompt as a dictionary.

        Returns:
            dict: A dictionary representing the Prompt.
        """
        return {"role": self.role, "content": self.content}

@define
class MessagePrompt:
    system: Prompt = []
    user: Prompt = []
    
    
    def render(self) -> None:
        """
        Render the MessagePrompt as a list of dictionaries.

        Returns:
            list: A list of dictionaries representing the MessagePrompt.
        """
        result = [prompt.render() for prompt in [self.system, self.user]]
        logging.debug(f'Class: MessagePrompt -> Method: render() -> Value: {result}')
        return result


@define
class ChatPrompt:
    api_key: str
    engine: str
    message: MessagePrompt
    response: List[str] = None
    
    
    def chat_completion(self):
        """
        Perform a chat completion using OpenAI's API.

        Returns:
            bool: True if the API call was successful, False otherwise.
        """
        if not self.api_key:
            return False
        openai.api_key = self.api_key
        self.response = openai.ChatCompletion.create(
            model=self.engine,
            messages=self.message.render()
        )
        logging.debug(f'Class: ChatPrompt -> Method: chat_completion() -> Value: {self.response}')
        return True
    
      
    def render(self) -> None:
        """
        Render the ChatPrompt and perform the chat completion.

        Returns:
            None
        """
        self.chat_completion()
        return True


def microphone_select():
    """
    Displays a list of available microphones and prompts the user to select a microphone index.
    
    Returns:
        int: The selected microphone index.
    """
    print('Microphone List:')
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  Microphone: [{index}] - {name}")
    return int(input('Select the mic input index (number)?'))


def countdown(t):
    """
    Countdown timer function.

    Args:
        t (int): Duration in seconds.

    Returns:
        None
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def speech_to_text(type, content, duration, mic) -> str:
    """
    Converts spoken language to text using a microphone.

    Args:
        content (str): The context or instruction for the user.
        duration (int): The duration in seconds to record audio.

    Returns:
        str: The recognized text from the spoken audio.
    """
    print(f'{content}')
    
    with sr.Microphone(device_index=mic) as source:
        audio_data = init_rec.record(source, duration=duration)
        logging.info("Recognizing your text.............")
        try: 
            global text 
            text = init_rec.recognize_google(audio_data)
            #with open(filename, 'a') as f:
            #    f.write(f'Speech ({type}):\n[{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}] {text}\n')
            logging.info(text)
            if not params.conversation in conversation:
                conversation[params.conversation] = []
            conversation[params.conversation].append(dict(
                datetime=datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                type=type,
                content=text,       
            ))
            logging.info(f'Conversation Dictionary:  {conversation}')
        except UnknownValueError as e:
            logging.warning(e)
    
    logging.debug(f'Module: myspeechtotext -> Method: speechtotext() -> Value: {text}')


def text_to_speech(message):
    """
    Converts the given message into speech.

    Parameters:
    - message (str): The message to be converted into speech.

    Returns:
    - None

    This function uses the text-to-speech engine to convert the given message into speech. It utilizes the `say` function from the engine which takes the message as input and outputs the corresponding speech. The `runAndWait` function is then called to ensure the speech is played immediately after it is generated.
    """
    engine.say(message)
    engine.runAndWait()


def run(type, duration, content, mic):
    """
    Run the speech to text conversion and countdown simultaneously using multi-threading.
    
    Args:
        type (str): The type of speech recognition to use.
        duration (int): The duration of the recording in seconds.
        content (str): The content to convert to text.
        mic (int): The microphone index to use for the recording.
    
    Returns:
        str: The converted text.
    """
    thread1 = threading.Thread(target=speech_to_text, kwargs={"content": content, "duration": duration, "mic": mic, "type": type})
    thread2 = threading.Thread(target=countdown, kwargs={"t": duration })
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    logging.debug(f'Module: myspeechtotext -> Method: run() -> Value: {text}')
    return text


def get_history_json(history):
    """
    Converts the given history into a JSON string.

    Parameters:
    - history (list): The history to be converted into a JSON string.

    Returns:
    - str: The JSON string containing the converted history.

    This function takes a history, which is a list of conversations, and converts it into a JSON string. Each conversation in the history consists of multiple parts, including context, question, and response. The function extracts the content of each part and creates a string in the format 'context, question? response' for each conversation. These strings are then added to a list. Finally, the list is joined using newlines to create a single JSON string representation of the history.
    """
    _ =  []
    for conversation in history:
        context  = [ content['content'] for content in conversation if content['type'] == 'context']
        question = [ content['content'] for content in conversation if content['type'] == 'question']
        response = [ content['content'] for content in conversation if content['type'] == 'response']
        _.append(f'{context[0]}, {question[0]}? {response[0]}')  
    return '\n'.join(_)


def main():
    """
    Run the main conversational loop, prompting the user for input and generating a response.

    Returns:
        None
    """
    mic = microphone_select()
    isMessageReady: bool = False
    while not isMessageReady:
        history_conversation = ''
        
        #if os.path.isfile(filename):
        #    with open(filename, 'r') as f:
        #        history_conversation = f.read()
        
        if os.path.isfile(filename_json):
            with open(filename_json, 'r') as f:
                _conversation = json.load(f) 
                history_conversation = get_history_json(_conversation)
                logging.info(f'Get History: {history_conversation}' )
                
        logging.debug(f'Method func(main) -> {history_conversation}')
        
        
        context = run('context', duration, 'Speak the system instruction or guidance to the AI model', mic )
        question = run('question', duration, "Speak the user's input or query", mic)
        if input('Is both system and user input ready to submit (y/n)?') == 'y':
            isMessageReady = True

            mysystem = Prompt(role='system', content=f'{history_conversation}\n{context}')
            myuser = Prompt(role='user', content=question)
            
            mymessage = MessagePrompt(
                system=mysystem,
                user=myuser
            )
            
            chat = ChatPrompt(
                api_key=secrets['API_KEY'],
                engine='gpt-3.5-turbo',
                message=mymessage,
            )
            
            chat.render()
            content = chat.response["choices"][0]["message"]["content"]
            logging.info(f'Chat Response: {content}')
            if not params.conversation in conversation:
                conversation[params.conversation] = []
                
            conversation[params.conversation].append(dict(
                datetime=datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                type='response',
                content=content  
            ))
            logging.info(f'Conversation Dictionary:  {conversation}')
            
            #with open(filename, 'a') as f:
            #    f.write(f'Response (chat):\n[{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}] {content}\n')
            
            existing_data = []
            if os.path.isfile(filename_json):
                with open(filename_json, "r") as json_file:
                    existing_data = json.load(json_file)
                
            # Append the new data to the existing JSON data
            existing_data.append(conversation[params.conversation])
            
            with open(filename_json, 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, indent=4)                    
                
            text_to_speech(content)
    
    engine.stop()

  
if __name__ == '__main__':
    main()
