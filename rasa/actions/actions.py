import json

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from typing import Any, Text, Dict, List
import os
import pandas as pd
from fuzzywuzzy import fuzz

from dotenv import load_dotenv
load_dotenv();

# fuzzy matching threshold (max = 100)
T = 80

home = os.getenv("PROJ_HOME")
data_filepath = os.path.join(home, "explorer_ai/data/adv_data.json")

with open(data_filepath, "r") as infile:
    data_dict = json.load(infile)

df = pd.DataFrame(data_dict)

df_titles = df["title"]
df_alt_titles = df["alt_titles"]
df_field = df["field"]
df_person = df["is_person"]
df_text = df["text"]

titles_list = []
for main_title, alt_titles in zip(df_titles, df_alt_titles):
    these_titles = [main_title] + alt_titles
    titles_list.append(these_titles)

df = pd.DataFrame({"titles": titles_list, "field": df_field, "is_person": df_person, "text": df_text})


def is_match(text1, text2, threshold):
    return fuzz.token_sort_ratio(text1, text2) >= threshold


class ValidateExplanationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_explanation_form"

    def validate_subject(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        matches = []
        for titles in titles_list:
            for title in titles:
                if (score := fuzz.token_sort_ratio(slot_value, title)) >= T:
                    matches.append((titles[0], score))
        if matches:
            matches.sort(key=lambda i: i[1], reverse=True)
            return {"subject": matches[0][0]}
        else:
            dispatcher.utter_message(response="utter_ask_about_other")
            return {"subject": None}


class ActionGetResults(Action):
    def name(self) -> Text:
        return "action_get_results"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        subject = tracker.get_slot("subject")
        mask = df["titles"].apply(lambda x: any(is_match(y, subject, T) for y in x))
        results = df["text"][mask].tolist()

        return [SlotSet("match", results[0] if results is not None else "")]


class ActionResetSubject(Action):
    def name(self) -> Text:
        return "action_reset_subject"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("subject", None)]
