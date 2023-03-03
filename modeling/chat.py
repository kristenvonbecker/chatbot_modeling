import os
import json
import numpy as np
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences
import colorama
from colorama import Fore, Style
import pickle

from dotenv import load_dotenv
load_dotenv()

colorama.init()

home = os.getenv("PROJ_HOME")
modeling_dir = os.path.join(home, "explorer_ai/modeling")
intents_filepath = os.path.join(modeling_dir, "intents.json")

with open(intents_filepath, "r") as infile:
    data = json.load(infile)

opening_prompt = '''Hello! I'm Explorer AI, an educational chatbot. 
I'm learning to answer questions about sciency stuff...so ask away! '''

def chat():
    model = keras.models.load_model("chat_model")

    with open("tokenizer.pickle", "rb") as handle:
        tokenizer = pickle.load(handle)

    with open("label_encoder.pickle", "rb") as enc:
        encoder = pickle.load(enc)

    max_len = 20

    while True:
        print(Fore.LIGHTBLUE_EX + "User: " + Style.RESET_ALL, end="")
        usr_in = input()
        if usr_in == "QUIT_NOW":
            break

        result = model.predict(pad_sequences(tokenizer.texts_to_sequences([usr_in]),
                                             truncating="post",
                                             maxlen=max_len))

        label = encoder.inverse_transform([np.argmax(result)])

        for item in data:
            if item["intent"] == label:
                print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, item["responses"])


print(Fore.YELLOW + "Start messaging with the bot. Type QUIT_NOW to stop.\n" + Style.RESET_ALL)
print(Fore.GREEN + "Chatbot: " + Style.RESET_ALL + opening_prompt + Style.RESET_ALL)

chat()