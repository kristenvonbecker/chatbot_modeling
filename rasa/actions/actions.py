from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, BotUttered
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import ValidationAction
from typing import Any, Text, Dict, List
from actions import scripts
from actions import knowledgebase
from dotenv import load_dotenv
import logging
import random
from importlib import reload
reload(scripts)
reload(knowledgebase)

load_dotenv()
logger = logging.getLogger(__name__)


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
            matches += scripts.get_title_matches(subject)
        match_ids = []
        for match in matches:
            for article_id, aliases in knowledgebase.alias_id_lookup.items():
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
            explanation = scripts.get_text(match_ids[num_tries])
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


class ActionGiveFaveExhibit(Action):
    def name(self) -> Text:
        return "action_give_fave_exhibit"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> List[Dict[Text, Any]]:
        exhibit_id, exhibit_name, fun_fact = scripts.get_fave_exhibit()
        if fun_fact:
            fun_fact_alt = fun_fact[0].lower() + fun_fact[1:].rstrip(".")
            msgs = [
                f"My favorite exhibit at the Exploratorium is {exhibit_name}, because {fun_fact_alt}.",
                f"I like to recommend an exhibit called {exhibit_name}. {fun_fact}",
                f"One of the highlights of the Exploratorium is {exhibit_name}, since {fun_fact_alt}."
            ]
        else:
            msgs = [
                f"My favorite exhibit at the Exploratorium is {exhibit_name}.",
                f"I like to recommend an exhibit called {exhibit_name}.",
                f"One of the highlights of the Exploratorium is {exhibit_name}."
            ]
        msg = random.choice(msgs)
        dispatcher.utter_message(text=msg)
        return []


class ActionResetExplanationSlots(Action):
    def name(self) -> Text:
        return "action_reset_explanation_slots"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [
            SlotSet("subject", None),
            SlotSet("match_ids", []),
            SlotSet("matches_available", False),
            SlotSet("num_tries", 0)
        ]


class ActionResetSubject(Action):
    def name(self) -> Text:
        return "action_reset_subject"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("subject", None)]
