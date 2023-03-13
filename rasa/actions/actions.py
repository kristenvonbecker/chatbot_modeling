import logging

from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, BotUttered
from rasa_sdk import Action, Tracker
from rasa_sdk.forms import ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from typing import Any, Text, Dict, List
import os
import json
import pandas as pd
import ast
from fuzzywuzzy import fuzz, process
from nltk.tokenize import sent_tokenize

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


# import data needed for chatbot responses

home = os.getenv("PROJ_HOME")
exhibits_filepath = os.path.join(home, "data/chatbot_knowledgebase/institutional/exhibits.json")
galleries_filepath = os.path.join(home, "data/chatbot_knowledgebase/institutional/galleries.json")
articles_filepath = os.path.join(home, "data/chatbot_knowledgebase/subject_matter/encyclopedia_britannica.csv")

with open(exhibits_filepath, "r") as f:
    exhibits = json.load(f)

with open(galleries_filepath, "r") as f:
    galleries = json.load(f)

articles = pd.read_csv(articles_filepath,
                       header=0,
                       names=["Id", "Title", "Alt Title", "Field", "Is Person", "Text"],
                       index_col=0)

ids = articles.index.tolist()
titles = articles["Title"]
alt_titles = articles["Alt Title"].apply(lambda x: ast.literal_eval(x))
field = articles["Field"].apply(lambda x: ast.literal_eval(x))
is_person = articles["Is Person"]
text = articles["Text"]

alias_id_lookup = {}
title_aliases = []
for article_id, main_title, alt_titles in zip(ids, titles, alt_titles):
    aliases = [main_title] + alt_titles
    alias_id_lookup.update({article_id: aliases})
    title_aliases += aliases


text_id_lookup = {}
for article_id, text in zip(ids, text):
    text_id_lookup.update({article_id: text})


def get_title_matches(subject, threshold=90, scorer=fuzz.WRatio):
    matches = process.extract(subject, title_aliases, scorer=scorer, limit=5)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches


def get_text(article_id, num_sent=3):
    full_text = text_id_lookup[article_id]
    sentences = sent_tokenize(full_text)
    txt = " ".join(sentences[:num_sent])
    return txt


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: DomainDict
                  ) -> List[Dict[Text, Any]]:
        intro = domain["responses"]["utter_intro"][0]["text"]
        what_i_do = domain["responses"]["utter_what_i_do"][0]["text"]
        how_help = domain["responses"]["utter_how_help"][0]["text"]
        events = [
            SessionStarted(),
            BotUttered(text=intro),
            BotUttered(text=what_i_do),
            BotUttered(text=how_help),
            ActionExecuted("action_listen")
        ]
        return events


class ActionGetMatchIds(Action):
    def name(self) -> Text:
        return "action_get_match_ids"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
        subject = tracker.get_slot("subject")
        matches = []
        if subject:
            matches += get_title_matches(subject)
        match_ids = []
        for match in matches:
            for article_id, aliases in alias_id_lookup.items():
                if match in aliases:
                    match_ids.append(article_id)
        match_ids = list(set(match_ids))
        matches_available = True if match_ids else False
        return [
            SlotSet("match_ids", match_ids),
            SlotSet("matches_available", matches_available)
        ]


class ActionGiveExplanation(Action):
    def name(self) -> Text:
        return "action_give_explanation"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> List[Dict[Text, Any]]:
        subject = tracker.get_slot("subject")
        match_ids = tracker.get_slot("match_ids")
        matches_available = tracker.get_slot("matches_available")
        num_tries = int(tracker.get_slot("num_tries"))
        if not subject:
            return []
        if matches_available:
            explanation = get_text(match_ids[num_tries], num_sent=3)
            if num_tries == 0:
                dispatcher.utter_message(response="utter_found_something")
            else:
                dispatcher.utter_message(response="utter_found_something_else")
            dispatcher.utter_message(text=explanation)
            num_tries += 1
            matches_available = (len(match_ids) > num_tries)
            return [
                SlotSet("subject", subject),
                SlotSet("num_tries", num_tries),
                SlotSet("matches_available", matches_available)
            ]
        else:
            dispatcher.utter_message(response="utter_found_nothing_else")
            return [
                SlotSet("subject", None),
                SlotSet("match_ids", []),
                SlotSet("num_tries", 0)
            ]


class ActionResetSubject(Action):
    def name(self) -> Text:
        return "action_reset_subject"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("subject", None)]


class ActionResetMatchIds(Action):
    def name(self) -> Text:
        return "action_reset_match_ids"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("match_ids", [])]


class ActionResetMatchesAvailable(Action):
    def name(self) -> Text:
        return "action_reset_matches_available"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("matches_available", False)]


class ActionResetNumTries(Action):
    def name(self) -> Text:
        return "action_reset_num_tries"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("num_tries", 0)]
